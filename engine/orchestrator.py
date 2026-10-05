"""
JARVIS System Orchestration Pipeline.
Unifies Intermarket Analysis (DXY + US10Y), Dynamic Auto-Trailing Stops,
ElevenLabs Vocal Briefings, and Interactive Telegram HUD.
"""

import os
import sys
import json
import time
import logging
from datetime import datetime
import pandas as pd
from typing import Optional

# Graceful redirection for headless / pythonw.exe execution (prevents NoneType write crashes)
if sys.stdout is None:
    try:
        os.makedirs("data", exist_ok=True)
        sys.stdout = open("data/jarvis_stdout.log", "a", encoding="utf-8", buffering=1)
    except Exception:
        sys.stdout = open(os.devnull, "w")
if sys.stderr is None:
    try:
        os.makedirs("data", exist_ok=True)
        sys.stderr = open("data/jarvis_stderr.log", "a", encoding="utf-8", buffering=1)
    except Exception:
        sys.stderr = open(os.devnull, "w")

try:
    import MetaTrader5 as mt5
except ImportError:
    mt5 = None

from engine.mt5_execution import MT5ExecutionBridge
from engine.strategy import JarvisStrategyEngine
from communication.jarvis_voice import JarvisVoiceCore
from communication.telegram_hud import JarvisTelegramHUD
from database.jarvis_logger import JarvisDatabaseLogger
from intelligence.war_room import TitanWarRoom, ConsensusVerdict
from engine.session_reporter import TitanSessionReporter

logger = logging.getLogger("JarvisOrchestrator")


class JarvisOrchestrator:
    """
    JARVIS Autonomous Trading & Protection Matrix with Database Telemetry.
    """

    def __init__(
        self,
        symbol: str = "XAUUSD",
        magic: int = 20260926,
        telegram_token: Optional[str] = None,
        telegram_chat_id: Optional[str] = None,
        elevenlabs_key: Optional[str] = None,
        risk_pct: float = 0.01,
        trail_activation_pips: float = 25.0,
        trail_step_pips: float = 8.0,
        max_open_positions: int = 2,
        db_path: str = "data/jarvis_metrics.db"
    ):
        self.symbol = symbol
        self.magic = magic
        self.risk_pct = risk_pct
        self.trail_activation_pips = trail_activation_pips
        self.trail_step_pips = trail_step_pips
        self.max_open_positions = max_open_positions

        # Auto-load credentials from .env or vault if not passed directly
        from config.credentials import load_credentials
        creds = load_credentials()
        telegram_token = telegram_token or creds.TELEGRAM_BOT_TOKEN or None
        telegram_chat_id = telegram_chat_id or creds.TELEGRAM_CHAT_ID or None
        elevenlabs_key = elevenlabs_key or creds.ELEVENLABS_API_KEY or None
        elevenlabs_voice = creds.ELEVENLABS_VOICE_ID or "pNInz6obpgDQGcFmaJgB"

        self.db = JarvisDatabaseLogger(db_path=db_path)
        self.bridge = MT5ExecutionBridge(symbol=self.symbol, magic=self.magic)
        self.strategy = JarvisStrategyEngine()
        self.war_room = TitanWarRoom(hawk=self.strategy, base_risk_pct=self.risk_pct)
        self.voice = JarvisVoiceCore(api_key=elevenlabs_key, voice_id=elevenlabs_voice)
        self.latest_consensus = None
        self.latest_xau = 0.0
        self.latest_spread = 0.0
        self.hud = JarvisTelegramHUD(
            token=telegram_token or "",
            execution_bridge=self.bridge,
            elevenlabs_key=elevenlabs_key,
            elevenlabs_voice=elevenlabs_voice,
            chat_id=telegram_chat_id,
            strategy_engine=self.strategy,
            db_logger=self.db,
            war_room=self.war_room,
            orchestrator=self
        )
        self.reporter = TitanSessionReporter(db_path=db_path)
        self._last_report_time = time.time()

        self.running = False
        self._last_signal_time = 0.0
        self._last_telegram_heartbeat = time.time()
        self.telegram_interval_seconds = 15 * 60  # 15 minutes
        self.backup_dispatched_this_week = False

    def initialize(self) -> bool:
        """Boots the DON AURELIUS core and verifies broker telemetry channels."""
        print("======================================================================")
        print("          [+] DON AURELIUS: SOVEREIGN QUANTUM SYNDICATE [+]           ")
        print("======================================================================")
        logger.info("[DON-AURELIUS] Initializing hardware bridge and neural filters...")

        # Lock Windows Execution State: Never sleep, enable Away Mode for closed-lid/overnight trading
        try:
            import ctypes
            ES_CONTINUOUS = 0x80000000
            ES_SYSTEM_REQUIRED = 0x00000001
            ES_AWAYMODE_REQUIRED = 0x00000040
            ctypes.windll.kernel32.SetThreadExecutionState(
                ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_AWAYMODE_REQUIRED
            )
            logger.info("[DON-AURELIUS] Windows Execution State Locked: Sleep & Suspend disabled.")
        except Exception as e:
            logger.warning(f"[DON-AURELIUS] Could not set Windows execution state: {e}")

        if not self.bridge.connect():
            logger.error("[DON-AURELIUS] Failed to connect to MetaTrader 5 terminal profile.")
            return False

        equity = self.bridge.get_account_equity()
        print(f"[+] Sovereign Terminal Connected: Account Equity = ${equity:,.2f} USD | Symbol = {self.symbol}")

        # Resolve Macro Index Feeds
        resolved_any = self.strategy.resolve_broker_tickers()
        dxy_name = self.strategy.resolved_dxy or "Proxy/Standalone"
        us10y_name = self.strategy.resolved_us10y or "Standalone"
        if resolved_any:
            print(f"[+] Macro Radar Active: DXY -> {dxy_name} | US10Y -> {us10y_name}")
        else:
            print("[!] Notice: Exact macro indexes not found directly. Running in resilient standalone/proxy mode.")

        # Launch Telegram HUD
        self.hud.launch_interface()

        # Send initial boot announcement
        boot_report = (
            f"Don Aurelius online. Sovereign systems nominal. Account equity stands at "
            f"{int(equity):,} dollars. Trailing stop protection arrays engaged."
        )
        audio = self.voice.compile_vocal_briefing(boot_report)
        if audio and self.hud.chat_id:
            self.hud._send_voice(self.hud.chat_id, audio, caption="👑 Don Aurelius Online Audio Briefing")

        self.running = True
        return True

    def run_step(self):
        """Single execution iteration for the orchestration loop."""
        if mt5 is None:
            return

        # Automated Friday afternoon data backup routing logic (4:00 PM every Friday)
        now_dt = datetime.now()
        current_day = now_dt.strftime("%A")
        current_hour = now_dt.hour

        if current_day == "Friday" and current_hour == 16:
            if not self.backup_dispatched_this_week:
                logger.info("[JARVIS] Scheduled Friday 16:00 database backup dispatch triggered.")
                self.hud.transmit_database_archive(chat_id=self.hud.chat_id, logger_instance=self.db)
                self.backup_dispatched_this_week = True
        else:
            if current_day != "Friday":
                self.backup_dispatched_this_week = False

        # 1. Manage Active Positions Trailing Safeties smoothly
        try:
            self.bridge.execute_trailing_stops(
                trail_activation_pips=self.trail_activation_pips,
                trail_step_pips=self.trail_step_pips
            )
        except Exception as e:
            logger.error(f"[AUREUS] Trailing Stop Guard: {e}")

        # 2. Extract Data for Analysis Strategy Loop
        rates = mt5.copy_rates_from_pos(self.symbol, mt5.TIMEFRAME_M15, 0, 50)
        if rates is None or len(rates) < 30:
            return

        xau_df = pd.DataFrame(rates)

        # Extract comparative parameters independently if tickers are mapped
        dxy_df = pd.DataFrame()
        if self.strategy.resolved_dxy:
            dxy_rates = mt5.copy_rates_from_pos(self.strategy.resolved_dxy, mt5.TIMEFRAME_M15, 0, 50)
            if dxy_rates is not None and len(dxy_rates) >= 30:
                dxy_df = pd.DataFrame(dxy_rates)

        us10y_df = pd.DataFrame()
        if self.strategy.resolved_us10y:
            us10y_rates = mt5.copy_rates_from_pos(self.strategy.resolved_us10y, mt5.TIMEFRAME_M15, 0, 50)
            if us10y_rates is not None and len(us10y_rates) >= 30:
                us10y_df = pd.DataFrame(us10y_rates)

        # 3. Process Signals through TITAN-X Multi-Agent Consensus Council
        current_spread_pips = 1.8
        if mt5 is not None:
            try:
                tick = mt5.symbol_info_tick(self.symbol)
                if tick and tick.ask and tick.bid:
                    spread_raw = tick.ask - tick.bid
                    current_spread_pips = round(spread_raw / 0.10, 1)  # $1 gold = 10 pips ($0.10/pip)
            except Exception:
                pass

        consensus = self.war_room.convene_council(
            xau_df=xau_df,
            dxy_df=dxy_df if len(dxy_df) > 0 else None,
            us10y_df=us10y_df if len(us10y_df) > 0 else None,
            current_spread_pips=current_spread_pips
        )
        decision = consensus.final_decision
        current_atr = consensus.telemetry.get("atr", 1.50)
        active_risk_pct = consensus.recommended_risk_pct if consensus.consensus_achieved else self.risk_pct

        # Log system telemetry snapshot to persistent database
        current_xau = float(xau_df['close'].iloc[-1])
        dxy_val = float(dxy_df['close'].iloc[-1]) if ('close' in dxy_df and len(dxy_df) > 0) else 0.0
        us10y_val = float(us10y_df['close'].iloc[-1]) if ('close' in us10y_df and len(us10y_df) > 0) else 0.0
        self.latest_consensus = consensus
        self.latest_xau = current_xau
        self.latest_spread = current_spread_pips
        self.db.log_system_telemetry(current_xau, dxy_val, us10y_val, current_atr, status=decision)

        # Export Council Telemetry directly to MT5 Common Files for On-Chart HUD
        try:
            mt5_common_dir = os.path.expandvars(r"%APPDATA%\MetaQuotes\Terminal\Common\Files")
            if os.path.exists(mt5_common_dir):
                telemetry_payload = {
                    "timestamp": time.time(),
                    "decision": decision,
                    "ratio": consensus.supermajority_ratio,
                    "risk_pct": active_risk_pct,
                    "atr": current_atr,
                    "spread": current_spread_pips,
                    "veto": consensus.veto_triggered,
                    "hawk": getattr(consensus.votes.get("HAWK"), "vote", "N/A"),
                    "radar": getattr(consensus.votes.get("RADAR"), "vote", "N/A"),
                    "predator": getattr(consensus.votes.get("PREDATOR"), "vote", "N/A"),
                    "inquisitor": getattr(consensus.votes.get("INQUISITOR"), "vote", "N/A"),
                    "rationale": consensus.rationale
                }
                filepath = os.path.join(mt5_common_dir, "titan_council.json")
                with open(filepath, "w") as f:
                    json.dump(telemetry_payload, f, indent=2)
        except Exception:
            pass

        now = time.time()
        # Continuously refresh Desktop Executive Report for user review
        if (now - self._last_report_time) >= 60.0:
            try:
                self.reporter.generate_html_report()
                self._last_report_time = now
            except Exception:
                pass

        # 4. Scheduled 15-Minute Syndicate Telemetry Dispatch to Telegram
        if (now - self._last_telegram_heartbeat) >= self.telegram_interval_seconds:
            try:
                self._dispatch_periodic_telemetry_briefing(
                    current_xau=current_xau,
                    current_spread_pips=current_spread_pips,
                    consensus=consensus
                )
                self._last_telegram_heartbeat = now
            except Exception as e:
                logger.error(f"[AUREUS] Periodic Telegram briefing failed: {e}")

        # Institutional Exposure Gate: Only deploy if below max concurrent positions
        open_contracts = mt5.positions_get(symbol=self.symbol) if mt5 else None
        current_contract_count = len(open_contracts) if open_contracts else 0

        if decision in ["BUY", "SELL"] and (now - self._last_signal_time) > 900 and current_contract_count < self.max_open_positions:
            sl_calculated_pips = consensus.telemetry.get("sl_pips", max(15, int((current_atr * 2.5) * 10)))
            tp_calculated_pips = consensus.telemetry.get("tp_pips", int(sl_calculated_pips * 3.0))

            result = self.bridge.transmit_order_packet(
                direction=decision,
                risk_pct=active_risk_pct,
                sl_pips=sl_calculated_pips,
                tp_pips=tp_calculated_pips
            )

            if result.get("status") == "SUCCESS":
                self._last_signal_time = now
                lots = result.get("lots", 0.01)
                price = result.get("price", 0.0)
                sl = result.get("sl", 0.0)
                tp = result.get("tp", 0.0)
                ticket = result.get("ticket", int(now))

                # Log trade execution to persistent database
                self.db.log_trade_deployment(
                    ticket_id=ticket,
                    direction=decision,
                    volume=lots,
                    entry_price=price,
                    sl=sl,
                    tp=tp
                )

                # Send Telegram notification & vocal briefing
                v_hawk = consensus.votes.get("HAWK", None)
                v_radar = consensus.votes.get("RADAR", None)
                v_predator = consensus.votes.get("PREDATOR", None)
                v_inquisitor = consensus.votes.get("INQUISITOR", None)

                order_msg = (
                    f"👑 **DON AURELIUS • SOVEREIGN SYNDICATE**\n"
                    f"⚡ **COUNCIL CONSENSUS: {consensus.supermajority_ratio}**\n"
                    f"🚀 **ORDER EXECUTED**\n"
                    f"● Ticket: `#{ticket}`\n"
                    f"● Direction: **{decision}**\n"
                    f"● Volume: `{lots:.2f} lots` (Kelly Risk: {active_risk_pct*100:.2f}%)\n"
                    f"● Entry: `${price:.2f}`\n"
                    f"● Stop Loss: `${sl:.2f}`\n"
                    f"● Take Profit: `${tp:.2f}`\n"
                    f"● Spread: `{current_spread_pips:.1f} pips` | ATR: `${current_atr:.2f}`\n"
                    f"● **Council Ballots**:\n"
                    f"   - 🦅 HAWK (Macro): {getattr(v_hawk, 'vote', 'N/A')}\n"
                    f"   - 📡 RADAR (Sentiment): {getattr(v_radar, 'vote', 'N/A')}\n"
                    f"   - 🦈 PREDATOR (Order Flow): {getattr(v_predator, 'vote', 'N/A')}\n"
                    f"   - ⚔️ INQUISITOR (Red-Team): {getattr(v_inquisitor, 'vote', 'N/A')}"
                )
                self.hud._send_message(self.hud.chat_id, order_msg)

                narrative = self.voice.generate_trade_narrative(decision, lots, price, sl, tp)
                voice_audio = self.voice.compile_vocal_briefing(narrative)
                if voice_audio and self.hud.chat_id:
                    self.hud._send_voice(self.hud.chat_id, voice_audio, caption=f"🎯 Trade Execution Briefing ({decision})")

    def _dispatch_periodic_telemetry_briefing(self, current_xau: float, current_spread_pips: float, consensus: Any):
        """Transmits automated 15-minute operational updates directly to user's Telegram."""
        if not self.hud or not self.hud.chat_id or not self.hud.token:
            return

        equity_raw = self.bridge.get_account_equity() if self.bridge else 0.0
        try:
            equity = float(equity_raw)
        except (TypeError, ValueError):
            equity = 0.0

        try:
            xau_val = float(current_xau)
        except (TypeError, ValueError):
            xau_val = 0.0

        try:
            spread_val = float(current_spread_pips)
        except (TypeError, ValueError):
            spread_val = 0.0

        open_positions = mt5.positions_get(symbol=self.symbol) if mt5 else None
        pos_count = len(open_positions) if open_positions else 0
        try:
            floating_pl = sum(float(getattr(p, 'profit', 0.0)) for p in open_positions) if open_positions else 0.0
        except (TypeError, ValueError):
            floating_pl = 0.0
        pl_sign = "+" if floating_pl >= 0 else ""

        pos_str = ""
        if open_positions:
            for p in open_positions:
                try:
                    p_type = getattr(p, "type", 0)
                    dir_label = "BUY" if p_type == 0 else "SELL"
                    p_vol = float(getattr(p, "volume", 0.0))
                    p_open = float(getattr(p, "price_open", 0.0))
                    p_curr = float(getattr(p, "price_current", 0.0))
                    p_prof = float(getattr(p, "profit", 0.0))
                    p_sl = float(getattr(p, "sl", 0.0))
                    p_tp = float(getattr(p, "tp", 0.0))
                    p_sign = "+" if p_prof >= 0 else ""
                    pos_str += (
                        f"\n   • 📋 `#{getattr(p, 'ticket', 'N/A')}`: **{dir_label} {p_vol:.2f}L** @ `${p_open:.2f}`\n"
                        f"     Current: `${p_curr:.2f}` | P&L: `{p_sign}${p_prof:,.2f}`\n"
                        f"     🛡️ SL: `${p_sl:.2f}` | 🎯 TP: `${p_tp:.2f}`"
                    )
                except Exception:
                    continue

        v_hawk = getattr(consensus.votes.get("HAWK"), "vote", "N/A") if hasattr(consensus, "votes") and consensus.votes else "N/A"
        v_radar = getattr(consensus.votes.get("RADAR"), "vote", "N/A") if hasattr(consensus, "votes") and consensus.votes else "N/A"
        v_predator = getattr(consensus.votes.get("PREDATOR"), "vote", "N/A") if hasattr(consensus, "votes") and consensus.votes else "N/A"
        v_inquisitor = getattr(consensus.votes.get("INQUISITOR"), "vote", "N/A") if hasattr(consensus, "votes") and consensus.votes else "N/A"

        now_str = datetime.now().strftime("%I:%M %p")
        ratio_str = getattr(consensus, "supermajority_ratio", "N/A")
        decision_str = getattr(consensus, "final_decision", "N/A")
        rationale_str = str(getattr(consensus, "rationale", "Scanning markets..."))[:140]

        briefing_msg = (
            f"👑 **DON AURELIUS • 15-MIN SYNDICATE BRIEFING** ({now_str})\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"💰 **Treasury Equity**: `${equity:,.2f} USD`\n"
            f"⚡ **Active Contracts**: `{pos_count}` | Floating P&L: `{pl_sign}${floating_pl:,.2f}`"
            f"{pos_str}\n"
            f"🥇 **XAUUSD (Gold)**: `${xau_val:.2f}` (Spread: `{spread_val:.1f} pips`)\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🏛️ **Council Radar** ({ratio_str}):\n"
            f"   - 🦅 HAWK: `{v_hawk}`\n"
            f"   - 📡 RADAR: `{v_radar}`\n"
            f"   - 🦈 PREDATOR: `{v_predator}`\n"
            f"   - ⚔️ INQUISITOR: `{v_inquisitor}`\n"
            f"🎯 **Consensus State**: **{decision_str}**\n"
            f"📝 *Directive*: {rationale_str}..."
        )

        inline_keyboard = {
            "inline_keyboard": [
                [
                    {"text": "🎙️ Voice Briefing", "callback_data": "voice_briefing"},
                    {"text": "📊 Full HUD", "callback_data": "refresh_hud"}
                ]
            ]
        }

        self.hud._send_message(self.hud.chat_id, briefing_msg, reply_markup=inline_keyboard)
        logger.info(f"[AUREUS] Dispatched scheduled 15-min syndicate update ({now_str}) to Telegram.")

    def run_loop(self):
        """Continuous execution loop with graceful crash protection."""
        if not self.initialize():
            print("[-] Unable to initialize AUREUS engine. Aborting.")
            return

        print("[+] AUREUS Sovereign Matrix running in background. Press Ctrl+C to stop.")
        while self.running:
            try:
                self.run_step()
            except Exception as e:
                logger.error(f"[AUREUS] Execution Loop Interrupt: {str(e)}")
            time.sleep(10)  # 10-second cycling speed: cool CPU efficiency & rock-solid execution


def run_orchestration_loop():
    """CLI Entrypoint conforming to specification with single-instance protection."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )
    os.makedirs("data", exist_ok=True)
    lock_file = "data/orchestrator.pid"
    my_pid = os.getpid()

    # Check if an older orchestrator process is still running
    if os.path.exists(lock_file):
        try:
            with open(lock_file, "r") as f:
                old_pid = int(f.read().strip())
            if old_pid != my_pid:
                import ctypes
                kernel32 = ctypes.windll.kernel32
                SYNCHRONIZE = 0x00100000
                process = kernel32.OpenProcess(SYNCHRONIZE, False, old_pid)
                if process != 0:
                    kernel32.CloseHandle(process)
                    logger.warning(f"[AUREUS] Existing orchestrator instance PID {old_pid} is already running. Preventing duplicate collision.")
                    return
        except Exception:
            pass

    with open(lock_file, "w") as f:
        f.write(str(my_pid))

    from config.credentials import load_credentials
    creds = load_credentials()
    orchestrator = JarvisOrchestrator(
        telegram_token=creds.TELEGRAM_BOT_TOKEN or None,
        telegram_chat_id=creds.TELEGRAM_CHAT_ID or None,
        elevenlabs_key=creds.ELEVENLABS_API_KEY or None
    )
    try:
        orchestrator.run_loop()
    finally:
        try:
            if os.path.exists(lock_file):
                os.remove(lock_file)
        except Exception:
            pass


if __name__ == "__main__":
    run_orchestration_loop()

# Sovereign Syndicate Class Aliases
AureusOrchestrator = JarvisOrchestrator
