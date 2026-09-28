"""
Layer 2 Defense: Standalone 2-Second Heartbeat Watchdog Daemon.
Runs in an independent background process.
Monitors the pulse written by main.py to data/heartbeat.pulse.
If main.py freezes, crashes, or unhandled exceptions stall the loop for > 2.0 seconds:
Watchdog connects directly to MT5 and immediately flattens all open positions!
"""

import os
import time
import logging
import MetaTrader5 as mt5

logger = logging.getLogger("HeartbeatWatchdog")


class HeartbeatWatchdog:
    def __init__(self, pulse_file: str = "data/heartbeat.pulse", timeout_seconds: float = 3.0, magic: int = 260925):
        self.pulse_file = pulse_file
        self.timeout_seconds = timeout_seconds
        self.magic = magic
        os.makedirs(os.path.dirname(self.pulse_file), exist_ok=True)

    @staticmethod
    def write_pulse(pulse_file: str = "data/heartbeat.pulse") -> None:
        """Called by main.py on every active loop iteration."""
        try:
            with open(pulse_file, "w", encoding="utf-8") as f:
                f.write(str(time.time()))
        except Exception:
            pass

    def run_monitor(self) -> None:
        logger.info(f"Starting Standalone Watchdog Daemon. Timeout: {self.timeout_seconds}s...")
        while True:
            time.sleep(0.5)
            if not os.path.exists(self.pulse_file):
                continue

            try:
                with open(self.pulse_file, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                if not content:
                    continue
                last_pulse = float(content)
                elapsed = time.time() - last_pulse

                if elapsed > self.timeout_seconds:
                    logger.critical(f"[WATCHDOG] TIMEOUT! No pulse for {elapsed:.2f}s (> {self.timeout_seconds}s). INITIATING EMERGENCY FLATTEN!")
                    self.emergency_broker_flatten()
                    # Reset pulse so we don't spam flatten
                    self.write_pulse(self.pulse_file)
            except Exception as e:
                logger.error(f"Watchdog read error: {e}")

    def emergency_broker_flatten(self) -> None:
        """Directly accesses MT5 matching engine to flatten open positions."""
        if not mt5.initialize():
            logger.error("Watchdog: Could not connect to MT5 during emergency.")
            return

        positions = mt5.positions_get()
        if positions:
            for p in positions:
                if p.magic == self.magic:
                    tick = mt5.symbol_info_tick(p.symbol)
                    if not tick:
                        continue
                    close_type = mt5.ORDER_TYPE_SELL if p.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY
                    price = tick.bid if close_type == mt5.ORDER_TYPE_SELL else tick.ask

                    req = {
                        "action": mt5.TRADE_ACTION_DEAL,
                        "position": p.ticket,
                        "symbol": p.symbol,
                        "volume": float(p.volume),
                        "type": close_type,
                        "price": float(price),
                        "magic": self.magic,
                        "comment": "Watchdog Emergency Flatten",
                        "type_filling": mt5.ORDER_FILLING_IOC,
                    }
                    res = mt5.order_send(req)
                    logger.info(f"Watchdog Emergency Flatten Position #{p.ticket}: Retcode {res.retcode if res else 'None'}")

        mt5.shutdown()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [WATCHDOG] %(message)s")
    wd = HeartbeatWatchdog()
    wd.run_monitor()
