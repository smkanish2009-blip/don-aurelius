"""
SQLite Trade Journal & Performance Tracker.
Records all trade setups, entry/exit prices, slippage, and AI probability outputs for post-trade analysis.
"""

import os
import sqlite3
import logging
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Dict, Any

logger = logging.getLogger("TradeJournal")


class TradeJournal:
    def __init__(self, db_path: str = "data/trade_journal.sqlite"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._init_db()

    @contextmanager
    def _get_connection(self):
        """Thread-safe SQLite connection manager with WAL mode and guaranteed closure."""
        conn = sqlite3.connect(self.db_path, timeout=10.0)
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA busy_timeout=5000;")
        try:
            with conn:
                yield conn
        finally:
            conn.close()

    def _init_db(self) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS trades (
                ticket INTEGER PRIMARY KEY,
                open_time TEXT,
                close_time TEXT,
                setup_type TEXT,
                direction TEXT,
                entry_price REAL,
                sl_price REAL,
                tp_price REAL,
                exit_price REAL,
                lots REAL,
                pnl_usd REAL,
                pnl_r REAL,
                ai_confidence REAL,
                exit_reason TEXT
            )
            """)

    def record_entry(self, ticket: int, setup_type: str, direction: str,
                     entry: float, sl: float, tp: float, lots: float, ai_confidence: float) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT OR REPLACE INTO trades (
                ticket, open_time, setup_type, direction, entry_price, sl_price, tp_price, lots, ai_confidence
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                ticket,
                datetime.now(timezone.utc).isoformat(),
                setup_type,
                direction,
                entry,
                sl,
                tp,
                lots,
                ai_confidence
            ))

    def record_exit(self, ticket: int, exit_price: float, pnl_usd: float, pnl_r: float, exit_reason: str) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            UPDATE trades SET
                close_time = ?,
                exit_price = ?,
                pnl_usd = ?,
                pnl_r = ?,
                exit_reason = ?
            WHERE ticket = ?
            """, (
                datetime.now(timezone.utc).isoformat(),
                exit_price,
                pnl_usd,
                pnl_r,
                exit_reason,
                ticket
            ))
