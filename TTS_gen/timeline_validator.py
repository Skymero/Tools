"""Strict validation for authored timelines and generated scene plans."""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

MOTIONS = {"static", "push_in", "pull_out", "pan_left", "pan_right"}
TIMELINE_KEYS = {"name", "image", "start", "end", "motion", "intensity"}
PLAN_KEYS = {"paragraph_start", "paragraph_end", "image_id", "motion", "intensity"}


class ValidationError(ValueError):
    pass


def _load(value: Any) -> dict:
    if isinstance(value, (str, Path)):
        with Path(value).open(encoding="utf-8-sig") as stream:
            value = json.load(stream)
    if not isinstance(value, dict) or set(value) != {"scenes"}:
        raise ValidationError("top level must contain only 'scenes'")
    if not isinstance(value["scenes"], list) or not value["scenes"]:
        raise ValidationError("scenes must be a non-empty array")
    return value


def _number(scene: dict, field: str, index: int) -> float:
    value = scene.get(field)
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValidationError(f"scene {index} field '{field}' must be a finite number")
    return float(value)


def _common(scene: dict, index: int, allowed: set[str]) -> tuple[str, float]:
    unknown = set(scene) - allowed
    missing = allowed - {"name"} - set(scene)
    if unknown:
        raise ValidationError(f"scene {index} unknown field(s): {', '.join(sorted(unknown))}")
    if missing:
        raise ValidationError(f"scene {index} missing field(s): {', '.join(sorted(missing))}")
    motion = scene.get("motion")
    if motion not in MOTIONS:
        raise ValidationError(f"scene {index} field 'motion' must be one of {sorted(MOTIONS)}")
    intensity = _number(scene, "intensity", index)
    if not 0 <= intensity <= 1:
        raise ValidationError(f"scene {index} field 'intensity' must be between 0 and 1")
    return motion, intensity


def validate_timeline(value: Any, images_dir: str | Path, *, audio_duration: float | None = None,
                      fps: int = 30, tolerance: float | None = None) -> dict:
    data = _load(value)
    root = Path(images_dir).resolve()
    if not root.is_dir():
        raise ValidationError(f"images directory not found: {root}")
    frame = 1 / fps
    tolerance = frame if tolerance is None else tolerance
    normalized = []
    previous_end = 0.0
    for index, scene in enumerate(data["scenes"], 1):
        if not isinstance(scene, dict):
            raise ValidationError(f"scene {index} must be an object")
        motion, intensity = _common(scene, index, TIMELINE_KEYS)
        image = scene.get("image")
        if not isinstance(image, str) or not image.strip():
            raise ValidationError(f"scene {index} field 'image' must be a non-empty string")
        image_path = (root / image).resolve()
        try:
            image_path.relative_to(root)
        except ValueError as exc:
            raise ValidationError(f"scene {index} field 'image' escapes images directory") from exc
        if not image_path.is_file():
            raise ValidationError(f"scene {index} image not found: {image}")
        start, end = _number(scene, "start", index), _number(scene, "end", index)
        if end <= start:
            raise ValidationError(f"scene {index} field 'end' must be greater than 'start'")
        if abs(start - previous_end) > frame:
            raise ValidationError(f"scene {index} field 'start' is not contiguous with previous scene")
        previous_end = end
        normalized.append({**scene, "image": image, "start": start, "end": end,
                           "motion": motion, "intensity": intensity})
    if audio_duration is not None:
        if not math.isfinite(audio_duration) or audio_duration <= 0:
            raise ValidationError("audio_duration must be positive and finite")
        if abs(previous_end - audio_duration) > tolerance:
            raise ValidationError(
                f"timeline duration {previous_end:.3f}s differs from audio {audio_duration:.3f}s")
    return {"scenes": normalized}


def validate_scene_plan(value: Any, paragraph_count: int, artwork_ids: set[str]) -> dict:
    data = _load(value)
    if paragraph_count < 1:
        raise ValidationError("paragraph_count must be positive")
    expected = 1
    normalized = []
    for index, scene in enumerate(data["scenes"], 1):
        if not isinstance(scene, dict):
            raise ValidationError(f"scene {index} must be an object")
        motion, intensity = _common(scene, index, PLAN_KEYS)
        start, end = scene.get("paragraph_start"), scene.get("paragraph_end")
        if isinstance(start, bool) or not isinstance(start, int) or isinstance(end, bool) or not isinstance(end, int):
            raise ValidationError(f"scene {index} paragraph range must use integers")
        if start != expected or end < start or end > paragraph_count:
            raise ValidationError(f"scene {index} paragraph range is gapped, overlapping, or out of bounds")
        image_id = scene.get("image_id")
        if image_id not in artwork_ids:
            raise ValidationError(f"scene {index} field 'image_id' is not in the artwork inventory")
        expected = end + 1
        normalized.append({**scene, "motion": motion, "intensity": intensity})
    if expected != paragraph_count + 1:
        raise ValidationError("scene paragraph ranges do not cover the complete source")
    return {"scenes": normalized}

