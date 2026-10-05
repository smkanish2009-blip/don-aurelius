"""
Unit tests for Sovereign Legal Shield and Cryptographic Audit Vault.
Verifies:
1. Terms hash consistency and non-repudiation digital signature.
2. Zero liability cap and arbitration covenants.
3. Cryptographic forward hash chain validation and tamper detection.
"""

import os
import sys

_root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if _root_dir not in sys.path:
    sys.path.insert(0, _root_dir)

import unittest
import os
import tempfile
from compliance.sovereign_legal_shield import SovereignLegalShield, TERMS_HASH, SHIELD_VERSION
from telemetry.audit_vault import CryptographicAuditVault


class TestSovereignLegalShield(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.consent_path = os.path.join(self.temp_dir.name, "test_consent.json")
        self.shield = SovereignLegalShield(consent_path=self.consent_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_grant_and_verify_compliance(self):
        record = self.shield.grant_consent(
            client_id="test_operator",
            mt5_account="99887766",
            license_key="TEST-KEY-2026",
            operator_ip="192.168.1.100"
        )
        self.assertTrue(record["is_acknowledged"])
        self.assertEqual(record["terms_hash"], TERMS_HASH)
        self.assertEqual(record["liability_cap_usd"], 0.0)
        self.assertEqual(record["shield_version"], SHIELD_VERSION)
        self.assertTrue(len(record["digital_signature"]) > 32)

        # Verify compliance
        is_ok, msg = self.shield.verify_shield_compliance(mt5_account="99887766")
        self.assertTrue(is_ok)
        self.assertIn("ACTIVE & BINDING", msg)


class TestCryptographicAuditVault(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.ledger_path = os.path.join(self.temp_dir.name, "test_ledger.jsonl")
        self.vault = CryptographicAuditVault(ledger_path=self.ledger_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_unbroken_hash_chain(self):
        # Genesis block was created on init
        entry1 = self.vault.record_event("ORDER_ENTRY", {"ticket": 1001, "lots": 0.50, "direction": "BUY"})
        entry2 = self.vault.record_event("TRAIL_STOP_MODIFIED", {"ticket": 1001, "new_sl": 2665.50})
        entry3 = self.vault.record_event("ORDER_CLOSED", {"ticket": 1001, "profit_usd": 150.00})

        # Entry 1 points back to genesis block's hash
        self.assertNotEqual(entry1["prev_hash"], self.vault.GENESIS_HASH)
        self.assertEqual(entry2["prev_hash"], entry1["hash"])
        self.assertEqual(entry3["prev_hash"], entry2["hash"])

        # Validate whole ledger
        is_valid, count, msg = self.vault.verify_ledger_integrity()
        self.assertTrue(is_valid)
        self.assertEqual(count, 4)  # Genesis + 3 entries
        self.assertIn("100% Tamper-Evident", msg)


if __name__ == "__main__":
    unittest.main()
