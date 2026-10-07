"""
Unit tests for Jarvis 2-Way Interactive AI Commander.
"""

import unittest
from unittest.mock import MagicMock
from telemetry.telegram_commander import TelegramCommander


class TestTelegramCommander(unittest.TestCase):
    def setUp(self):
        self.commander = TelegramCommander(
            token="MOCK_TOKEN",
            chat_id="12345678",
            poll_interval_sec=1.0,
        )
        # Mock send_reply so it doesn't make real network calls
        self.commander.send_reply = MagicMock(return_value=True)

    def test_unauthorized_access_denied(self):
        resp = self.commander.process_command(sender_chat_id="99999999", text="/status")
        self.assertIn("ACCESS DENIED", resp)
        self.commander.send_reply.assert_called_once()

    def test_canonical_status_command(self):
        resp = self.commander.process_command(sender_chat_id="12345678", text="/status")
        self.assertIn("DON AURELIUS • LIVE HUD", resp)

    def test_natural_language_status(self):
        resp = self.commander.process_command(sender_chat_id="12345678", text="what is our pnl right now?")
        self.assertIn("DON AURELIUS • LIVE HUD", resp)

    def test_regime_command_and_nlp(self):
        resp_cmd = self.commander.process_command(sender_chat_id="12345678", text="/regime")
        self.assertIn("CHAMELEON BRAIN • ACTIVE REGIME", resp_cmd)

        resp_nlp = self.commander.process_command(sender_chat_id="12345678", text="what is the market regime?")
        self.assertIn("CHAMELEON BRAIN • ACTIVE REGIME", resp_nlp)

    def test_audit_and_risk_commands(self):
        resp_audit = self.commander.process_command(sender_chat_id="12345678", text="/audit")
        self.assertIn("INSTITUTIONAL EXECUTION AUDIT", resp_audit)

        resp_risk = self.commander.process_command(sender_chat_id="12345678", text="/risk")
        self.assertIn("INQUISITOR DEFENSE & RISK MATRIX", resp_risk)

    def test_flatten_two_step_safety_latch(self):
        # Flatten mock callback
        mock_flatten = MagicMock(return_value="[TEST-FLATTEN-SUCCESS]")
        self.commander.flatten_callback = mock_flatten

        # 1. First trigger without confirmation prompt
        resp1 = self.commander.process_command(sender_chat_id="12345678", text="/flatten")
        self.assertIn("CONFIRMATION REQUIRED", resp1)
        mock_flatten.assert_not_called()

        # 2. Reply with CONFIRM executes the flatten callback
        resp2 = self.commander.process_command(sender_chat_id="12345678", text="CONFIRM")
        self.assertEqual(resp2, "[TEST-FLATTEN-SUCCESS]")
        mock_flatten.assert_called_once()

    def test_flatten_direct_confirm(self):
        mock_flatten = MagicMock(return_value="[TEST-FLATTEN-DIRECT-SUCCESS]")
        self.commander.flatten_callback = mock_flatten

        resp = self.commander.process_command(sender_chat_id="12345678", text="/flatten CONFIRM")
        self.assertEqual(resp, "[TEST-FLATTEN-DIRECT-SUCCESS]")
        mock_flatten.assert_called_once()


if __name__ == "__main__":
    unittest.main()
