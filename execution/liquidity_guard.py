"""
Layer 3 Defense: Liquidity & Market Depth Thresholds.
Verifies that our order size does not exceed 1% of the available market depth
or recent 5-minute bar volume to eliminate self-inflicted price distortion.
"""

import logging
from typing import Tuple

logger = logging.getLogger("LiquidityGuard")


class LiquidityGuard:
    def __init__(self, max_liquidity_share_pct: float = 1.0):
        self.max_share = max_liquidity_share_pct / 100.0

    def verify_volume_share(self, lots: float, recent_m5_tick_volume: int) -> Tuple[bool, str]:
        """
        Assumes 1 standard lot = 100 oz.
        Verifies that lot volume is less than 1% of the recent volume.
        """
        if recent_m5_tick_volume <= 0:
            return True, "No volume data, passing."

        # Gold volume normalization
        estimated_volume_capacity = max(100.0, float(recent_m5_tick_volume))
        allowed_lots = estimated_volume_capacity * self.max_share

        if lots > allowed_lots:
            msg = f"Liquidity Veto: Order size {lots:.2f} lots exceeds 1% market capacity ({allowed_lots:.2f} lots)."
            logger.warning(msg)
            return False, msg

        return True, "Liquidity threshold verified."
