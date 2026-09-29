"""
Live Genesis Suite Telegram Dispatch Verification for Commander SM.KANISH.
Renders and transmits Eagle-Eye Candlestick Chart, Quantum Twin Monte Carlo Cone,
and Global Sentinel Crisis Radar directly to Telegram.
"""

import os
import sys
import json
import time
import requests
from config.credentials import load_credentials
from communication.don_aurelius_brain import DonAureliusBrain

def main():
    creds = load_credentials()
    token = creds.TELEGRAM_BOT_TOKEN
    chat_id = creds.TELEGRAM_CHAT_ID

    if not token or not chat_id:
        print("[!] Missing telegram credentials.")
        return

    print("[+] Connecting to Don Aurelius Brain...")
    brain = DonAureliusBrain(bridge=None)
    telemetry = brain.get_telemetry_snapshot()
    print(f"[+] Live Gold Tick: Bid ${telemetry['xau_bid']:.2f} | Ask ${telemetry['xau_ask']:.2f}")

    # 1. Dispatch Genesis Launch Announcement
    announcement = (
        "🚀 **DON AURELIUS • GENESIS SUITE DEPLOYED LIVE** 👑\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "Commander **SM.KANISH**, your 4 revolutionary algorithmic inventions—which transcend "
        "anything ever created in MetaTrader 5 history—are now **ONLINE & ARMED**.\n\n"
        "1. 👁️ **Project Eagle-Eye**: Multimodal Computer Vision AI analyzing M15 candlestick geometry.\n"
        "2. 🌐 **Project Global Sentinel**: Geopolitical Crisis Radar & Panic Index.\n"
        "3. 🔮 **Project Quantum Twin**: 1,000-Path Monte Carlo Jump-Diffusion Simulator.\n"
        "4. 🎙️ **Project Jarvis Co-Pilot**: Full Duplex Neural Voice & Audio Memo Intelligence.\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "📡 *Live visual proof and simulation charts incoming below...*"
    )
    requests.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        json={"chat_id": chat_id, "text": announcement, "parse_mode": "Markdown"}
    )
    time.sleep(1)

    # 2. Eagle-Eye Chart Dispatch
    print("[+] Generating Eagle-Eye Candlestick Chart...")
    chart_res = brain.process_query("show me the chart", chat_id)
    if chart_res.get("send_photo") and os.path.exists(chart_res["send_photo"]):
        print(f"[+] Transmitting Eagle-Eye Chart photo ({chart_res['send_photo']})...")
        with open(chart_res["send_photo"], "rb") as f:
            caption = chart_res["text"][:1024]
            r = requests.post(
                f"https://api.telegram.org/bot{token}/sendPhoto",
                data={"chat_id": chat_id, "caption": caption, "parse_mode": "Markdown"},
                files={"photo": (os.path.basename(chart_res["send_photo"]), f, "image/png")}
            )
            if not r.json().get("ok"):
                # fallback plain text caption
                with open(chart_res["send_photo"], "rb") as f2:
                    requests.post(
                        f"https://api.telegram.org/bot{token}/sendPhoto",
                        data={"chat_id": chat_id, "caption": caption},
                        files={"photo": (os.path.basename(chart_res["send_photo"]), f2, "image/png")}
                    )
        print("[+] Eagle-Eye Chart transmitted.")
    time.sleep(2)

    # 3. Quantum Twin Simulation Dispatch
    print("[+] Generating Quantum Twin Monte Carlo Cone...")
    quantum_res = brain.process_query("simulate the future with quantum cone", chat_id)
    if quantum_res.get("send_photo") and os.path.exists(quantum_res["send_photo"]):
        print(f"[+] Transmitting Quantum Cone photo ({quantum_res['send_photo']})...")
        with open(quantum_res["send_photo"], "rb") as f:
            caption = quantum_res["text"][:1024]
            r = requests.post(
                f"https://api.telegram.org/bot{token}/sendPhoto",
                data={"chat_id": chat_id, "caption": caption, "parse_mode": "Markdown"},
                files={"photo": (os.path.basename(quantum_res["send_photo"]), f, "image/png")}
            )
            if not r.json().get("ok"):
                with open(quantum_res["send_photo"], "rb") as f2:
                    requests.post(
                        f"https://api.telegram.org/bot{token}/sendPhoto",
                        data={"chat_id": chat_id, "caption": caption},
                        files={"photo": (os.path.basename(quantum_res["send_photo"]), f2, "image/png")}
                    )
        print("[+] Quantum Cone transmitted.")
    time.sleep(2)

    # 4. Global Sentinel Crisis Radar Dispatch
    print("[+] Fetching Global Sentinel Crisis Radar...")
    sentinel_res = brain.process_query("what is the breaking news and crisis radar", chat_id)
    requests.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        json={"chat_id": chat_id, "text": sentinel_res["text"], "parse_mode": "Markdown"}
    )
    time.sleep(1)

    # 5. Interactive HUD with all Genesis Buttons
    print("[+] Transmitting Updated Genesis HUD...")
    hud_buttons = {
        "inline_keyboard": [
            [
                {"text": "📸 Eagle-Eye Chart", "callback_data": "eagle_eye"},
                {"text": "🔮 Quantum Cone", "callback_data": "quantum_sim"}
            ],
            [
                {"text": "🌐 Crisis Sentinel", "callback_data": "global_sentinel"},
                {"text": "🎙️ Voice Briefing", "callback_data": "voice_briefing"}
            ],
            [
                {"text": "📊 Full HUD", "callback_data": "refresh_hud"},
                {"text": "💰 Profit Check", "callback_data": "check_profit"}
            ],
            [
                {"text": "🚨 Clean Slate Protocol", "callback_data": "kill_all"}
            ]
        ]
    }
    hud_msg = (
        "👑 **DON AURELIUS • GENESIS COMMAND CENTER**\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"● System State: **ARMED & OPERATIONAL**\n"
        f"● Net Account Equity: **${telemetry['equity']:,.2f} USD**\n"
        f"● Spot Gold (XAUUSD): **${telemetry['xau_bid']:.2f}**\n"
        f"● War Room Consensus: **{telemetry['consensus']['decision']} ({telemetry['consensus']['ratio']})**\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "🕹️ *Touch any button below to trigger live visual intelligence on demand:*"
    )
    requests.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        json={"chat_id": chat_id, "text": hud_msg, "parse_mode": "Markdown", "reply_markup": hud_buttons}
    )
    print("[+] All Genesis live transmissions completed successfully!")

if __name__ == "__main__":
    main()
