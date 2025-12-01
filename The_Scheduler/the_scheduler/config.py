"""Central configuration for Sheets + Calendar IDs."""

from dataclasses import dataclass


@dataclass(slots=True)
class Config:
    """Runtime configuration for the scheduler."""

    spreadsheet_id: str
    master_sheet_name: str
    dates_sheet_name: str
    calendar_id: str


DEFAULT_CONFIG = Config(
    spreadsheet_id="10LVvOI180cUrD2D9xzCr7Zl-pEIUcX2perIDNFfCV24",
    master_sheet_name="Sheet1",
    dates_sheet_name="Dates",
    calendar_id="goof516@gmail.com",
)
