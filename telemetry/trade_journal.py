"""
SQLite Trade Journal & Performance Tracker.
Records all trade setups, entry/exit prices, slippage, and AI probability outputs for post-trade analysis.
"""

import os
import json
import sqlite3
import logging
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Dict, Any, Optional

logger = logging.getLogger("TradeJournal")


class TradeJournal:
    def __init__(self, db_path: str = "data/trade_journal.sqlite"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
        self._init_db()

    @contextmanager
    def _get_connection(self):
        """Thread-safe SQLite connection manager with WAL mode and guaranteed closure."""
        conn = sqlite3.connect(self.db_path, timeout=10.0)
        conn.row_factory = sqlite3.Row
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
                exit_reason TEXT,
                ml_features_json TEXT
            )
            """)
            # Schema migration for existing tables without ml_features_json
            cursor.execute("PRAGMA table_info(trades)")
            columns = [row[1] for row in cursor.fetchall()]
            if "ml_features_json" not in columns:
                try:
                    cursor.execute("ALTER TABLE trades ADD COLUMN ml_features_json TEXT")
                except Exception:
                    pass

    def record_entry(
        self,
        ticket: int,
        setup_type: str,
        direction: str,
        entry: float,
        sl: float,
        tp: float,
        lots: float,
        ai_confidence: float,
        features: Optional[Dict[str, Any]] = None
    ) -> None:
        feat_str = json.dumps(features or {})
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT OR REPLACE INTO trades (
                ticket, open_time, setup_type, direction, entry_price, sl_price, tp_price, lots, ai_confidence, ml_features_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                ticket,
                datetime.now(timezone.utc).isoformat(),
                str(setup_type),
                str(direction),
                float(entry),
                float(sl),
                float(tp),
                float(lots),
                float(ai_confidence),
                feat_str
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
                float(exit_price),
                float(pnl_usd),
                float(pnl_r),
                str(exit_reason),
                ticket
            ))

    def get_performance_summary(self) -> Dict[str, Any]:
        """Returns summarized performance metrics from the journal."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as total, SUM(CASE WHEN pnl_usd > 0 THEN 1 ELSE 0 END) as wins, SUM(pnl_usd) as net_pnl FROM trades WHERE close_time IS NOT NULL")
            row = cursor.fetchone()

        total = row["total"] if row and row["total"] else 0
        wins = row["wins"] if row and row["wins"] else 0
        net_pnl = float(row["net_pnl"]) if row and row["net_pnl"] is not None else 0.0
        win_rate = round((wins / total * 100.0), 2) if total > 0 else 0.0

        return {
            "total_trades": total,
            "wins": wins,
            "win_rate_pct": win_rate,
            "net_pnl_usd": round(net_pnl, 2)
        }
