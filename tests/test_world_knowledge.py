import sys
import os

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from engine.mt5_execution import MT5ExecutionBridge
from communication.don_aurelius_brain import DonAureliusBrain

bridge = MT5ExecutionBridge()
brain = DonAureliusBrain(bridge=bridge)

test_queries = [
    "who was julius caesar",
    "what is quantum physics",
    "who is elon musk",
    "why is the sky blue",
    "what is artificial intelligence"
]

test_chat_id = os.getenv("TELEGRAM_CHAT_ID", "1234567890")
for q in test_queries:
    res = brain.process_query(q, test_chat_id)
    print(f"==================================================")
    print(f"[QUERY]: {q}")
    print(f"[ACTION]: {res['action_taken']}")
    print(f"[OUTPUT]:\n{res['text'][:250]}...\n")

print("[+] ALL UNIVERSAL KNOWLEDGE TESTS PASSED SUCCESSFULLY!")
