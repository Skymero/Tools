"""Offline neural text-to-speech using Kokoro-82M.

Reads a UTF-8 text file and writes 24 kHz mono narration as WAV (or MP3 via
ffmpeg). Optional heavyweight dependencies (kokoro, soundfile, misaki) are
lazy-imported so the script's argument handling and validation work without
them installed.
"""

import argparse
import math
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SAMPLE_RATE = 24_000
DEFAULT_VOICE = "af_heart"
DEFAULT_LANGUAGE = "en-us"
DEFAULT_SPEED = 1.0
REPO_ID = "hexgrad/Kokoro-82M"

# External CLI language names mapped to Kokoro's one-character pipeline codes.
LANGUAGE_CODES = {
    "en-us": "a",
    "en-gb": "b",
    "es": "e",
    "fr-fr": "f",
    "hi": "h",
    "it": "i",
    "ja": "j",
    "pt-br": "p",
    "cmn": "z",
}

SUPPORTED_SUFFIXES = {".wav", ".mp3"}


class _ArgumentParser(argparse.ArgumentParser):
    """ArgumentParser that exits 1 (not argparse's default 2) on bad input."""

    def error(self, message):
        self.exit(1, f"{self.prog}: error: {message}\n")


def _positive_speed(value):
    """Argparse type: finite float strictly greater than zero."""
    try:
        speed = float(value)
    except (TypeError, ValueError):
        raise argparse.ArgumentTypeError(
            f"invalid speed {value!r}: expected a number")
    if not math.isfinite(speed) or speed <= 0:
        raise argparse.ArgumentTypeError(
            f"speed must be a finite number greater than zero, got {value!r}")
    return speed


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse CLI arguments into (input, output, voice, lang, speed)."""
    parser = _ArgumentParser(
        description="Convert a text file to narrated audio with Kokoro-82M "
                    "(offline, local neural TTS).")
    parser.add_argument("input", type=Path,
                        help="input .txt file to narrate")
    parser.add_argument("output", type=Path, nargs="?", default=None,
                        help="output .wav or .mp3 path (default: input name "
                             "with a .wav extension)")
    parser.add_argument("--voice", type=str.lower, default=DEFAULT_VOICE,
                        help=f"Kokoro voice name (default: {DEFAULT_VOICE})")
    parser.add_argument("--lang", choices=sorted(LANGUAGE_CODES),
                        default=DEFAULT_LANGUAGE,
                        help=f"narration language (default: {DEFAULT_LANGUAGE})")
    parser.add_argument("--speed", type=_positive_speed, default=DEFAULT_SPEED,
                        help=f"speech rate multiplier (default: {DEFAULT_SPEED})")
    args = parser.parse_args(argv)
    if args.output is None:
        args.output = args.input.with_suffix(".wav")
    return args


def _extract_audio(result):
    """Pull the audio payload out of a Kokoro result.

    Kokoro 0.9.4 yields (graphemes, phonemes, audio) tuples; newer versions
    expose result objects with an .audio attribute.
    """
    audio = getattr(result, "audio", None)
    if audio is None and isinstance(result, (tuple, list)) and len(result) >= 3:
        audio = result[2]
    return audio


def _to_1d_samples(audio):
    """Convert tensor/ndarray audio into a flat sample sequence."""
    if hasattr(audio, "detach"):
        audio = audio.detach().cpu().numpy()
    elif hasattr(audio, "cpu") and hasattr(audio, "numpy"):
        audio = audio.cpu().numpy()
    if hasattr(audio, "reshape"):
        audio = audio.reshape(-1)
    return audio


def _count_samples(samples):
    """Sample count without truth-value testing on arrays/tensors."""
    size = getattr(samples, "size", None)
    if size is not None:
        return int(size)
    return len(samples)


def create_narration(input_path: Path, output_path: Path, voice: str,
                     language: str, speed: float) -> float:
    """Synthesize input_path text to output_path; return duration seconds.

    Raises normal exceptions (FileNotFoundError, ValueError, RuntimeError,
    subprocess errors) on failure; the caller owns user-facing messaging.
    """
    # Pre-flight validation (before any heavyweight imports or I/O).
    if not input_path.is_file():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    suffix = output_path.suffix.lower()
    if suffix not in SUPPORTED_SUFFIXES:
        raise ValueError(
            f"Output file must end in .wav or .mp3, got '{output_path.suffix}'")
    if not output_path.parent.is_dir():
        raise FileNotFoundError(
            f"Output directory not found: {output_path.parent}")
    if not voice:
        raise ValueError("Voice must not be empty")
    expected_prefix = LANGUAGE_CODES[language]
    if voice[0] != expected_prefix:
        raise ValueError(
            f"Voice '{voice}' does not match language '{language}' "
            f"(voices for this language start with '{expected_prefix}')")
    ffmpeg_exe = None
    if suffix == ".mp3":
        ffmpeg_exe = shutil.which("ffmpeg")
        if ffmpeg_exe is None:
            raise RuntimeError("MP3 output requires FFmpeg on PATH")

    # Read the script; utf-8-sig tolerates an optional UTF-8 BOM.
    text = input_path.read_text(encoding="utf-8-sig").strip()
    if not text:
        raise ValueError("Input file is empty")

    # Heavy optional dependencies load only after validation succeeds.
    try:
        from kokoro import KPipeline
        import soundfile as sf
    except ImportError as exc:
        raise RuntimeError(
            "Kokoro dependencies are not installed; run: "
            "pip install -r requirements-kokoro.txt") from exc

    temp_paths: list[Path] = []
    try:
        pipeline = KPipeline(
            lang_code=LANGUAGE_CODES[language],
            repo_id=REPO_ID,
            device="cpu",
        )

        # Temp files live beside the output so the final replace() stays
        # on the same filesystem (atomic rename).
        with tempfile.NamedTemporaryFile(
                delete=False, dir=output_path.parent,
                prefix=f".{output_path.stem}-", suffix=".wav") as tmp:
            temp_wav = Path(tmp.name)
        temp_paths.append(temp_wav)

        # Stream every generated chunk into one mono PCM16 24 kHz WAV.
        total_samples = 0
        with sf.SoundFile(
                str(temp_wav), mode="w", samplerate=SAMPLE_RATE, channels=1,
                subtype="PCM_16", format="WAV") as wav_file:
            for result in pipeline(text, voice=voice, speed=speed):
                audio = _extract_audio(result)
                if audio is None:
                    continue
                samples = _to_1d_samples(audio)
                count = _count_samples(samples)
                if count == 0:
                    continue
                wav_file.write(samples)
                total_samples += count

        if total_samples == 0:
            raise RuntimeError("Kokoro produced no audio")

        if suffix == ".mp3":
            # Encode the WAV to MP3 with the ffmpeg resolved earlier.
            with tempfile.NamedTemporaryFile(
                    delete=False, dir=output_path.parent,
                    prefix=f".{output_path.stem}-", suffix=".mp3") as tmp:
                temp_mp3 = Path(tmp.name)
            temp_paths.append(temp_mp3)
            try:
                subprocess.run(
                    [ffmpeg_exe, "-y", "-hide_banner", "-loglevel", "error",
                     "-i", str(temp_wav), "-codec:a", "libmp3lame",
                     "-b:a", "192k", str(temp_mp3)],
                    check=True, capture_output=True, text=True)
            except subprocess.CalledProcessError as exc:
                detail = (exc.stderr or "").strip()
                raise RuntimeError(
                    f"FFmpeg MP3 encoding failed: {detail}"
                    if detail else "FFmpeg MP3 encoding failed") from exc
            finished_path = temp_mp3
        else:
            finished_path = temp_wav

        # Publish the finished file atomically (existing output is replaced).
        finished_path.replace(output_path)
        return total_samples / SAMPLE_RATE
    finally:
        # Remove any intermediates still on disk (the moved finished temp is
        # already gone, so missing_ok keeps this safe).
        for temp_path in temp_paths:
            temp_path.unlink(missing_ok=True)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point: parse args, narrate, report. Returns an exit code."""
    args = parse_args(argv)
    try:
        duration = create_narration(
            args.input, args.output, args.voice, args.lang, args.speed)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    print(f"Successfully created narration: {args.output}")
    print(f"Duration: {duration:.2f} seconds")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
