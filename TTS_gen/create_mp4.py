"""Create a narrated MP4 from a strict scene timeline."""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from media_probe import duration_seconds, probe_media
from timeline_validator import validate_timeline

OUTPUT_WIDTH, OUTPUT_HEIGHT, OUTPUT_FPS = 1080, 1920, 30


class RenderError(RuntimeError):
    pass


def _tool(name):
    value = shutil.which(name)
    if not value:
        raise RenderError(f"{name} is not available on PATH")
    return value


def _run(command):
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode:
        detail = (result.stderr or result.stdout or "unknown error").strip()
        raise RenderError(f"FFmpeg failed: {detail}")


def _render_duration_tolerance(scene_count, fps, override=None):
    """Allow one frame of quantization per independently rendered segment."""
    if override is not None:
        return override
    return max(1 / fps, scene_count / fps)


def _video_filter(scene, width, height, fps):
    base = f"scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:black,setsar=1"
    motion, intensity = scene["motion"], scene["intensity"]
    if motion == "push_in":
        return base + f",zoompan=z='min(zoom+{intensity},1.5)':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d=1:s={width}x{height}:fps={fps}"
    if motion == "pull_out":
        return base + f",zoompan=z='max(1.5-on*{intensity},1.0)':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d=1:s={width}x{height}:fps={fps}"
    if motion in {"pan_left", "pan_right"}:
        x = "iw-iw/zoom" if motion == "pan_left" else "0"
        return base + f",zoompan=z=1.1:x='{x}':y='ih/2-ih/zoom/2':d=1:s={width}x{height}:fps={fps}"
    return base + f",fps={fps}"


def create_video_from_timeline(audio_file, images_dir, timeline_file, output_file,
                               *, width=OUTPUT_WIDTH, height=OUTPUT_HEIGHT,
                               fps=OUTPUT_FPS, duration_tolerance=None):
    """Render one strict timeline. Returns True; raises on any failure."""
    ffmpeg, _ = _tool("ffmpeg"), _tool("ffprobe")
    audio, images = Path(audio_file).resolve(), Path(images_dir).resolve()
    timeline, output = Path(timeline_file).resolve(), Path(output_file).resolve()
    if not audio.is_file():
        raise FileNotFoundError(f"audio file not found: {audio}")
    audio_duration = duration_seconds(probe_media(audio))
    validated = validate_timeline(timeline, images, audio_duration=audio_duration,
                                  fps=fps, tolerance=duration_tolerance)
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".render-", dir=output.parent) as temp_name:
        temp, segments = Path(temp_name), []
        for index, scene in enumerate(validated["scenes"]):
            segment = temp / f"segment-{index:04d}.mp4"
            duration = scene["end"] - scene["start"]
            _run([ffmpeg, "-y", "-hide_banner", "-loglevel", "error", "-loop", "1",
                  "-framerate", str(fps), "-i", str(images / scene["image"]),
                  "-vf", _video_filter(scene, width, height, fps), "-t", f"{duration:.6f}",
                  "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "medium", str(segment)])
            segments.append(segment)
        concat = temp / "concat.txt"
        concat.write_text("".join(f"file '{p.as_posix()}'\n" for p in segments), encoding="utf-8")
        video = temp / "video.mp4"
        _run([ffmpeg, "-y", "-hide_banner", "-loglevel", "error", "-f", "concat", "-safe", "0",
              "-i", str(concat), "-c", "copy", str(video)])
        video_duration = duration_seconds(probe_media(video))
        tolerance = _render_duration_tolerance(
            len(validated["scenes"]), fps, duration_tolerance)
        if abs(video_duration - audio_duration) > tolerance:
            raise RenderError(f"rendered video duration {video_duration:.3f}s differs from audio {audio_duration:.3f}s")
        temp_output = temp / "final.mp4"
        _run([ffmpeg, "-y", "-hide_banner", "-loglevel", "error", "-i", str(video), "-i", str(audio),
              "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", str(temp_output)])
        os.replace(temp_output, output)
    return True


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("audio_file"); parser.add_argument("images_dir"); parser.add_argument("timeline_file")
    parser.add_argument("output_file", nargs="?", default="output.mp4")
    parser.add_argument("--width", type=int, default=OUTPUT_WIDTH)
    parser.add_argument("--height", type=int, default=OUTPUT_HEIGHT)
    parser.add_argument("--fps", type=int, default=OUTPUT_FPS)
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    try:
        create_video_from_timeline(args.audio_file, args.images_dir, args.timeline_file,
                                   args.output_file, width=args.width, height=args.height, fps=args.fps)
    except Exception as exc:
        print(f"Error: {exc}")
        return 1
    print(f"Successfully created video: {args.output_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
