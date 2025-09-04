import sqlite3
import pandas as pd
from pathlib import Path
from typing import Optional

SALES_TABLE = "sales"

class Database:
    def __init__(self, db_path: str | Path):
        self.db_path = str(db_path)
        self.con = sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES)
        self._ensure_schema()

    def _ensure_schema(self):
        cur = self.con.cursor()
        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS {SALES_TABLE} (
                itemId TEXT PRIMARY KEY,
                query TEXT,
                dateSold TEXT,
                price_value REAL,
                price_currency TEXT,
                condition TEXT,
                itemWebUrl TEXT
            )
        """)
        self.con.commit()

    def upsert_sales(self, query: str, df: pd.DataFrame):
        if df.empty:
            return 0
        df = df.copy()
        df['query'] = query
        # Rename DataFrame columns to match DB schema
        df = df.rename(columns={
            'price.value': 'price_value',
            'price.currency': 'price_currency',
        })
        cols = ['itemId', 'query', 'dateSold', 'price_value', 'price_currency', 'condition', 'itemWebUrl']
        rows = [tuple(row) for row in df[cols].itertuples(index=False, name=None)]
        sql = f"""
            INSERT INTO {SALES_TABLE} (itemId, query, dateSold, price_value, price_currency, condition, itemWebUrl)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(itemId) DO UPDATE SET
                price_value=excluded.price_value,
                price_currency=excluded.price_currency,
                dateSold=excluded.dateSold,
                condition=excluded.condition,
                itemWebUrl=excluded.itemWebUrl,
                query=excluded.query
        """
        cur = self.con.cursor()
        inserted = 0
        for row in rows:
            cur.execute(sql, row)
            inserted += int(cur.rowcount > 0)
        self.con.commit()
        print(f"[DB] Upserted {inserted} sales rows for query '{query}'")
        return inserted
