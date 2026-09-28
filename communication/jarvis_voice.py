"""
JARVIS ElevenLabs Voice Synthesis Engine.
Interfaces directly with ElevenLabs API to transform telemetry stats
into custom-voiced audio update briefings.
"""

import io
import wave
import struct
import math
import logging
import requests
from typing import Optional

logger = logging.getLogger("JarvisVoice")


class JarvisVoiceCore:
    """
    Interfaces directly with ElevenLabs API to transform telemetry stats
    into custom-voiced audio update briefings.
    """

    def __init__(self, api_key: Optional[str] = None, voice_id: str = "nPczCjzI2devNBz1zQrb"):
        # Default voice: "Brian - Deep & Resonant" (nPczCjzI2devNBz1zQrb)
        self.api_key = api_key or ""
        self.voice_id = voice_id or "nPczCjzI2devNBz1zQrb"
        self.default_fallback_voice = "nPczCjzI2devNBz1zQrb"

    def compile_vocal_briefing(self, narrative_text: str) -> Optional[io.BytesIO]:
        """
        Converts textual trading reports into high-fidelity voice packets.
        If custom voice encounters tier limitations (e.g. 402 on free tier),
        automatically falls back to high-grade premade Adam voice.
        """
        if self.api_key and len(self.api_key) > 5 and not self.api_key.startswith("your_"):
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": self.api_key
            }
            data = {
                "text": narrative_text,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {
                    "stability": 0.65,
                    "similarity_boost": 0.85
                }
            }

            # Attempt 1: Configured voice
            voices_to_try = [self.voice_id]
            if self.voice_id != self.default_fallback_voice:
                voices_to_try.append(self.default_fallback_voice)

            for vid in voices_to_try:
                try:
                    url = f"https://api.elevenlabs.io/v1/text-to-speech/{vid}"
                    response = requests.post(url, json=data, headers=headers, timeout=15)
                    if response.status_code == 200 and len(response.content) > 100:
                        stream = io.BytesIO(response.content)
                        stream.name = "don_aurelius_briefing.mp3"
                        logger.info(f"[DON-AURELIUS-VOICE] ElevenLabs briefing generated successfully with voice: {vid}")
                        return stream
                    else:
                        logger.warning(f"[DON-AURELIUS-VOICE] ElevenLabs voice {vid} returned {response.status_code}: {response.text[:120]}")
                except Exception as e:
                    logger.warning(f"[DON-AURELIUS-VOICE] ElevenLabs network error for {vid}: {str(e)}")

        # Fallback generator: creates valid audio container for Telegram voice message transmission
        return self._generate_fallback_audio(narrative_text)

    def _generate_fallback_audio(self, text: str) -> io.BytesIO:
        """
        Synthesizes a clean audio chime packet (WAV formatted) so Telegram voice
        transmission never fails even when API keys are not supplied.
        """
        sample_rate = 16000
        duration_sec = 1.5
        num_samples = int(sample_rate * duration_sec)

        buf = io.BytesIO()
        with wave.open(buf, 'wb') as wav:
            wav.setnchannels(1)  # Mono
            wav.setsampwidth(2)  # 16-bit
            wav.setframerate(sample_rate)

            # Generate pleasant JARVIS acoustic harmonic chime (440Hz -> 880Hz)
            data = bytearray()
            for i in range(num_samples):
                t = i / sample_rate
                freq = 440.0 + (440.0 * (i / num_samples))
                amplitude = 12000.0 * math.exp(-2.5 * t)  # Exponential decay
                sample = int(amplitude * math.sin(2.0 * math.pi * freq * t))
                data.extend(struct.pack('<h', max(-32767, min(32767, sample))))

            wav.writeframes(data)

        buf.seek(0)
        buf.name = "jarvis_briefing.wav"
        return buf

    def generate_status_narrative(
        self,
        equity: float,
        open_trades: int = 0,
        xau_trend: str = "BULLISH",
        dxy_trend: str = "BEARISH",
        decision: str = "HOLD"
    ) -> str:
        """Generates authentic Don Aurelius AUREUS royal syndicate vocal briefings."""
        return (
            f"Greetings Boss. Don Aurelius AUREUS Core is fully operational and guarding your empire. "
            f"Total treasury equity stands at {int(equity):,} dollars. "
            f"Active market contracts: {open_trades}. "
            f"Intermarket telemetry confirms Gold flow is {xau_trend}, while the US Dollar Index is {dxy_trend}. "
            f"The Sovereign Council consensus is {decision}. Sleep in peace, Boss. The Syndicate never sleeps."
        )

    def generate_trade_narrative(
        self,
        direction: str,
        lots: float,
        price: float,
        sl: float,
        tp: float
    ) -> str:
        """Generates Don Aurelius order deployment announcement."""
        return (
            f"Syndicate Execution, Boss. Don Aurelius has authorized an aggressive {direction} strike on Gold. "
            f"Volume: {lots:.2f} lots at price {price:.2f}. "
            f"Ironclad Stop Loss secured at {sl:.2f}. Imperial Take Profit locked at {tp:.2f}."
        )

    def generate_liquidation_narrative(self, count: int) -> str:
        """Generates emergency kill announcement."""
        return (
            f"Clean Slate Protocol executed, Boss. The syndicate has liquidated all {count} open positions. "
            f"The treasury is flattened and secured."
        )
