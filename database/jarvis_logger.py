"""
JARVIS Persistent Database Logging Engine.
Provides thread-safe SQLite storage for historical trade executions,
real-time macro telemetry snapshots (DXY, US10Y), and performance analytics.
"""

import os
import sqlite3
import zipfile
import shutil
import logging
from datetime import datetime
from contextlib import contextmanager
from typing import Dict, Any, List, Optional

logger = logging.getLogger("JarvisDB")


class JarvisDatabaseLogger:
    """
    Manages persistent data storage for all Jarvis transaction logs,
    risk metrics, and macro tracking data. Uses thread-safe SQLite with WAL mode.
    """

    def __init__(self, db_path: str = "data/jarvis_metrics.db"):
        self.db_path = db_path
        # Ensure database storage directory exists securely
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.initialize_tables()

    @contextmanager
    def _get_connection(self):
        """Creates a direct connection with WAL journal mode and busy timeout, safely closed on exit."""
        conn = sqlite3.connect(self.db_path, timeout=10.0)
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA busy_timeout=5000;")
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def initialize_tables(self):
        """Builds relational table layouts and performance indexes if they do not exist."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # 1. Historical Trade Records Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    ticket_id INTEGER UNIQUE,
                    direction TEXT NOT NULL,
                    volume REAL NOT NULL,
                    entry_price REAL NOT NULL,
                    stop_loss REAL NOT NULL,
                    take_profit REAL NOT NULL,
                    status TEXT NOT NULL,
                    profit REAL DEFAULT 0.0
                )
            """)

            # Index on ticket_id and status for sub-millisecond lookups
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_trades_ticket ON trades(ticket_id);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_trades_status ON trades(status);")

            # 2. Macro Telemetry Analytics Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS telemetry_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    xau_price REAL NOT NULL,
                    dxy_value REAL NOT NULL,
                    us10y_yield REAL NOT NULL,
                    atr_value REAL NOT NULL,
                    system_status TEXT NOT NULL
                )
            """)

            cursor.execute("CREATE INDEX IF NOT EXISTS idx_telemetry_ts ON telemetry_logs(timestamp);")
            conn.commit()

    def log_trade_deployment(
        self,
        ticket_id: int,
        direction: str,
        volume: float,
        entry_price: float,
        sl: float,
        tp: float
    ) -> bool:
        """Inserts an active trade execution record into the persistent table."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self._get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT INTO trades (timestamp, ticket_id, direction, volume, entry_price, stop_loss, take_profit, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, 'ACTIVE')
                """, (timestamp, ticket_id, direction, volume, entry_price, sl, tp))
                conn.commit()
                logger.info(f"[💾 DB Log] Position Ticket #{ticket_id} ({direction} {volume}L @ ${entry_price:.2f}) logged successfully.")
                return True
            except sqlite3.IntegrityError:
                logger.warning(f"[!] Notice: Ticket #{ticket_id} already exists in database.")
                return False

    def log_trade_liquidation(self, ticket_id: int, final_profit: float) -> bool:
        """Updates an existing trade record when a position is closed."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE trades 
                SET status = 'CLOSED', profit = ? 
                WHERE ticket_id = ?
            """, (final_profit, ticket_id))
            conn.commit()
            rows_affected = cursor.rowcount
            if rows_affected > 0:
                logger.info(f"[💾 DB Log] Position Ticket #{ticket_id} updated to CLOSED with profit: ${final_profit:,.2f}")
                return True
            else:
                logger.warning(f"[!] Notice: Ticket #{ticket_id} not found in database to close.")
                return False

    def log_system_telemetry(
        self,
        xau: float,
        dxy: float,
        us10y: float,
        atr: float,
        status: str = "NOMINAL"
    ):
        """Saves a snapshot of current market conditions to the telemetry log table."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO telemetry_logs (timestamp, xau_price, dxy_value, us10y_yield, atr_value, system_status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (timestamp, xau, dxy, us10y, atr, status))
            conn.commit()

    def extract_weekly_summary(self) -> Dict[str, Any]:
        """Fetches the past week of performance data to generate natural voice updates."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*), COALESCE(SUM(profit), 0.0)
                FROM trades 
                WHERE timestamp >= datetime('now', '-7 days') AND status = 'CLOSED'
            """)
            row = cursor.fetchone()
            count = row[0] if row else 0
            net_profit = row[1] if row else 0.0
            return {
                "trade_count": int(count or 0),
                "net_profit": float(net_profit or 0.0)
            }

    def get_recent_trades(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Returns the most recent trade executions."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM trades ORDER BY id DESC LIMIT ?
            """, (limit,))
            return [dict(row) for row in cursor.fetchall()]

    def run_maintenance(self, retention_days: int = 30) -> Dict[str, Any]:
        """
        Runs automated maintenance:
        1. Purges telemetry older than retention_days to free disk space.
        2. VACUUMs database to reclaim pages.
        3. ANALYZEs database for query planner optimization.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"DELETE FROM telemetry_logs WHERE timestamp <= datetime('now', '-{retention_days} days');"
            )
            deleted_rows = cursor.rowcount
            conn.commit()

        # VACUUM must run outside transaction block
        with self._get_connection() as conn:
            conn.execute("VACUUM;")
            conn.execute("ANALYZE;")

        logger.info(f"[JARVIS-MAINTENANCE] Database optimized. Cleared {deleted_rows} old telemetry records.")
        return {"status": "OPTIMIZED", "deleted_telemetry_rows": deleted_rows}

    def generate_compressed_snapshot(self, output_zip_path: str = "data/backups/jarvis_backup.zip") -> Optional[str]:
        """
        Creates a compressed ZIP archive of the current live database file.
        Flushes WAL frames and creates a safe detached copy to prevent corruption from active writes.
        """
        try:
            # Step 0: Flush WAL frames to ensure consistent snapshot
            try:
                with self._get_connection() as conn:
                    conn.execute("PRAGMA wal_checkpoint(TRUNCATE);")
            except Exception as e:
                logger.warning(f"[JARVIS-BACKUP] WAL checkpoint notice: {e}")

            # Define temporary workspace paths
            backup_dir = os.path.dirname(output_zip_path)
            if backup_dir:
                os.makedirs(backup_dir, exist_ok=True)

            temp_db_copy = os.path.join(backup_dir or ".", "temp_snapshot.db")

            # Step 1: Create a safe, detached copy of the active database file
            shutil.copy2(self.db_path, temp_db_copy)

            # Step 2: Compress the copied snapshot file into a ZIP archive
            with zipfile.ZipFile(output_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(temp_db_copy, arcname=os.path.basename(self.db_path))

            # Step 3: Clean up the temporary workspace file
            if os.path.exists(temp_db_copy):
                os.remove(temp_db_copy)

            logger.info(f"[🛡️ Safety Engine] Secure database snapshot packed successfully: {output_zip_path}")
            return output_zip_path
        except Exception as e:
            logger.error(f"[-] Database backup serialization failure: {str(e)}")
            return None

