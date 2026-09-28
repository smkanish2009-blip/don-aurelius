"""
Configuration settings for XAUUSD AI Trading Bot.
Encapsulates all parameters specified in the strategy specification:
'Session-Range Breakout & Liquidity-Sweep Strategy (Gold SRB)'
"""

from dataclasses import dataclass, field
from typing import Tuple


@dataclass(frozen=True)
class SessionSettings:
    # Asian range measurement window (GMT)
    ASIAN_START_GMT: str = "00:00"
    ASIAN_END_GMT: str = "07:00"  # 07:00 cleanly separates pre-London manipulation

    # Entry windows (GMT)
    SETUP_B_START_GMT: str = "07:45"
    SETUP_B_END_GMT: str = "10:30"

    SETUP_A_WINDOW_1_START: str = "08:00"
    SETUP_A_WINDOW_1_END: str = "11:30"
    SETUP_A_WINDOW_2_START: str = "13:00"
    SETUP_A_WINDOW_2_END: str = "16:30"

    # Hard cutoffs
    NO_NEW_TRADES_GMT: str = "17:00"
    FLATTEN_ALL_GMT: str = "20:00"  # Avoid 21:00-23:00 rollover spread spike
    FRIDAY_CUTOFF_GMT: str = "14:00"  # Avoid weekend gap risk


@dataclass(frozen=True)
class StrategyParameters:
    # Range validity
    RANGE_USES_WICKS: bool = True
    MIN_RANGE_X_ATR: float = 0.8  # Min Asian range height relative to H1 ATR(14)
    MAX_RANGE_X_ATR: float = 3.0  # Max Asian range height relative to H1 ATR(14)

    # Trend & Direction Filter (H1)
    TREND_EMA_PERIOD: int = 200
    EMA_SLOPE_BARS: int = 5
    ADX_PERIOD: int = 14
    ADX_MIN: float = 20.0  # Minimum ADX to confirm trend strength

    # Setup A: Breakout
    A_BREAKOUT_BUFFER_X_ATR: float = 0.10  # Must close beyond edge + buffer * M15 ATR
    A_CONFIRM_CANDLES: int = 1  # Number of closed M15 candles outside
    A_MAX_EXTENSION_X_ATR: float = 0.60  # Do not chase if close > edge + max_ext * M15 ATR
    A_MIN_BODY_RATIO: float = 0.50  # Candle body >= 50% of range
    A_TOP_CLOSE_PERCENTILE: float = 0.30  # Close in top 30% for buy, bottom 30% for sell
    A_SL_MULT_ATR: float = 1.50  # Initial SL = entry - 1.5 * H1 ATR(14)
    A_TP_RR: float = 2.00  # Reward-to-risk ratio

    # Setup B: Sweep and Reclaim
    B_SWEEP_MIN_X_ATR: float = 0.10  # Normalized sweep min (0.1x H1 ATR)
    B_SWEEP_MAX_X_ATR: float = 0.40  # Normalized sweep max (0.4x H1 ATR)
    B_REJECTION_BODY_MIN: float = 0.50  # Reclaim candle body >= 50% of its range
    B_SL_BUFFER_X_ATR: float = 0.15  # SL = Sweep wick + 0.15 * H1 ATR
    B_TP_MIDPOINT_RATIO: float = 0.50  # Target 1 = 50% range midpoint

    # Exits and Active Management
    BREAKEVEN_TRIGGER_R: float = 1.00  # Move SL to entry + spread + $0.10 at +1R
    BREAKEVEN_BUFFER_USD: float = 0.10  # Buffer above entry for BE
    PARTIAL_CLOSE_TRIGGER_R: float = 1.50  # Bank half at +1.5R
    PARTIAL_CLOSE_RATIO: float = 0.50  # 50% position partial close
    TRAIL_TRIGGER_R: float = 1.50  # Start trailing after +1.5R
    TRAIL_ATR_MULT: float = 2.00  # Chandelier trail: highest close - 2.0 * M15 ATR
    TIME_STOP_BARS_M15: int = 24  # 6 hours (24 x 15m) without reaching +0.5R -> close


@dataclass(frozen=True)
class RiskParameters:
    RISK_PER_TRADE_PERCENT: float = 0.50  # 0.5% default, live start 0.25%
    MAX_TRADES_PER_DAY: int = 2
    DAILY_LOSS_LIMIT_PERCENT: float = 2.00  # Hard stop for the day
    MAX_DRAWDOWN_KILL_PERCENT: float = 8.00  # Global kill switch from peak equity
    CONSECUTIVE_LOSS_HALVE_COUNT: int = 3  # Halve risk after 3 consecutive losses
    MAX_SPREAD_USD: float = 0.40  # Max spread allowed to enter trade
    MAX_SLIPPAGE_POINTS: int = 30  # Max slippage tolerance
    DAILY_RANGE_USED_MAX_PERCENT: float = 50.0  # Skip if today's high-low > 50% of D1 ATR


@dataclass(frozen=True)
class NewsFilterSettings:
    NEWS_BLACKOUT_MINUTES_BEFORE: int = 30
    NEWS_BLACKOUT_MINUTES_AFTER: int = 30
    HIGH_IMPACT_CURRENCIES: Tuple[str, ...] = ("USD",)
    CRITICAL_KEYWORDS: Tuple[str, ...] = (
        "Non-Farm", "CPI", "FOMC", "Fed Chair", "Interest Rate", "PCE", "GDP"
    )
    CALENDAR_FEED_URL: str = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"
    CACHE_EXPIRY_HOURS: int = 1


@dataclass(frozen=True)
class AISettings:
    ENABLED: bool = True
    META_MODEL_MIN_PROBABILITY: float = 0.58  # Filter trade if P(win) < 58%
    HIGH_CONFIDENCE_THRESHOLD: float = 0.68  # Scale up position if P(win) >= 68%
    HIGH_CONFIDENCE_RISK_SCALE: float = 1.30  # 1.3x risk sizing for high confidence
    GEMINI_SENTIMENT_ENABLED: bool = True
    GEMINI_MODEL: str = "gemini-2.5-flash"


@dataclass(frozen=True)
class BillingSettings:
    PERFORMANCE_FEE_PERCENT: float = 20.0
    GAS_WALLET_WARNING_USD: float = 20.0
    GAS_WALLET_INITIAL_DEMO_USD: float = 100.0
    BILLING_CURRENCY: str = "USDT"


@dataclass(frozen=True)
class PropFirmSettings:
    PROP_FIRM_MODE: bool = True  # Enforces FTMO/FundedNext compliance
    MIN_TRADE_DURATION_SEC: int = 120  # 120s anti-scalping rule
    MAX_SINGLE_ORDER_LOTS: float = 5.00  # Hard cap per single order
    CONSISTENCY_MAX_DAILY_PROFIT_PCT: float = 45.0  # 45% consistency rule
    ALLOW_HEDGING: bool = False  # Strictly forbid opposite direction positions


@dataclass(frozen=True)
class MacroTrendSettings:
    ENABLED: bool = True
    H4_EMA_FAST: int = 50
    H4_EMA_SLOW: int = 200
    D1_EMA_TREND: int = 200
    COUNTER_TREND_SWEEP_MIN_WICK_PCT: float = 0.60  # Require 60% wick for counter-trend sweep


@dataclass(frozen=True)
class HolidaySettings:
    ROLLOVER_START_GMT: str = "21:50"
    ROLLOVER_END_GMT: str = "22:20"
    MAX_ALLOWED_SPREAD_USD: float = 0.40  # Max spread before blocking order


@dataclass(frozen=True)
class BotConfig:
    SYMBOL: str = "XAUUSD"
    MAGIC_NUMBER: int = 260925  # Unique identifier for this bot's orders
    STEALTH_MODE: bool = True  # Avoid EA fingerprinting by brokers/prop-firms
    ORDER_COMMENT: str = ""  # Clean/discreet order comment (blank = no EA watermark)
    POLL_INTERVAL_ACTIVE_SEC: float = 0.5  # Check frequency during active windows
    POLL_INTERVAL_IDLE_SEC: float = 5.0  # Check frequency during idle/measuring
    DATA_DIR: str = "data"
    LOGS_DIR: str = "logs"

    sessions: SessionSettings = field(default_factory=SessionSettings)
    strategy: StrategyParameters = field(default_factory=StrategyParameters)
    risk: RiskParameters = field(default_factory=RiskParameters)
    news: NewsFilterSettings = field(default_factory=NewsFilterSettings)
    ai: AISettings = field(default_factory=AISettings)
    billing: BillingSettings = field(default_factory=BillingSettings)
    prop_firm: PropFirmSettings = field(default_factory=PropFirmSettings)
    macro_trend: MacroTrendSettings = field(default_factory=MacroTrendSettings)
    holiday: HolidaySettings = field(default_factory=HolidaySettings)



