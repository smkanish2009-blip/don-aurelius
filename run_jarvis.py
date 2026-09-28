"""
JARVIS Autonomous Algorithmic Matrix - Master CLI Entrypoint.
Run this script to initialize the JARVIS trading system with intermarket filters,
dynamic auto-trailing stops, ElevenLabs voice synthesis, and interactive Telegram HUD.
"""

import sys
import logging
from config.credentials import load_credentials
from engine.orchestrator import JarvisOrchestrator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s]: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("logs/jarvis_execution.log", encoding="utf-8")
    ]
)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BANNER = r"""
================================================================================
     _   _    ____ __     __ ___  ____     MARK-VII QUANTUM
    | | / \  |  _ \\ \   / /|_ _// ___|    AUTONOMOUS ALGORITHMIC MATRIX
 _  | |/ _ \ | |_) |\ \ / /  | | \___ \    ------------------------------
| |_| / ___ \|  _ <  \ V /   | |  ___) |   XAUUSD GOLD TRADING ALGO
 \___/_/   \_|_| \_\  \_/   |___||____/    ELEVENLABS VOICE & TELEGRAM HUD
                                           INTERMARKET CO-INTEGRATION RADAR
================================================================================
"""


def main():
    print(BANNER)
    creds = load_credentials()

    orchestrator = JarvisOrchestrator(
        symbol="XAUUSD",
        magic=20260926,
        telegram_token=creds.TELEGRAM_BOT_TOKEN,
        telegram_chat_id=creds.TELEGRAM_CHAT_ID,
        elevenlabs_key=creds.ELEVENLABS_API_KEY,
        risk_pct=0.01,
        trail_activation_pips=25.0,
        trail_step_pips=8.0
    )

    try:
        orchestrator.run_loop()
    except KeyboardInterrupt:
        print("\n[!] JARVIS Standby Protocol Engaged. Shutting down gracefully...")
        orchestrator.hud.stop()


if __name__ == "__main__":
    main()
