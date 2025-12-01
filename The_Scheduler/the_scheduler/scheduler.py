"""Main orchestration entry point for the scheduler."""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from typing import Any, MutableMapping

from .config import Config, DEFAULT_CONFIG
from .data_filters import (
    filter_by_type,
    filter_non_completed_tasks,
    filter_productive_tasks,
    pick_by_priority_then_date,
    top3_p0_closest_to_today_unique_task_id,
)
from .google_services import (
    GoogleClients,
    append_rows,
    create_calendar_event,
    create_sheet,
    delete_columns,
    read_sheet,
    update_rows,
)

Task = MutableMapping[str, Any]


def _clone_with_dates(task: Task, g_date: str | None, g_end_date: str | None) -> Task:
    cloned = dict(task)
    cloned["g_date"] = g_date
    cloned["g_end_date"] = g_end_date
    return cloned


def process_one_day(
    day_row: Task,
    master_tasks: Sequence[Task],
    *,
    clients: GoogleClients,
    config: Config = DEFAULT_CONFIG,
) -> None:
    """
    Process a single day worth of tasks.

    Corresponds to the SplitInBatches iteration in the original n8n workflow.
    """

    g_date = day_row.get("g_Dates")
    g_end_date = day_row.get("g_end_Dates")

    non_completed = filter_non_completed_tasks(master_tasks)
    productive_tasks = filter_productive_tasks(non_completed)
    health_tasks = filter_by_type(non_completed, "Health")
    chore_tasks = filter_by_type(non_completed, "Chore")

    top3 = [
        _clone_with_dates(task, g_date, g_end_date)
        for task in top3_p0_closest_to_today_unique_task_id(productive_tasks)
    ]
    health_chosen = pick_by_priority_then_date(health_tasks)
    health_chosen = (
        _clone_with_dates(health_chosen, g_date, g_end_date) if health_chosen else None
    )
    chore_chosen = pick_by_priority_then_date(chore_tasks)
    chore_chosen = (
        _clone_with_dates(chore_chosen, g_date, g_end_date) if chore_chosen else None
    )

    selected_tasks: list[Task] = []
    selected_tasks.extend(top3)
    if health_chosen:
        selected_tasks.append(health_chosen)
    if chore_chosen:
        selected_tasks.append(chore_chosen)

    if not selected_tasks:
        return

    day_sheet_meta = create_sheet(clients, config.spreadsheet_id, title=str(g_date))
    day_sheet_id = int(day_sheet_meta["sheetId"])

    append_rows(clients, config.spreadsheet_id, day_sheet_id, selected_tasks)
    delete_columns(clients, config.spreadsheet_id, day_sheet_id, num_columns=6)

    for task in selected_tasks:
        summary = str(task.get("Task", "Task"))
        start = str(task.get("g_date"))
        end = str(task.get("g_end_date"))
        create_calendar_event(clients, config.calendar_id, start, end, summary)

    rows_to_update: list[dict[str, Any]] = []
    for task in selected_tasks:
        task_id = task.get("task_id")
        if not task_id:
            continue
        rows_to_update.append(
            {
                "task_id": task_id,
                "Status": "Completed",
            }
        )

    if rows_to_update:
        update_rows(
            clients,
            config.spreadsheet_id,
            config.master_sheet_name,
            rows_to_update,
            key_column="task_id",
        )


def main(*, clients: GoogleClients | None = None, config: Config = DEFAULT_CONFIG) -> None:
    """Manual trigger entry point."""
    clients = clients or GoogleClients()

    dates_list = read_sheet(clients, config.spreadsheet_id, config.dates_sheet_name)
    master_tasks = read_sheet(clients, config.spreadsheet_id, config.master_sheet_name)

    for day_row in dates_list:
        process_one_day(day_row, master_tasks, clients=clients, config=config)


if __name__ == "__main__":
    main()
