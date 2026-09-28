"""
Layer 1 Defense: Stale Data Protection & Tick Latency Guard.
Measures millisecond delay between the broker's tick timestamp and the local system clock.
Rejects trades if market data is older than 500 milliseconds.
"""

import time
import logging
from typing import Tuple

logger = logging.getLogger("LatencyGuard")


class LatencyGuard:
    def __init__(self, max_allowed_latency_ms: float = 500.0):
        self.max_allowed_latency_ms = max_allowed_latency_ms
        self._server_offset_ms: float = 0.0
        self._is_calibrated: bool = False

    def calibrate(self, tick_time_msc: int) -> None:
        """Calibrates broker server time offset to the nearest hour."""
        current_time_ms = int(time.time() * 1000)
        raw_diff = tick_time_msc - current_time_ms
        offset_hours = round(raw_diff / 3600000.0)
        self._server_offset_ms = offset_hours * 3600000.0
        self._is_calibrated = True
        logger.info(f"Latency Guard Calibrated: Broker Server Offset = {offset_hours:+} hours ({self._server_offset_ms:.0f} ms).")

    def verify_tick_freshness(self, tick_time_msc: int) -> Tuple[bool, float, str]:
        """
        Compares broker tick timestamp in milliseconds with calibrated current time.
        Returns: (is_fresh: bool, latency_ms: float, message: str)
        """
        if not self._is_calibrated:
            self.calibrate(tick_time_msc)

        current_time_ms = int(time.time() * 1000)
        calibrated_server_time = current_time_ms + self._server_offset_ms
        delta_ms = abs(calibrated_server_time - tick_time_msc)

        if delta_ms > self.max_allowed_latency_ms:
            msg = f"Stale Data Rejected: Tick latency is {delta_ms:.1f}ms (Threshold: {self.max_allowed_latency_ms}ms)."
            logger.warning(msg)
            return False, delta_ms, msg

        return True, delta_ms, "Tick data is fresh."
