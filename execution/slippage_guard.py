"""
Layer 3 Defense: Slippage Cap Policy.
Rejects or aborts trades if actual broker execution price deviates by more than
the maximum slippage cap ($0.30 - $0.50 on gold, or 0.02%).
"""

import logging
from typing import Tuple

logger = logging.getLogger("SlippageGuard")


class SlippageGuard:
    def __init__(self, max_slippage_usd: float = 0.30):
        self.max_slippage_usd = max_slippage_usd

    def verify_execution_slippage(self, expected_price: float, filled_price: float) -> Tuple[bool, float, str]:
        """Compares filled price against expected quote."""
        slippage = abs(filled_price - expected_price)
        if slippage > self.max_slippage_usd:
            msg = f"Slippage Alert: Fill price ${filled_price:.2f} slipped ${slippage:.2f} from expected ${expected_price:.2f} (Limit: ${self.max_slippage_usd:.2f})."
            logger.warning(msg)
            return False, slippage, msg
        return True, slippage, "Slippage within acceptable tolerance."
