"""
Don Aurelius WhatsApp Sovereign Dispatcher & Webhook Engine.
Provides complete Meta WhatsApp Business Cloud API registration & webhook processing,
alongside instant Twilio WhatsApp fallback and real-time Telegram notification routing.

Founder: SM.KANISH (Founder & Chief Strategic AI Architect)
Direct Contact: +91 93424 10313
Telegram Bot: @DonAurelius_AI_bot (Chat ID: 8775976760)
"""

import os
import json
import logging
import requests
from typing import Dict, Any, Optional
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("WhatsAppSovereignBot")

# ==============================================================================
# Configuration & Credentials
# ==============================================================================
WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "100657286438921")
WHATSAPP_BUSINESS_ACCOUNT_ID = os.getenv("WHATSAPP_WABA_ID", "100657286438920")
WHATSAPP_ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN", "")
WHATSAPP_VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "DON_AURELIUS_VERIFY_TOKEN_2026")
WHATSAPP_API_VERSION = "v21.0"
WHATSAPP_API_BASE = f"https://graph.facebook.com/{WHATSAPP_API_VERSION}"

# Twilio Fallback Configuration
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_WHATSAPP_FROM = os.getenv("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886")

# Real-time Founder Telegram Bridge
FOUNDER_TELEGRAM_TOKEN = "8612051079:AAFH-8pdVmlr0B3Xt6boAu_30NJ62d4OeXU"
FOUNDER_TELEGRAM_CHAT_ID = "8775976760"
FOUNDER_WHATSAPP_DIRECT = "919342410313"


class WhatsAppBot:
    """
    WhatsApp Business Cloud API Client & Autonomous Responder.
    Handles phone registration, message dispatch, interactive components,
    and forwards incoming buyer queries directly to Founder SM.KANISH.
    """

    def __init__(self, token: Optional[str] = None, phone_id: Optional[str] = None):
        self.token = token or WHATSAPP_ACCESS_TOKEN
        self.phone_id = phone_id or WHATSAPP_PHONE_NUMBER_ID
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    def register_phone(self, pin: str = "123456") -> Dict[str, Any]:
        """
        Registers the Business Phone Number with Meta WhatsApp Cloud API.
        Must be invoked after setting up the two-step verification PIN in Meta Business Manager.
        """
        url = f"{WHATSAPP_API_BASE}/{self.phone_id}/register"
        payload = {
            "messaging_product": "whatsapp",
            "pin": pin
        }
        logger.info(f"Registering phone ID {self.phone_id} with Meta WhatsApp Cloud API...")
        try:
            res = requests.post(url, headers=self.headers, json=payload, timeout=15)
            data = res.json()
            logger.info(f"Registration response: {data}")
            return data
        except Exception as e:
            logger.error(f"Failed to register phone: {e}")
            return {"error": str(e)}

    def send_text_message(self, recipient_phone: str, message: str) -> Dict[str, Any]:
        """
        Sends an automated text message via WhatsApp Business Cloud API.
        Recipient must be in international format without '+' or spaces (e.g. 919342410313).
        """
        clean_phone = recipient_phone.replace("+", "").replace(" ", "").replace("-", "")
        url = f"{WHATSAPP_API_BASE}/{self.phone_id}/messages"
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": clean_phone,
            "type": "text",
            "text": {
                "preview_url": True,
                "body": message
            }
        }
        try:
            res = requests.post(url, headers=self.headers, json=payload, timeout=15)
            return res.json()
        except Exception as e:
            logger.error(f"WhatsApp Cloud API send failed: {e}. Trying Twilio fallback...")
            return self._send_twilio_fallback(clean_phone, message)

    def send_interactive_menu(self, recipient_phone: str) -> Dict[str, Any]:
        """
        Sends an interactive quick-reply button menu for fast buyer navigation.
        """
        clean_phone = recipient_phone.replace("+", "").replace(" ", "").replace("-", "")
        url = f"{WHATSAPP_API_BASE}/{self.phone_id}/messages"
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": clean_phone,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "header": {
                    "type": "text",
                    "text": "⚜️ DON AURELIUS • QUANTITATIVE AI"
                },
                "body": {
                    "text": (
                        "Welcome to Don Aurelius Sovereign Desk.\n\n"
                        "Spot Gold (XAUUSD) Quantitative Execution Engine on MetaTrader 5.\n"
                        "Founder: SM.KANISH\n\n"
                        "Select an option below to proceed immediately:"
                    )
                },
                "footer": {
                    "text": "Institutional Risk Management • Zero Curve Fitting"
                },
                "action": {
                    "buttons": [
                        {
                            "type": "reply",
                            "reply": {
                                "id": "btn_price",
                                "title": "⚡ Price List & Plans"
                            }
                        },
                        {
                            "type": "reply",
                            "reply": {
                                "id": "btn_buy",
                                "title": "💳 Buy License (USDT)"
                            }
                        },
                        {
                            "type": "reply",
                            "reply": {
                                "id": "btn_founder",
                                "title": "👤 Talk to Founder"
                            }
                        }
                    ]
                }
            }
        }
        try:
            res = requests.post(url, headers=self.headers, json=payload, timeout=15)
            return res.json()
        except Exception as e:
            logger.error(f"Failed to send interactive WhatsApp menu: {e}")
            return {"error": str(e)}

    def _send_twilio_fallback(self, to_phone: str, message: str) -> Dict[str, Any]:
        """Twilio WhatsApp REST API fallback."""
        if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
            return {"status": "error", "message": "Twilio fallback credentials not configured."}
        url = f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_ACCOUNT_SID}/Messages.json"
        auth = (TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        payload = {
            "From": TWILIO_WHATSAPP_FROM,
            "To": f"whatsapp:+{to_phone}",
            "Body": message
        }
        try:
            res = requests.post(url, auth=auth, data=payload, timeout=15)
            return res.json()
        except Exception as e:
            logger.error(f"Twilio WhatsApp fallback failed: {e}")
            return {"status": "error", "error": str(e)}

    def forward_lead_to_telegram(self, sender_phone: str, text: str, name: str = "Prospective Client"):
        """
        Instantly bridges incoming WhatsApp messages to Founder Kanish's Telegram War Room bot.
        """
        tele_url = f"https://api.telegram.org/bot{FOUNDER_TELEGRAM_TOKEN}/sendMessage"
        tele_msg = (
            "🟢 <b>NEW WHATSAPP INQUIRY RECEIVED!</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 <b>Client:</b> {name}\n"
            f"📱 <b>WhatsApp:</b> <code>+{sender_phone}</code>\n"
            f"💬 <b>Message:</b>\n<i>\"{text}\"</i>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            f"👉 <a href=\"https://wa.me/{sender_phone}\">Click to Reply on WhatsApp</a>"
        )
        try:
            requests.post(tele_url, json={
                "chat_id": FOUNDER_TELEGRAM_CHAT_ID,
                "text": tele_msg,
                "parse_mode": "HTML"
            }, timeout=10)
            logger.info(f"Forwarded WhatsApp lead from {sender_phone} to Founder Telegram.")
        except Exception as e:
            logger.error(f"Failed to bridge lead to Telegram: {e}")

    def process_incoming_message(self, message_data: Dict[str, Any]):
        """
        Parses incoming Meta WhatsApp Cloud API Webhook payload and responds.
        """
        try:
            entry = message_data.get("entry", [{}])[0]
            changes = entry.get("changes", [{}])[0]
            value = changes.get("value", {})
            messages = value.get("messages", [])
            contacts = value.get("contacts", [])

            if not messages:
                return

            msg = messages[0]
            sender_id = msg.get("from")
            contact_name = contacts[0].get("profile", {}).get("name", "Prospective Client") if contacts else "Client"

            user_text = ""
            if msg.get("type") == "text":
                user_text = msg.get("text", {}).get("body", "").strip()
            elif msg.get("type") == "interactive":
                btn_reply = msg.get("interactive", {}).get("button_reply", {})
                user_text = btn_reply.get("id", "")

            logger.info(f"Received WhatsApp from {sender_id} ({contact_name}): {user_text}")

            # Forward query to Founder Telegram immediately
            self.forward_lead_to_telegram(sender_id, user_text, contact_name)

            # Automated Sovereign Responses
            low_text = user_text.lower()
            if "price" in low_text or "btn_price" in low_text or "cost" in low_text or "quote" in low_text:
                resp = (
                    "⚡ *DON AURELIUS INSTITUTIONAL PRICING*\n"
                    "━━━━━━━━━━━━━━━━━━━━━\n"
                    "• *Quarterly Tactical Pass:* $499 (3 Months MT5 Access)\n"
                    "• *Annual Sovereign Pass:* $1,499 (Full Year + VIP Radar Desk)\n"
                    "• *Lifetime Institutional Monolith:* $3,999 (Perpetual Updates + Source Code Access)\n\n"
                    "💳 *Crypto TRC-20 & Instant USDT Settlement:* Available.\n"
                    "🌐 Visit our verified portal: https://donaurelius.ai/checkout.html\n\n"
                    "Reply *BUY* to get direct TRC-20 payment instructions."
                )
                self.send_text_message(sender_id, resp)

            elif "buy" in low_text or "btn_buy" in low_text or "pay" in low_text or "tether" in low_text:
                resp = (
                    "💳 *INSTANT LICENSE CHECKOUT*\n"
                    "━━━━━━━━━━━━━━━━━━━━━\n"
                    "Official USDT TRC-20 Vault:\n"
                    "`TFdDBCaBEbvyT3F8ZQLdb2ZmZtcksawWbs`\n\n"
                    "After deposit, send your Transaction Hash (TxID) and MetaTrader 5 Account Number here or visit:\n"
                    "👉 https://donaurelius.ai/checkout.html\n\n"
                    "Your cryptographic license key will be generated instantly."
                )
                self.send_text_message(sender_id, resp)

            elif "founder" in low_text or "btn_founder" in low_text or "kanish" in low_text or "call" in low_text:
                resp = (
                    "👤 *DIRECT SOVEREIGN FOUNDER DESK*\n"
                    "━━━━━━━━━━━━━━━━━━━━━\n"
                    "*SM.KANISH* (Founder & Chief Strategic AI Architect)\n"
                    "📞 Direct Call: +91 93424 10313\n"
                    "💬 WhatsApp: https://wa.me/919342410313\n"
                    "✉️ Email: contact@donaurelius.ai\n"
                    "🏛️ Global HQ: 88 Wood Street, Financial District, London, UK\n\n"
                    "Founder Kanish has been notified on Telegram and will review your inquiry shortly."
                )
                self.send_text_message(sender_id, resp)

            else:
                self.send_interactive_menu(sender_id)

        except Exception as e:
            logger.error(f"Error handling WhatsApp incoming message: {e}")


# ==============================================================================
# Lightweight HTTP Webhook Server for Meta Cloud API Verification
# ==============================================================================
class WhatsAppWebhookHandler(BaseHTTPRequestHandler):
    bot = WhatsAppBot()

    def do_GET(self):
        """Handles Meta Cloud API Webhook Verification Challenge."""
        from urllib.parse import urlparse, parse_qs
        parsed_url = urlparse(self.path)
        params = parse_qs(parsed_url.query)

        mode = params.get("hub.mode", [""])[0]
        token = params.get("hub.verify_token", [""])[0]
        challenge = params.get("hub.challenge", [""])[0]

        if mode == "subscribe" and token == WHATSAPP_VERIFY_TOKEN:
            logger.info("WhatsApp Webhook challenge verified successfully by Meta!")
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(challenge.encode("utf-8"))
        else:
            logger.warning(f"Failed verification attempt: token={token}")
            self.send_response(403)
            self.end_headers()

    def do_POST(self):
        """Handles incoming messages and status callbacks from Meta."""
        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length)

        try:
            payload = json.loads(post_data.decode("utf-8"))
            threading.Thread(target=self.bot.process_incoming_message, args=(payload,)).start()
        except Exception as e:
            logger.error(f"Error processing webhook POST: {e}")

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"status": "received"}).encode("utf-8"))


def run_webhook_server(port: int = 8085):
    """Launches local webhook server for Meta Cloud API integration."""
    server_address = ("", port)
    httpd = HTTPServer(server_address, WhatsAppWebhookHandler)
    logger.info(f"Don Aurelius WhatsApp Webhook Server listening on port {port}...")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("Stopping WhatsApp webhook server.")
        httpd.server_close()


if __name__ == "__main__":
    import sys
    bot = WhatsAppBot()

    if len(sys.argv) > 1 and sys.argv[1] == "register":
        pin = sys.argv[2] if len(sys.argv) > 2 else "123456"
        print("Registering Phone with Meta Cloud API...")
        res = bot.register_phone(pin)
        print("Result:", res)
    elif len(sys.argv) > 1 and sys.argv[1] == "test-send":
        target = sys.argv[2] if len(sys.argv) > 2 else FOUNDER_WHATSAPP_DIRECT
        msg = sys.argv[3] if len(sys.argv) > 3 else "Don Aurelius WhatsApp Sovereign Engine Active."
        print(f"Sending test WhatsApp message to {target}...")
        res = bot.send_text_message(target, msg)
        print("Result:", res)
    elif len(sys.argv) > 1 and sys.argv[1] == "test-lead":
        print("Simulating inbound lead bridge to Telegram...")
        bot.forward_lead_to_telegram(FOUNDER_WHATSAPP_DIRECT, "Inquiry from website: Want Lifetime Monolith pass.", "VIP Buyer")
        print("Dispatched to Founder Telegram!")
    else:
        print("Starting WhatsApp Webhook listener on port 8085...")
        run_webhook_server()
