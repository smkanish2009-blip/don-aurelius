"""
Institutional Lot Sizer for XAUUSD.
Implements the exact mathematical formula from Section 8 of the PDF specification:
Dynamically computes contract exposure using MT5 broker tick values and steps.
"""

import math
import logging
from typing import Optional, Tuple
from config.settings import RiskParameters

logger = logging.getLogger("PositionSizer")


class PositionSizer:
    def __init__(self, risk_params: RiskParameters):
        self.params = risk_params

    def calculate_lots(self, equity: float, entry_price: float, stop_loss: float,
                       tick_size: float, tick_value: float,
                       min_lot: float = 0.01, max_lot: float = 100.0,
                       lot_step: float = 0.01, risk_pct_override: Optional[float] = None) -> Tuple[float, float]:
        """
        Calculates position lots and total risked dollar amount.
        Returns: (lots: float, risk_money: float)
        """
        risk_pct = risk_pct_override if risk_pct_override is not None else self.params.RISK_PER_TRADE_PERCENT
        risk_money = equity * (risk_pct / 100.0)

        stop_dist = abs(entry_price - stop_loss)
        if stop_dist <= 0:
            logger.error("Stop distance is zero or negative. Cannot size position.")
            return 0.0, 0.0

        loss_per_lot = (stop_dist / tick_size) * tick_value
        if loss_per_lot <= 0:
            logger.error("Loss per lot calculation yielded zero.")
            return 0.0, 0.0

        raw_lots = risk_money / loss_per_lot

        # Round DOWN to nearest lot_step
        steps = math.floor(raw_lots / lot_step)
        lots = round(steps * lot_step, 2)

        # Clamp between min_lot and max_lot
        lots = max(min_lot, min(lots, max_lot))

        # PDF Safety check: if min_lot risks > 125% of intended risk_money, skip trade
        actual_risk = lots * loss_per_lot
        if actual_risk > (1.25 * risk_money):
            logger.warning(f"Calculated lots ({lots}) risk ${actual_risk:.2f} which exceeds 1.25x limit (${risk_money:.2f}). Skipping.")
            return 0.0, 0.0

        logger.info(f"Position Sized: Equity=${equity:.2f} | Risk={risk_pct}% (${risk_money:.2f}) | "
                    f"StopDist=${stop_dist:.2f} | Loss/Lot=${loss_per_lot:.2f} | FinalLots={lots}")
        return lots, risk_money
