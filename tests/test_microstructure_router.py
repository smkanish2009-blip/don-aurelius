"""
Unit tests for Microstructure Intelligence & Smart Order Routing Suite.
"""

import unittest
from execution.microstructure_router import (
    SpreadHeatmap,
    IcebergSlicer,
    StealthTrailingStopManager,
)


class TestMicrostructureRouter(unittest.TestCase):
    def test_spread_heatmap_anomaly_detection(self):
        heatmap = SpreadHeatmap(window_size=100, z_score_threshold=2.0)

        # Feed 50 normal ticks around 0.18 - 0.22
        for _ in range(50):
            metrics = heatmap.evaluate_spread(0.20)

        self.assertFalse(metrics.is_anomaly)
        self.assertAlmostEqual(metrics.median_spread, 0.20, places=2)

        # Feed sudden spike
        spike_metrics = heatmap.evaluate_spread(0.85)
        self.assertTrue(spike_metrics.is_anomaly)
        self.assertGreater(spike_metrics.z_score, 2.0)

    def test_iceberg_slicer_small_order(self):
        slicer = IcebergSlicer(threshold_lot=0.75)
        plan = slicer.generate_plan(0.50, recent_tick_volume=1200)

        self.assertEqual(plan.chunk_count, 1)
        self.assertEqual(plan.chunks, [0.50])
        self.assertEqual(plan.total_lots, 0.50)

    def test_iceberg_slicer_large_order(self):
        slicer = IcebergSlicer(threshold_lot=0.75)
        plan = slicer.generate_plan(2.10, recent_tick_volume=1500)

        self.assertGreater(plan.chunk_count, 1)
        self.assertAlmostEqual(sum(plan.chunks), 2.10, places=2)
        for c in plan.chunks:
            self.assertLessEqual(c, 0.50)

    def test_stealth_trailing_stop_buy(self):
        mgr = StealthTrailingStopManager()
        ticket = 1043471
        mgr.register_trade(
            ticket=ticket,
            direction="BUY",
            entry_price=2650.00,
            initial_sl=2645.00,
            trailing_atr_mult=1.5,
        )

        atr = 2.0  # trail distance = 3.0

        # Price advances to 2655 -> new stealth SL should be 2655 - 3.0 = 2652.00
        should_close, trigger_p, reason = mgr.update_tick(ticket, current_bid=2655.00, current_ask=2655.20, atr_m15=atr)
        self.assertFalse(should_close)
        self.assertEqual(trigger_p, 2652.00)

        # Price pulls back to 2653 -> should NOT close yet, SL remains at 2652.00
        should_close, trigger_p, _ = mgr.update_tick(ticket, current_bid=2653.00, current_ask=2653.20, atr_m15=atr)
        self.assertFalse(should_close)
        self.assertEqual(trigger_p, 2652.00)

        # Price penetrates stealth SL to 2651.80 -> trigger close!
        should_close, trigger_p, reason = mgr.update_tick(ticket, current_bid=2651.80, current_ask=2652.00, atr_m15=atr)
        self.assertTrue(should_close)
        self.assertEqual(trigger_p, 2652.00)

    def test_stealth_trailing_stop_sell(self):
        mgr = StealthTrailingStopManager()
        ticket = 1043472
        mgr.register_trade(
            ticket=ticket,
            direction="SELL",
            entry_price=2650.00,
            initial_sl=2655.00,
            trailing_atr_mult=1.5,
        )

        atr = 2.0  # trail distance = 3.0

        # Price drops to 2642 -> new stealth SL should be 2642 + 3.0 = 2645.00
        should_close, trigger_p, _ = mgr.update_tick(ticket, current_bid=2641.80, current_ask=2642.00, atr_m15=atr)
        self.assertFalse(should_close)
        self.assertEqual(trigger_p, 2645.00)

        # Price climbs back to 2645.50 -> ask penetrates stealth SL 2645.00 -> trigger close!
        should_close, trigger_p, _ = mgr.update_tick(ticket, current_bid=2645.30, current_ask=2645.50, atr_m15=atr)
        self.assertTrue(should_close)
        self.assertEqual(trigger_p, 2645.00)


if __name__ == "__main__":
    unittest.main()
