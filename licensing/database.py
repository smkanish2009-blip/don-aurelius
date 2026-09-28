"""
Thread-safe ACID SQLite Entitlement Database.
Handles Users, Licenses, Subscriptions, Gas Balances, MT5 Account Binds, and Audit Trails.
"""

import os
import sqlite3
import threading
import logging
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timezone, timedelta
from licensing.models import BillingTier, LicenseStatus, LicenseRecord, PaymentGateway, PaymentStatus

logger = logging.getLogger("LicensingDatabase")


class LicensingDatabase:
    def __init__(self, db_path: str = "data/entitlement.db"):
        self.db_path = db_path
        self._local = threading.local()
        self._lock = threading.Lock()
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = getattr(self._local, "conn", None)
        conn_path = getattr(self._local, "conn_path", None)
        if conn is None or conn_path != self.db_path:
            if conn is not None:
                try:
                    conn.close()
                except Exception:
                    pass
            conn = sqlite3.connect(self.db_path, timeout=15.0)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA journal_mode = WAL;")
            conn.execute("PRAGMA synchronous = NORMAL;")
            conn.execute("PRAGMA foreign_keys = ON;")
            self._local.conn = conn
            self._local.conn_path = self.db_path
        return conn

    def close(self) -> None:
        """Closes thread-local connection."""
        conn = getattr(self._local, "conn", None)
        if conn is not None:
            try:
                conn.close()
            except Exception:
                pass
            self._local.conn = None
            self._local.conn_path = None

    def _init_db(self) -> None:
        conn = self._get_connection()
        with conn:
            conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                stripe_customer_id TEXT,
                whop_user_id TEXT,
                created_at TEXT NOT NULL
            );
            """)

            conn.execute("""
            CREATE TABLE IF NOT EXISTS licenses (
                license_key TEXT PRIMARY KEY,
                user_email TEXT NOT NULL,
                tier TEXT NOT NULL,
                mt5_account_id INTEGER,
                machine_fingerprint TEXT,
                status TEXT NOT NULL,
                expires_at TEXT,
                gas_balance_usd REAL NOT NULL DEFAULT 0.0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (user_email) REFERENCES users(email) ON DELETE CASCADE
            );
            """)

            conn.execute("""
            CREATE TABLE IF NOT EXISTS payment_transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_id TEXT UNIQUE NOT NULL,
                user_email TEXT NOT NULL,
                gateway TEXT NOT NULL,
                amount_usd REAL NOT NULL,
                tier TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            """)

            conn.execute("""
            CREATE TABLE IF NOT EXISTS audit_trail (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                license_key TEXT,
                details TEXT NOT NULL,
                timestamp TEXT NOT NULL
            );
            """)
            conn.commit()
        logger.info(f"Initialized Licensing Database at {self.db_path} (WAL Mode)")

    def get_or_create_user(self, email: str, stripe_customer_id: Optional[str] = None, whop_user_id: Optional[str] = None) -> int:
        conn = self._get_connection()
        email_clean = email.lower().strip()
        with conn:
            cursor = conn.execute("SELECT id FROM users WHERE email = ?", (email_clean,))
            row = cursor.fetchone()
            if row:
                if stripe_customer_id or whop_user_id:
                    conn.execute("""
                    UPDATE users SET
                        stripe_customer_id = COALESCE(?, stripe_customer_id),
                        whop_user_id = COALESCE(?, whop_user_id)
                    WHERE email = ?
                    """, (stripe_customer_id, whop_user_id, email_clean))
                    conn.commit()
                return row["id"]
            else:
                now_str = datetime.now(timezone.utc).isoformat()
                cursor = conn.execute("""
                INSERT INTO users (email, stripe_customer_id, whop_user_id, created_at)
                VALUES (?, ?, ?, ?)
                """, (email_clean, stripe_customer_id, whop_user_id, now_str))
                conn.commit()
                return cursor.lastrowid

    def create_license(self,
                       license_key: str,
                       user_email: str,
                       tier: BillingTier,
                       mt5_account_id: Optional[int] = None,
                       machine_fingerprint: Optional[str] = None,
                       expires_at: Optional[datetime] = None,
                       gas_balance_usd: float = 0.0) -> LicenseRecord:
        conn = self._get_connection()
        self.get_or_create_user(user_email)
        now = datetime.now(timezone.utc)
        now_str = now.isoformat()
        expires_str = expires_at.isoformat() if expires_at else None

        with conn:
            conn.execute("""
            INSERT INTO licenses (
                license_key, user_email, tier, mt5_account_id, machine_fingerprint,
                status, expires_at, gas_balance_usd, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(license_key) DO UPDATE SET
                tier = excluded.tier,
                status = excluded.status,
                expires_at = excluded.expires_at,
                gas_balance_usd = excluded.gas_balance_usd,
                updated_at = excluded.updated_at
            """, (
                license_key, user_email.lower().strip(), tier.value, mt5_account_id, machine_fingerprint,
                LicenseStatus.ACTIVE.value, expires_str, gas_balance_usd, now_str, now_str
            ))
            conn.commit()

        self.log_audit("LICENSE_CREATED", license_key, f"Tier={tier.value} | User={user_email} | Expiry={expires_str}")
        return self.get_license(license_key)

    def get_license(self, license_key: str) -> Optional[LicenseRecord]:
        conn = self._get_connection()
        cursor = conn.execute("SELECT * FROM licenses WHERE license_key = ?", (license_key,))
        row = cursor.fetchone()
        if not row:
            return None
        return self._row_to_record(row)

    def get_license_by_account(self, mt5_account_id: int) -> Optional[LicenseRecord]:
        conn = self._get_connection()
        cursor = conn.execute("SELECT * FROM licenses WHERE mt5_account_id = ?", (mt5_account_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return self._row_to_record(row)

    def get_licenses_by_email(self, email: str) -> List[LicenseRecord]:
        conn = self._get_connection()
        cursor = conn.execute("SELECT * FROM licenses WHERE user_email = ?", (email.lower().strip(),))
        return [self._row_to_record(r) for r in cursor.fetchall()]

    def bind_account_and_machine(self,
                                 license_key: str,
                                 mt5_account_id: int,
                                 machine_fingerprint: str) -> Tuple[bool, str]:
        record = self.get_license(license_key)
        if not record:
            return False, f"License key '{license_key}' not found."

        if record.status in (LicenseStatus.REVOKED, LicenseStatus.SUSPENDED):
            return False, f"License is {record.status.value}. Contact support."

        if record.mt5_account_id is not None and record.mt5_account_id != mt5_account_id:
            msg = f"Anti-Piracy Violation: License is locked to MT5 #{record.mt5_account_id}, cannot bind to #{mt5_account_id}."
            logger.warning(msg)
            self.log_audit("BIND_REJECTED", license_key, msg)
            return False, msg

        conn = self._get_connection()
        now_str = datetime.now(timezone.utc).isoformat()
        with conn:
            conn.execute("""
            UPDATE licenses SET
                mt5_account_id = ?,
                machine_fingerprint = ?,
                updated_at = ?
            WHERE license_key = ?
            """, (mt5_account_id, machine_fingerprint, now_str, license_key))
            conn.commit()

        self.log_audit("ACCOUNT_BOUND", license_key, f"Bound to MT5 #{mt5_account_id} | Machine={machine_fingerprint}")
        return True, "Account bound successfully."

    def extend_license(self, license_key: str, days: int) -> Optional[LicenseRecord]:
        record = self.get_license(license_key)
        if not record:
            return None

        now = datetime.now(timezone.utc)
        current_exp = record.expires_at or now
        base_date = max(now, current_exp)
        new_exp = base_date + timedelta(days=days)

        conn = self._get_connection()
        with conn:
            conn.execute("""
            UPDATE licenses SET
                expires_at = ?,
                status = ?,
                updated_at = ?
            WHERE license_key = ?
            """, (new_exp.isoformat(), LicenseStatus.ACTIVE.value, now.isoformat(), license_key))
            conn.commit()

        self.log_audit("LICENSE_EXTENDED", license_key, f"Extended by {days} days. New Expiry: {new_exp.isoformat()}")
        return self.get_license(license_key)

    def update_license_status(self, license_key: str, status: LicenseStatus) -> bool:
        conn = self._get_connection()
        now_str = datetime.now(timezone.utc).isoformat()
        with conn:
            conn.execute("""
            UPDATE licenses SET status = ?, updated_at = ? WHERE license_key = ?
            """, (status.value, now_str, license_key))
            conn.commit()
        self.log_audit("STATUS_CHANGED", license_key, f"Status updated to {status.value}")
        return True

    def topup_gas(self, license_key: str, amount_usd: float) -> float:
        conn = self._get_connection()
        now_str = datetime.now(timezone.utc).isoformat()
        with conn:
            conn.execute("""
            UPDATE licenses SET
                gas_balance_usd = gas_balance_usd + ?,
                status = CASE WHEN status = 'GRACEFUL_DISCONNECT' THEN 'ACTIVE' ELSE status END,
                updated_at = ?
            WHERE license_key = ?
            """, (amount_usd, now_str, license_key))
            conn.commit()

        record = self.get_license(license_key)
        new_bal = record.gas_balance_usd if record else 0.0
        self.log_audit("GAS_TOPUP", license_key, f"Added ${amount_usd:.2f} | New Balance: ${new_bal:.2f}")
        return new_bal

    def deduct_gas(self, license_key: str, amount_usd: float) -> Tuple[bool, float]:
        record = self.get_license(license_key)
        if not record:
            return False, 0.0

        new_bal = max(0.0, record.gas_balance_usd - amount_usd)
        new_status = LicenseStatus.GRACEFUL_DISCONNECT.value if new_bal <= 0.0 else record.status.value

        conn = self._get_connection()
        now_str = datetime.now(timezone.utc).isoformat()
        with conn:
            conn.execute("""
            UPDATE licenses SET
                gas_balance_usd = ?,
                status = ?,
                updated_at = ?
            WHERE license_key = ?
            """, (new_bal, new_status, now_str, license_key))
            conn.commit()

        self.log_audit("GAS_DEDUCTION", license_key, f"Deducted ${amount_usd:.2f} | Balance: ${new_bal:.2f}")
        return True, new_bal

    def record_payment(self,
                       transaction_id: str,
                       user_email: str,
                       gateway: PaymentGateway,
                       amount_usd: float,
                       tier: BillingTier,
                       status: PaymentStatus) -> bool:
        conn = self._get_connection()
        now_str = datetime.now(timezone.utc).isoformat()
        with conn:
            conn.execute("""
            INSERT INTO payment_transactions (
                transaction_id, user_email, gateway, amount_usd, tier, status, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(transaction_id) DO UPDATE SET
                status = excluded.status
            """, (transaction_id, user_email.lower().strip(), gateway.value, amount_usd, tier.value, status.value, now_str))
            conn.commit()
        return True

    def log_audit(self, event_type: str, license_key: Optional[str], details: str) -> None:
        try:
            conn = self._get_connection()
            now_str = datetime.now(timezone.utc).isoformat()
            with conn:
                conn.execute("""
                INSERT INTO audit_trail (event_type, license_key, details, timestamp)
                VALUES (?, ?, ?, ?)
                """, (event_type, license_key, details, now_str))
                conn.commit()
        except Exception as e:
            logger.error(f"Audit log failed: {e}")

    def _row_to_record(self, row: sqlite3.Row) -> LicenseRecord:
        exp_dt = None
        if row["expires_at"]:
            try:
                exp_dt = datetime.fromisoformat(row["expires_at"])
            except Exception:
                pass
        return LicenseRecord(
            license_key=row["license_key"],
            user_email=row["user_email"],
            tier=BillingTier(row["tier"]),
            mt5_account_id=row["mt5_account_id"],
            machine_fingerprint=row["machine_fingerprint"],
            status=LicenseStatus(row["status"]),
            expires_at=exp_dt,
            gas_balance_usd=float(row["gas_balance_usd"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"])
        )
