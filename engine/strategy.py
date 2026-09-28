"""
JARVIS Intermarket Strategy Engine.
Evaluates algorithmic entry matrices for XAUUSD by filtering setups
against co-integrated macro metrics (DXY and 10-Year Treasury Yields US10Y).
"""

import logging
import time
import numpy as np
import pandas as pd
from typing import Tuple, Dict, Any, Optional

try:
    import MetaTrader5 as mt5
except ImportError:
    mt5 = None

logger = logging.getLogger("JarvisStrategy")


class JarvisStrategyEngine:
    """
    Evaluates algorithmic entry matrices for XAUUSD by filtering setups
    against co-integrated macro metrics (DXY and 10-Year Treasury Yields).
    """

    def __init__(self, ema_fast: int = 12, ema_slow: int = 26, atr_period: int = 14):
        self.ema_fast = ema_fast
        self.ema_slow = ema_slow
        self.atr_period = atr_period

        # Real-world common broker variations for tracking assets
        self.dxy_tickers = ["USDX", "DXY", "USDOLLAR", "DXY.pro", "DX", "USDIndex"]
        self.us10y_tickers = ["US10Y", "US10YT", "UST10Y", "US10YEAR", "TNX", "US10Y_"]

        self.resolved_dxy: Optional[str] = None
        self.resolved_us10y: Optional[str] = None
        self.using_proxy: bool = False

        self._last_logged_radar: Optional[str] = None
        self._last_radar_log_time: float = 0.0

    def _log_radar(self, message: str):
        """Throttles repeated radar messages to once per 60s when market states hold."""
        now = time.time()
        if message != self._last_logged_radar or (now - self._last_radar_log_time) >= 60.0:
            logger.info(message)
            self._last_logged_radar = message
            self._last_radar_log_time = now

    def resolve_broker_tickers(self) -> bool:
        """
        Discovers valid index naming conventions supported by the host broker.
        If host broker does not provide index CFDs, gracefully falls back to
        inverted EURUSD as a proxy for DXY.
        """
        if self.resolved_dxy and self.resolved_us10y:
            return True

        if mt5 is None:
            logger.warning("[JARVIS-STRATEGY] MetaTrader5 library unavailable in environment.")
            return False

        # 1. Search for DXY (rejecting equity ETFs or stocks)
        for ticker in self.dxy_tickers:
            try:
                s_info = mt5.symbol_info(ticker)
                if s_info and mt5.symbol_select(ticker, True):
                    path = (getattr(s_info, 'path', '') or '').lower()
                    desc = (getattr(s_info, 'description', '') or '').lower()
                    if any(bad in path or bad in desc for bad in ['etf', 'stock', 'equity', 'shares', 'nasdaq', 'nyse']):
                        continue
                    self.resolved_dxy = ticker
                    logger.info(f"[JARVIS-MACRO] Resolved DXY Symbol: {ticker}")
                    break
            except Exception:
                pass

        # 2. Search for US10Y (rejecting equity ETFs or stocks)
        for ticker in self.us10y_tickers:
            try:
                s_info = mt5.symbol_info(ticker)
                if s_info and mt5.symbol_select(ticker, True):
                    path = (getattr(s_info, 'path', '') or '').lower()
                    desc = (getattr(s_info, 'description', '') or '').lower()
                    if any(bad in path or bad in desc for bad in ['etf', 'stock', 'equity', 'shares', 'nasdaq', 'nyse']):
                        continue
                    self.resolved_us10y = ticker
                    logger.info(f"[JARVIS-MACRO] Resolved US10Y Symbol: {ticker}")
                    break
            except Exception:
                pass

        # 3. Fallback: If DXY not directly available on retail broker, look for EURUSD proxy
        if not self.resolved_dxy:
            try:
                if mt5.symbol_select("EURUSD", True):
                    self.resolved_dxy = "EURUSD"
                    self.using_proxy = True
                    logger.info("[JARVIS-MACRO] Using inverted EURUSD as real-time DXY proxy (57.6% weight).")
            except Exception:
                pass

        return self.resolved_dxy is not None or self.resolved_us10y is not None

    def calculate_ema(self, prices: np.ndarray, period: int) -> float:
        """Calculates Exponential Moving Average using vectorization."""
        if len(prices) < period:
            return float(np.nan)
        return float(pd.Series(prices).ewm(span=period, adjust=False).mean().iloc[-1])

    def calculate_atr(self, high: np.ndarray, low: np.ndarray, close: np.ndarray) -> float:
        """Calculates True Range and Average True Range metrics for volatility sizing."""
        if len(close) < self.atr_period + 1:
            return 1.50  # Safe gold default ATR

        df = pd.DataFrame({'high': high, 'low': low, 'close': close})
        df['prev_close'] = df['close'].shift(1)

        df['tr1'] = df['high'] - df['low']
        df['tr2'] = (df['high'] - df['prev_close']).abs()
        df['tr3'] = (df['low'] - df['prev_close']).abs()

        df['tr'] = df[['tr1', 'tr2', 'tr3']].max(axis=1)
        val = df['tr'].rolling(window=self.atr_period).mean().iloc[-1]
        return float(val) if not np.isnan(val) else 1.50

    def evaluate_generation_signal(
        self,
        xau_data: pd.DataFrame,
        dxy_data: Optional[pd.DataFrame] = None,
        us10y_data: Optional[pd.DataFrame] = None
    ) -> Tuple[str, float]:
        """
        Processes core indicators to output systemic decisions:
        - "BUY", "SELL", or "HOLD"
        - Traps Shield: Bull Trap rejection when DXY or Yields are rising;
          Bear Trap rejection when DXY and Yields are dumping.
        Handles independent presence of DXY, US10Y, or standalone proxy mode.
        """
        xau_closes = np.array(xau_data['close'].values, dtype=float) if 'close' in xau_data else np.array([], dtype=float)
        xau_fast = self.calculate_ema(xau_closes, self.ema_fast)
        xau_slow = self.calculate_ema(xau_closes, self.ema_slow)

        highs = np.array(xau_data['high'].values, dtype=float) if 'high' in xau_data else xau_closes
        lows = np.array(xau_data['low'].values, dtype=float) if 'low' in xau_data else xau_closes
        atr = self.calculate_atr(highs, lows, xau_closes)

        if np.isnan(xau_fast) or np.isnan(xau_slow):
            return "HOLD", atr

        # Evaluate DXY if available and not a direct copy of XAU
        has_dxy = False
        dxy_fast, dxy_slow = np.nan, np.nan
        dxy_rising, dxy_falling = False, False
        if dxy_data is not None and 'close' in dxy_data and len(dxy_data['close']) >= self.ema_slow:
            dxy_closes = np.array(dxy_data['close'].values, dtype=float)
            if not np.array_equal(dxy_closes, xau_closes):
                if self.using_proxy and len(dxy_closes) > 0:
                    dxy_closes = 1.0 / dxy_closes
                dxy_fast = self.calculate_ema(dxy_closes, self.ema_fast)
                dxy_slow = self.calculate_ema(dxy_closes, self.ema_slow)
                if not np.isnan(dxy_fast) and not np.isnan(dxy_slow):
                    has_dxy = True
                    dxy_rising = dxy_fast > dxy_slow
                    dxy_falling = dxy_fast < dxy_slow

        # Evaluate US10Y if available and not a direct copy of XAU
        has_us10y = False
        us10y_fast, us10y_slow = np.nan, np.nan
        us10y_rising, us10y_falling = False, False
        if us10y_data is not None and 'close' in us10y_data and len(us10y_data['close']) >= self.ema_slow:
            us10y_closes = np.array(us10y_data['close'].values, dtype=float)
            if not np.array_equal(us10y_closes, xau_closes):
                us10y_fast = self.calculate_ema(us10y_closes, self.ema_fast)
                us10y_slow = self.calculate_ema(us10y_closes, self.ema_slow)
                if not np.isnan(us10y_fast) and not np.isnan(us10y_slow):
                    has_us10y = True
                    us10y_rising = us10y_fast > us10y_slow
                    us10y_falling = us10y_fast < us10y_slow

        # Signal Logic
        if xau_fast > xau_slow:
            # Bull Trap Prevention: Gold rising but Dollar or 10-Year yields also rising
            if (has_dxy and dxy_rising) or (has_us10y and us10y_rising):
                dxy_msg = f"DXY Proxy ({dxy_fast:.4f} > {dxy_slow:.4f})" if self.using_proxy else f"DXY ({dxy_fast:.2f} > {dxy_slow:.2f})" if has_dxy and dxy_rising else ""
                us10y_msg = f"US10Y ({us10y_fast:.2f} > {us10y_slow:.2f})" if has_us10y and us10y_rising else ""
                reasons = " or ".join(filter(None, [dxy_msg, us10y_msg]))
                self._log_radar(
                    f"[JARVIS-RADAR] Bull Trap Shield: XAU Bullish ({xau_fast:.2f} > {xau_slow:.2f}), "
                    f"but {reasons} surging. HOLD."
                )
                return "HOLD", atr
            return "BUY", atr

        elif xau_fast < xau_slow:
            # Bear Trap Prevention: Gold dropping but Dollar and 10-Year yields both dropping
            if (has_dxy and has_us10y and dxy_falling and us10y_falling) or \
               (has_dxy and not has_us10y and dxy_falling) or \
               (not has_dxy and has_us10y and us10y_falling):
                self._log_radar(
                    f"[JARVIS-RADAR] Bear Trap Shield: XAU Bearish ({xau_fast:.2f} < {xau_slow:.2f}), "
                    f"but macro indicators weakening. HOLD."
                )
                return "HOLD", atr
            return "SELL", atr

        return "HOLD", atr

    def get_market_diagnostics(
        self,
        xau_data: pd.DataFrame,
        dxy_data: Optional[pd.DataFrame] = None,
        us10y_data: Optional[pd.DataFrame] = None
    ) -> Dict[str, Any]:
        """Provides full telemetry diagnostics for the JARVIS HUD and Voice Briefings."""
        decision, atr = self.evaluate_generation_signal(xau_data, dxy_data, us10y_data)
        xau_closes = np.array(xau_data['close'].values, dtype=float)
        xau_fast = self.calculate_ema(xau_closes, self.ema_fast)
        xau_slow = self.calculate_ema(xau_closes, self.ema_slow)

        has_dxy = False
        dxy_fast, dxy_slow = 0.0, 0.0
        dxy_trend = "N/A"
        if dxy_data is not None and 'close' in dxy_data and len(dxy_data['close']) >= self.ema_slow:
            dxy_closes = np.array(dxy_data['close'].values, dtype=float)
            if not np.array_equal(dxy_closes, xau_closes):
                if self.using_proxy and len(dxy_closes) > 0:
                    dxy_closes = 1.0 / dxy_closes
                fast = self.calculate_ema(dxy_closes, self.ema_fast)
                slow = self.calculate_ema(dxy_closes, self.ema_slow)
                if not np.isnan(fast) and not np.isnan(slow):
                    has_dxy = True
                    dxy_fast = round(fast, 4 if self.using_proxy else 2)
                    dxy_slow = round(slow, 4 if self.using_proxy else 2)
                    dxy_trend = "BULLISH" if fast > slow else "BEARISH"

        dxy_display = f"{self.resolved_dxy} (Proxy)" if self.using_proxy else (self.resolved_dxy or "UNRESOLVED")
        return {
            "decision": decision,
            "atr": round(atr, 2),
            "xau_trend": "BULLISH" if xau_fast > xau_slow else "BEARISH",
            "dxy_trend": dxy_trend,
            "dxy_symbol": dxy_display,
            "us10y_symbol": self.resolved_us10y or "STANDALONE",
            "xau_fast": round(xau_fast, 2),
            "xau_slow": round(xau_slow, 2),
            "dxy_fast": dxy_fast,
            "dxy_slow": dxy_slow,
        }
