"""Render one frozen chapter job directory."""
from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

from create_mp4 import _render_duration_tolerance, create_video_from_timeline
from media_probe import duration_seconds, probe_media, verify_chapter_output
from text_to_speech_kokoro import DEFAULT_LANGUAGE, DEFAULT_SPEED, DEFAULT_VOICE, create_narration
from timeline_validator import validate_timeline


def _write_state(path, status, stage, error=None, artifacts=None):
    path.write_text(json.dumps({"status": status, "stage": stage, "error": error,
                                "artifacts": artifacts or {}}, indent=2) + "\n", encoding="utf-8")


def render_job(job_dir):
    root = Path(job_dir).resolve()
    chapter, images, timeline = root / "chapter.txt", root / "images", root / "video-timeline.json"
    state, log_path = root / "state.json", root / "job.log"
    root.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger(f"tts_gen.job.{id(root)}")
    logger.setLevel(logging.INFO); logger.propagate = False
    handler = logging.FileHandler(log_path, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s")); logger.addHandler(handler)
    try:
        config = json.loads((root / "job.json").read_text(encoding="utf-8")) if (root / "job.json").is_file() else {}
        for path in (chapter, timeline):
            if not path.is_file():
                raise FileNotFoundError(f"required job input not found: {path.name}")
        if not images.is_dir():
            raise FileNotFoundError("required job input not found: images")
        narration, output = root / "narration.wav", root / "full-chapter.mp4"
        _write_state(state, "rendering", "narration")
        if not narration.is_file():
            create_narration(chapter, narration, config.get("voice", DEFAULT_VOICE),
                             config.get("language", DEFAULT_LANGUAGE), config.get("speed", DEFAULT_SPEED))
        duration = duration_seconds(probe_media(narration))
        fps = config.get("fps", 30)
        validated = validate_timeline(timeline, images, audio_duration=duration, fps=fps)
        stream_tolerance = _render_duration_tolerance(len(validated["scenes"]), fps)
        _write_state(state, "rendering", "video", artifacts={"narration": str(narration)})
        if not output.is_file():
            create_video_from_timeline(narration, images, timeline, output,
                                       width=config.get("width", 1080), height=config.get("height", 1920),
                                       fps=fps)
        verify_chapter_output(output, {"width": config.get("width", 1080),
                                      "height": config.get("height", 1920), "fps": fps,
                                      "video_codec": "h264", "audio_codec": "aac",
                                      "duration_tolerance": stream_tolerance})
        artifacts = {"narration": str(narration), "full_chapter": str(output)}
        teaser = config.get("teaser", {})
        if teaser.get("enabled"):
            teaser_text, teaser_timeline = root / "teaser.txt", root / "teaser-timeline.json"
            if not teaser_text.is_file() or not teaser_timeline.is_file():
                raise FileNotFoundError("requested teaser requires teaser.txt and teaser-timeline.json")
            teaser_audio, teaser_output = root / "teaser.wav", root / "vertical-teaser.mp4"
            if not teaser_audio.is_file():
                create_narration(teaser_text, teaser_audio, config.get("voice", DEFAULT_VOICE),
                                 config.get("language", DEFAULT_LANGUAGE), config.get("speed", DEFAULT_SPEED))
            teaser_duration = duration_seconds(probe_media(teaser_audio))
            validate_timeline(teaser_timeline, images, audio_duration=teaser_duration, fps=config.get("fps", 30))
            if not teaser_output.is_file():
                create_video_from_timeline(teaser_audio, images, teaser_timeline, teaser_output,
                                           width=teaser.get("width", 1080), height=teaser.get("height", 1920),
                                           fps=config.get("fps", 30))
            verify_chapter_output(teaser_output, {"width": teaser.get("width", 1080),
                                                  "height": teaser.get("height", 1920), "fps": config.get("fps", 30),
                                                  "video_codec": "h264", "audio_codec": "aac"})
            artifacts["vertical_teaser"] = str(teaser_output)
        _write_state(state, "verified", "verified", artifacts=artifacts)
        logger.info("job verified")
        return artifacts
    except Exception as exc:
        logger.exception("job failed")
        _write_state(state, "failed", "failed", str(exc))
        raise
    finally:
        handler.flush(); handler.close(); logger.removeHandler(handler)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--job-dir", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        render_job(args.job_dir)
    except Exception as exc:
        print(f"Error: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
