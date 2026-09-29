"""
Unit Test Suite for JARVIS Orchestrator TITAN-X Integration:
Verifies that the orchestrator invokes the TitanWarRoom Consensus Council,
executes trades only on 3/4 supermajority, applies fractional Kelly sizing,
and aborts immediately when Inquisitor issues a veto.
"""

import unittest
from unittest.mock import MagicMock, patch
import pandas as pd
import numpy as np

from engine.orchestrator import JarvisOrchestrator
from intelligence.war_room import ConsensusVerdict, CouncilVote


class TestOrchestratorTitanX(unittest.TestCase):

    def setUp(self):
        with patch("engine.orchestrator.MT5ExecutionBridge"), \
             patch("engine.orchestrator.JarvisVoiceCore"), \
             patch("engine.orchestrator.JarvisTelegramHUD"), \
             patch("engine.orchestrator.JarvisDatabaseLogger"):
            self.orchestrator = JarvisOrchestrator(symbol="XAUUSD", magic=20260926)

        # Mock dependencies
        self.orchestrator.bridge = MagicMock()
        self.orchestrator.voice = MagicMock()
        self.orchestrator.hud = MagicMock()
        self.orchestrator.db = MagicMock()

    @patch("engine.orchestrator.mt5")
    def test_run_step_executes_on_consensus(self, mock_mt5):
        # Setup mock M15 rates
        dates = pd.date_range("2026-09-25 00:00", periods=50, freq="15min")
        prices = [2650.0 + i * 0.20 for i in range(50)]
        mock_rates = np.array(
            [(int(d.timestamp()), p - 0.2, p + 0.5, p - 0.3, p, 100, 0, 0) for d, p in zip(dates, prices)],
            dtype=[('time', '<i8'), ('open', '<f8'), ('high', '<f8'), ('low', '<f8'),
                   ('close', '<f8'), ('tick_volume', '<u8'), ('spread', '<i4'), ('real_volume', '<u8')]
        )
        mock_mt5.copy_rates_from_pos.return_value = mock_rates
        mock_mt5.TIMEFRAME_M15 = 15

        # Mock tick
        mock_tick = MagicMock()
        mock_tick.ask = 2660.20
        mock_tick.bid = 2660.00  # Spread $0.20 = 2.0 pips
        mock_mt5.symbol_info_tick.return_value = mock_tick

        # Mock War Room consensus returning BUY
        mock_consensus = ConsensusVerdict(
            consensus_achieved=True,
            final_decision="BUY",
            supermajority_count=4,
            supermajority_ratio="4/4",
            recommended_risk_pct=0.0125,
            kelly_fraction=0.10,
            veto_triggered=False,
            votes={
                "HAWK": CouncilVote("HAWK", "BUY", 0.75, "Bullish Trend"),
                "RADAR": CouncilVote("RADAR", "BUY", 0.80, "Bullish Sentiment"),
                "PREDATOR": CouncilVote("PREDATOR", "BUY", 0.85, "Bullish Sweep"),
                "INQUISITOR": CouncilVote("INQUISITOR", "BUY", 0.90, "Approved")
            },
            telemetry={"atr": 2.10, "sl_pips": 52, "tp_pips": 156}
        )
        self.orchestrator.war_room.convene_council = MagicMock(return_value=mock_consensus)

        # Mock bridge order packet return
        self.orchestrator.bridge.transmit_order_packet.return_value = {
            "status": "SUCCESS",
            "ticket": 778899,
            "price": 2660.10,
            "lots": 0.50,
            "sl": 2654.90,
            "tp": 2675.70
        }

        # Run step
        self.orchestrator._last_signal_time = 0.0
        self.orchestrator.run_step()

        # Verify bridge order packet called with Kelly risk
        self.orchestrator.bridge.transmit_order_packet.assert_called_once_with(
            direction="BUY",
            risk_pct=0.0125,
            sl_pips=52,
            tp_pips=156
        )

        # Verify DB logged trade deployment
        self.orchestrator.db.log_trade_deployment.assert_called_once_with(
            ticket_id=778899,
            direction="BUY",
            volume=0.50,
            entry_price=2660.10,
            sl=2654.90,
            tp=2675.70
        )

        # Verify Telegram message contains Council Consensus
        self.orchestrator.hud._send_message.assert_called_once()
        msg = self.orchestrator.hud._send_message.call_args[0][1]
        self.assertIn("COUNCIL CONSENSUS: 4/4", msg)
        self.assertIn("Kelly Risk: 1.25%", msg)

    @patch("engine.orchestrator.mt5")
    def test_run_step_aborts_when_inquisitor_vetoes(self, mock_mt5):
        # Setup mock M15 rates
        mock_rates = np.array(
            [(1700000000 + i * 900, 2650, 2652, 2648, 2650, 100, 0, 0) for i in range(50)],
            dtype=[('time', '<i8'), ('open', '<f8'), ('high', '<f8'), ('low', '<f8'),
                   ('close', '<f8'), ('tick_volume', '<u8'), ('spread', '<i4'), ('real_volume', '<u8')]
        )
        mock_mt5.copy_rates_from_pos.return_value = mock_rates
        mock_mt5.TIMEFRAME_M15 = 15

        # Mock War Room consensus returning HOLD due to Inquisitor VETO
        mock_consensus = ConsensusVerdict(
            consensus_achieved=False,
            final_decision="HOLD",
            supermajority_count=3,
            supermajority_ratio="3/4",
            recommended_risk_pct=0.0,
            kelly_fraction=0.0,
            veto_triggered=True,
            votes={
                "HAWK": CouncilVote("HAWK", "BUY", 0.75, "Bullish Trend"),
                "RADAR": CouncilVote("RADAR", "BUY", 0.80, "Bullish Sentiment"),
                "PREDATOR": CouncilVote("PREDATOR", "BUY", 0.85, "Bullish Sweep"),
                "INQUISITOR": CouncilVote("INQUISITOR", "VETO", 0.10, "Economic embargo")
            },
            rationale="TRADE VETOED BY INQUISITOR. High impact news approaching."
        )
        self.orchestrator.war_room.convene_council = MagicMock(return_value=mock_consensus)

        self.orchestrator._last_signal_time = 0.0
        self.orchestrator.run_step()

        # Bridge must NEVER be called
        self.orchestrator.bridge.transmit_order_packet.assert_not_called()
        self.orchestrator.hud._send_message.assert_not_called()


if __name__ == "__main__":
    unittest.main()
