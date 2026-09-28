"""
Test Suite for DON AURELIUS Conversational AI Brain & Telegram HUD Integration.
"""

import sys
import os

# Ensure UTF-8 output encoding for emojis on Windows console
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Add root directory to sys.path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from engine.mt5_execution import MT5ExecutionBridge
from communication.don_aurelius_brain import DonAureliusBrain
from communication.telegram_hud import JarvisTelegramHUD

def test_conversational_brain():
    print("[*] Initializing MT5 Bridge...")
    bridge = MT5ExecutionBridge(symbol="XAUUSD")
    bridge.connect()

    print("[*] Initializing DonAureliusBrain...")
    brain = DonAureliusBrain(bridge=bridge)

    queries = [
        "what is our profit and balance?",
        "how is gold looking today?",
        "do we have any active trades open?",
        "should we buy or sell right now?",
        "can i go to sleep now with laptop closed for school?",
        "are we safe from liquidation?",
        "who are you bro?",
        "send me a voice note",
        "thanks for the great work"
    ]

    for q in queries:
        print(f"\n==================================================")
        print(f"[USER ASKS]: \"{q}\"")
        res = brain.process_query(q, "8775976760")
        print(f"[ACTION]: {res.get('action_taken')}")
        print(f"[SEND_VOICE]: {res.get('send_voice')}")
        if res.get('send_voice'):
            print(f"[VOICE SCRIPT]: {res.get('voice_text')}")
        print(f"[RESPONSE TEXT]:\n{res.get('text')[:200]}...")

    print("\n[*] Initializing JarvisTelegramHUD...")
    hud = JarvisTelegramHUD(
        token="8612051079:AAFx7jK-Duaxn4bRxqeNeQ2EZhvwrxON61c",
        execution_bridge=bridge,
        chat_id="8775976760"
    )
    assert hasattr(hud, "brain"), "HUD must have brain instance"
    print("[+] JarvisTelegramHUD successfully initialized with DonAureliusBrain!")

if __name__ == "__main__":
    test_conversational_brain()
    print("\n[SUCCESS] All conversational brain tests passed!")
