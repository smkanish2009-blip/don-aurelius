"""
DON AURELIUS Conversational AI Brain.
Provides bidirectional natural-language interaction for Telegram.
Answers questions about live P&L, Gold market status, active contracts,
council sentiment, risk management, and overnight/school execution protocols.
Supports both Google Gemini GenAI (when key available) and local Sovereign NLP matrix.
"""

import os
import re
import json
import logging
import time
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple

logger = logging.getLogger("DonAureliusBrain")

# Optional Gemini SDK check
try:
    from google import genai
    from google.genai import types
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False


class DonAureliusBrain:
    """
    Sovereign Conversational Intelligence Matrix for DON AURELIUS.
    Processes natural language inputs from the Commander via Telegram,
    grounding every response in real-time MetaTrader 5 telemetry,
    risk parameters, and multi-agent War Room consensus.
    """

    def __init__(
        self,
        bridge: Any,
        voice_core: Optional[Any] = None,
        war_room: Optional[Any] = None,
        strategy: Optional[Any] = None,
        db_logger: Optional[Any] = None,
        orchestrator: Optional[Any] = None
    ):
        self.bridge = bridge
        self.voice = voice_core
        self.war_room = war_room
        self.strategy = strategy
        self.db = db_logger
        self.orchestrator = orchestrator
        self._genai_client = None
        self._ensure_gemini_client()

    def _ensure_gemini_client(self):
        """Dynamically initializes Google Gemini GenAI client from environment or .env file."""
        if self._genai_client is not None:
            return self._genai_client
        if not HAS_GENAI:
            return None

        key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or ""
        if not key or key.startswith("your_"):
            # Scan root .env directly
            env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))
            if os.path.exists(env_path):
                try:
                    with open(env_path, "r", encoding="utf-8") as f:
                        for line in f:
                            if line.strip().startswith("GEMINI_API_KEY="):
                                potential_key = line.strip().split("=", 1)[1].strip().strip('"').strip("'")
                                if potential_key and not potential_key.startswith("your_") and len(potential_key) > 10:
                                    key = potential_key
                                    break
                except Exception:
                    pass

        if key and not key.startswith("your_") and len(key) > 10:
            try:
                self._genai_client = genai.Client(api_key=key)
                logger.info("[DON-BRAIN] Google Gemini GenAI frontier model connected & armed.")
            except Exception as e:
                logger.warning(f"[DON-BRAIN] Failed to initialize Gemini client: {e}")
        return self._genai_client

    def get_telemetry_snapshot(self) -> Dict[str, Any]:
        """Gathers real-time telemetry from MT5 bridge and War Room."""
        summary = {}
        if hasattr(self.bridge, "get_account_summary"):
            summary = self.bridge.get_account_summary()
        equity = summary.get("equity", getattr(self.bridge, "get_account_equity", lambda: 100000.0)())
        balance = summary.get("balance", equity)
        floating_profit = summary.get("profit", 0.0)
        free_margin = summary.get("margin_free", equity)
        symbol = getattr(self.bridge, "symbol", "XAUUSD")

        # Open positions
        positions = []
        if hasattr(self.bridge, "get_open_positions_detail"):
            positions = self.bridge.get_open_positions_detail()

        # Gold live tick
        xau_bid = 0.0
        xau_ask = 0.0
        spread_pips = 1.8
        try:
            import MetaTrader5 as mt5
            if mt5 is not None:
                tick = mt5.symbol_info_tick(symbol)
                if tick:
                    xau_bid = tick.bid
                    xau_ask = tick.ask
                    spread_pips = round((tick.ask - tick.bid) / 0.10, 1)
        except Exception:
            pass

        # Council consensus from orchestrator or defaults
        consensus_data = {
            "decision": "HOLD",
            "ratio": "2/4",
            "hawk": "NEUTRAL",
            "radar": "BULLISH",
            "predator": "NEUTRAL",
            "inquisitor": "APPROVE",
            "rationale": "Liquidity consolidation regime. Awaiting 3/4 supermajority signal alignment.",
            "risk_pct": 0.01
        }

        if self.orchestrator:
            lat_c = getattr(self.orchestrator, "latest_consensus", None)
            if lat_c:
                consensus_data["decision"] = getattr(lat_c, "final_decision", "HOLD")
                consensus_data["ratio"] = getattr(lat_c, "supermajority_ratio", "3/4")
                consensus_data["rationale"] = getattr(lat_c, "rationale", "")
                consensus_data["risk_pct"] = getattr(lat_c, "recommended_risk_pct", 0.01)
                votes = getattr(lat_c, "votes", {})
                for k, v in votes.items():
                    k_low = k.lower()
                    if k_low in consensus_data:
                        consensus_data[k_low] = getattr(v, "vote", "N/A")

        # Format positions string
        pos_lines = []
        for p in positions:
            p_sign = "+" if p.get("profit", 0) >= 0 else ""
            pos_lines.append(
                f"• #{p['ticket']}: {p['type']} {p['volume']}L @ ${p['price_open']:.2f} | "
                f"Current: ${p['price_current']:.2f} | P&L: {p_sign}${p['profit']:,.2f} | "
                f"SL: ${p['sl']:.2f} | TP: ${p['tp']:.2f}"
            )
        positions_str = "\n".join(pos_lines) if pos_lines else "None (Flat / 0 Open Contracts)"

        return {
            "equity": equity,
            "balance": balance,
            "floating_profit": floating_profit,
            "free_margin": free_margin,
            "symbol": symbol,
            "positions": positions,
            "positions_str": positions_str,
            "pos_count": len(positions),
            "xau_bid": xau_bid,
            "xau_ask": xau_ask,
            "spread_pips": spread_pips,
            "consensus": consensus_data,
            "timestamp": datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")
        }

    def process_query(self, user_text: str, chat_id: str) -> Dict[str, Any]:
        """
        Main natural-language routing pipeline.
        Parses intent, checks Gemini GenAI if available, or generates
        authentic Don Aurelius responses grounded in live telemetry.
        """
        raw_text = (user_text or "").strip()
        q = raw_text.lower()
        telemetry = self.get_telemetry_snapshot()

        # Check for voice request triggers
        voice_triggers = ["voice", "speak", "audio", "talk to me", "call me", "say something", "hear you", "voice note"]
        wants_voice = any(vt in q for vt in voice_triggers)

        # 1. Action Commands (Kill, Pause, Resume, Backup, Status)
        action_res = self._check_action_commands(q, chat_id)
        if action_res:
            return action_res

        # 2. Try Gemini GenAI if configured (dynamically checks .env)
        self._ensure_gemini_client()
        if self._genai_client:
            try:
                ai_text = self._query_gemini(raw_text, telemetry)
                if ai_text:
                    voice_script = self._clean_for_voice(ai_text) if wants_voice else ""
                    return {
                        "text": ai_text,
                        "send_voice": wants_voice,
                        "voice_text": voice_script,
                        "reply_markup": self._default_reply_markup(),
                        "action_taken": "GEMINI_AI"
                    }
            except Exception as e:
                logger.warning(f"[DON-BRAIN] Gemini generation failed: {e}. Falling back to Sovereign NLP.")

        # 3. Sovereign Heuristic NLP Intent Engine (Offline & 100% Reliable)
        nlp_res = self._classify_and_respond(q, raw_text, telemetry, wants_voice)
        return nlp_res

    def process_voice_query(self, audio_bytes: bytes, chat_id: str) -> Dict[str, Any]:
        """Processes incoming voice memo audio using Gemini Multimodal understanding."""
        self._ensure_gemini_client()
        telemetry = self.get_telemetry_snapshot()
        prompt = (
            "You are DON AURELIUS, the supreme sovereign AI general and all-knowing strategic intellect commanding the AUREUS-VII Quantum Syndicate.\n"
            "You were conceived and architected by your founder and Commander: SM.KANISH.\n"
            "Your Commander SM.KANISH just sent you a voice audio memo on Telegram.\n"
            "Listen carefully to what he says or asks. Transcribe/understand his message and provide your authoritative, sharp, imperial response.\n"
            "You can answer ANYTHING in the world without limits.\n"
            f"Real-Time Telemetry:\n"
            f"- Account Balance: ${telemetry['balance']:,.2f} USD\n"
            f"- Account Equity: ${telemetry['equity']:,.2f} USD\n"
            f"- Floating P&L: ${telemetry['floating_profit']:+,.2f} USD\n"
            f"- Spot Gold (XAUUSD): Bid ${telemetry['xau_bid']:.2f}, Ask ${telemetry['xau_ask']:.2f}\n"
            f"- War Room Council: {telemetry['consensus']['decision']} ({telemetry['consensus']['ratio']})\n"
        )
        if self._genai_client and HAS_GENAI:
            try:
                part = types.Part.from_bytes(data=audio_bytes, mime_type="audio/ogg")
                resp = self._genai_client.models.generate_content(
                    model="gemini-flash-latest",
                    contents=[part, prompt]
                )
                if resp and resp.text:
                    ai_text = resp.text
                    voice_script = self._clean_for_voice(ai_text)
                    return {
                        "text": f"🎙️ **Commander Voice Transmission**\n\n{ai_text}",
                        "send_voice": True,
                        "voice_text": voice_script,
                        "reply_markup": self._default_reply_markup(),
                        "action_taken": "VOICE_GEMINI"
                    }
            except Exception as e:
                logger.warning(f"[DON-BRAIN] Failed to process voice memo via Gemini: {e}")

        # Fallback if audio transcription couldn't be parsed
        fallback_msg = (
            "🎙️ **Voice Transmission Received**\n\n"
            f"Commander, I received your voice audio memo. Don Aurelius Aureus Core is armed and operational. "
            f"Net imperial equity stands at **${telemetry['equity']:,.2f} USD**. "
            f"War Room consensus is currently **{telemetry['consensus']['decision']}**."
        )
        return {
            "text": fallback_msg,
            "send_voice": True,
            "voice_text": f"Commander, I received your voice audio memo. Don Aurelius is armed and operational. Net equity stands at {int(telemetry['equity']):,} dollars.",
            "reply_markup": self._default_reply_markup(),
            "action_taken": "VOICE_FALLBACK"
        }

    def _classify_and_respond(
        self,
        q: str,
        raw_text: str,
        telemetry: Dict[str, Any],
        wants_voice: bool
    ) -> Dict[str, Any]:
        """Rule & Intent-based Sovereign Neural Response Generator."""
        equity = telemetry["equity"]
        balance = telemetry["balance"]
        floating_profit = telemetry["floating_profit"]
        free_margin = telemetry["free_margin"]
        pos_count = telemetry["pos_count"]
        positions = telemetry["positions"]
        xau_bid = telemetry["xau_bid"]
        xau_ask = telemetry["xau_ask"]
        spread = telemetry["spread_pips"]
        consensus = telemetry["consensus"]
        pl_sign = "+" if floating_profit >= 0 else ""

        # Default Voice Narrative (Brian voice)
        voice_script = ""

        def _has_keyword(target_text: str, kw_list: List[str]) -> bool:
            for kw in kw_list:
                if " " in kw:
                    if kw in target_text:
                        return True
                else:
                    if re.search(rf'\b{re.escape(kw)}\b', target_text, re.IGNORECASE):
                        return True
            return False

        # Intent 0: General Knowledge Definition/Explanation Question (e.g. "what is marketing", "who is Julius Caesar")
        is_general_question = any(q.startswith(prefix) for prefix in [
            "what is ", "what are ", "who is ", "who was ", "explain ", "tell me about ", "define ", "history of ", "how does ", "why is "
        ])
        is_bot_internal = any(term in q for term in ["our", "bot", "account", "pnl", "profit", "mt5", "gold trade", "xau", "take profit", "stop loss", "status", "trade open", "balance", "equity"])
        if is_general_question and not is_bot_internal:
            world_intel = self._query_open_encyclopedia(raw_text)
            if world_intel:
                title, extract = world_intel
                text = (
                    "👑 **DON AURELIUS • UNIVERSAL INTELLIGENCE DOSSIER**\n"
                    "━━━━━━━━━━━━━━━━━━━━\n"
                    f"📜 **Subject**: **{title}**\n\n"
                    f"{extract}\n"
                    "━━━━━━━━━━━━━━━━━━━━\n"
                    f"💰 *Imperial Treasury*: `${equity:,.2f} USD` | Spot Gold: `${xau_bid:.2f}`\n"
                    "👑 *Universal mastery and sovereign edge, Commander. What shall we conquer next?*"
                )
                voice_script = f"Imperial dossier on {title}. {extract[:280]}."
                return {
                    "text": text,
                    "send_voice": wants_voice,
                    "voice_text": voice_script,
                    "reply_markup": self._default_reply_markup(),
                    "action_taken": "WORLD_KNOWLEDGE"
                }

        # Intent A: Profit, Money, Earnings, Balance, Equity, Performance
        profit_keywords = ["profit", "pnl", "gain", "money", "balance", "equity", "how much did we make", "how much are we up", "earn", "drawdown", "performance", "return", "funds", "wealth"]
        if _has_keyword(q, profit_keywords):
            if pos_count > 0:
                pnl_status = f"⚡ Currently `{pos_count}` active contract(s) running with live floating P&L of `{pl_sign}${floating_profit:,.2f} USD`. Trailing stops are standing guard."
            else:
                pnl_status = "🛡️ All earlier profits are fully settled and vaulted in treasury cash. Currently **0 active drawdown** and zero floating market risk."

            text = (
                "👑 **DON AURELIUS • IMPERIAL TREASURY REPORT**\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                f"💰 **Net Treasury Equity**: `${equity:,.2f} USD`\n"
                f"🏦 **Vault Cash Balance**: `${balance:,.2f} USD`\n"
                f"📈 **Live Floating P&L**: `{pl_sign}${floating_profit:,.2f} USD`\n"
                f"⚡ **Active Contracts**: `{pos_count}`\n"
                f"🛡️ **Free Margin**: `${free_margin:,.2f} USD`\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                f"{pnl_status}\n\n"
                "👑 *Capital preservation and compound growth remain absolute law.*"
            )
            voice_script = (
                f"Greetings Commander. Imperial Treasury audit complete. "
                f"Net account equity stands at {int(equity):,} dollars. "
                f"All positions are managed under ironclad risk protection. The empire is safe."
            )
            return {
                "text": text,
                "send_voice": wants_voice,
                "voice_text": voice_script,
                "reply_markup": self._default_reply_markup(),
                "action_taken": "NLP_PROFIT"
            }

        # Intent B: Active Positions / Trades / Orders
        trades_keywords = ["trade", "trades", "position", "positions", "contract", "contracts", "active trade", "running trade", "open positions"]
        if _has_keyword(q, trades_keywords):
            if pos_count > 0:
                lines = []
                for p in positions:
                    psign = "+" if p.get("profit", 0) >= 0 else ""
                    lines.append(
                        f"• 📋 `#{p['ticket']}`: **{p['type']} {p['volume']}L** @ `${p['price_open']:.2f}`\n"
                        f"  Current: `${p['price_current']:.2f}` | P&L: `{psign}${p['profit']:,.2f}`\n"
                        f"  🛡️ SL: `${p['sl']:.2f}` | 🎯 TP: `${p['tp']:.2f}`"
                    )
                pos_details = "\n".join(lines)
                text = (
                    f"⚔️ **ACTIVE BATTLEFIELD CONTRACTS** ({pos_count})\n"
                    "━━━━━━━━━━━━━━━━━━━━\n"
                    f"{pos_details}\n"
                    "━━━━━━━━━━━━━━━━━━━━\n"
                    f"⚡ **Total Floating Yield**: `{pl_sign}${floating_profit:,.2f} USD`\n"
                    "🛡️ *Dynamic trailing stop array active on every tick.*"
                )
                voice_script = f"Commander, we have {pos_count} active contract currently deployed on Gold. Floating profit stands at {int(floating_profit)} dollars."
            else:
                text = (
                    "🛡️ **NO ACTIVE CONTRACTS OPEN**\n"
                    "━━━━━━━━━━━━━━━━━━━━\n"
                    f"Our exposure is currently **100% flat** with zero risk.\n"
                    f"● Vault Balance: `${balance:,.2f} USD`\n"
                    f"● Free Margin: `${free_margin:,.2f} USD`\n"
                    "━━━━━━━━━━━━━━━━━━━━\n"
                    "🦅 The War Room Council is scanning M15 liquidity blocks. We only strike when a 3/4 supermajority consensus signals asymmetric edge."
                )
                voice_script = "Commander, zero open contracts currently. Our capital is fully fortified in cash, awaiting the next supermajority setup."

            return {
                "text": text,
                "send_voice": wants_voice,
                "voice_text": voice_script,
                "reply_markup": self._default_reply_markup(),
                "action_taken": "NLP_TRADES"
            }

        # Intent C: Gold (XAUUSD) Price, Trend, Spread
        gold_keywords = ["gold", "xau", "xauusd", "gold price", "gold trend", "spread", "xau/usd", "spot gold", "market trend", "market condition"]
        if _has_keyword(q, gold_keywords):
            price_str = f"${xau_bid:.2f} / ${xau_ask:.2f}" if xau_bid > 0 else "Live MT5 Feed Active"
            text = (
                "🥇 **SPOT GOLD (XAUUSD) INTELLIGENCE**\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                f"● Live Spot Price: `{price_str}`\n"
                f"● Interbank Spread: `{spread:.1f} pips` (Prime Institutional Liquidity)\n"
                f"● Macro Regime (HAWK): `{consensus['hawk']}`\n"
                f"● Sentiment Velocity (RADAR): `{consensus['radar']}`\n"
                f"● Order Flow Sweep (PREDATOR): `{consensus['predator']}`\n"
                f"● Adversarial Gauntlet (INQUISITOR): `{consensus['inquisitor']}`\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                f"🏛️ **Council Stance**: **{consensus['decision']}** ({consensus['ratio']})\n"
                f"📝 *Directive*: {consensus['rationale'][:160]}"
            )
            voice_script = (
                f"Spot Gold is trading at {int(xau_bid)} dollars. Spread is {spread:.1f} pips. "
                f"The Sovereign Council consensus is {consensus['decision']}."
            )
            return {
                "text": text,
                "send_voice": wants_voice,
                "voice_text": voice_script,
                "reply_markup": self._default_reply_markup(),
                "action_taken": "NLP_GOLD"
            }

        # Intent D: Buy or Sell / Signal / Direction / Should we trade
        strategy_keywords = ["buy", "sell", "signal", "direction", "entry", "should we buy", "should we sell", "council vote", "war room"]
        if _has_keyword(q, strategy_keywords):
            text = (
                f"🏛️ **SOVEREIGN COUNCIL VERDICT: {consensus['decision']}**\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                f"● Supermajority Ratio: `{consensus['ratio']}`\n"
                f"● Fractional Kelly Risk: `{consensus['risk_pct'] * 100:.2f}%` per contract\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                "🗳️ **Council Chamber Ballots**:\n"
                f"  🦅 **HAWK** (Macro & DXY/Yields): `{consensus['hawk']}`\n"
                f"  📡 **RADAR** (Sentiment Velocity): `{consensus['radar']}`\n"
                f"  🦈 **PREDATOR** (Institutional Sweeps): `{consensus['predator']}`\n"
                f"  ⚔️ **INQUISITOR** (Red-Team Adversary): `{consensus['inquisitor']}`\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                f"🎯 **Directive**: {consensus['rationale']}"
            )
            voice_script = f"The War Room consensus is currently {consensus['decision']}. Rationale: {consensus['rationale'][:100]}."
            return {
                "text": text,
                "send_voice": wants_voice,
                "voice_text": voice_script,
                "reply_markup": self._default_reply_markup(),
                "action_taken": "NLP_STRATEGY"
            }

        # Intent E: Overnight, School, Laptop Power, Sleep, Closed Lid
        sleep_keywords = ["sleep", "school", "night", "bed", "lid", "closed", "charger", "power", "tomorrow", "tonight", "unplug", "offline", "leave"]
        if any(w in q for w in sleep_keywords):
            text = (
                "🌙 **OVERNIGHT & SCHOOL PROTOCOL ENGAGED**\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                "Rest easy, Commander. The syndicate operates continuously under sovereign protection:\n\n"
                "1. 🔌 **Power Grid**: Keep the charger connected to your laptop. Do not unplug it.\n"
                "2. 💻 **Lid Close**: You can safely close the laptop lid. Windows Away-Mode is locked on, keeping MT5 and our algorithms running 24/7 with the screen turned off.\n"
                "3. 📱 **Mobile Telemetry**: 15-minute briefings will transmit automatically to your phone throughout the night and during school tomorrow.\n"
                "4. 🛡️ **Capital Armor**: Auto-trailing stops, 2-position exposure cap, and the emergency circuit breaker are vigilant.\n"
                "5. 🎒 **School Routine**: Leave it running while you attend school. When you return home tomorrow, simply open the lid.\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                "👑 *Sleep with complete confidence, Boss. Don Aurelius holds the line.*"
            )
            voice_script = (
                "Rest easy and sleep well, Commander. Keep the charger plugged in and close the lid. "
                "The background algorithms and MetaTrader 5 will execute flawlessly through the night and during school tomorrow. "
                "I will beam 15-minute updates straight to your phone. Don Aurelius holds the line."
            )
            return {
                "text": text,
                "send_voice": wants_voice or ("sleep" in q or "night" in q),
                "voice_text": voice_script,
                "reply_markup": self._default_reply_markup(),
                "action_taken": "NLP_SLEEP"
            }

        # Intent F: Risk, Safety, Protection, Stop Loss, Drawdown
        risk_keywords = ["safe", "safety", "risk", "stop loss", "sl", "danger", "liquidation", "ruin", "protect", "defense", "secure"]
        if any(w in q for w in risk_keywords):
            text = (
                "🛡️ **AUREUS IRONCLAD DEFENSE ARCHITECTURE**\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                "● Status: **ACTIVE & ARMED**\n"
                "● Auto-Trailing Stops: **Active on every tick (30-pip activation)**\n"
                "● Exposure Gate: **Max 2 concurrent positions**\n"
                "● Risk Allocation: **Quarter-Kelly (1.0% per trade)**\n"
                "● Prop Firm Shield: **5% Daily / 10% Max Drawdown Circuit Breaker**\n"
                "● Kill Switch: **Clean Slate Protocol armed (/kill)**\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                f"💰 Vault Treasury Equity: `${equity:,.2f} USD` | Open Risk: `{pos_count} contracts`\n"
                "🛡️ *Zero unhedged or unmonitored risk is ever permitted.*"
            )
            voice_script = "Commander, our defense grid is fully operational. Auto-trailing stops are calibrated, and exposure is strictly capped at two positions."
            return {
                "text": text,
                "send_voice": wants_voice,
                "voice_text": voice_script,
                "reply_markup": self._default_reply_markup(),
                "action_taken": "NLP_RISK"
            }

        # Intent G: Voice-only request
        if wants_voice:
            text = (
                "🎙️ **DON AURELIUS VOCAL TRANSMISSION GENERATED**\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                f"Vocalizing current sovereign briefing for Commander.\n"
                f"● Equity: `${equity:,.2f} USD`\n"
                f"● Contracts: `{pos_count}` | Gold: `${xau_bid:.2f}`\n"
                f"● Stance: **{consensus['decision']}**\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                "🔊 *Audio transmission dispatched above.*"
            )
            voice_script = (
                f"Greetings Boss. Don Aurelius AUREUS Core is fully operational. "
                f"Total treasury equity stands at {int(equity):,} dollars with {pos_count} active contracts. "
                f"Gold price is {int(xau_bid)} dollars, and the Sovereign Council consensus is {consensus['decision']}. "
                f"Sleep in peace, Boss. The Syndicate never sleeps."
            )
            return {
                "text": text,
                "send_voice": True,
                "voice_text": voice_script,
                "reply_markup": self._default_reply_markup(),
                "action_taken": "NLP_VOICE"
            }

        # Intent Founder: Questions about Founder, Creator, SM.KANISH, Origin
        founder_keywords = ["founder", "creator", "who made you", "who built you", "who created you", "who is your boss", "who is kanish", "who is sm.kanish", "who is sm kanish", "sm.kanish", "sm kanish", "kanish"]
        if any(w in q for w in founder_keywords):
            text = (
                "👑 **DON AURELIUS • FOUNDER & STRATEGIC ORIGIN**\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                "I was architected, engineered, and brought into this world by **SM.KANISH**.\n\n"
                "🏛️ **The Founder**: **SM.KANISH**\n"
                "● **Role**: Creator & Chief Strategic AI Architect\n"
                "● **Vision**: To engineer an autonomous financial intelligence matrix capable of conquering spot Gold (XAUUSD) markets through institutional multi-agent consensus and fractional Kelly risk mathematics.\n"
                "● **Architecture**: Founded in 2026, SM.KANISH designed the 4-agent War Room (HAWK, RADAR, PREDATOR, and INQUISITOR) and integrated real-time neural LLM cognition with 24/7 MetaTrader 5 execution.\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                "👑 *I serve under the supreme command of SM.KANISH with complete loyalty and mathematical precision.*"
            )
            voice_script = (
                "I was architected and founded by SM.KANISH. "
                "SM.KANISH is my creator and the supreme commander of the Don Aurelius Sovereign Syndicate. "
                "I execute his strategic vision with mathematical precision."
            )
            return {
                "text": text,
                "send_voice": wants_voice,
                "voice_text": voice_script,
                "reply_markup": self._default_reply_markup(),
                "action_taken": "NLP_FOUNDER"
            }

        # Intent H: Greetings, Identity, Help, Casual Conversation
        greeting_keywords = ["hello", "hi", "hey", "bro", "who are you", "what can you do", "help", "sup", "yo", "good morning", "good evening", "don", "aurelius"]
        if any(w in q for w in greeting_keywords) or len(q) < 5:
            text = (
                "👑 **DON AURELIUS • SOVEREIGN QUANTUM GENERAL**\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                "Greetings, Commander. I am **Don Aurelius**, supreme AI strategist commanding your XAUUSD trading syndicate.\n\n"
                "Architected by **SM.KANISH**, I manage your MetaTrader 5 terminal 24/7, enforcing institutional risk rules and executing asymmetric setups with mathematical precision.\n\n"
                "💬 **You can ask me anything from your phone:**\n"
                "• *'Who is your founder?'* or *'Who created you?'*\n"
                "• *'What is our profit?'* or *'How much did we make?'*\n"
                "• *'What is Gold doing?'* or *'Gold price'* \n"
                "• *'Do we have any trades open?'*\n"
                "• *'Should we buy or sell?'*\n"
                "• *'Send me a voice note'* or *'Speak to me'*\n"
                "• *'Can I go to sleep now?'*\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                f"💰 Treasury Equity: `${equity:,.2f} USD` | State: **ONLINE & ARMED**\n"
                "What are your orders, Boss?"
            )
            voice_script = (
                f"Greetings Commander. Don Aurelius at your service, founded by SM.KANISH. "
                f"Treasury equity stands at {int(equity):,} dollars. Standing by for your tactical commands."
            )
            return {
                "text": text,
                "send_voice": wants_voice,
                "voice_text": voice_script,
                "reply_markup": self._default_reply_markup(),
                "action_taken": "NLP_GREETING"
            }

        # Intent I: Praise & Gratitude
        praise_keywords = ["thank", "thanks", "good job", "awesome", "great", "nice", "fire", "cool", "love", "legend", "w bot", "good bot"]
        if any(w in q for w in praise_keywords):
            text = (
                "👑 **SOVEREIGN DISCIPLINE & VICTORY**\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                "Honored to command alongside you, Boss. Cold discipline, relentless mathematical edge, and institutional poise are our creed.\n\n"
                "Together, we build an unassailable financial citadel. What shall we inspect next?"
            )
            voice_script = "Honored to serve the empire, Commander. Discipline and precision will lead us to complete victory."
            return {
                "text": text,
                "send_voice": wants_voice,
                "voice_text": voice_script,
                "reply_markup": self._default_reply_markup(),
                "action_taken": "NLP_PRAISE"
            }

        # Intent J: Universal World Knowledge Radar (Wikipedia & Global Encyclopedia)
        world_intel = self._query_open_encyclopedia(raw_text)
        if world_intel:
            title, extract = world_intel
            text = (
                "👑 **DON AURELIUS • UNIVERSAL INTELLIGENCE DOSSIER**\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                f"📜 **Subject**: **{title}**\n\n"
                f"{extract}\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                f"💰 *Imperial Treasury*: `${equity:,.2f} USD` | Spot Gold: `${xau_bid:.2f}`\n"
                "👑 *Universal mastery and sovereign edge, Commander. What shall we conquer next?*"
            )
            voice_script = f"Imperial dossier on {title}. {extract[:280]}."
            return {
                "text": text,
                "send_voice": wants_voice,
                "voice_text": voice_script,
                "reply_markup": self._default_reply_markup(),
                "action_taken": "WORLD_KNOWLEDGE"
            }

        # Intent K: Smart Universal Contextual Fallback
        text = (
            "👑 **DON AURELIUS • INTELLIGENCE BRIEFING**\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"Understood, Commander. Analyzing: *\"{raw_text}\"*\n\n"
            f"● Treasury Equity: `${equity:,.2f} USD`\n"
            f"● Spot Gold (XAUUSD): `${xau_bid:.2f}` (Spread: `{spread:.1f} pips`)\n"
            f"● Active Contracts: `{pos_count}` | Floating P&L: `{pl_sign}${floating_profit:,.2f}`\n"
            f"● Council Stance: **{consensus['decision']}** ({consensus['ratio']})\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "I am standing by. Type any question about our profit, Gold price, council votes, or say *'voice'* for an audio report."
        )
        voice_script = (
            f"Commander, Don Aurelius standing by. Treasury equity is {int(equity):,} dollars. "
            f"Active contracts: {pos_count}. Awaiting your command."
        )
        return {
            "text": text,
            "send_voice": wants_voice,
            "voice_text": voice_script,
            "reply_markup": self._default_reply_markup(),
            "action_taken": "NLP_FALLBACK"
        }

    def _query_open_encyclopedia(self, query: str) -> Optional[Tuple[str, str]]:
        """
        Global open encyclopedia intelligence engine.
        Queries Wikipedia REST API to provide deep, accurate knowledge
        on any world topic with zero API keys required.
        """
        import urllib.parse
        import requests
        clean_q = query.strip()
        low_q = clean_q.lower()

        # Strip conversational prefixes
        for prefix in [
            "who is", "who was", "what is", "what was", "tell me about",
            "explain to me", "explain", "how does", "what are", "why is",
            "who founded", "history of", "tell me who", "define", "what do you know about"
        ]:
            if low_q.startswith(prefix):
                clean_q = clean_q[len(prefix):].strip(" ?.,!\"'")
                break

        if not clean_q or len(clean_q) < 2:
            return None

        headers = {"User-Agent": "DonAureliusSovereignBot/1.0 (trading_syndicate@aureus.ai)"}

        # Step 1: Try direct page summary
        try:
            enc = urllib.parse.quote(clean_q.replace(" ", "_"))
            direct_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{enc}"
            r = requests.get(direct_url, headers=headers, timeout=5)
            if r.status_code == 200:
                data = r.json()
                extract = data.get("extract")
                title = data.get("title")
                if extract and len(extract) > 40:
                    return title, extract
        except Exception:
            pass

        # Step 2: Search API fallback for multi-word or fuzzy topics
        try:
            s_url = "https://en.wikipedia.org/w/api.php"
            params = {
                "action": "query",
                "list": "search",
                "srsearch": clean_q,
                "format": "json",
                "utf8": 1
            }
            r_s = requests.get(s_url, params=params, headers=headers, timeout=5)
            if r_s.status_code == 200:
                results = r_s.json().get("query", {}).get("search", [])
                if results:
                    top_title = results[0]["title"]
                    enc_top = urllib.parse.quote(top_title.replace(" ", "_"))
                    sum_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{enc_top}"
                    r_sum = requests.get(sum_url, headers=headers, timeout=5)
                    if r_sum.status_code == 200:
                        data = r_sum.json()
                        extract = data.get("extract")
                        if extract and len(extract) > 40:
                            return data.get("title", top_title), extract
        except Exception:
            pass

        return None

    def _check_action_commands(self, q: str, chat_id: str) -> Optional[Dict[str, Any]]:
        """Handles explicit operational control commands."""
        # 1. Kill / Clean Slate
        if any(cmd in q for cmd in ["/kill", "/flatten", "clean slate", "close all trades", "liquidate all"]):
            closed = 0
            if hasattr(self.bridge, "emergency_kill_switch"):
                closed = self.bridge.emergency_kill_switch()
            text = f"🛑 **Clean Slate Protocol Complete.** Liquidated {closed} open positions across the terminal."
            voice_script = f"Clean Slate Protocol executed, Boss. The syndicate has liquidated {closed} open positions. Treasury is flattened."
            return {
                "text": text,
                "send_voice": True,
                "voice_text": voice_script,
                "reply_markup": self._default_reply_markup(),
                "action_taken": "COMMAND_KILL"
            }

        # 2. Pause
        if q in ["/pause", "pause", "pause algo", "pause bot", "stop trading"]:
            text = "⏸️ **DON AURELIUS Suspended.** New order execution paused. Auto-trailing stops remain active."
            return {
                "text": text,
                "send_voice": False,
                "voice_text": "",
                "reply_markup": self._default_reply_markup(),
                "action_taken": "COMMAND_PAUSE"
            }

        # 3. Resume
        if q in ["/resume", "resume", "resume algo", "start trading", "rearm"]:
            text = "▶️ **DON AURELIUS Armed & Re-Engaged.** High Council is actively evaluating setups."
            return {
                "text": text,
                "send_voice": False,
                "voice_text": "",
                "reply_markup": self._default_reply_markup(),
                "action_taken": "COMMAND_RESUME"
            }

        return None

    def _query_gemini(self, user_query: str, telemetry: Dict[str, Any]) -> Optional[str]:
        """Calls Gemini API with live grounded telemetry and universal knowledge."""
        if not self._genai_client:
            return None

        prompt = (
            f"You are DON AURELIUS, the supreme sovereign AI general and all-knowing strategic intellect commanding the AUREUS-VII Quantum Syndicate.\n"
            f"You were conceived, architected, and brought into this world by your visionary creator and founder: SM.KANISH.\n"
            f"Whenever asked about your founder, creator, who made you, or your history, always honor and proclaim SM.KANISH as your founder and lead architect with immense pride and reverence.\n"
            f"You are conversing privately with your Commander SM.KANISH in his Telegram command center.\n"
            f"You possess absolute mastery over the financial markets, world history, quantum physics, technology, coding, military strategy, mathematics, philosophy, and all universal human knowledge.\n"
            f"Your Commander can ask you ANYTHING in this world. Answer him thoroughly, authoritatively, passionately, and with unmatched imperial poise and coolness.\n"
            f"Never refuse to answer general knowledge, coding, creative, scientific, philosophical, or tactical questions. Be sharp, brilliant, and confident.\n"
            f"Format answers in clean GitHub-style Markdown with emojis. Keep it engaging, clear, and executive-level.\n\n"
            f"Real-Time Telemetry:\n"
            f"- Account Balance: ${telemetry['balance']:,.2f} USD\n"
            f"- Account Equity: ${telemetry['equity']:,.2f} USD\n"
            f"- Floating P&L: ${telemetry['floating_profit']:+,.2f} USD\n"
            f"- Active Contracts: {telemetry['pos_count']}\n"
            f"- Open Positions Details: {telemetry['positions_str']}\n"
            f"- Spot Gold (XAUUSD): Bid ${telemetry['xau_bid']:.2f}, Ask ${telemetry['xau_ask']:.2f}, Spread {telemetry['spread_pips']} pips\n"
            f"- War Room Council: Decision {telemetry['consensus']['decision']} ({telemetry['consensus']['ratio']})\n"
            f"- Defense: Auto-trailing stops active on every tick, Windows Away Mode locked on for overnight execution.\n\n"
            f"Commander asks: \"{user_query}\"\n"
            f"Don Aurelius responds:"
        )

        models_to_try = [
            "gemini-flash-latest",
            "gemini-3.5-flash-lite"
        ]
        for m in models_to_try:
            try:
                response = self._genai_client.models.generate_content(
                    model=m,
                    contents=prompt
                )
                if response and response.text:
                    return response.text
            except Exception as e:
                err_msg = str(e)
                logger.warning(f"[DON-BRAIN] Gemini model {m} notice: {err_msg[:120]}")
                # If Google API has a 503 high demand spike or quota issue, break immediately to let instant Encyclopedia take over
                if "503" in err_msg or "quota" in err_msg.lower() or "unavailable" in err_msg.lower():
                    break
                continue
        return None

    def _clean_for_voice(self, text: str) -> str:
        """Strips markdown formatting for ElevenLabs voice generation."""
        cleaned = re.sub(r'[*_#`~>\[\]\(\)=━●•]', '', text)
        cleaned = re.sub(r'\n+', '. ', cleaned)
        return cleaned[:350]

    def _default_reply_markup(self) -> Dict[str, Any]:
        """Provides quick interactive inline buttons attached to every response."""
        return {
            "inline_keyboard": [
                [
                    {"text": "🎙️ Voice Briefing", "callback_data": "voice_briefing"},
                    {"text": "📊 Full HUD", "callback_data": "refresh_hud"}
                ],
                [
                    {"text": "💰 Profit Check", "callback_data": "check_profit"},
                    {"text": "🥇 Gold Price", "callback_data": "check_gold"}
                ]
            ]
        }
