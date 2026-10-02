"""
Credentials & Environment configuration.
Reads broker details, Telegram tokens, and Gemini API keys securely from environment variables.
"""

import os
from dataclasses import dataclass
from core.vault_manager import VaultManager


@dataclass
class Credentials:
    # MetaTrader 5 account credentials
    MT5_LOGIN: int = int(os.getenv("MT5_LOGIN", "0"))
    MT5_PASSWORD: str = os.getenv("MT5_PASSWORD", "")
    MT5_SERVER: str = os.getenv("MT5_SERVER", "")
    MT5_PATH: str = os.getenv("MT5_PATH", "")  # Optional: path to terminal64.exe

    # Telegram alerts & remote control
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID: str = os.getenv("TELEGRAM_CHAT_ID", "")

    # Google Gemini AI API Key
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

    # ElevenLabs Voice Synthesis API
    ELEVENLABS_API_KEY: str = os.getenv("ELEVENLABS_API_KEY", "")
    ELEVENLABS_VOICE_ID: str = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")

    # Supabase Cloud Database & Realtime Telemetry
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_PUBLISHABLE_KEY: str = os.getenv("SUPABASE_PUBLISHABLE_KEY", "")
    SUPABASE_SECRET_KEY: str = os.getenv("SUPABASE_SECRET_KEY", "")


def load_credentials() -> Credentials:
    # Auto-load .env file if present
    env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
    if os.path.exists(env_file):
        try:
            with open(env_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        k = k.strip()
                        v = v.strip().strip("'\"")
                        if k and k not in os.environ:
                            os.environ[k] = v
        except Exception:
            pass

    vault = VaultManager()
    vault_data = vault.load_and_decrypt()

    login = int(os.getenv("MT5_LOGIN", str(vault_data.get("MT5_LOGIN", 0) if vault_data else 0)))
    password = os.getenv("MT5_PASSWORD", vault_data.get("MT5_PASSWORD", "") if vault_data else "")
    server = os.getenv("MT5_SERVER", vault_data.get("MT5_SERVER", "") if vault_data else "")
    path = os.getenv("MT5_PATH", vault_data.get("MT5_PATH", "") if vault_data else "")
    telegram_token = os.getenv("TELEGRAM_BOT_TOKEN", vault_data.get("TELEGRAM_BOT_TOKEN", "") if vault_data else "")
    telegram_chat = os.getenv("TELEGRAM_CHAT_ID", vault_data.get("TELEGRAM_CHAT_ID", "") if vault_data else "")
    gemini_key = os.getenv("GEMINI_API_KEY", vault_data.get("GEMINI_API_KEY", "") if vault_data else "")
    elevenlabs_key = os.getenv("ELEVENLABS_API_KEY", vault_data.get("ELEVENLABS_API_KEY", "") if vault_data else "")
    elevenlabs_voice = os.getenv("ELEVENLABS_VOICE_ID", vault_data.get("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM") if vault_data else "21m00Tcm4TlvDq8ikWAM")
    supabase_url = os.getenv("SUPABASE_URL", "")
    supabase_pub = os.getenv("SUPABASE_PUBLISHABLE_KEY", "")
    supabase_sec = os.getenv("SUPABASE_SECRET_KEY", "")

    if not vault_data and (login or password or telegram_token or gemini_key or elevenlabs_key):
        vault.encrypt_and_save({
            "MT5_LOGIN": login,
            "MT5_PASSWORD": password,
            "MT5_SERVER": server,
            "MT5_PATH": path,
            "TELEGRAM_BOT_TOKEN": telegram_token,
            "TELEGRAM_CHAT_ID": telegram_chat,
            "GEMINI_API_KEY": gemini_key,
            "ELEVENLABS_API_KEY": elevenlabs_key,
            "ELEVENLABS_VOICE_ID": elevenlabs_voice,
        })

    return Credentials(
        MT5_LOGIN=login,
        MT5_PASSWORD=password,
        MT5_SERVER=server,
        MT5_PATH=path,
        TELEGRAM_BOT_TOKEN=telegram_token,
        TELEGRAM_CHAT_ID=telegram_chat,
        GEMINI_API_KEY=gemini_key,
        ELEVENLABS_API_KEY=elevenlabs_key,
        ELEVENLABS_VOICE_ID=elevenlabs_voice,
        SUPABASE_URL=supabase_url,
        SUPABASE_PUBLISHABLE_KEY=supabase_pub,
        SUPABASE_SECRET_KEY=supabase_sec
    )



credentials = load_credentials()
