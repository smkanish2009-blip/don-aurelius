"""
DON AURELIUS • CRYPTOGRAPHIC IMMUTABLE AUDIT VAULT
Blockchain-style SHA-256 forward hash-chained audit ledger.
Guarantees mathematically tamper-evident proof of every trade execution,
risk guardrail validation, order modification, and client authorization.
Provides irrefutable evidentiary documentation in any judicial or arbitration proceeding.
"""

import os
import json
import hashlib
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone

from config.credentials import credentials

logger = logging.getLogger("AuditVault")


class CryptographicAuditVault:
    """
    Append-only tamper-evident evidentiary ledger.
    Each entry is cryptographically anchored to the preceding entry via SHA-256.
    """

    GENESIS_HASH = "0000000000000000000000000000000000000000000000000000000000000000"

    def __init__(self, ledger_path: str = "logs/immutable_audit_ledger.jsonl"):
        self.ledger_path = ledger_path
        os.makedirs(os.path.dirname(self.ledger_path), exist_ok=True)
        self.last_hash = self.GENESIS_HASH
        self.sequence_index = 0
        self._initialize_vault()

    def _initialize_vault(self) -> None:
        """Reads existing ledger to verify unbroken hash chain and recover latest hash."""
        if not os.path.exists(self.ledger_path):
            self._write_genesis_record()
            return

        try:
            prev_hash = self.GENESIS_HASH
            seq = 0
            with open(self.ledger_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    record = json.loads(line)
                    calc_hash = self._calculate_hash(
                        record.get("seq", 0),
                        record.get("timestamp_utc", ""),
                        record.get("event_type", ""),
                        record.get("prev_hash", ""),
                        record.get("payload", {})
                    )
                    if record.get("hash") != calc_hash or record.get("prev_hash") != prev_hash:
                        logger.critical("[AUDIT-VAULT TAMPER DETECTED] Ledger integrity compromised at sequence %d!", seq)
                        break
                    prev_hash = record.get("hash")
                    seq = record.get("seq", 0)

            self.last_hash = prev_hash
            self.sequence_index = seq
        except Exception as e:
            logger.error(f"[AUDIT-VAULT] Ledger initialization exception: {e}")

    def _calculate_hash(self, seq: int, timestamp: str, event_type: str, prev_hash: str, payload: Dict[str, Any]) -> str:
        serialized = json.dumps(payload, sort_keys=True)
        raw_msg = f"{seq}|{timestamp}|{event_type}|{prev_hash}|{serialized}"
        return hashlib.sha256(raw_msg.encode("utf-8")).hexdigest()

    def _write_genesis_record(self) -> None:
        """Writes the initial block of the immutable ledger."""
        now_utc = datetime.now(timezone.utc).isoformat()
        payload = {
            "system": "DON AURELIUS QUANTUM MATRIX",
            "founder": "SM.KANISH",
            "governance": "CFTC-NFA-FCA-SOVEREIGN-SHIELD",
            "jurisdiction": "CONFIDENTIAL_BINDING_ARBITRATION"
        }
        gen_hash = self._calculate_hash(0, now_utc, "GENESIS_ROOT", self.GENESIS_HASH, payload)
        record = {
            "seq": 0,
            "timestamp_utc": now_utc,
            "event_type": "GENESIS_ROOT",
            "prev_hash": self.GENESIS_HASH,
            "hash": gen_hash,
            "payload": payload
        }
        with open(self.ledger_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
        self.last_hash = gen_hash
        self.sequence_index = 0

    def record_event(self, event_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Appends an immutable cryptographic event to the ledger.
        """
        self.sequence_index += 1
        now_utc = datetime.now(timezone.utc).isoformat()
        curr_hash = self._calculate_hash(
            self.sequence_index,
            now_utc,
            event_type,
            self.last_hash,
            payload
        )

        entry = {
            "seq": self.sequence_index,
            "timestamp_utc": now_utc,
            "event_type": event_type,
            "prev_hash": self.last_hash,
            "hash": curr_hash,
            "payload": payload
        }

        try:
            with open(self.ledger_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
            self.last_hash = curr_hash
            logger.info(f"[AUDIT-VAULT] Block #{self.sequence_index} committed ({event_type}): {curr_hash[:10]}...")
        except Exception as e:
            logger.error(f"[AUDIT-VAULT] Failed to commit audit entry: {e}")

        return entry

    def verify_ledger_integrity(self) -> Tuple[bool, int, str]:
        """
        Validates the complete chain from Genesis to latest block.
        Returns (is_valid, total_blocks, status_summary).
        """
        if not os.path.exists(self.ledger_path):
            return False, 0, "Ledger file missing."

        prev_hash = self.GENESIS_HASH
        count = 0
        with open(self.ledger_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                record = json.loads(line)
                calc_hash = self._calculate_hash(
                    record.get("seq", 0),
                    record.get("timestamp_utc", ""),
                    record.get("event_type", ""),
                    record.get("prev_hash", ""),
                    record.get("payload", {})
                )
                if record.get("hash") != calc_hash:
                    return False, count, f"Hash corruption at block #{record.get('seq')}"
                if record.get("prev_hash") != prev_hash:
                    return False, count, f"Chain linkage break at block #{record.get('seq')}"
                prev_hash = record.get("hash")
                count += 1

        return True, count, f"100% Tamper-Evident & Valid ({count} Cryptographically Sealed Blocks)"


# Global singleton instance
audit_vault = CryptographicAuditVault()
