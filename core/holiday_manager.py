"""
Rollover Spread Spike & Bank Holiday Blackout Manager.
Protects the bot against:
1. Daily Rollover spread explosion between 21:50 and 22:20 GMT.
2. US & Global Bank Holidays with illiquid markets and high gap risks.
3. Abnormal live spread spikes exceeding institutional limits ($0.40).
"""

import logging
from typing import Tuple, Optional
from datetime import datetime, date, timezone
from config.settings import HolidaySettings

logger = logging.getLogger("HolidayManager")


class HolidayManager:
    def __init__(self, settings: Optional[HolidaySettings] = None):
        self.settings = settings or HolidaySettings()

    def is_rollover_window(self, now_utc: datetime) -> Tuple[bool, str]:
        """
        Checks if current time is inside the daily NY Close / Broker Rollover spread widening window
        (21:50 - 22:20 GMT). Spreads on Gold routinely spike to $2 - $5 during this period.
        """
        t_str = now_utc.strftime("%H:%M")
        start = self.settings.ROLLOVER_START_GMT
        end = self.settings.ROLLOVER_END_GMT

        # Support windows that stay within the same day or span midnight
        if start <= end:
            in_window = start <= t_str <= end
        else:
            in_window = start <= t_str or t_str <= end

        if in_window:
            msg = f"[ROLLOVER_BLACKOUT] Time {t_str} GMT is within daily rollover window ({start}-{end} GMT). Spreads widened."
            return True, msg

        return False, "Outside rollover window."

    def is_bank_holiday(self, now_utc: datetime) -> Tuple[bool, str]:
        """
        Checks if current date is a major US/UK market holiday.
        """
        d = now_utc.date()
        year = d.year
        month = d.month
        day = d.day
        weekday = d.weekday()  # 0=Monday, 6=Sunday

        # Fixed holidays
        if month == 1 and day == 1:
            return True, "New Year's Day (Global Market Closed)"
        if month == 6 and day == 19:
            return True, "Juneteenth National Independence Day (US Market Closed)"
        if month == 7 and day == 4:
            return True, "US Independence Day (US Market Closed)"
        if month == 12 and day == 25:
            return True, "Christmas Day (Global Market Closed)"

        # Floating US holidays
        # MLK Day: 3rd Monday of January
        if month == 1 and weekday == 0 and 15 <= day <= 21:
            return True, "Martin Luther King Jr. Day (US Market Early Close)"

        # Presidents' Day: 3rd Monday of February
        if month == 2 and weekday == 0 and 15 <= day <= 21:
            return True, "Presidents' Day (US Market Closed)"

        # Memorial Day: Last Monday of May
        if month == 5 and weekday == 0 and day >= 25:
            return True, "Memorial Day (US Market Closed)"

        # Labor Day: 1st Monday of September
        if month == 9 and weekday == 0 and day <= 7:
            return True, "Labor Day (US Market Closed)"

        # Thanksgiving: 4th Thursday of November
        if month == 11 and weekday == 3 and 22 <= day <= 28:
            return True, "Thanksgiving Day (US Market Closed)"

        # Black Friday: Day after Thanksgiving (Early Close at 13:00 EST)
        if month == 11 and weekday == 4 and 23 <= day <= 29:
            return True, "Black Friday (US Market Early Liquidity Drain)"

        # Good Friday approximation (variable spring Friday)
        # 2026 Good Friday is April 3, 2026
        if year == 2026 and month == 4 and day == 3:
            return True, "Good Friday (Global Precious Metals Market Closed)"

        return False, "Normal trading day."

    def verify_spread(self, current_spread: float) -> Tuple[bool, str]:
        """
        Rejects signal if live spread exceeds maximum allowable threshold ($0.40).
        """
        if current_spread > self.settings.MAX_ALLOWED_SPREAD_USD:
            msg = f"[SPREAD_GATE] Live spread ${current_spread:.2f} exceeds cap of ${self.settings.MAX_ALLOWED_SPREAD_USD:.2f}."
            return False, msg

        return True, "Spread normal."

    def can_trade_now(self, now_utc: datetime, current_spread: float) -> Tuple[bool, str]:
        """Master validation for market liquidity and schedule safety."""
        # 1. Bank Holiday check
        is_holiday, holiday_msg = self.is_bank_holiday(now_utc)
        if is_holiday:
            return False, f"Holiday Blackout: {holiday_msg}"

        # 2. Rollover window check
        in_rollover, rollover_msg = self.is_rollover_window(now_utc)
        if in_rollover:
            return False, rollover_msg

        # 3. Spread check
        spread_ok, spread_msg = self.verify_spread(current_spread)
        if not spread_ok:
            return False, spread_msg

        return True, "Market conditions liquid and approved for trading."
