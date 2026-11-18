"""Process at most one Google Drive chapter job per --once invocation."""
from __future__ import annotations

import argparse
import json
import os
import shutil
from pathlib import Path

import job_store
import gemini_quota
from create_mp4 import _render_duration_tolerance
from gemini_client import count_tokens
from google_drive_auth import AuthAttentionError
from google_drive_client import DriveClient, GOOGLE_DOC, GOOGLE_FOLDER, normalize_google_doc
from media_probe import verify_chapter_output
from process_lock import AlreadyRunningError, ProcessLock
from render_chapter import render_job
from langflow_client import build_input, plan_scenes
from scene_audio import generate_scene_audio, paragraphs


def _required(name):
    value = os.environ.get(name)
    if not value: raise RuntimeError(f"missing required environment variable: {name}")
    return value


def _flatten_inputs(client, folder):
    values = []
    for item in client.list_children(folder["id"]):
        if item.get("mimeType") == GOOGLE_FOLDER:
            for child in client.list_children(item["id"]):
                child = dict(child); child["relative_parent"] = item["name"]; values.append(child)
        else: values.append(item)
    return values


def _snapshot(client, files, destination):
    destination.mkdir(parents=True, exist_ok=False)
    images = destination / "images"; images.mkdir()
    chapter_count = 0
    for item in files:
        mime, name = item.get("mimeType"), item["name"]
        if mime == GOOGLE_DOC or name.lower() in {"chapter.txt", "chapter"}:
            chapter_count += 1
            if chapter_count > 1: raise RuntimeError("Drive job has multiple chapter sources")
            target = destination / "chapter.txt"; client.download(item["id"], target, google_doc=mime == GOOGLE_DOC)
            if mime == GOOGLE_DOC: target.write_text(normalize_google_doc(target.read_text(encoding="utf-8-sig")), encoding="utf-8")
        elif name.lower() in {"video-timeline.json", "job.json"}:
            client.download(item["id"], destination / name)
        elif item.get("relative_parent", "").lower() == "images" or Path(name).suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}:
            client.download(item["id"], images / name)
    if chapter_count == 0: raise RuntimeError("Drive job has no chapter text or native Google Doc")


def _prepare_generated_timeline(root, db, job_id):
    """Run the opt-in Phase 2 planner once, preserving raw output before validation."""
    timeline = root / "video-timeline.json"
    if timeline.is_file(): return
    config_path = root / "job.json"
    config = json.loads(config_path.read_text(encoding="utf-8")) if config_path.is_file() else {}
    planner = config.get("planner", {})
    if not planner.get("enabled") or os.environ.get("ENABLE_GEMINI_PLANNING", "false").lower() != "true":
        raise RuntimeError("authored video-timeline.json is required unless Phase 2 planning is explicitly enabled")
    artwork_config = config.get("artwork", {})
    if not artwork_config: raise RuntimeError("generated planning requires job.json artwork metadata")
    source_parts = paragraphs((root / "chapter.txt").read_text(encoding="utf-8-sig"))
    descriptions = {key: value["description"] for key, value in artwork_config.items()}
    prompt = build_input(source_parts, descriptions)
    estimated = count_tokens(prompt)
    limit = int(_required("GEMINI_TPM_LIMIT"))
    gemini_quota.reserve_quota(db, job_id=job_id, model=_required("GEMINI_MODEL"),
                               estimated_tokens=estimated, token_limit=limit)
    raw = root / "gemini-output.json"
    plan, metadata = plan_scenes(source_parts, descriptions, raw)
    (root / "scene-plan.json").write_text(json.dumps({**plan, "metadata": metadata}, indent=2) + "\n", encoding="utf-8")
    artwork_files = {key: value["file"] for key, value in artwork_config.items()}
    generate_scene_audio(root / "chapter.txt", plan, artwork_files, root)


def process_once(client=None, *, work_root="work", db_path="work/tts_gen.db"):
    client = client or DriveClient(); incoming = _required("DRIVE_INCOMING_FOLDER_ID")
    finished = _required("DRIVE_FINISHED_FOLDER_ID")
    db = job_store.init(db_path)
    work_path = Path(work_root); work_path.mkdir(parents=True, exist_ok=True)
    known = {row[0] for row in db.execute("SELECT snapshot_path FROM jobs WHERE snapshot_path IS NOT NULL") if row[0]}
    for workspace in work_path.iterdir():
        if workspace.is_dir() and str(workspace) not in known:
            print(f"orphaned workspace retained for review: {workspace}")
    folders = sorted((x for x in client.list_children(incoming) if x.get("mimeType") == GOOGLE_FOLDER),
                     key=lambda x: (x.get("modifiedTime", ""), x["id"]))
    if not folders: db.close(); return "no-work"
    selected = None
    for candidate in folders:
        candidate_files = _flatten_inputs(client, candidate); candidate_fp = job_store.fingerprint(candidate_files)
        candidate_id = job_store.create_job(db, candidate["id"], candidate_fp, candidate_files)
        candidate_row = db.execute("SELECT * FROM jobs WHERE id=?", (candidate_id,)).fetchone()
        candidate_root = work_path / f"{candidate['id']}-{candidate_fp[:12]}"
        if candidate_row["status"] == "completed": continue
        if candidate_row["attempts"] >= int(os.environ.get("TTS_GEN_MAX_ATTEMPTS", "3")): continue
        if candidate_row["status"] == "failed":
            retry = candidate_root / "RETRY"
            if not retry.is_file(): continue
            retry.unlink(); db.execute("UPDATE jobs SET status='ready',stage='ready',error_text=NULL WHERE id=?", (candidate_id,))
            candidate_row = db.execute("SELECT * FROM jobs WHERE id=?", (candidate_id,)).fetchone()
        selected = candidate, candidate_files, candidate_fp, candidate_id, candidate_row, candidate_root
        break
    if selected is None: db.close(); return "no-work"
    folder, files, fp, job_id, row, root = selected
    try:
        if not root.exists():
            job_store.transition(db, job_id, row["status"], "snapshotting")
            _snapshot(client, files, root)
            db.execute("UPDATE jobs SET snapshot_path=? WHERE id=?", (str(root), job_id))
            if job_store.fingerprint(_flatten_inputs(client, folder)) != fp:
                job_store.transition(db, job_id, "snapshotting", "discovered", stage="changed")
                return "changed"
            job_store.transition(db, job_id, "snapshotting", "ready", stage="ready")
        current = db.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
        output = root / "full-chapter.mp4"
        if not output.is_file():
            job_store.transition(db, job_id, current["status"], "rendering")
            _prepare_generated_timeline(root, db, job_id)
            render_job(root); job_store.transition(db, job_id, "rendering", "verifying")
        timeline_data = json.loads((root / "video-timeline.json").read_text(encoding="utf-8"))
        stream_tolerance = _render_duration_tolerance(len(timeline_data["scenes"]), 30)
        verify_chapter_output(output, {"width": 1080, "height": 1920, "fps": 30,
                                       "video_codec": "h264", "audio_codec": "aac",
                                       "duration_tolerance": stream_tolerance})
        db.execute("UPDATE jobs SET status='uploading',stage='uploading' WHERE id=?", (job_id,))
        current = db.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
        ids = json.loads(current["output_ids"])
        output_id = ids.get("full_chapter") or client.generate_id()
        if not ids.get("full_chapter"):
            ids["full_chapter"] = output_id
            db.execute("UPDATE jobs SET output_ids=? WHERE id=?", (json.dumps(ids), job_id))
        try:
            client.confirm_upload(output_id, parent_id=finished, name=f"{folder['name']}-full-chapter.mp4", local_path=output)
        except Exception:
            client.upload(output, file_id=output_id, name=f"{folder['name']}-full-chapter.mp4", parent_id=finished)
            client.confirm_upload(output_id, parent_id=finished, name=f"{folder['name']}-full-chapter.mp4", local_path=output)
        raw = root / "gemini-output.json"
        gemini_parent = os.environ.get("DRIVE_GEMINI_OUTPUT_FOLDER_ID")
        if raw.is_file() and gemini_parent:
            raw_id = ids.get("gemini_raw") or client.generate_id()
            if not ids.get("gemini_raw"):
                ids["gemini_raw"] = raw_id
                db.execute("UPDATE jobs SET output_ids=?,raw_output_path=? WHERE id=?", (json.dumps(ids), str(raw), job_id))
            try:
                client.confirm_upload(raw_id, parent_id=gemini_parent, name=f"{folder['name']}-gemini-output.json", local_path=raw)
            except Exception:
                client.upload(raw, file_id=raw_id, name=f"{folder['name']}-gemini-output.json",
                              parent_id=gemini_parent, mime_type="application/json")
                client.confirm_upload(raw_id, parent_id=gemini_parent, name=f"{folder['name']}-gemini-output.json", local_path=raw)
        if not job_store.transition(db, job_id, "uploading", "completed"):
            raise RuntimeError("job completion transition failed")
        return "completed"
    except AuthAttentionError:
        db.execute("UPDATE jobs SET status='auth_attention', stage='auth_attention', attempts=attempts+1 WHERE id=?", (job_id,)); raise
    except gemini_quota.QuotaHoldError:
        db.execute("UPDATE jobs SET status='quota_hold', stage='quota_hold' WHERE id=?", (job_id,)); raise
    except Exception as exc:
        db.execute("UPDATE jobs SET status='failed', stage='failed', attempts=attempts+1, error_text=? WHERE id=?", (str(exc), job_id)); raise
    finally: db.close()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("--once", action="store_true")
    args = parser.parse_args(argv)
    if not args.once: parser.error("--once is required")
    try:
        with ProcessLock(Path("work") / "run_drive_queue.lock"):
            print(process_once())
    except AlreadyRunningError as exc: print(exc); return 0
    except Exception as exc: print(f"Error: {exc}"); return 1
    return 0


if __name__ == "__main__": raise SystemExit(main())

