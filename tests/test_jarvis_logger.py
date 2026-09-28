"""
Unit Test Suite for JARVIS Database Logging & Maintenance Pipeline.
Tests SQLite table initialization, transaction logging, liquidation updates,
telemetry snapshots, weekly performance summaries, and database optimization.
"""

import os
import unittest
import tempfile
from datetime import datetime, timedelta

from database.jarvis_logger import JarvisDatabaseLogger


class TestJarvisDatabaseLogger(unittest.TestCase):

    def setUp(self):
        # Create unique temporary SQLite database file for isolation
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "test_metrics.db")
        self.logger = JarvisDatabaseLogger(db_path=self.db_path)

    def tearDown(self):
        import gc
        del self.logger
        gc.collect()
        try:
            self.temp_dir.cleanup()
        except Exception:
            pass

    def test_database_tables_created(self):
        self.assertTrue(os.path.exists(self.db_path))
        with self.logger._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall()]
            self.assertIn("trades", tables)
            self.assertIn("telemetry_logs", tables)

    def test_log_trade_deployment_and_liquidation(self):
        ticket = 998877
        # 1. Log deployment
        success = self.logger.log_trade_deployment(
            ticket_id=ticket,
            direction="BUY",
            volume=1.50,
            entry_price=2650.00,
            sl=2645.00,
            tp=2665.00
        )
        self.assertTrue(success)

        # Verify active record
        with self.logger._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM trades WHERE ticket_id = ?", (ticket,))
            row = dict(cursor.fetchone())
            self.assertEqual(row["ticket_id"], ticket)
            self.assertEqual(row["direction"], "BUY")
            self.assertEqual(row["volume"], 1.50)
            self.assertEqual(row["status"], "ACTIVE")

        # 2. Test duplicate ticket rejection
        dup = self.logger.log_trade_deployment(
            ticket_id=ticket,
            direction="BUY",
            volume=1.50,
            entry_price=2650.00,
            sl=2645.00,
            tp=2665.00
        )
        self.assertFalse(dup)

        # 3. Log liquidation with profit
        closed = self.logger.log_trade_liquidation(ticket_id=ticket, final_profit=750.50)
        self.assertTrue(closed)

        with self.logger._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM trades WHERE ticket_id = ?", (ticket,))
            row = dict(cursor.fetchone())
            self.assertEqual(row["status"], "CLOSED")
            self.assertEqual(row["profit"], 750.50)

    def test_log_system_telemetry(self):
        self.logger.log_system_telemetry(
            xau=2655.40,
            dxy=104.25,
            us10y=4.28,
            atr=2.45,
            status="NOMINAL"
        )
        with self.logger._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM telemetry_logs")
            rows = cursor.fetchall()
            self.assertEqual(len(rows), 1)
            row = dict(rows[0])
            self.assertEqual(row["xau_price"], 2655.40)
            self.assertEqual(row["dxy_value"], 104.25)
            self.assertEqual(row["system_status"], "NOMINAL")

    def test_extract_weekly_summary(self):
        # Insert 3 closed trades
        self.logger.log_trade_deployment(101, "BUY", 1.0, 2000.0, 1995.0, 2010.0)
        self.logger.log_trade_liquidation(101, 500.00)

        self.logger.log_trade_deployment(102, "SELL", 0.5, 2005.0, 2010.0, 1995.0)
        self.logger.log_trade_liquidation(102, 250.00)

        summary = self.logger.extract_weekly_summary()
        self.assertEqual(summary["trade_count"], 2)
        self.assertEqual(summary["net_profit"], 750.00)

    def test_run_maintenance(self):
        # Insert recent telemetry
        self.logger.log_system_telemetry(2000.0, 100.0, 4.0, 1.5, "RECENT")

        # Insert old telemetry manually
        old_time = (datetime.now() - timedelta(days=40)).strftime("%Y-%m-%d %H:%M:%S")
        with self.logger._get_connection() as conn:
            conn.execute(
                "INSERT INTO telemetry_logs (timestamp, xau_price, dxy_value, us10y_yield, atr_value, system_status) VALUES (?, 1900.0, 95.0, 3.5, 1.0, 'OLD')",
                (old_time,)
            )
            conn.commit()

        # Run maintenance with 30-day retention
        res = self.logger.run_maintenance(retention_days=30)
        self.assertEqual(res["status"], "OPTIMIZED")
        self.assertEqual(res["deleted_telemetry_rows"], 1)

        # Verify only recent remains
        with self.logger._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM telemetry_logs")
            count = cursor.fetchone()[0]
            self.assertEqual(count, 1)

    def test_generate_compressed_snapshot(self):
        import zipfile
        # Populate with sample data
        self.logger.log_trade_deployment(201, "BUY", 1.0, 2650.0, 2640.0, 2670.0)

        zip_out = os.path.join(self.temp_dir.name, "backups", "test_backup.zip")
        result_path = self.logger.generate_compressed_snapshot(output_zip_path=zip_out)

        self.assertIsNotNone(result_path)
        self.assertTrue(os.path.exists(result_path))
        self.assertGreater(os.path.getsize(result_path), 0)

        # Inspect ZIP archive contents
        with zipfile.ZipFile(result_path, 'r') as zf:
            files = zf.namelist()
            self.assertIn(os.path.basename(self.db_path), files)


if __name__ == "__main__":
    unittest.main()
