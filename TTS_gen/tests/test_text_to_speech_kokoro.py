"""Unit tests for text_to_speech_kokoro.py.

All Kokoro/soundfile interactions are faked via sys.modules injection, so the
suite runs without the optional heavyweight dependencies and never downloads
a model.
"""

import contextlib
import io
import subprocess
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import text_to_speech_kokoro as tts_kokoro


def make_fake_kokoro(chunks=None, error=None):
    """Build a fake `kokoro` module exposing a recording KPipeline."""
    module = types.ModuleType("kokoro")
    init_calls = []
    synth_calls = []

    class KPipeline:
        def __init__(self, **kwargs):
            init_calls.append(kwargs)

        def __call__(self, text, voice=None, speed=None):
            synth_calls.append({"text": text, "voice": voice, "speed": speed})
            if error is not None:
                raise error
            return iter(list(chunks or []))

    module.KPipeline = KPipeline
    return module, init_calls, synth_calls


class FakeSoundFile:
    """Records every write() per path instead of touching real audio I/O."""

    writes = {}
    open_kwargs = {}

    def __init__(self, path, mode="r", **kwargs):
        self.path = path
        FakeSoundFile.open_kwargs[path] = dict(kwargs)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def write(self, samples):
        FakeSoundFile.writes.setdefault(self.path, []).append(list(samples))


def make_fake_soundfile():
    """Build a fake `soundfile` module sharing the class-level write log."""
    FakeSoundFile.writes = {}
    FakeSoundFile.open_kwargs = {}
    module = types.ModuleType("soundfile")
    module.SoundFile = FakeSoundFile
    return module


def run_main(argv):
    """Run main() capturing exit code (incl. SystemExit), stdout, stderr."""
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            code = tts_kokoro.main(argv)
        except SystemExit as exc:
            code = exc.code
    return code, out.getvalue(), err.getvalue()


def leftover_temps(directory):
    return [p for p in Path(directory).iterdir() if p.name.startswith(".")]


class ParseArgsTests(unittest.TestCase):
    def test_defaults(self):
        args = tts_kokoro.parse_args(["input.txt"])
        self.assertEqual(args.input, Path("input.txt"))
        self.assertEqual(args.output, Path("input.wav"))
        self.assertEqual(args.voice, "af_heart")
        self.assertEqual(args.lang, "en-us")
        self.assertEqual(args.speed, 1.0)


class ValidationTests(unittest.TestCase):
    def test_nonpositive_and_nonfinite_speed_rejected(self):
        for bad in ("0", "-2", "nan", "inf", "abc"):
            code, _, err = run_main(["in.txt", "--speed", bad])
            self.assertEqual(code, 1, bad)
            self.assertTrue(err.strip(), bad)

    def test_missing_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp) / "missing.txt"
            code, _, err = run_main([str(missing)])
            self.assertEqual(code, 1)
            self.assertIn("not found", err.lower())

    def test_empty_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "empty.txt"
            src.write_text("   \n\t  ", encoding="utf-8")
            code, _, err = run_main([str(src)])
            self.assertEqual(code, 1)
            self.assertIn("Input file is empty", err)

    def test_unsupported_extension(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "in.txt"
            src.write_text("hello", encoding="utf-8")
            code, _, err = run_main([str(src), str(Path(tmp) / "out.ogg")])
            self.assertEqual(code, 1)
            self.assertIn(".wav or .mp3", err)

    def test_voice_language_mismatch(self):
        fake_kokoro, init_calls, _ = make_fake_kokoro()
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "in.txt"
            src.write_text("hello", encoding="utf-8")
            with patch.dict(sys.modules, {"kokoro": fake_kokoro,
                                          "soundfile": make_fake_soundfile()}):
                code, _, err = run_main(
                    [str(src), str(Path(tmp) / "out.wav"),
                     "--voice", "af_heart", "--lang", "en-gb"])
            self.assertEqual(code, 1)
            self.assertIn("does not match language", err)
            self.assertEqual(init_calls, [])

    def test_mp3_requires_ffmpeg(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "in.txt"
            src.write_text("hello", encoding="utf-8")
            with patch.object(tts_kokoro.shutil, "which", return_value=None):
                code, _, err = run_main(
                    [str(src), str(Path(tmp) / "out.mp3")])
            self.assertEqual(code, 1)
            self.assertIn("MP3 output requires FFmpeg on PATH", err)


class SynthesisTests(unittest.TestCase):
    def _patched(self, chunks=None, error=None):
        fake_kokoro, init_calls, synth_calls = make_fake_kokoro(
            chunks=chunks, error=error)
        fake_sf = make_fake_soundfile()
        ctx = patch.dict(sys.modules,
                         {"kokoro": fake_kokoro, "soundfile": fake_sf})
        return ctx, init_calls, synth_calls

    def test_bom_input_two_chunks_wav(self):
        chunks = [("g", "p", [0.1] * 24000), ("g", "p", [0.2] * 12000)]
        ctx, init_calls, synth_calls = self._patched(chunks=chunks)
        with tempfile.TemporaryDirectory() as tmp, ctx:
            src = Path(tmp) / "in.txt"
            src.write_bytes("﻿Hello world".encode("utf-8"))
            out = Path(tmp) / "out.wav"
            code, stdout, _ = run_main([str(src), str(out)])
            self.assertEqual(code, 0)
            self.assertTrue(out.exists())
            self.assertIn("Duration: 1.50 seconds", stdout)
            writes = FakeSoundFile.writes
            all_written = [s for path in writes for s in writes[path]]
            self.assertEqual(all_written, [[0.1] * 24000, [0.2] * 12000])
            self.assertEqual(init_calls[0]["lang_code"], "a")
            self.assertEqual(synth_calls[0]["voice"], "af_heart")
            self.assertEqual(leftover_temps(tmp), [])

    def test_zero_samples_fails(self):
        ctx, _, _ = self._patched(chunks=[])
        with tempfile.TemporaryDirectory() as tmp, ctx:
            src = Path(tmp) / "in.txt"
            src.write_text("hello", encoding="utf-8")
            out = Path(tmp) / "out.wav"
            code, _, err = run_main([str(src), str(out)])
            self.assertEqual(code, 1)
            self.assertIn("Kokoro produced no audio", err)
            self.assertFalse(out.exists())
            self.assertEqual(leftover_temps(tmp), [])

    def test_pipeline_exception_cleans_up(self):
        ctx, _, _ = self._patched(error=RuntimeError("synthesis exploded"))
        with tempfile.TemporaryDirectory() as tmp, ctx:
            src = Path(tmp) / "in.txt"
            src.write_text("hello", encoding="utf-8")
            out = Path(tmp) / "out.wav"
            code, _, err = run_main([str(src), str(out)])
            self.assertEqual(code, 1)
            self.assertIn("Error: synthesis exploded", err)
            self.assertFalse(out.exists())
            self.assertEqual(leftover_temps(tmp), [])

    def test_mp3_success_via_ffmpeg(self):
        chunks = [("g", "p", [0.5] * 24000)]
        ctx, _, _ = self._patched(chunks=chunks)
        commands = []

        def fake_run(cmd, **kwargs):
            commands.append(cmd)
            Path(cmd[-1]).write_bytes(b"fake mp3")
            return subprocess.CompletedProcess(cmd, 0, "", "")

        with tempfile.TemporaryDirectory() as tmp, ctx, \
                patch.object(tts_kokoro.shutil, "which",
                             return_value="C:\\ffmpeg\\ffmpeg.exe"), \
                patch.object(tts_kokoro.subprocess, "run",
                             side_effect=fake_run):
            src = Path(tmp) / "in.txt"
            src.write_text("hello", encoding="utf-8")
            out = Path(tmp) / "out.mp3"
            code, stdout, _ = run_main([str(src), str(out)])
            self.assertEqual(code, 0)
            self.assertTrue(out.exists())
            self.assertEqual(out.read_bytes(), b"fake mp3")
            cmd = commands[0]
            self.assertIn("libmp3lame", cmd)
            self.assertIn("192k", cmd)
            self.assertIn("Duration: 1.00 seconds", stdout)
            self.assertEqual(leftover_temps(tmp), [])


if __name__ == "__main__":
    unittest.main()
