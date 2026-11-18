"""Transactional local 80% Gemini quota policy gate."""
from __future__ import annotations

import math
from datetime import datetime, timedelta, timezone


class QuotaHoldError(RuntimeError): pass


def reserve_quota(db, *, job_id, model, estimated_tokens, token_limit, now=None, window_seconds=60):
    # 80% is a local safety policy, not a provider guarantee.
    if not token_limit or token_limit <= 0: raise QuotaHoldError("Gemini token limit is not configured")
    now = now or datetime.now(timezone.utc); floor = (now - timedelta(seconds=window_seconds)).isoformat()
    ceiling = math.floor(token_limit * .8)
    db.execute("BEGIN IMMEDIATE")
    try:
        used = db.execute("SELECT COALESCE(SUM(COALESCE(actual_tokens,estimated_tokens)),0) FROM reservations WHERE model=? AND created_at>=? AND status IN ('reserved','reconciled')", (model, floor)).fetchone()[0]
        if used + estimated_tokens > ceiling: raise QuotaHoldError(f"projected tokens exceed local 80% policy ({ceiling})")
        expires = (now + timedelta(seconds=window_seconds)).isoformat()
        cursor = db.execute("INSERT INTO reservations(job_id,model,estimated_tokens,status,created_at,expires_at) VALUES(?,?,?,'reserved',?,?)", (job_id, model, estimated_tokens, now.isoformat(), expires))
        db.commit(); return int(cursor.lastrowid)
    except Exception: db.rollback(); raise


def reconcile(db, reservation_id, actual_tokens):
    db.execute("UPDATE reservations SET actual_tokens=?, status='reconciled' WHERE id=?", (actual_tokens, reservation_id))


def release_stale(db, now=None):
    now = (now or datetime.now(timezone.utc)).isoformat()
    return db.execute("UPDATE reservations SET status='released' WHERE status='reserved' AND expires_at<?", (now,)).rowcount
