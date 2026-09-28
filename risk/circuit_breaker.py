"""
Layer 1 Defense: Dynamic Circuit Breakers.
Monitors consecutive losses. When 3 consecutive losses occur,
triggers a 4-hour automatic lockout cooling period to eliminate tilt/revenge loops.
"""

import time
import logging
from typing import Tuple

logger = logging.getLogger("CircuitBreaker")


class CircuitBreaker:
    def __init__(self, max_consecutive_losses: int = 3, cooldown_seconds: int = 14400):  # 14400s = 4 hours
        self.max_consecutive_losses = max_consecutive_losses
        self.cooldown_seconds = cooldown_seconds
        self.consecutive_losses = 0
        self.lockout_until = 0.0

    def record_outcome(self, is_win: bool) -> None:
        if is_win:
            self.consecutive_losses = 0
            logger.info("Circuit Breaker: Winning trade recorded. Consecutive loss counter reset.")
        else:
            self.consecutive_losses += 1
            logger.warning(f"Circuit Breaker: Loss recorded. Current streak: {self.consecutive_losses} losses.")
            if self.consecutive_losses >= self.max_consecutive_losses:
                self.lockout_until = time.time() + self.cooldown_seconds
                logger.critical(f"[CIRCUIT-BREAKER] TRIPPED! 3 Consecutive Losses. Trading locked out for {self.cooldown_seconds / 3600:.1f} hours.")

    def is_locked_out(self) -> Tuple[bool, float]:
        """Returns: (is_locked: bool, remaining_seconds: float)"""
        now = time.time()
        if now < self.lockout_until:
            rem = self.lockout_until - now
            return True, rem
        return False, 0.0
