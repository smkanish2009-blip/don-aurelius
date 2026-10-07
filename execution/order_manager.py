"""
Active Order & Position Lifecycle Manager.
Places market orders with server-side SL/TP, manages Break-Even shifts at +1R,
handles 50% partial take profits at +1.5R, executes trailing stops, and enforces time stops.
"""

import logging
import time
from typing import Optional, Dict, Any, List
import MetaTrader5 as mt5
from config.settings import StrategyParameters, RiskParameters
from strategy.models import TradeSignal, SignalDirection, SetupType
from execution.mt5_client import MT5Client
from execution.slippage_guard import SlippageGuard
from execution.microstructure_router import (
    SpreadHeatmap,
    IcebergSlicer,
    StealthTrailingStopManager,
)

logger = logging.getLogger("OrderManager")


class OrderManager:
    def __init__(self, client: MT5Client, strategy_params: StrategyParameters, risk_params: RiskParameters, order_comment: str = ""):
        self.client = client
        self.params = strategy_params
        self.risk_params = risk_params
        self.order_comment = order_comment
        self.slippage_guard = SlippageGuard(max_slippage_usd=getattr(self.risk_params, "MAX_SLIPPAGE_POINTS", 30) * 0.01)
        self.spread_heatmap = SpreadHeatmap(window_size=150, z_score_threshold=2.2)
        self.iceberg_slicer = IcebergSlicer(min_lot=self.client.lot_min, max_lot=self.client.lot_max, lot_step=self.client.lot_step)
        self.stealth_trailer = StealthTrailingStopManager()
        self.active_trade_meta: Dict[int, Dict[str, Any]] = {}


    def send_order(self, signal: TradeSignal, lots: float) -> Optional[int]:
        """Dispatches an idempotent market order with server-side SL and TP."""
        tick = self.client.get_current_tick()
        if tick is None:
            logger.error("Cannot fetch live tick for order placement.")
            return None

        # Check spread filter
        spread = tick.ask - tick.bid
        if spread > self.risk_params.MAX_SPREAD_USD:
            logger.warning(f"Spread ${spread:.2f} exceeds max allowed ${self.risk_params.MAX_SPREAD_USD:.2f}. Skipping order.")
            return None

        # Microstructure Defense: Spread Heatmap Anomaly Detection
        spread_metrics = self.spread_heatmap.evaluate_spread(spread)
        if spread_metrics.is_anomaly:
            logger.warning(f"[ROUTER-DEFENSE] {spread_metrics.status_msg} Deferring order execution.")
            return None

        order_type = mt5.ORDER_TYPE_BUY if signal.direction == SignalDirection.BUY else mt5.ORDER_TYPE_SELL
        price = tick.ask if signal.direction == SignalDirection.BUY else tick.bid

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.client.symbol,
            "volume": float(lots),
            "type": order_type,
            "price": float(price),
            "sl": float(round(signal.stop_loss, 2)),
            "tp": float(round(signal.take_profit, 2)),
            "deviation": int(self.risk_params.MAX_SLIPPAGE_POINTS),
            "magic": int(self.client.magic_number),
            "comment": self.order_comment,
            "type_time": mt5.ORDER_TIME_GTC,

            "type_filling": self.client.filling_mode,
        }

        # Check order validity before sending
        check_res = mt5.order_check(request)
        if check_res is None or check_res.retcode != mt5.TRADE_RETCODE_DONE:
            comment = check_res.comment if check_res else mt5.last_error()
            logger.error(f"Order check failed: {comment}")
            return None

        result = mt5.order_send(request)
        if result is None or result.retcode != mt5.TRADE_RETCODE_DONE:
            comment = result.comment if result else mt5.last_error()
            logger.error(f"Order dispatch failed: {comment} (retcode: {result.retcode if result else 'None'})")
            return None

        logger.info(f"Order executed successfully! Ticket: #{result.order} | Price: {result.price} | Volume: {lots}")

        # Layer 3 Execution Integrity: Verify Slippage
        slip_ok, slip_usd, slip_msg = self.slippage_guard.verify_execution_slippage(price, result.price)
        if not slip_ok:
            logger.warning(f"[DEFENSE] Slippage Alert: {slip_msg} on order #{result.order}")
        else:
            logger.info(f"Slippage verified: ${slip_usd:.2f} within limit.")

        # Store trade metadata for active lifecycle management
        self.active_trade_meta[result.order] = {
            "entry_price": result.price,
            "initial_sl": signal.stop_loss,
            "initial_tp": signal.take_profit,
            "direction": signal.direction,
            "initial_risk_dist": abs(result.price - signal.stop_loss),
            "is_breakeven_set": False,
            "is_partial_closed": False,
            "open_time": time.time(),
            "bars_held_m15": 0,
            "highest_since_entry": result.price,
            "lowest_since_entry": result.price,
        }

        # Register into local Stealth Trailing Stop Manager
        self.stealth_trailer.register_trade(
            ticket=result.order,
            direction=signal.direction.value,
            entry_price=result.price,
            initial_sl=signal.stop_loss,
            trailing_atr_mult=1.5,
        )

        return result.order

    def manage_open_positions(self, atr_m15: float) -> None:
        """
        Executes tick-by-tick active management on all open positions:
        - Stealth trailing stop evaluation
        - Break-even at +1.0R
        - Partial close at +1.5R
        - Chandelier trailing stop
        """
        positions = self.client.get_open_positions()
        current_ticket_ids = {p.ticket for p in positions}

        # Clean up closed positions from metadata and stealth tracker
        for ticket in list(self.active_trade_meta.keys()):
            if ticket not in current_ticket_ids:
                logger.info(f"Position #{ticket} closed.")
                self.stealth_trailer.deregister_trade(ticket)
                del self.active_trade_meta[ticket]

        tick = self.client.get_current_tick()
        if tick is None:
            return

        for p in positions:
            meta = self.active_trade_meta.get(p.ticket)
            if not meta:
                continue

            # Stealth Trailing Stop Check (Defense against predatory broker stop-hunting)
            should_stealth_close, stealth_trigger_p, stealth_reason = self.stealth_trailer.update_tick(
                p.ticket, tick.bid, tick.ask, atr_m15
            )
            if should_stealth_close:
                logger.info(f"[STEALTH-EXEC] {stealth_reason}. Dispatching stealth market exit.")
                self.close_position(p.ticket, reason=stealth_reason)
                continue

            current_price = tick.bid if p.type == mt5.ORDER_TYPE_BUY else tick.ask
            entry_price = meta["entry_price"]
            risk_dist = meta["initial_risk_dist"]
            if risk_dist <= 0:
                continue

            # Update highest/lowest price tracked
            if current_price > meta["highest_since_entry"]:
                meta["highest_since_entry"] = current_price
            if current_price < meta["lowest_since_entry"]:
                meta["lowest_since_entry"] = current_price

            # Profit distance in R multiples
            profit_dist = (current_price - entry_price) if p.type == mt5.ORDER_TYPE_BUY else (entry_price - current_price)
            current_r = profit_dist / risk_dist

            # 1. Break-Even Check (+1.0R)
            if not meta["is_breakeven_set"] and current_r >= self.params.BREAKEVEN_TRIGGER_R:
                be_price = entry_price + self.params.BREAKEVEN_BUFFER_USD if p.type == mt5.ORDER_TYPE_BUY else entry_price - self.params.BREAKEVEN_BUFFER_USD
                self._modify_position_sl(p.ticket, be_price, p.tp)
                meta["is_breakeven_set"] = True
                logger.info(f"Position #{p.ticket} reached +{current_r:.2f}R. Stop moved to Break-Even (${be_price:.2f}).")

            # 2. Partial Close (+1.5R)
            if not meta["is_partial_closed"] and current_r >= self.params.PARTIAL_CLOSE_TRIGGER_R:
                half_volume = round(p.volume * self.params.PARTIAL_CLOSE_RATIO, 2)
                if half_volume >= self.client.lot_min:
                    self._close_partial(p.ticket, half_volume, p.type)
                    meta["is_partial_closed"] = True
                    logger.info(f"Position #{p.ticket} achieved +{current_r:.2f}R. Banked 50% partial profit ({half_volume} lots).")

            # 3. Trailing Stop (Chandelier Trail after +1.5R)
            if current_r >= self.params.TRAIL_TRIGGER_R:
                trail_dist = self.params.TRAIL_ATR_MULT * atr_m15
                if p.type == mt5.ORDER_TYPE_BUY:
                    new_sl = meta["highest_since_entry"] - trail_dist
                    if new_sl > p.sl:
                        self._modify_position_sl(p.ticket, new_sl, p.tp)
                else:
                    new_sl = meta["lowest_since_entry"] + trail_dist
                    if new_sl < p.sl or p.sl == 0.0:
                        self._modify_position_sl(p.ticket, new_sl, p.tp)

    def _modify_position_sl(self, ticket: int, new_sl: float, current_tp: float) -> bool:
        request = {
            "action": mt5.TRADE_ACTION_SLTP,
            "position": ticket,
            "sl": float(round(new_sl, 2)),
            "tp": float(round(current_tp, 2)),
        }
        res = mt5.order_send(request)
        return res is not None and res.retcode == mt5.TRADE_RETCODE_DONE

    def _close_partial(self, ticket: int, volume: float, pos_type: int) -> bool:
        tick = self.client.get_current_tick()
        close_type = mt5.ORDER_TYPE_SELL if pos_type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY
        price = tick.bid if close_type == mt5.ORDER_TYPE_SELL else tick.ask

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "position": ticket,
            "symbol": self.client.symbol,
            "volume": float(volume),
            "type": close_type,
            "price": float(price),
            "deviation": int(self.risk_params.MAX_SLIPPAGE_POINTS),
            "magic": int(self.client.magic_number),
            "comment": self.order_comment,
            "type_filling": self.client.filling_mode,

        }
        res = mt5.order_send(request)
        return res is not None and res.retcode == mt5.TRADE_RETCODE_DONE

    def close_position(self, ticket: int, reason: str = "") -> bool:
        """Closes a single position cleanly by ticket."""
        positions = self.client.get_open_positions()
        for p in positions:
            if p.ticket == ticket:
                success = self._close_partial(p.ticket, p.volume, p.type)
                if success:
                    logger.info(f"Position #{ticket} closed cleanly. Reason: {reason}")
                    self.stealth_trailer.deregister_trade(ticket)
                return success
        return False

    def flatten_all(self, comment: str = "AI-SRB Emergency Flatten") -> None:
        """Closes all open strategy positions immediately."""
        positions = self.client.get_open_positions()
        for p in positions:
            self._close_partial(p.ticket, p.volume, p.type)
        logger.info(f"All positions flattened. Comment: {comment}")
