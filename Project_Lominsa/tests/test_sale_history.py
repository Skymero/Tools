import pandas as pd
import pytest
from unittest.mock import MagicMock

from analytics import sale_history

def test_fetch_and_cache_history(monkeypatch):
    # Mock EbayClient.search_sales to simulate two pages
    fake_rows_page1 = [{
        "itemId": "1",
        "dateSold": "2025-07-01T12:00:00Z",
        "price": {"value": "100.0", "currency": "USD"},
        "condition": "New",
        "itemWebUrl": "http://ebay.com/itm/1"
    } for _ in range(200)]
    fake_rows_page2 = [{
        "itemId": "2",
        "dateSold": "2025-07-02T12:00:00Z",
        "price": {"value": "120.0", "currency": "USD"},
        "condition": "Used",
        "itemWebUrl": "http://ebay.com/itm/2"
    }]
    call_counter = {"page": 0}
    def fake_search_sales(query, date_start, date_end, page=0):
        if page == 0:
            return {"itemSales": fake_rows_page1}
        elif page == 1:
            return {"itemSales": fake_rows_page2}
        else:
            return {"itemSales": []}
    monkeypatch.setattr(sale_history.client, "search_sales", fake_search_sales)
    # Mock _db.upsert_sales to just record calls
    upsert_mock = MagicMock()
    monkeypatch.setattr(sale_history, "_db", MagicMock(upsert_sales=upsert_mock))
    df = sale_history.fetch_and_cache_history("test-query", days=2)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 201
    assert set(df.columns) >= {"itemId", "dateSold", "price.value", "price.currency", "condition", "itemWebUrl"}
    upsert_mock.assert_called_once()

def test_fetch_and_cache_history_empty(monkeypatch):
    # Simulate zero-item response
    monkeypatch.setattr(sale_history.client, "search_sales", lambda *a, **kw: {"itemSales": []})
    monkeypatch.setattr(sale_history, "_db", MagicMock(upsert_sales=MagicMock()))
    df = sale_history.fetch_and_cache_history("test-query", days=2)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 0
    assert set(df.columns) >= {"itemId", "dateSold", "price.value", "price.currency", "condition", "itemWebUrl"}
