"""FFprobe-backed media inspection and acceptance checks."""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path


class MediaVerificationError(RuntimeError):
    pass


def probe_media(path: str | Path) -> dict:
    target = Path(path)
    if not target.is_file() or target.stat().st_size <= 0:
        raise MediaVerificationError(f"media file is missing or empty: {target}")
    executable = shutil.which("ffprobe")
    if not executable:
        raise MediaVerificationError("ffprobe is not available on PATH")
    result = subprocess.run(
        [executable, "-v", "error", "-show_format", "-show_streams", "-of", "json", str(target)],
        capture_output=True, text=True)
    if result.returncode:
        raise MediaVerificationError(f"ffprobe failed: {(result.stderr or '').strip()}")
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise MediaVerificationError("ffprobe returned invalid JSON") from exc


def duration_seconds(data: dict) -> float:
    try:
        value = float(data["format"]["duration"])
    except (KeyError, TypeError, ValueError) as exc:
        raise MediaVerificationError("media has no valid duration") from exc
    if value <= 0:
        raise MediaVerificationError("media duration must be positive")
    return value


def _fps(value: str) -> float:
    numerator, denominator = value.split("/", 1)
    return float(numerator) / float(denominator)


def verify_chapter_output(path: str | Path, expectations: dict | None = None) -> dict:
    data = probe_media(path)
    expectations = expectations or {}
    videos = [s for s in data.get("streams", []) if s.get("codec_type") == "video"]
    audios = [s for s in data.get("streams", []) if s.get("codec_type") == "audio"]
    if len(videos) != 1 or len(audios) != 1:
        raise MediaVerificationError("chapter output must contain exactly one video and one audio stream")
    duration_seconds(data)
    video, audio = videos[0], audios[0]
    checks = {"width": video.get("width"), "height": video.get("height"),
              "video_codec": video.get("codec_name"), "audio_codec": audio.get("codec_name")}
    for key, actual in checks.items():
        expected = expectations.get(key)
        if expected is not None and actual != expected:
            raise MediaVerificationError(f"expected {key}={expected!r}, got {actual!r}")
    if "fps" in expectations:
        actual_fps = _fps(video.get("avg_frame_rate", "0/1"))
        if abs(actual_fps - float(expectations["fps"])) > 0.01:
            raise MediaVerificationError(f"expected fps={expectations['fps']}, got {actual_fps}")
    stream_durations = []
    for stream in (video, audio):
        try:
            stream_durations.append(float(stream["duration"]))
        except (KeyError, TypeError, ValueError):
            pass
    if len(stream_durations) == 2 and abs(stream_durations[0] - stream_durations[1]) > expectations.get("duration_tolerance", 1 / 30):
        raise MediaVerificationError("audio and video stream durations do not agree")
    return data

