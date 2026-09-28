"""
TITAN-X Agent RADAR (OSINT & Sentiment Velocity Interceptor).
Scrapes real-time global news wires, parses geopolitical developments,
and computes institutional Sentiment Velocity (d(Sentiment)/dt) for XAUUSD & DXY.
"""

import time
import urllib.request
import xml.etree.ElementTree as ET
import logging
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Tuple

logger = logging.getLogger("TitanX.Radar")


@dataclass
class SentimentSnapshot:
    timestamp: float
    raw_score: float              # -1.0 (Dollar Bullish / Gold Bearish) to +1.0 (Gold Bullish / Dollar Bearish)
    sentiment_velocity: float     # Rate of sentiment change per minute
    gold_bias: str                # "BULLISH", "BEARISH", or "NEUTRAL"
    shock_event: bool             # True if sudden geopolitical or economic shock detected
    confidence: float             # 0.0 to 1.0 based on headline sample density
    headlines_analyzed: int
    top_shock_headline: Optional[str] = None


class AgentRadar:
    """
    Agent RADAR intercepts real-time alternative data and news feeds to predict
    institutional market direction before technical indicators register the move.
    """

    def __init__(self, cache_ttl_seconds: int = 60):
        self.cache_ttl = cache_ttl_seconds
        self._last_poll_time: float = 0.0
        self._cached_snapshot: Optional[SentimentSnapshot] = None
        self._history: List[Tuple[float, float]] = []  # List of (timestamp, score)

        # High-impact global RSS wire feeds
        self.rss_feeds = [
            "https://news.google.com/rss/search?q=gold+price+or+xauusd+or+dollar+index+or+federal+reserve&hl=en-US&gl=US&ceid=US:en",
            "https://feeds.content.dowjones.io/public/rss/mw_topstories",
            "https://finance.yahoo.com/news/rssindex"
        ]

        # Financial Lexicon Weights (Loughran-McDonald Institutional Quant Adapted)
        # Positive values = BULLISH for Gold / BEARISH for Dollar
        # Negative values = BEARISH for Gold / BULLISH for Dollar
        self.bullish_gold_lexicon = {
            "rate cut": 0.85,
            "rate cuts": 0.85,
            "dovish": 0.75,
            "inflation surge": 0.80,
            "inflation accelerates": 0.80,
            "safe haven": 0.90,
            "safe-haven": 0.90,
            "geopolitical tension": 0.85,
            "escalation": 0.80,
            "conflict": 0.75,
            "war": 0.85,
            "missile strike": 0.95,
            "dollar slides": 0.80,
            "dollar tumbles": 0.85,
            "dollar drops": 0.75,
            "dollar weakens": 0.75,
            "de-dollarization": 0.85,
            "central bank buying": 0.90,
            "gold reserves": 0.70,
            "bank failure": 0.90,
            "banking crisis": 0.95,
            "yields slide": 0.70,
            "yields drop": 0.75,
            "yields tumble": 0.80,
            "debt crisis": 0.85,
            "stimulus": 0.65,
            "gold rallies": 0.80,
            "gold surges": 0.85,
            "gold hits record": 0.90,
        }

        self.bearish_gold_lexicon = {
            "rate hike": -0.85,
            "rate hikes": -0.85,
            "hawkish": -0.75,
            "dollar surges": -0.85,
            "dollar rallies": -0.80,
            "dollar jumps": -0.80,
            "dollar strengthens": -0.75,
            "yields jump": -0.75,
            "yields surge": -0.80,
            "yields spike": -0.85,
            "strong jobs": -0.75,
            "payroll beats": -0.80,
            "hot cpi": -0.75,
            "ceasefire": -0.80,
            "peace talks": -0.75,
            "recession averted": -0.65,
            "soft landing": -0.60,
            "quantitative tightening": -0.75,
            "fed pauses cuts": -0.80,
            "gold drops": -0.75,
            "gold tumbles": -0.80,
            "gold sells off": -0.85,
            "gold slumps": -0.80,
        }

        self.intensifiers = {
            "surging": 1.3,
            "soaring": 1.35,
            "exploding": 1.4,
            "plunging": 1.3,
            "tumbling": 1.3,
            "massive": 1.25,
            "historic": 1.3,
            "unexpected": 1.2,
            "sharply": 1.2,
        }

        self.negations = ["not", "no", "never", "unlikely", "failed to", "denies", "pauses"]

    def score_headline(self, headline: str) -> float:
        """
        Parses a single financial headline and computes directional polarity:
        - Returns positive for Bullish Gold / Bearish Dollar
        - Returns negative for Bearish Gold / Bullish Dollar
        """
        text = headline.lower()
        score = 0.0
        match_count = 0

        # Check Bullish Lexicon
        for phrase, weight in self.bullish_gold_lexicon.items():
            if phrase in text:
                w = weight
                # Check for negation in preceding 20 chars
                idx = text.find(phrase)
                preceding = text[max(0, idx - 25):idx]
                if any(neg in preceding for neg in self.negations):
                    w = -w * 0.75
                score += w
                match_count += 1

        # Check Bearish Lexicon
        for phrase, weight in self.bearish_gold_lexicon.items():
            if phrase in text:
                w = weight
                idx = text.find(phrase)
                preceding = text[max(0, idx - 25):idx]
                if any(neg in preceding for neg in self.negations):
                    w = -w * 0.75
                score += w
                match_count += 1

        if match_count == 0:
            return 0.0

        # Apply intensifiers if present
        multiplier = 1.0
        for word, boost in self.intensifiers.items():
            if word in text:
                multiplier = max(multiplier, boost)

        final_score = (score / match_count) * multiplier
        # Clamp to [-1.0, 1.0]
        return max(-1.0, min(1.0, round(final_score, 4)))

    def fetch_live_headlines(self) -> List[str]:
        """Scrapes headlines across authenticated and public institutional RSS wires."""
        headlines = []
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

        for url in self.rss_feeds:
            try:
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req, timeout=4) as response:
                    data = response.read()
                    root = ET.fromstring(data)
                    for item in root.findall(".//item"):
                        title_node = item.find("title")
                        if title_node is not None and title_node.text:
                            headlines.append(title_node.text.strip())
            except Exception as e:
                logger.debug(f"[RADAR-FEED-SKIP] {url}: {e}")
                continue

        return headlines

    def poll_and_evaluate(self, simulated_headlines: Optional[List[str]] = None) -> SentimentSnapshot:
        """
        Polls current wires, aggregates sentiment, and calculates Sentiment Velocity.
        Returns a rich SentimentSnapshot telemetry packet.
        """
        now = time.time()

        # Honor cache TTL unless simulated headlines provided
        if simulated_headlines is None and self._cached_snapshot and (now - self._last_poll_time) < self.cache_ttl:
            return self._cached_snapshot

        headlines = simulated_headlines if simulated_headlines is not None else self.fetch_live_headlines()

        # If offline or rate limited, gracefully handle with synthetic neutral snapshot
        if not headlines:
            raw_score = 0.0
            velocity = 0.0
            self._cached_snapshot = SentimentSnapshot(
                timestamp=now,
                raw_score=0.0,
                sentiment_velocity=0.0,
                gold_bias="NEUTRAL",
                shock_event=False,
                confidence=0.1,
                headlines_analyzed=0,
                top_shock_headline=None
            )
            self._last_poll_time = now
            return self._cached_snapshot

        scores: List[float] = []
        shock_headline = None
        max_abs_score = 0.0

        for h in headlines:
            s = self.score_headline(h)
            if abs(s) > 0.05:
                scores.append(s)
                if abs(s) > max_abs_score:
                    max_abs_score = abs(s)
                    shock_headline = h

        # Aggregate Raw Score
        if scores:
            raw_score = sum(scores) / len(scores)
            confidence = min(1.0, len(scores) / 10.0)
        else:
            raw_score = 0.0
            confidence = 0.2

        raw_score = round(raw_score, 4)

        # Update History & Compute Velocity over 15-minute window
        self._history.append((now, raw_score))
        # Prune history older than 60 minutes
        cutoff = now - 3600
        self._history = [pt for pt in self._history if pt[0] >= cutoff]

        # Calculate Velocity: (Current - Score 15 mins ago) / minutes
        velocity = 0.0
        target_past_time = now - 900  # 15 minutes ago
        past_points = [pt for pt in self._history if pt[0] <= target_past_time]

        if past_points:
            past_score = past_points[-1][1]
            elapsed_minutes = (now - past_points[-1][0]) / 60.0
            if elapsed_minutes > 0.5:
                velocity = round((raw_score - past_score) / elapsed_minutes, 4)
        elif len(self._history) >= 2:
            # Short-term instant delta if recently booted
            dt_min = (self._history[-1][0] - self._history[0][0]) / 60.0
            if dt_min > 0.2:
                velocity = round((self._history[-1][1] - self._history[0][1]) / dt_min, 4)

        # Shock Detection Thresholds
        shock_event = (abs(velocity) >= 0.08) or (max_abs_score >= 0.85)

        # Determine Bias
        if raw_score >= 0.15 and velocity >= -0.02:
            bias = "BULLISH"
        elif raw_score <= -0.15 and velocity <= 0.02:
            bias = "BEARISH"
        else:
            bias = "NEUTRAL"

        snapshot = SentimentSnapshot(
            timestamp=now,
            raw_score=raw_score,
            sentiment_velocity=velocity,
            gold_bias=bias,
            shock_event=shock_event,
            confidence=confidence,
            headlines_analyzed=len(headlines),
            top_shock_headline=shock_headline if shock_event else None
        )

        self._cached_snapshot = snapshot
        self._last_poll_time = now

        logger.info(
            f"[AGENT-RADAR] Score: {raw_score:+.2f} | Velocity: {velocity:+.4f}/m | "
            f"Bias: {bias} | Shock: {shock_event} | Analyzed: {len(headlines)}"
        )
        return snapshot

    def get_radar_telemetry(self) -> Dict[str, Any]:
        """Provides full telemetry dictionary for HUD, database, and voice."""
        snap = self.poll_and_evaluate()
        return {
            "sentiment_score": snap.raw_score,
            "sentiment_velocity": snap.sentiment_velocity,
            "gold_bias": snap.gold_bias,
            "shock_event": snap.shock_event,
            "confidence_pct": round(snap.confidence * 100, 1),
            "headlines_count": snap.headlines_analyzed,
            "shock_headline": snap.top_shock_headline or "None"
        }
