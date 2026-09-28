"""
Economic Calendar Manager.
Downloads, caches, and parses high-impact economic news releases directly from the
Forex Factory weekly JSON feed. Enforces strict news blackout windows around USD releases.
"""

import os
import json
import logging
import requests
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional
from config.settings import NewsFilterSettings

logger = logging.getLogger("CalendarManager")


class CalendarManager:
    def __init__(self, settings: NewsFilterSettings, cache_file: str = "data/ff_calendar.json"):
        self.settings = settings
        self.cache_file = cache_file
        self.events: List[Dict] = []
        self.last_fetch: Optional[datetime] = None
        os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
        self.load_calendar()

    def load_calendar(self) -> None:
        """Loads events from local cache if recent, else updates from network."""
        if os.path.exists(self.cache_file):
            mtime = datetime.fromtimestamp(os.path.getmtime(self.cache_file), tz=timezone.utc)
            if datetime.now(timezone.utc) - mtime < timedelta(hours=self.settings.CACHE_EXPIRY_HOURS):
                try:
                    with open(self.cache_file, "r", encoding="utf-8") as f:
                        self.events = json.load(f)
                    self.last_fetch = mtime
                    logger.info(f"Loaded {len(self.events)} events from local calendar cache.")
                    return
                except Exception as e:
                    logger.warning(f"Failed to read calendar cache: {e}. Fetching fresh feed.")

        self.fetch_fresh_calendar()

    def fetch_fresh_calendar(self) -> bool:
        """Fetches the weekly JSON feed from Forex Factory with rate-limit respect."""
        try:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            resp = requests.get(self.settings.CALENDAR_FEED_URL, headers=headers, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                with open(self.cache_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
                self.events = data
                self.last_fetch = datetime.now(timezone.utc)
                logger.info(f"Successfully fetched and cached {len(self.events)} calendar events.")
                return True
            else:
                logger.error(f"Calendar fetch failed with status {resp.status_code}")
                return False
        except Exception as e:
            logger.error(f"Error connecting to economic calendar feed: {e}")
            # Fail-safe: if cache exists, use stale cache
            if os.path.exists(self.cache_file):
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    self.events = json.load(f)
            return False

    def is_news_blackout(self, current_gmt: datetime) -> Tuple[bool, Optional[str]]:
        """
        Checks if current_gmt falls within +/- 30 minutes of a high-impact USD event.
        Returns: (is_blackout: bool, event_title: Optional[str])
        """
        if not self.events:
            return False, None

        if current_gmt.tzinfo is None:
            current_gmt = current_gmt.replace(tzinfo=timezone.utc)

        before_delta = timedelta(minutes=self.settings.NEWS_BLACKOUT_MINUTES_BEFORE)
        after_delta = timedelta(minutes=self.settings.NEWS_BLACKOUT_MINUTES_AFTER)

        for event in self.events:
            # Check impact and currency
            impact = event.get("impact", "")
            currency = event.get("country", "")
            if impact != "High" or currency not in self.settings.HIGH_IMPACT_CURRENCIES:
                continue

            event_date_str = event.get("date", "")  # ISO 8601 format e.g. "2026-09-25T13:30:00-04:00"
            if not event_date_str:
                continue

            try:
                event_dt = datetime.fromisoformat(event_date_str)
                event_gmt = event_dt.astimezone(timezone.utc)

                if (event_gmt - before_delta) <= current_gmt <= (event_gmt + after_delta):
                    title = event.get("title", "High-Impact USD Event")
                    return True, f"{currency} {title} at {event_gmt.strftime('%H:%M GMT')}"
            except Exception as e:
                continue

        return False, None
