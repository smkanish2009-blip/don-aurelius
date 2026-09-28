"""
JARVIS & DON AURELIUS Dual Voice Synthesis Engine.
Combines ElevenLabs API and Microsoft Edge Neural High-Definition TTS
to transform telemetry stats, alerts, and AI responses into deep, authoritative vocal briefings.
"""

import io
import re
import wave
import struct
import math
import logging
import asyncio
import concurrent.futures
import requests
from typing import Optional

logger = logging.getLogger("JarvisVoice")

try:
    import edge_tts
    HAS_EDGE_TTS = True
except ImportError:
    HAS_EDGE_TTS = False


class JarvisVoiceCore:
    """
    Dual-Core Voice Engine for DON AURELIUS.
    Primary: Microsoft Edge Neural TTS (Deep, authoritative, zero quota limits, 100% free)
    Secondary: ElevenLabs API (Custom cloned voices when available and within tier quota)
    Fallback: Acoustic harmonic chime
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        voice_id: str = "nPczCjzI2devNBz1zQrb",
        neural_voice: str = "en-US-ChristopherNeural"
    ):
        self.api_key = api_key or ""
        self.voice_id = voice_id or "nPczCjzI2devNBz1zQrb"
        self.default_fallback_voice = "nPczCjzI2devNBz1zQrb"
        self.neural_voice = neural_voice  # Deep, resonant, commanding General/AI voice

    def _clean_speech_text(self, text: str) -> str:
        """Sanitizes Markdown, emojis, and acronyms for natural human speech delivery."""
        if not text:
            return ""
        s = text
        # Pronunciation replacements
        s = re.sub(r'\bXAUUSD\b', 'Gold spot', s, flags=re.IGNORECASE)
        s = re.sub(r'\bUS10Y\b', 'ten year treasury yield', s, flags=re.IGNORECASE)
        s = re.sub(r'\bDXY\b', 'US Dollar Index', s, flags=re.IGNORECASE)
        s = re.sub(r'\bP&L\b', 'profit and loss', s, flags=re.IGNORECASE)
        s = re.sub(r'\bMT5\b', 'MetaTrader 5', s, flags=re.IGNORECASE)
        s = re.sub(r'\bSL\b', 'Stop Loss', s)
        s = re.sub(r'\bTP\b', 'Take Profit', s)
        # Strip markdown syntax and special characters
        s = re.sub(r'[*_#`~>\[\]\(\)=━●•|/]', ' ', s)
        # Strip emojis / non-ascii characters that might confuse TTS
        s = re.sub(r'[^\x00-\x7F]+', ' ', s)
        # Collapse multiple spaces and newlines
        s = re.sub(r'\s+', ' ', s).strip()
        return s

    def _synthesize_edge_tts(self, narrative_text: str) -> Optional[io.BytesIO]:
        """Synthesizes high-fidelity studio audio via Microsoft Edge Neural TTS."""
        if not HAS_EDGE_TTS:
            return None

        clean_text = self._clean_speech_text(narrative_text)
        if not clean_text:
            return None

        # Truncate to reasonable speech length (~45 seconds max for snappy messaging)
        if len(clean_text) > 600:
            clean_text = clean_text[:600].rsplit('.', 1)[0] + "."

        async def _run_edge():
            comm = edge_tts.Communicate(clean_text, self.neural_voice)
            buf = io.BytesIO()
            async for chunk in comm.stream():
                if chunk["type"] == "audio":
                    buf.write(chunk["data"])
            buf.seek(0)
            buf.name = "don_aurelius_briefing.mp3"
            return buf

        try:
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    with concurrent.futures.ThreadPoolExecutor() as pool:
                        return pool.submit(lambda: asyncio.run(_run_edge())).result(timeout=20)
                else:
                    return loop.run_until_complete(_run_edge())
            except RuntimeError:
                return asyncio.run(_run_edge())
        except Exception as e:
            logger.warning(f"[DON-AURELIUS-VOICE] Edge Neural TTS error: {e}")
            return None

    def compile_vocal_briefing(self, narrative_text: str) -> Optional[io.BytesIO]:
        """
        Converts textual trading reports into high-fidelity voice packets.
        Uses Edge Neural TTS as robust primary/instant-fallback so voice NEVER fails.
        """
        if not narrative_text or not narrative_text.strip():
            return None

        # 1. First Priority: Try Microsoft Edge Neural Voice (deep, realistic, zero quota limits)
        edge_stream = self._synthesize_edge_tts(narrative_text)
        if edge_stream and len(edge_stream.getvalue()) > 500:
            logger.info("[DON-AURELIUS-VOICE] Edge Neural voice briefing generated successfully.")
            return edge_stream

        # 2. Second Priority: ElevenLabs API (if available and within quota)
        if self.api_key and len(self.api_key) > 5 and not self.api_key.startswith("your_"):
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": self.api_key
            }
            data = {
                "text": narrative_text[:400],
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {
                    "stability": 0.65,
                    "similarity_boost": 0.85
                }
            }

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

        # 3. Emergency Fallback: Acoustic Harmonic Chime
        return self._generate_fallback_audio(narrative_text)

    def _generate_fallback_audio(self, text: str) -> io.BytesIO:
        """
        Synthesizes a clean audio chime packet (WAV formatted) so Telegram voice
        transmission never fails even when API keys or network are unreachable.
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
            f"Greetings Boss. Don Aurelius Aureus Core is fully operational and guarding your empire. "
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
