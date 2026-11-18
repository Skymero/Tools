"""Create per-scene narration and a cumulative measured timeline."""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

from media_probe import duration_seconds, probe_media
from text_to_speech_kokoro import DEFAULT_LANGUAGE, DEFAULT_SPEED, DEFAULT_VOICE, create_narration
from timeline_validator import validate_scene_plan, validate_timeline


def paragraphs(text):
    import re
    return [part.strip() for part in re.split(r"\n\s*\n+", text.replace("\r\n", "\n").strip()) if part.strip()]


def generate_scene_audio(chapter_path, plan, artwork, workspace, *, voice=DEFAULT_VOICE,
                         language=DEFAULT_LANGUAGE, speed=DEFAULT_SPEED, fps=30):
    root = Path(workspace); clips = root / "scene-audio"; clips.mkdir(parents=True, exist_ok=True)
    parts = paragraphs(Path(chapter_path).read_text(encoding="utf-8-sig"))
    checked = validate_scene_plan(plan, len(parts), set(artwork))
    scenes, cursor = [], 0.0
    for index, item in enumerate(checked["scenes"], 1):
        text = "\n\n".join(parts[item["paragraph_start"] - 1:item["paragraph_end"]])
        source, clip = clips / f"scene-{index:04d}.txt", clips / f"scene-{index:04d}.wav"
        source.write_text(text, encoding="utf-8")
        create_narration(source, clip, voice, language, speed)
        duration = duration_seconds(probe_media(clip)); end = cursor + duration
        scenes.append({"name": f"scene-{index:04d}", "image": artwork[item["image_id"]],
                       "start": cursor, "end": end, "motion": item["motion"], "intensity": item["intensity"]})
        cursor = end
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg: raise RuntimeError("ffmpeg is not available on PATH")
    concat = clips / "concat.txt"; concat.write_text("".join(f"file '{p.as_posix()}'\n" for p in sorted(clips.glob("scene-*.wav"))), encoding="utf-8")
    narration = root / "narration.wav"
    result = subprocess.run([ffmpeg, "-y", "-hide_banner", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(concat), "-c", "copy", str(narration)], capture_output=True, text=True)
    if result.returncode: raise RuntimeError(f"scene audio concatenation failed: {result.stderr.strip()}")
    timeline = {"scenes": scenes}; timeline_path = root / "video-timeline.json"
    timeline_path.write_text(json.dumps(timeline, indent=2) + "\n", encoding="utf-8")
    validate_timeline(timeline, root / "images", audio_duration=duration_seconds(probe_media(narration)), fps=fps)
    return timeline_path, narration

