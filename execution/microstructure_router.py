"""
Microstructure Intelligence & Smart Order Routing Engine.
=========================================================
Institutional Execution Defense Suite for XAUUSD:
  1. Dynamic Spread Heatmap: Real-time statistical spread anomaly detection (percentile + Z-score).
  2. Iceberg / TWAP Order Slicer: Splits institutional lots into micro-chunks to minimize market impact.
  3. Stealth Trailing Stop Manager: Calculates trailing stops in local memory without exposing resting
     stop loss orders to dealing desk stop-hunting algorithms.
"""

import logging
import math
import time
from collections import deque
from dataclasses import dataclass
from typing import List, Optional, Tuple, Dict, Any
import numpy as np

logger = logging.getLogger("MicrostructureRouter")


@dataclass
class SpreadMetrics:
    current_spread: float
    median_spread: float
    p90_spread: float
    z_score: float
    is_anomaly: bool
    status_msg: str


@dataclass
class IcebergPlan:
    total_lots: float
    chunk_count: int
    chunks: List[float]
    recommended_delay_sec: float
    reason: str


class SpreadHeatmap:
    """
    Maintains a rolling statistical window of live market spreads.
    Detects predatory broker spread widening before order dispatch.
    """

    def __init__(self, window_size: int = 150, z_score_threshold: float = 2.2):
        self.window_size = window_size
        self.z_score_threshold = z_score_threshold
        self.history: deque = deque(maxlen=window_size)

    def record_tick(self, spread: float) -> None:
        """Appends current tick spread to rolling window."""
        if spread > 0.0:
            self.history.append(float(spread))

    def evaluate_spread(self, current_spread: float) -> SpreadMetrics:
        """
        Analyzes the current spread against the historical distribution.
        """
        self.record_tick(current_spread)

        if len(self.history) < 20:
            # Insufficient samples for robust statistical distribution
            return SpreadMetrics(
                current_spread=current_spread,
                median_spread=current_spread,
                p90_spread=current_spread,
                z_score=0.0,
                is_anomaly=False,
                status_msg="Warm-up: establishing baseline spread distribution.",
            )

        arr = np.array(self.history)
        median = float(np.median(arr))
        p90 = float(np.percentile(arr, 90))
        std = float(np.std(arr))

        z_score = float((current_spread - median) / (std + 1e-6)) if std > 0 else 0.0
        is_anomaly = (current_spread > p90 and current_spread > median * 1.45) or (z_score >= self.z_score_threshold)

        if is_anomaly:
            msg = f"Spread Anomaly Detected: {current_spread:.2f} (median: {median:.2f}, p90: {p90:.2f}, Z: {z_score:.2f})."
        else:
            msg = f"Spread Nominal: {current_spread:.2f} (median: {median:.2f}, Z: {z_score:.2f})."

        return SpreadMetrics(
            current_spread=round(current_spread, 3),
            median_spread=round(median, 3),
            p90_spread=round(p90, 3),
            z_score=round(z_score, 2),
            is_anomaly=is_anomaly,
            status_msg=msg,
        )


class IcebergSlicer:
    """
    Slices large orders into stealth micro-chunks to eliminate market footprint and slippage.
    """

    def __init__(self, min_lot: float = 0.01, max_lot: float = 50.0, lot_step: float = 0.01, threshold_lot: float = 0.75):
        self.min_lot = min_lot
        self.max_lot = max_lot
        self.lot_step = lot_step
        self.threshold_lot = threshold_lot

    def generate_plan(self, requested_lots: float, recent_tick_volume: int = 1000) -> IcebergPlan:
        """
        Generates micro-chunks based on trade size and recent liquidity depth.
        """
        lots = round(max(self.min_lot, min(self.max_lot, requested_lots)), 2)

        # If below threshold, dispatch in single direct chunk
        if lots <= self.threshold_lot:
            return IcebergPlan(
                total_lots=lots,
                chunk_count=1,
                chunks=[lots],
                recommended_delay_sec=0.0,
                reason="Order size under iceberg threshold; direct dispatch optimal.",
            )

        # Dynamic chunk sizing based on tick volume
        # High volume allows larger chunks (0.40 - 0.50 lots); thin volume mandates 0.20 - 0.25 lots
        if recent_tick_volume >= 2500:
            slice_size = 0.50
        elif recent_tick_volume >= 1000:
            slice_size = 0.35
        else:
            slice_size = 0.20

        chunks: List[float] = []
        rem = lots
        while rem > 0:
            c = round(min(slice_size, rem), 2)
            if rem - c < self.min_lot and rem - c > 0:
                c = round(rem, 2)
            chunks.append(c)
            rem = round(rem - c, 2)

        return IcebergPlan(
            total_lots=lots,
            chunk_count=len(chunks),
            chunks=chunks,
            recommended_delay_sec=0.35,  # 350ms pacing between sub-second bursts
            reason=f"Institutional Iceberg Slicing: {lots} lots split into {len(chunks)} stealth micro-chunks.",
        )


class StealthTrailingStopManager:
    """
    Maintains stealth trailing stop levels locally in volatile gold trading.
    Prevents broker dealing desks from hunting visible server-side stops.
    """

    def __init__(self):
        # Maps ticket -> dict of state
        self.stealth_trades: Dict[int, Dict[str, Any]] = {}

    def register_trade(
        self,
        ticket: int,
        direction: str,
        entry_price: float,
        initial_sl: float,
        trailing_atr_mult: float = 1.5,
    ) -> None:
        self.stealth_trades[ticket] = {
            "direction": direction,
            "entry_price": entry_price,
            "initial_sl": initial_sl,
            "stealth_sl": initial_sl,
            "highest_seen": entry_price,
            "lowest_seen": entry_price,
            "trailing_atr_mult": trailing_atr_mult,
            "activated": False,
        }
        logger.info(f"[STEALTH-TRAIL] Trade #{ticket} registered with stealth SL at {initial_sl:.2f}.")

    def update_tick(self, ticket: int, current_bid: float, current_ask: float, atr_m15: float) -> Tuple[bool, float, str]:
        """
        Updates stealth trailing stop level.
        Returns: (should_close, trigger_price, reason)
        """
        meta = self.stealth_trades.get(ticket)
        if not meta:
            return False, 0.0, "Trade not tracked in stealth registry."

        direction = meta["direction"]
        trail_dist = max(0.50, atr_m15 * meta["trailing_atr_mult"])

        if direction == "BUY":
            current_price = current_bid
            if current_price > meta["highest_seen"]:
                meta["highest_seen"] = current_price
                new_stealth = current_price - trail_dist
                # Only ratchet stop upwards
                if new_stealth > meta["stealth_sl"]:
                    meta["stealth_sl"] = round(new_stealth, 2)
                    meta["activated"] = True

            # Trigger condition: market bid penetrates stealth SL
            if current_price <= meta["stealth_sl"] and meta["activated"]:
                return True, meta["stealth_sl"], f"Stealth Trailing Stop triggered at {meta['stealth_sl']:.2f} (Bid: {current_price:.2f})."

        elif direction == "SELL":
            current_price = current_ask
            if current_price < meta["lowest_seen"]:
                meta["lowest_seen"] = current_price
                new_stealth = current_price + trail_dist
                # Only ratchet stop downwards
                if new_stealth < meta["stealth_sl"]:
                    meta["stealth_sl"] = round(new_stealth, 2)
                    meta["activated"] = True

            # Trigger condition: market ask penetrates stealth SL
            if current_price >= meta["stealth_sl"] and meta["activated"]:
                return True, meta["stealth_sl"], f"Stealth Trailing Stop triggered at {meta['stealth_sl']:.2f} (Ask: {current_price:.2f})."

        return False, meta["stealth_sl"], "Active in stealth bounds."

    def deregister_trade(self, ticket: int) -> None:
        if ticket in self.stealth_trades:
            del self.stealth_trades[ticket]
            logger.info(f"[STEALTH-TRAIL] Trade #{ticket} deregistered.")
