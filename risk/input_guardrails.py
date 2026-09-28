"""
Layer 1 Defense: Input Sanitization & Geometry Guardrails.
Filters AI outputs to block erratic predictions, unrealistic price quotes,
and invalid order geometries before MT5 submission.
"""

import logging
from typing import Tuple
from pydantic import BaseModel, Field, model_validator
from strategy.models import SignalDirection

logger = logging.getLogger("InputGuardrails")


class SanitizedOrderRequest(BaseModel):
    direction: SignalDirection
    current_market_price: float = Field(..., gt=0.0)
    entry_price: float = Field(..., gt=0.0)
    stop_loss: float = Field(..., gt=0.0)
    take_profit: float = Field(..., gt=0.0)
    lots: float = Field(..., ge=0.01, le=20.0)

    @model_validator(mode="after")
    def validate_entry_vs_market(self):
        if self.current_market_price > 0:
            deviation_pct = abs(self.entry_price - self.current_market_price) / self.current_market_price * 100.0
            if deviation_pct > 0.35:
                raise ValueError(
                    f"Erratic Entry Price: Proposed entry ${self.entry_price:.2f} deviates {deviation_pct:.2f}% "
                    f"from market ${self.current_market_price:.2f} (Limit: 0.35%)."
                )
        return self


class InputGuardrails:
    @staticmethod
    def sanitize(direction: SignalDirection, entry: float, sl: float, tp: float,
                 lots: float, current_market_price: float) -> Tuple[bool, str]:
        """
        Validates order schema, price bounds, and geometric ordering:
        BUY: SL < Entry < TP
        SELL: TP < Entry < SL
        """
        try:
            req = SanitizedOrderRequest(
                direction=direction,
                entry_price=round(entry, 2),
                stop_loss=round(sl, 2),
                take_profit=round(tp, 2),
                lots=round(lots, 2),
                current_market_price=round(current_market_price, 2)
            )

            # Geometry Assertions
            if req.direction == SignalDirection.BUY:
                if not (req.stop_loss < req.entry_price < req.take_profit):
                    return False, f"Geometry Inversion: Buy requires SL ({req.stop_loss}) < Entry ({req.entry_price}) < TP ({req.take_profit})."
            elif req.direction == SignalDirection.SELL:
                if not (req.take_profit < req.entry_price < req.stop_loss):
                    return False, f"Geometry Inversion: Sell requires TP ({req.take_profit}) < Entry ({req.entry_price}) < SL ({req.stop_loss})."

            logger.info("Order input sanitization passed.")
            return True, "Input Sanitization Clean."

        except Exception as e:
            msg = f"Sanitization Guardrail Blocked Order: {e}"
            logger.error(msg)
            return False, msg
