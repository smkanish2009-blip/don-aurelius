"""
High-Precision Time & Session Management Engine.
Handles UTC/GMT normalization, broker server time offsets, astronomical Daylight Savings Time (DST)
switches across US and European calendars, and exact session window state tracking.
"""

from datetime import datetime, time, timezone, timedelta
from typing import Tuple
from config.settings import SessionSettings


class TimeEngine:
    def __init__(self, sessions: SessionSettings, broker_gmt_offset_hours: int = 2):
        self.sessions = sessions
        self.base_offset = timedelta(hours=broker_gmt_offset_hours)

    @staticmethod
    def is_dst_us(dt: datetime) -> bool:
        """
        Calculates US Daylight Savings Time:
        Starts on 2nd Sunday in March, ends on 1st Sunday in November.
        """
        year = dt.year
        # 2nd Sunday in March
        march_first = datetime(year, 3, 1, tzinfo=timezone.utc)
        first_sun_march = 1 + (6 - march_first.weekday()) % 7
        dst_start = datetime(year, 3, first_sun_march + 7, 2, tzinfo=timezone.utc)

        # 1st Sunday in November
        nov_first = datetime(year, 11, 1, tzinfo=timezone.utc)
        first_sun_nov = 1 + (6 - nov_first.weekday()) % 7
        dst_end = datetime(year, 11, first_sun_nov, 2, tzinfo=timezone.utc)

        return dst_start <= dt < dst_end

    @staticmethod
    def is_dst_eu(dt: datetime) -> bool:
        """
        Calculates European Daylight Savings Time:
        Starts on last Sunday in March, ends on last Sunday in October.
        """
        year = dt.year
        # Last Sunday in March
        march_31 = datetime(year, 3, 31, tzinfo=timezone.utc)
        last_sun_march = 31 - (march_31.weekday() + 1) % 7
        dst_start = datetime(year, 3, last_sun_march, 1, tzinfo=timezone.utc)

        # Last Sunday in October
        oct_31 = datetime(year, 10, 31, tzinfo=timezone.utc)
        last_sun_oct = 31 - (oct_31.weekday() + 1) % 7
        dst_end = datetime(year, 10, last_sun_oct, 1, tzinfo=timezone.utc)

        return dst_start <= dt < dst_end

    def server_to_gmt(self, server_dt: datetime) -> datetime:
        """Converts broker server datetime to GMT (UTC)."""
        if server_dt.tzinfo is None:
            # Assume naive datetime is in server time
            pass
        # Dynamic DST adjustment: typical broker server runs on EET (UTC+2 in winter, UTC+3 in summer)
        is_dst = self.is_dst_us(server_dt.replace(tzinfo=timezone.utc))
        offset = timedelta(hours=3 if is_dst else 2)
        return server_dt - offset

    def gmt_to_server(self, gmt_dt: datetime) -> datetime:
        """Converts GMT (UTC) datetime to broker server time."""
        is_dst = self.is_dst_us(gmt_dt if gmt_dt.tzinfo else gmt_dt.replace(tzinfo=timezone.utc))
        offset = timedelta(hours=3 if is_dst else 2)
        return gmt_dt + offset

    @staticmethod
    def parse_time_str(time_str: str) -> time:
        parts = time_str.split(":")
        return time(int(parts[0]), int(parts[1]))

    def is_in_asian_window(self, gmt_dt: datetime) -> bool:
        t = gmt_dt.time()
        start = self.parse_time_str(self.sessions.ASIAN_START_GMT)
        end = self.parse_time_str(self.sessions.ASIAN_END_GMT)
        return start <= t < end

    def is_in_setup_b_window(self, gmt_dt: datetime) -> bool:
        t = gmt_dt.time()
        start = self.parse_time_str(self.sessions.SETUP_B_START_GMT)
        end = self.parse_time_str(self.sessions.SETUP_B_END_GMT)
        return start <= t <= end

    def is_in_setup_a_window(self, gmt_dt: datetime) -> bool:
        t = gmt_dt.time()
        w1_start = self.parse_time_str(self.sessions.SETUP_A_WINDOW_1_START)
        w1_end = self.parse_time_str(self.sessions.SETUP_A_WINDOW_1_END)
        w2_start = self.parse_time_str(self.sessions.SETUP_A_WINDOW_2_START)
        w2_end = self.parse_time_str(self.sessions.SETUP_A_WINDOW_2_END)
        return (w1_start <= t <= w1_end) or (w2_start <= t <= w2_end)

    def is_past_new_trades_cutoff(self, gmt_dt: datetime) -> bool:
        t = gmt_dt.time()
        cutoff = self.parse_time_str(self.sessions.NO_NEW_TRADES_GMT)
        return t >= cutoff

    def is_past_session_flatten(self, gmt_dt: datetime) -> bool:
        t = gmt_dt.time()
        flatten = self.parse_time_str(self.sessions.FLATTEN_ALL_GMT)
        return t >= flatten

    def is_friday_cutoff(self, gmt_dt: datetime) -> bool:
        # Friday is weekday 4
        if gmt_dt.weekday() == 4:
            cutoff = self.parse_time_str(self.sessions.FRIDAY_CUTOFF_GMT)
            return gmt_dt.time() >= cutoff
        return False

    def is_friday_weekend_gap_flatten(self, gmt_dt: datetime) -> bool:
        """
        The Friday Close / Weekend Gap Policy:
        Forcefully closes all intraday XAUUSD positions every Friday at 21:00 UTC
        to prevent massive weekend gap exposure.
        """
        if gmt_dt.weekday() == 4:
            return gmt_dt.time() >= time(21, 0)
        return False

    def is_holiday(self, gmt_dt: datetime) -> bool:
        # Major thin liquidity gold holidays specified in PDF
        month, day = gmt_dt.month, gmt_dt.day
        if (month == 12 and day in (24, 25, 31)) or (month == 1 and day == 1):
            return True
        return False
