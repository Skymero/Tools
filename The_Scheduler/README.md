# The Scheduler

Prototype Python project that mirrors the behavior of the existing n8n workflow.  
It reads date batches from Google Sheets, selects tasks via deterministic rules,
creates day-specific Sheets, syncs Google Calendar, and marks completed tasks on
the master sheet.

> **Status:** Skeleton project. Google APIs are represented by placeholder
> functions inside `the_scheduler/google_services.py`.

## Project layout

```
The_Scheduler/
|-- pyproject.toml          # Packaging metadata / CLI entry point
|-- README.md
`-- the_scheduler/
    |-- __init__.py
    |-- config.py           # IDs, sheet names, and Config dataclass
    |-- data_filters.py     # Date + task filtering helpers
    |-- google_services.py  # Google Sheets/Calendar integration points
    `-- scheduler.py        # process_one_day + CLI entry (main)
```

## Usage

Create a virtual environment (Python 3.11+) and install the package in editable
mode:

```powershell
cd The_Scheduler
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e .
```

Then run the workflow manually:

```powershell
the-scheduler         # or: python -m the_scheduler.scheduler
```

## Next steps

1. Implement the Google Sheets + Calendar calls inside `google_services.py` using
   the Google APIs of your choice.
2. Connect OAuth credentials / service accounts and wire them into
   `GoogleClients`.
3. Replace the in-memory stub in `GoogleClients.read_sheet` with real Sheets
   queries.
