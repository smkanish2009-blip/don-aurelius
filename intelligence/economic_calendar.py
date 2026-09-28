"""
TITAN-X Economic Calendar & News Proximity Shield.
Protects the Algorithmic Matrix against Tier-1 Macroeconomic Slippage & Liquidity Voids
(FOMC, NFP, CPI, Core PCE, Central Bank Speeches).
"""

from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional, Tuple
import logging

logger = logging.getLogger("TitanX.Calendar")


class EconomicCalendarShield:
    """
    Evaluates real-time proximity to high-impact economic releases.
    When a Tier-1 event is within the embargo window (default 15 minutes before
    and 15 minutes after), the shield vetoes new entries to prevent extreme slippage.
    """

    def __init__(self, pre_embargo_minutes: int = 15, post_embargo_minutes: int = 15):
        self.pre_embargo_minutes = pre_embargo_minutes
        self.post_embargo_minutes = post_embargo_minutes
        self._manual_events: List[Dict[str, Any]] = []

    def register_event(self, name: str, event_time: datetime, impact: str = "HIGH"):
        """Registers a custom scheduled event."""
        if event_time.tzinfo is None:
            event_time = event_time.replace(tzinfo=timezone.utc)
        self._manual_events.append({
            "name": name,
            "time": event_time,
            "impact": impact.upper()
        })
        self._manual_events.sort(key=lambda x: x["time"])

    def generate_algorithmic_events(self, base_dt: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """
        Synthesizes standard known high-impact institutional release schedules
        for the current month (NFP first Friday, CPI mid-month, FOMC cycles).
        """
        now = base_dt or datetime.now(timezone.utc)
        if now.tzinfo is None:
            now = now.replace(tzinfo=timezone.utc)

        events: List[Dict[str, Any]] = []

        # 1. Non-Farm Payrolls (First Friday of current and next month @ 12:30 UTC)
        for month_offset in [0, 1]:
            year = now.year + (now.month + month_offset - 1) // 12
            month = (now.month + month_offset - 1) % 12 + 1
            # Find first Friday
            for day in range(1, 8):
                d = datetime(year, month, day, 12, 30, tzinfo=timezone.utc)
                if d.weekday() == 4:  # Friday
                    events.append({
                        "name": f"US Non-Farm Payrolls & Unemployment ({month}/{year})",
                        "time": d,
                        "impact": "HIGH"
                    })
                    break

        # 2. US CPI Release (Around 12th-14th of month @ 12:30 UTC)
        for month_offset in [0, 1]:
            year = now.year + (now.month + month_offset - 1) // 12
            month = (now.month + month_offset - 1) % 12 + 1
            cpi_date = datetime(year, month, 12, 12, 30, tzinfo=timezone.utc)
            if cpi_date.weekday() >= 5:  # Weekend shift to Monday
                cpi_date += timedelta(days=(7 - cpi_date.weekday()))
            events.append({
                "name": f"US Consumer Price Index (CPI) Inflation ({month}/{year})",
                "time": cpi_date,
                "impact": "HIGH"
            })

        # Add manual registered events
        events.extend(self._manual_events)
        events.sort(key=lambda x: x["time"])
        return events

    def get_next_event(self, current_dt: Optional[datetime] = None) -> Optional[Dict[str, Any]]:
        """Finds the next upcoming high-impact event."""
        now = current_dt or datetime.now(timezone.utc)
        if now.tzinfo is None:
            now = now.replace(tzinfo=timezone.utc)

        events = self.generate_algorithmic_events(now)
        for ev in events:
            diff_seconds = (ev["time"] - now).total_seconds()
            if diff_seconds > -(self.post_embargo_minutes * 60):
                ev_copy = dict(ev)
                ev_copy["minutes_remaining"] = round(diff_seconds / 60.0, 1)
                return ev_copy
        return None

    def is_embargo_active(
        self,
        current_dt: Optional[datetime] = None
    ) -> Tuple[bool, str]:
        """
        Determines if a high-impact news embargo is currently active.
        Returns: (is_active, reason_message)
        """
        now = current_dt or datetime.now(timezone.utc)
        if now.tzinfo is None:
            now = now.replace(tzinfo=timezone.utc)

        events = self.generate_algorithmic_events(now)
        for ev in events:
            ev_time = ev["time"]
            delta = (now - ev_time).total_seconds() / 60.0

            # Delta is negative if event is in future: -15 <= delta <= 0 means within 15 min before
            # Delta is positive if event just passed: 0 <= delta <= 15 means within 15 min after
            if -self.pre_embargo_minutes <= delta <= self.post_embargo_minutes:
                if delta < 0:
                    mins = abs(int(delta))
                    msg = f"NEWS EMBARGO: {ev['name']} releases in {mins}m. VETO ENTRIES."
                else:
                    mins = int(delta)
                    msg = f"NEWS VOLATILITY COOL-DOWN: {ev['name']} released {mins}m ago. VETO ENTRIES."
                logger.warning(f"[CALENDAR-SHIELD] {msg}")
                return True, msg

        return False, "CLEAR: No immediate high-impact news embargo active."
