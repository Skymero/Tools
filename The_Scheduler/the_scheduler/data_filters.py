"""Task filtering logic that mirrors the n8n workflow."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Iterable, List, MutableMapping, Sequence

Task = MutableMapping[str, Any]


def normalize_type_field(task: Task) -> list[str]:
    """Split the Type column on commas and strip whitespace."""
    raw = str(task.get("Type") or "")
    return [part.strip() for part in raw.split(",") if part.strip()]


def _with_type_list(task: Task) -> Task:
    clone = dict(task)
    clone["Type_list"] = normalize_type_field(task)
    return clone


def filter_non_completed_tasks(master_tasks: Sequence[Task]) -> list[Task]:
    """Return tasks whose Status != 'Completed', with Type as list."""
    result: list[Task] = []
    for task in master_tasks:
        if task.get("Status") == "Completed":
            continue
        result.append(_with_type_list(task))
    return result


def filter_productive_tasks(non_completed_tasks: Sequence[Task]) -> list[Task]:
    """
    Priority P0 or P1 AND Type contains 'Business' or 'Productive'
    AND does NOT contain 'Chore'
    """
    out: list[Task] = []
    for task in non_completed_tasks:
        priority = task.get("Priority")
        types = task.get("Type_list", [])
        if priority in ("P0", "P1"):
            if (("Business" in types) or ("Productive" in types)) and ("Chore" not in types):
                out.append(task)
    return out


def filter_by_type(tasks: Sequence[Task], type_label: str) -> list[Task]:
    """Generic helper for Health or Chore."""
    return [task for task in tasks if type_label in task.get("Type_list", [])]


def parse_date_or_none(value: str | None) -> datetime | None:
    """Parse ISO-like date strings and normalize to UTC midnight."""
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value)
    except Exception:
        return None

    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    else:
        parsed = parsed.astimezone(timezone.utc)
    return parsed


def filter_by_date_closest_to_today(tasks: Sequence[Task], date_key_variants: Sequence[str]) -> Task | None:
    """
    Pick the task whose Due Date is closest to today.
    If tie: prefer overdue (negative diff) over future.
    """
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    best_task: Task | None = None
    best_distance = float("inf")
    best_diff_days = 0.0

    for task in tasks:
        raw_date = None
        for key in date_key_variants:
            if key in task:
                raw_date = task.get(key)
                break

        dt = parse_date_or_none(str(raw_date) if raw_date is not None else None)
        if dt is None:
            continue

        diff_days = (dt - today).total_seconds() / 86400.0
        distance = abs(diff_days)

        if best_task is None or distance < best_distance:
            best_task = task
            best_distance = distance
            best_diff_days = diff_days
        elif distance == best_distance and best_task is not None:
            if diff_days < 0 <= best_diff_days:
                best_task = task
                best_diff_days = diff_days

    return best_task


def pick_by_priority_then_date(tasks: Sequence[Task]) -> Task | None:
    """
    Iterate priorities [P0, P1, P2, P3].
    For first priority containing tasks, choose one closest to today by Due Date.
    """
    priorities = ["P0", "P1", "P2", "P3"]
    date_keys = ["Due Date", "Due date", "DueDate", "Due_Date"]

    for priority in priorities:
        filtered = [
            task for task in tasks if str(task.get("Priority", "")).upper().strip() == priority
        ]
        if not filtered:
            continue
        chosen = filter_by_date_closest_to_today(filtered, date_keys)
        if chosen:
            return chosen
    return None


def top3_p0_closest_to_today_unique_task_id(productive_tasks: Sequence[Task]) -> list[Task]:
    """
    - Only Priority P0
    - Sort by closeness of Due Date to today, then by actual date
    - Take up to 3 with unique task_id
    """
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    scored: list[dict[str, Any]] = []

    for task in productive_tasks:
        if task.get("Priority") != "P0":
            continue
        dt = parse_date_or_none(task.get("Due Date"))
        if dt is None:
            continue
        diff_days = (dt - today).total_seconds() / 86400.0
        distance = abs(diff_days)
        task_id = str(task.get("task_id") or "")
        if not task_id:
            continue
        scored.append({"task": task, "distance": distance, "diff": diff_days, "task_id": task_id})

    scored.sort(key=lambda item: (item["distance"], item["diff"]))

    seen_ids: set[str] = set()
    output: list[Task] = []
    for entry in scored:
        if len(output) >= 3:
            break
        task_id = entry["task_id"]
        if task_id in seen_ids:
            continue
        seen_ids.add(task_id)
        output.append(entry["task"])

    return output
