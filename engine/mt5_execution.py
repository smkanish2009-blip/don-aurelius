"""
JARVIS MetaTrader 5 Dynamic Execution Engine.
Includes Dynamic Auto-Trailing Stops, Dynamic Lot Allocation, and Clean Slate Liquidation.
"""

import logging
from typing import Dict, Any, Optional

try:
    import MetaTrader5 as mt5
except ImportError:
    mt5 = None

logger = logging.getLogger("JarvisExecution")


class MT5ExecutionBridge:
    def __init__(self, symbol: str = "XAUUSD", magic: int = 20260926):
        self.symbol = symbol
        self.magic = magic
        self._connected: bool = False
        self._fill_mode: Optional[int] = None

    def connect(self) -> bool:
        """Connects to active MetaTrader 5 instance and verifies symbol availability."""
        if mt5 is None:
            logger.warning("[JARVIS-EXECUTION] MetaTrader 5 library not available.")
            return False

        if not mt5.initialize():
            # Auto-healing: Reset stale IPC pipes and retry
            try:
                mt5.shutdown()
                import time
                time.sleep(1)
            except Exception:
                pass
            if not mt5.initialize():
                logger.error(f"[JARVIS-EXECUTION] MT5 initialization crash: {mt5.last_error()}")
                return False

        # Attempt to select primary symbol
        if not mt5.symbol_select(self.symbol, True):
            discovered = False
            # 1. Try known common broker suffixes
            for alt in ["GOLD", "XAUUSD.m", "XAUUSDm", "XAUUSD.pro", "XAUUSD_i", "XAUUSDr", "XAUUSD.raw", "XAUUSD_raw", "XAUUSD#"]:
                if mt5.symbol_select(alt, True):
                    self.symbol = alt
                    logger.info(f"[JARVIS-EXECUTION] Discovered alternate gold symbol by suffix: {alt}")
                    discovered = True
                    break

            # 2. Dynamic catalog inspection across all broker instruments
            if not discovered:
                all_symbols = mt5.symbols_get() or []
                for s in all_symbols:
                    s_name = s.name.upper()
                    if ("XAUUSD" in s_name or s_name == "GOLD") and getattr(s, "trade_mode", 4) == 4:
                        if mt5.symbol_select(s.name, True):
                            self.symbol = s.name
                            logger.info(f"[JARVIS-EXECUTION] Auto-detected active broker gold symbol: {s.name}")
                            discovered = True
                            break

            if not discovered:
                logger.warning(f"[JARVIS-EXECUTION] Could not locate an active gold symbol matching {self.symbol} in broker catalog.")

        # Negotiate optimal fill mode
        info = mt5.symbol_info(self.symbol)
        if info:
            modes = getattr(info, "filling_mode", 0)
            if modes & 1:  # FOK
                self._fill_mode = mt5.ORDER_FILLING_FOK
            elif modes & 2:  # IOC
                self._fill_mode = mt5.ORDER_FILLING_IOC
            else:
                self._fill_mode = mt5.ORDER_FILLING_RETURN

        self._connected = True
        return True

    def execute_trailing_stops(self, trail_activation_pips: float = 30.0, trail_step_pips: float = 10.0):
        """
        Scans active order contexts and locks in yields dynamically based on current market peaks.
        $1.00 Gold movement = 10 standard pips ($0.10 per pip).
        """
        if not self._connected:
            self.connect()

        if mt5 is None:
            return

        positions = mt5.positions_get(symbol=self.symbol)
        if not positions:
            return

        for pos in positions:
            # Only trail bot-managed positions or all if magic matches
            if pos.magic != self.magic and self.magic != 0:
                continue

            tick = mt5.symbol_info_tick(self.symbol)
            if not tick:
                continue

            current_price = tick.bid if pos.type == mt5.ORDER_TYPE_BUY else tick.ask
            activation_dist = trail_activation_pips * 0.10
            step_dist = trail_step_pips * 0.10

            if pos.type == mt5.ORDER_TYPE_BUY:
                # Check if price has moved sufficiently into profit zone
                if (current_price - pos.price_open) >= activation_dist:
                    new_sl = round(current_price - step_dist, 2)
                    # Verify if the new Stop Loss is higher than the current one
                    if pos.sl == 0.0 or new_sl > pos.sl:
                        self._modify_position_sl(pos.ticket, new_sl, pos.tp)

            elif pos.type == mt5.ORDER_TYPE_SELL:
                if (pos.price_open - current_price) >= activation_dist:
                    new_sl = round(current_price + step_dist, 2)
                    # Verify if the new Stop Loss is lower than the current one
                    if pos.sl == 0.0 or new_sl < pos.sl:
                        self._modify_position_sl(pos.ticket, new_sl, pos.tp)

    def _modify_position_sl(self, ticket: int, target_sl: float, target_tp: float):
        """Transmits alteration packets to the broker backend terminal."""
        if mt5 is None:
            return

        mod_request = {
            "action": mt5.TRADE_ACTION_SLTP,
            "position": ticket,
            "sl": target_sl,
            "tp": target_tp
        }
        result = mt5.order_send(mod_request)
        if result and result.retcode == mt5.TRADE_RETCODE_DONE:
            logger.info(f"[🛡️ AUREUS Trailing Stop] Ticket #{ticket} safely locked at SL: ${target_sl:.2f}")

    def get_account_equity(self) -> float:
        """Returns live account equity from MT5."""
        if mt5 is None:
            return 100000.0
        info = mt5.account_info()
        return float(info.equity) if info is not None else 100000.0

    def get_account_summary(self) -> Dict[str, Any]:
        """Returns comprehensive account metrics from MT5."""
        if mt5 is None:
            return {"balance": 100000.0, "equity": 100000.0, "profit": 0.0, "margin": 0.0, "margin_free": 100000.0, "currency": "USD"}
        info = mt5.account_info()
        if not info:
            return {"balance": 100000.0, "equity": 100000.0, "profit": 0.0, "margin": 0.0, "margin_free": 100000.0, "currency": "USD"}
        return {
            "login": getattr(info, "login", 0),
            "balance": float(getattr(info, "balance", 0.0)),
            "equity": float(getattr(info, "equity", 0.0)),
            "profit": float(getattr(info, "profit", 0.0)),
            "margin": float(getattr(info, "margin", 0.0)),
            "margin_free": float(getattr(info, "margin_free", 0.0)),
            "currency": str(getattr(info, "currency", "USD")),
            "server": str(getattr(info, "server", "MetaQuotes-Demo")),
            "leverage": int(getattr(info, "leverage", 100))
        }

    def get_open_positions_detail(self) -> List[Dict[str, Any]]:
        """Returns detailed breakdown of all active positions."""
        if mt5 is None:
            return []
        positions = mt5.positions_get(symbol=self.symbol)
        if not positions:
            return []
        details = []
        for p in positions:
            dir_str = "BUY" if p.type == 0 else "SELL"
            details.append({
                "ticket": p.ticket,
                "type": dir_str,
                "volume": p.volume,
                "price_open": p.price_open,
                "price_current": p.price_current,
                "sl": p.sl,
                "tp": p.tp,
                "profit": p.profit,
                "magic": p.magic,
                "comment": p.comment
            })
        return details

    def compute_precision_lot(self, risk_pct: float, sl_pips: float) -> float:
        """Computes institutional lot size dynamically based on equity, broker step, and SL distance."""
        equity = self.get_account_equity()
        risk_capital = equity * risk_pct
        pip_value_per_lot = 10.0  # standard gold pip value per 1.00 lot ($1.00 move = 10 pips = $100 per lot)
        try:
            raw_lot = risk_capital / (sl_pips * pip_value_per_lot)
        except ZeroDivisionError:
            raw_lot = 0.01

        info = mt5.symbol_info(self.symbol) if mt5 else None
        vol_min = float(getattr(info, "volume_min", 0.01) or 0.01)
        vol_max = float(getattr(info, "volume_max", 5.0) or 5.0)
        vol_step = float(getattr(info, "volume_step", 0.01) or 0.01)

        # Normalize to broker lot step
        if vol_step > 0:
            steps = round(raw_lot / vol_step)
            stepped_lot = steps * vol_step
        else:
            stepped_lot = raw_lot

        # Clamp between minimum lot and max cap (capped at 5.0 for prop risk safety)
        final_lot = max(vol_min, min(stepped_lot, min(vol_max, 5.0)))
        return round(final_lot, 2)

    def _diagnose_retcode(self, code: int, raw_comment: str) -> str:
        """Translates cryptic broker return codes into actionable diagnostic instructions."""
        codes_map = {
            10004: "Requote: Market moved before order completed. Re-polling price.",
            10006: "Request Rejected by broker.",
            10013: "Invalid Request: Check symbol parameters.",
            10014: "Invalid Volume: Proposed lot size violates broker minimum/maximum volume rules.",
            10015: "Invalid Price: Current price is stale.",
            10016: "Invalid Stops: Stop Loss or Take Profit violates broker minimum StopLevel/FreezeLevel.",
            10018: "Market Closed: Trading session is currently paused by broker.",
            10019: "Insufficient Margin: Free equity is too low for proposed contract size.",
            10021: "No Quotes: Liquidity provider has temporarily paused price feed.",
            10026: "Autotrading Disabled: Algorithmic trading is disabled in MetaTrader 5 terminal! Please click the 'Algo Trading' button on the MT5 toolbar.",
            10027: "Client Disabled Autotrading: Enable Expert Advisor execution in MT5 terminal options."
        }
        explanation = codes_map.get(code, raw_comment or "Unknown broker condition")
        return f"Broker Code {code}: {explanation}"

    def transmit_order_packet(
        self,
        direction: str,
        risk_pct: float,
        sl_pips: float,
        tp_pips: float
    ) -> Dict[str, Any]:
        """Submits institutional order packet to MT5 with risk bounds, retries, and stops_level enforcement."""
        if not self._connected:
            self.connect()

        if mt5 is None:
            return {"status": "FAILED", "reason": "MT5 unavailable"}

        info = mt5.symbol_info(self.symbol)
        if not info:
            return {"status": "FAILED", "reason": f"Symbol telemetry unavailable for {self.symbol}"}

        point = float(getattr(info, "point", 0.01) or 0.01)
        stops_level_pts = float(getattr(info, "trade_stops_level", 0) or 0)
        freeze_level_pts = float(getattr(info, "trade_freeze_level", 0) or 0)
        min_stop_dist = max(stops_level_pts * point, freeze_level_pts * point, point * 10)

        # Enforce broker minimum stops level distance
        sl_delta = max(sl_pips * 0.10, min_stop_dist + point * 5)
        tp_delta = max(tp_pips * 0.10, min_stop_dist + point * 5)

        lots = self.compute_precision_lot(risk_pct, sl_pips)
        order_type = mt5.ORDER_TYPE_BUY if direction == "BUY" else mt5.ORDER_TYPE_SELL
        filling = self._fill_mode if self._fill_mode is not None else mt5.ORDER_FILLING_IOC

        max_retries = 3
        last_code = -1
        last_comment = ""

        for attempt in range(max_retries):
            tick = mt5.symbol_info_tick(self.symbol)
            if not tick:
                return {"status": "FAILED", "reason": "No market tick telemetry"}

            price = tick.ask if direction == "BUY" else tick.bid
            sl = round(price - sl_delta if direction == "BUY" else price + sl_delta, 2)
            tp = round(price + tp_delta if direction == "BUY" else price - tp_delta, 2)

            order_struct = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": self.symbol,
                "volume": lots,
                "type": order_type,
                "price": price,
                "sl": sl,
                "tp": tp,
                "deviation": 25,  # 25 points tolerance buffer ($0.25 on gold)
                "magic": self.magic,
                "comment": "DON AURELIUS AUREUS-VII",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": filling
            }

            result = mt5.order_send(order_struct)
            if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                logger.info(f"[🚀 AUREUS DEPLOYED] {direction} {lots} lots @ ${price:.2f} | SL: ${sl:.2f} | TP: ${tp:.2f} (Deal #{result.deal})")
                return {
                    "status": "SUCCESS",
                    "ticket": result.deal,
                    "lots": lots,
                    "price": price,
                    "sl": sl,
                    "tp": tp
                }

            if result:
                last_code = result.retcode
                last_comment = result.comment
                # Retry on requote or transient price adjustment
                if result.retcode in [mt5.TRADE_RETCODE_REQUOTE, mt5.TRADE_RETCODE_PRICE_CHANGED, 10004, 10020]:
                    import time
                    time.sleep(0.2)
                    continue
                else:
                    break
            else:
                last_comment = "Order send returned None"
                break

        diag_msg = self._diagnose_retcode(last_code, last_comment)
        return {"status": "FAILED", "reason": diag_msg, "code": last_code}

    def emergency_kill_switch(self) -> int:
        """Clean Slate Protocol: Liquidates all open positions on the symbol immediately."""
        if not self._connected:
            self.connect()

        if mt5 is None:
            return 0

        positions = mt5.positions_get(symbol=self.symbol)
        if not positions:
            return 0

        closed_count = 0
        filling = self._fill_mode if self._fill_mode is not None else mt5.ORDER_FILLING_IOC

        for pos in positions:
            tick = mt5.symbol_info_tick(self.symbol)
            if not tick:
                continue

            order_type = mt5.ORDER_TYPE_SELL if pos.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY
            price = tick.bid if order_type == mt5.ORDER_TYPE_SELL else tick.ask

            close_struct = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": self.symbol,
                "volume": pos.volume,
                "type": order_type,
                "position": pos.ticket,
                "price": price,
                "deviation": 15,
                "magic": self.magic,
                "comment": "DON AURELIUS CLEAN SLATE",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": filling
            }
            res = mt5.order_send(close_struct)
            if res and res.retcode == mt5.TRADE_RETCODE_DONE:
                closed_count += 1
                logger.warning(f"[🛑 CLEAN SLATE] Liquidated ticket #{pos.ticket} ({pos.volume} lots).")

        return closed_count
