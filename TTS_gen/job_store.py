"""Durable SQLite job and Gemini quota state."""
from __future__ import annotations

import hashlib
import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

SCHEMA_VERSION = 1


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def connect(path: str | Path) -> sqlite3.Connection:
    db = sqlite3.connect(path, timeout=30, isolation_level=None)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("PRAGMA foreign_keys=ON")
    return db


def init(path: str | Path) -> sqlite3.Connection:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    db = connect(target)
    db.executescript("""
    CREATE TABLE IF NOT EXISTS schema_version(version INTEGER NOT NULL);
    INSERT INTO schema_version(version) SELECT 1 WHERE NOT EXISTS(SELECT 1 FROM schema_version);
    CREATE TABLE IF NOT EXISTS jobs(
      id INTEGER PRIMARY KEY, drive_folder_id TEXT NOT NULL, fingerprint TEXT NOT NULL,
      status TEXT NOT NULL, stage TEXT NOT NULL, attempts INTEGER NOT NULL DEFAULT 0,
      snapshot_path TEXT, raw_output_path TEXT, output_ids TEXT NOT NULL DEFAULT '{}',
      error_text TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
      UNIQUE(drive_folder_id, fingerprint));
    CREATE TABLE IF NOT EXISTS job_files(
      job_id INTEGER NOT NULL REFERENCES jobs(id) ON DELETE CASCADE, file_id TEXT NOT NULL,
      name TEXT NOT NULL, modified_time TEXT, md5_checksum TEXT, size INTEGER,
      PRIMARY KEY(job_id, file_id));
    CREATE TABLE IF NOT EXISTS reservations(
      id INTEGER PRIMARY KEY, job_id INTEGER REFERENCES jobs(id), model TEXT NOT NULL,
      estimated_tokens INTEGER NOT NULL, actual_tokens INTEGER, status TEXT NOT NULL,
      created_at TEXT NOT NULL, expires_at TEXT NOT NULL);
    """)
    return db


def fingerprint(files: list[dict]) -> str:
    lines = []
    for item in sorted(files, key=lambda value: value["id"]):
        lines.append("\0".join(str(item.get(key) or "") for key in
                               ("id", "modifiedTime", "md5Checksum", "size")) + "\n")
    return hashlib.sha256("".join(lines).encode()).hexdigest()


def create_job(db: sqlite3.Connection, drive_folder_id: str, value: str, files: list[dict] | None = None) -> int:
    now = _now()
    db.execute("BEGIN IMMEDIATE")
    try:
        db.execute("INSERT OR IGNORE INTO jobs(drive_folder_id,fingerprint,status,stage,created_at,updated_at) VALUES(?,?, 'discovered','discovered',?,?)",
                   (drive_folder_id, value, now, now))
        row = db.execute("SELECT id FROM jobs WHERE drive_folder_id=? AND fingerprint=?", (drive_folder_id, value)).fetchone()
        for item in files or []:
            db.execute("INSERT OR REPLACE INTO job_files(job_id,file_id,name,modified_time,md5_checksum,size) VALUES(?,?,?,?,?,?)",
                       (row[0], item["id"], item.get("name", ""), item.get("modifiedTime"), item.get("md5Checksum"), item.get("size")))
        db.commit()
        return int(row[0])
    except Exception:
        db.rollback(); raise


def transition(db: sqlite3.Connection, job_id: int, expected: str, new_status: str, *, stage: str | None = None, error: str | None = None) -> bool:
    cursor = db.execute("UPDATE jobs SET status=?, stage=?, error_text=?, updated_at=? WHERE id=? AND status=?",
                        (new_status, stage or new_status, error, _now(), job_id, expected))
    return cursor.rowcount == 1


def reserve(db: sqlite3.Connection, job_id: int | None, model: str, tokens: int, expires_at: str) -> int:
    cursor = db.execute("INSERT INTO reservations(job_id,model,estimated_tokens,status,created_at,expires_at) VALUES(?,?,?,'reserved',?,?)",
                        (job_id, model, tokens, _now(), expires_at))
    return int(cursor.lastrowid)

