"""
MetaTrader 5 Client Wrapper.
Handles terminal lifecycle, account authentication, dynamic symbol discovery,
tick math, margin estimation, and fill-mode negotiation.
"""

import time
import logging
from typing import Optional, Tuple, Dict, Any
import pandas as pd
from datetime import datetime, timezone
import MetaTrader5 as mt5


logger = logging.getLogger("MT5Client")


class MT5Client:
    def __init__(self, symbol: str = "XAUUSD", magic_number: int = 260925):
        self.preferred_symbol = symbol
        self.symbol = symbol
        self.magic_number = magic_number
        self.is_connected = False
        self.symbol_info = None
        self.tick_size = 0.01
        self.tick_value = 1.00
        self.point = 0.01
        self.lot_min = 0.01
        self.lot_max = 100.0
        self.lot_step = 0.01
        self.filling_mode = mt5.ORDER_FILLING_IOC

    def connect(self, login: int = 0, password: str = "", server: str = "", path: str = "") -> bool:
        """Initializes connection to MT5 terminal and logs in if credentials provided."""
        init_kwargs = {}
        if path:
            init_kwargs["path"] = path

        init_success = False
        for attempt in range(3):
            if mt5.initialize(**init_kwargs):
                init_success = True
                break
            time.sleep(1.5)

        if not init_success:
            logger.error(f"MT5 initialization failed: {mt5.last_error()}")
            return False


        if login and password and server:
            authorized = mt5.login(login=login, password=password, server=server)
            if not authorized:
                logger.error(f"Failed to log into MT5 account #{login}: {mt5.last_error()}")
                return False
            logger.info(f"Successfully logged into MT5 account #{login} on {server}")
        else:
            logger.info("Connected to currently active MT5 terminal profile.")

        self.is_connected = True
        self._resolve_symbol()
        return True

    def _resolve_symbol(self) -> None:
        """Finds the actual symbol name supported by the broker (e.g., XAUUSD, GOLD, XAUUSD.m)."""
        candidates = [self.preferred_symbol, "GOLD", "XAUUSD.m", "XAUUSD_raw", "XAUUSD+", "XAUUSDpro"]
        for s in candidates:
            info = mt5.symbol_info(s)
            if info is not None:
                self.symbol = s
                self.symbol_info = info
                if not info.visible:
                    mt5.symbol_select(s, True)
                self.tick_size = info.trade_tick_size or 0.01
                self.tick_value = info.trade_tick_value or 1.00
                self.point = info.point or 0.01
                self.lot_min = info.volume_min or 0.01
                self.lot_max = info.volume_max or 100.0
                self.lot_step = info.volume_step or 0.01
                self._resolve_filling_mode(info)
                logger.info(f"Resolved Symbol: {self.symbol} | TickSize: {self.tick_size} | "
                            f"TickVal: {self.tick_value} | LotStep: {self.lot_step} | "
                            f"FillMode: {self.filling_mode}")
                return

        logger.warning(f"Could not automatically resolve symbol '{self.preferred_symbol}'. Defaulting to original.")

    def _resolve_filling_mode(self, info) -> None:
        """Resolves broker-supported order filling mode."""
        fill_flags = info.filling_mode
        if fill_flags & mt5.ORDER_FILLING_IOC:
            self.filling_mode = mt5.ORDER_FILLING_IOC
        elif fill_flags & mt5.ORDER_FILLING_FOK:
            self.filling_mode = mt5.ORDER_FILLING_FOK
        else:
            self.filling_mode = mt5.ORDER_FILLING_RETURN

    def get_current_tick(self) -> Optional[Any]:
        """Fetches the latest live tick for the active symbol."""
        return mt5.symbol_info_tick(self.symbol)

    def get_rates(self, timeframe, n_bars: int = 300) -> Optional[pd.DataFrame]:
        """Fetches historical OHLCV data as a pandas DataFrame."""
        rates = mt5.copy_rates_from_pos(self.symbol, timeframe, 0, n_bars)
        if rates is None or len(rates) == 0:
            return None
        df = pd.DataFrame(rates)
        df["time"] = pd.to_datetime(df["time"], unit="s", utc=True)
        return df

    def get_account_equity(self) -> float:
        account_info = mt5.account_info()
        return account_info.equity if account_info else 0.0

    def get_account_id(self) -> int:
        info = mt5.account_info()
        return int(info.login) if info else 0

    def get_open_positions(self) -> list:
        """Returns open positions filtered by magic number."""
        positions = mt5.positions_get(symbol=self.symbol)
        if positions is None:
            return []
        return [p for p in positions if p.magic == self.magic_number]

    def shutdown(self) -> None:
        mt5.shutdown()
        self.is_connected = False
        logger.info("MT5 connection closed.")
