from datetime import datetime, timedelta
from typing import Union
import pandas as pd
import time
import requests

from api.ebay_client import EbayClient
from db.database   import Database   # built in Task‑3

# These will be injected or set in main.py
auth     = None
client   = EbayClient(auth)
_db      = Database("sales.db")
DEFAULT_DAYS = 90

class ApiError(Exception):
    pass

def fetch_and_cache_history(query: str, days: int = DEFAULT_DAYS) -> pd.DataFrame:
    """Fetch sold‑item data for *query*, cache it, and return as DataFrame.

    Parameters
    ----------
    query : str
        Keyword or product name (e.g. "playstation 2").
    days : int, optional
        How far back to look (max 90 per Insights API, default 90).

    Returns
    -------
    pd.DataFrame
        Normalised DataFrame of sold listings ready for analytics.

    Example
    -------
    >>> df = fetch_and_cache_history("playstation 2")
    >>> print(df.head())
    """
    # 1️⃣ Compute date range in ISO‑8601 (UTC)
    date_end   = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    date_start = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")

    # 2️⃣ Iterate through pages (200 rows per request)
    all_rows, page = [], 0
    while True:
        try:
            chunk = client.search_sales(query, date_start, date_end, page=page)
        except requests.exceptions.RequestException as e:
            raise ApiError(f"Network error: {e}")
        except Exception as e:
            # Handle HTTP 429 explicitly if possible
            if hasattr(e, 'response') and getattr(e.response, 'status_code', None) == 429:
                print("Rate limited (429). Sleeping for 15 minutes...")
                time.sleep(900)
                continue  # retry once
            raise ApiError(f"API error: {e}")
        items = chunk.get("itemSales", [])
        all_rows.extend(items)
        if len(items) < 200:
            break
        page += 1

    # 3️⃣ Flatten JSON → DataFrame
    if not all_rows:
        columns = ["itemId", "dateSold", "price.value", "price.currency", "condition", "itemWebUrl"]
        return pd.DataFrame(columns=columns)
    df = pd.json_normalize(all_rows, sep=".")

    # 4️⃣ Prune, cast, reorder columns
    keep_cols = [
        "itemId", "dateSold", "price.value", "price.currency", "condition", "itemWebUrl"
    ]
    for col in keep_cols:
        if col not in df.columns:
            df[col] = None
    df = df[keep_cols]
    df["price.value"] = pd.to_numeric(df["price.value"], errors="coerce")
    df["dateSold"] = pd.to_datetime(df["dateSold"], errors="coerce")
    df = df.sort_values("dateSold")

    # 5️⃣ Persist fresh data to SQLite (upsert dedupe)
    _db.upsert_sales(query, df)
    return df
