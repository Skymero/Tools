"""Integration points for Google Sheets and Google Calendar."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Mapping, Sequence

Row = Mapping[str, object]
MutableRow = dict[str, object]


@dataclass
class GoogleClients:
    """
    Container for Google API clients.

    Replace the stub methods with real calls (gspread, google-api-python-client,
    pygsheets, etc.). Keeping it as a simple dataclass makes dependency
    injection easier inside unit tests.
    """

    def read_sheet(self, spreadsheet_id: str, sheet_name: str) -> List[MutableRow]:
        raise NotImplementedError("Connect Google Sheets API here.")

    def append_rows(
        self,
        spreadsheet_id: str,
        sheet_id_or_name: str,
        rows: Sequence[Mapping[str, object]],
    ) -> None:
        raise NotImplementedError("Append rows via Google Sheets API.")

    def update_rows(
        self,
        spreadsheet_id: str,
        sheet_name: str,
        rows: Sequence[Mapping[str, object]],
        key_column: str,
    ) -> None:
        raise NotImplementedError("Update rows via Google Sheets API.")

    def delete_columns(self, spreadsheet_id: str, sheet_id: int, num_columns: int) -> None:
        raise NotImplementedError("Delete columns via Google Sheets API.")

    def delete_sheet(self, spreadsheet_id: str, sheet_id: int) -> None:
        raise NotImplementedError("Delete sheet via Google Sheets API.")

    def create_sheet(self, spreadsheet_id: str, title: str) -> Mapping[str, object]:
        raise NotImplementedError("Create sheet via Google Sheets API.")

    def create_calendar_event(
        self, calendar_id: str, start_iso: str, end_iso: str, summary: str
    ) -> None:
        raise NotImplementedError("Create Google Calendar event here.")


def read_sheet(clients: GoogleClients, spreadsheet_id: str, sheet_name: str) -> List[MutableRow]:
    """Return rows as list[dict]."""
    return clients.read_sheet(spreadsheet_id, sheet_name)


def append_rows(
    clients: GoogleClients,
    spreadsheet_id: str,
    sheet_id_or_name: str,
    rows: Sequence[Mapping[str, object]],
) -> None:
    """Append rows to a sheet."""
    clients.append_rows(spreadsheet_id, sheet_id_or_name, rows)


def update_rows(
    clients: GoogleClients,
    spreadsheet_id: str,
    sheet_name: str,
    rows: Sequence[Mapping[str, object]],
    key_column: str,
) -> None:
    """Update rows in a sheet using key_column matching."""
    clients.update_rows(spreadsheet_id, sheet_name, rows, key_column)


def delete_columns(
    clients: GoogleClients, spreadsheet_id: str, sheet_id: int, num_columns: int
) -> None:
    """Delete columns from a sheet."""
    clients.delete_columns(spreadsheet_id, sheet_id, num_columns)


def delete_sheet(clients: GoogleClients, spreadsheet_id: str, sheet_id: int) -> None:
    """Delete a sheet entirely."""
    clients.delete_sheet(spreadsheet_id, sheet_id)


def create_sheet(clients: GoogleClients, spreadsheet_id: str, title: str) -> Mapping[str, object]:
    """Create a sheet and return metadata."""
    return clients.create_sheet(spreadsheet_id, title)


def create_calendar_event(
    clients: GoogleClients, calendar_id: str, start_iso: str, end_iso: str, summary: str
) -> None:
    """Create an event."""
    clients.create_calendar_event(calendar_id, start_iso, end_iso, summary)
