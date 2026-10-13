#!/usr/bin/env python3
"""
Don Aurelius - 60-Second Video Tutorial Voiceover Generator
=============================================================
Synthesizes professional, high-retention narration for the Don Aurelius
algorithmic trading bot installation video using Edge-TTS (en-US-ChristopherNeural).

Generates:
- Individual segment audio files for modular video editing
- Master timeline-aligned tutorial_voiceover.mp3 (60.0s target duration)
"""

import asyncio
import os
import sys
from pathlib import Path
import edge_tts
import numpy as np
import soundfile as sf

# ---------------------------------------------------------------------------
# Configuration & Voice Profile
# ---------------------------------------------------------------------------
VOICE = "en-US-ChristopherNeural"
RATE = "+25%"         # High-retention fast-paced tech reel delivery (~175 wpm)
PITCH = "-1Hz"        # Subtle authoritative cinematic baritone
SAMPLE_RATE = 48000   # Broadcast standard 48 kHz
TARGET_MASTER_DURATION = 60.0  # 60-second video master duration

# ---------------------------------------------------------------------------
# Programmatic Speech Segments (Aligned with marketing/tutorial_script.md)
# ---------------------------------------------------------------------------
SEGMENTS = [
    {
        "id": 1,
        "timestamp": "0:00 – 0:05",
        "target_start_sec": 0.5,
        "phase": "HOOK",
        "text": "Deploy institutional gold trading in sixty seconds. No manual analysis. Zero guesswork.",
    },
    {
        "id": 2,
        "timestamp": "0:05 – 0:14",
        "target_start_sec": 5.2,
        "phase": "STEP 1: EXTRACTION",
        "text": "Step one: Unpack the setup package onto your drive. Inside, rename .env.example to .env to unlock your local configuration.",
    },
    {
        "id": 3,
        "timestamp": "0:14 – 0:24",
        "target_start_sec": 13.5,
        "phase": "STEP 2 (PART A): MT5 ALGO TOGGLE",
        "text": "Step two: Open your MetaTrader 5 terminal and verify the Algo Trading button is green. This enables high-speed execution.",
    },
    {
        "id": 4,
        "timestamp": "0:24 – 0:35",
        "target_start_sec": 21.8,
        "phase": "STEP 2 (PART B): PYTHON & BACKTRADER LINK",
        "text": "Next, launch the connection script. Python bridges instantly to your MT5 terminal through Backtrader, locking in live sub-second tick feeds for spot gold.",
    },
    {
        "id": 5,
        "timestamp": "0:35 – 0:43",
        "target_start_sec": 32.0,
        "phase": "STEP 3: DEMO SAFETY GUARDRAIL",
        "text": "Step three: Safety first. Don Aurelius automatically inspects your account credentials. The demo guardrail is hard-coded to lock trading to virtual funds.",
    },
    {
        "id": 6,
        "timestamp": "0:43 – 0:50",
        "target_start_sec": 40.2,
        "phase": "CIRCUIT BREAKER TEST",
        "text": "Zero real capital is ever risked. Every strategy, circuit breaker, and risk limiter runs in a complete sandbox until you choose otherwise.",
    },
    {
        "id": 7,
        "timestamp": "0:50 – 0:55",
        "target_start_sec": 48.0,
        "phase": "DEPLOYMENT PAYOFF",
        "text": "Double-click Start_Don_Aurelius.bat. The multi-agent neural consensus engine is now live and monitoring market liquidity.",
    },
    {
        "id": 8,
        "timestamp": "0:55 – 1:00",
        "target_start_sec": 54.5,
        "phase": "CALL TO ACTION",
        "text": "Claim your free demo package right now. The link is in the description. Deploy Don Aurelius today.",
    },
]


async def synthesize_segment(segment: dict, output_dir: Path) -> tuple[Path, float]:
    """
    Synthesize an individual speech segment using Edge-TTS.
    Returns the file path and actual audio duration in seconds.
    """
    clip_filename = output_dir / f"segment_{segment['id']:02d}_{segment['phase'].split(':')[0].strip().replace(' ', '_').lower()}.mp3"
    communicate = edge_tts.Communicate(
        text=segment["text"],
        voice=VOICE,
        rate=RATE,
        pitch=PITCH,
    )
    await communicate.save(str(clip_filename))
    
    info = sf.info(str(clip_filename))
    return clip_filename, info.duration


def assemble_timeline_audio(
    segment_records: list[dict],
    master_output_path: Path,
    target_duration: float = TARGET_MASTER_DURATION,
    sample_rate: int = SAMPLE_RATE,
) -> float:
    """
    Places each synthesized segment at its timeline start position.
    Applies collision prevention if any segment slightly overruns,
    and exports a master audio file matching the target 60-second video duration.
    """
    # Calculate required master buffer length
    # Determine the end time of the last segment
    last_end_time = 0.0
    current_cursor = 0.0
    scheduled_placements = []

    for item in segment_records:
        nominal_start = item["target_start_sec"]
        # Ensure at least 0.35s breathing room after previous segment
        actual_start = max(nominal_start, current_cursor + (0.35 if current_cursor > 0 else 0.0))
        duration = item["duration"]
        actual_end = actual_start + duration
        current_cursor = actual_end
        last_end_time = max(last_end_time, actual_end)
        scheduled_placements.append((item, actual_start, actual_end))

    total_track_duration = max(target_duration, last_end_time + 0.5)
    total_samples = int(total_track_duration * sample_rate)
    master_buffer = np.zeros(total_samples, dtype=np.float32)

    print("\n" + "=" * 80)
    print("TIMELINE ASSEMBLY & COLLISION CHECK")
    print("=" * 80)

    for item, start_t, end_t in scheduled_placements:
        audio_data, file_sr = sf.read(str(item["file_path"]))
        # Convert stereo to mono if needed
        if audio_data.ndim > 1:
            audio_data = audio_data.mean(axis=1)

        # Resample if sample rate doesn't match
        if file_sr != sample_rate:
            target_samples = int(len(audio_data) * sample_rate / file_sr)
            audio_data = np.interp(
                np.linspace(0, len(audio_data), target_samples, endpoint=False),
                np.arange(len(audio_data)),
                audio_data,
            )

        start_sample = int(start_t * sample_rate)
        end_sample = start_sample + len(audio_data)

        # Apply subtle 10ms raised-cosine fade-in/fade-out to eliminate clicks
        fade_len = int(0.01 * sample_rate)
        if len(audio_data) > 2 * fade_len:
            fade_in = 0.5 * (1.0 - np.cos(np.linspace(0, np.pi, fade_len)))
            fade_out = 0.5 * (1.0 + np.cos(np.linspace(0, np.pi, fade_len)))
            audio_data[:fade_len] *= fade_in
            audio_data[-fade_len:] *= fade_out

        master_buffer[start_sample:end_sample] += audio_data
        print(f"  • Beat {item['id']} [{item['timestamp']}] | Starts at {start_t:5.2f}s -> Ends at {end_t:5.2f}s | Duration: {item['duration']:4.2f}s")

    # Peak normalization to -1.0 dBFS to prevent clipping
    peak = np.max(np.abs(master_buffer))
    if peak > 0:
        target_peak = 10 ** (-1.0 / 20.0)  # ~0.891
        master_buffer = (master_buffer / peak) * target_peak

    # Duplicate mono to stereo for rich video playback
    stereo_buffer = np.column_stack((master_buffer, master_buffer))

    # Export master file
    sf.write(str(master_output_path), stereo_buffer, sample_rate, format="MP3")
    return total_track_duration


async def main():
    marketing_dir = Path(__file__).resolve().parent
    segments_dir = marketing_dir / "segments"
    segments_dir.mkdir(parents=True, exist_ok=True)
    master_output = marketing_dir / "tutorial_voiceover.mp3"

    print("=" * 80)
    print("DON AURELIUS - 60s TUTORIAL VOICEOVER SYNTHESIS")
    print("=" * 80)
    print(f"Voice Profile  : {VOICE}")
    print(f"Output Master  : {master_output}")
    print(f"Segments Folder: {segments_dir}")
    print(f"Target Duration: {TARGET_MASTER_DURATION} seconds\n")

    segment_records = []
    print("Synthesizing speech segments via Edge-TTS...")
    for seg in SEGMENTS:
        print(f"  [Seg {seg['id']}/8] {seg['phase']:<30} | \"{seg['text'][:45]}...\"")
        file_path, duration = await synthesize_segment(seg, segments_dir)
        record = {
            **seg,
            "file_path": file_path,
            "duration": duration,
        }
        segment_records.append(record)

    # Assemble timeline-aligned master audio
    final_duration = assemble_timeline_audio(
        segment_records=segment_records,
        master_output_path=master_output,
        target_duration=TARGET_MASTER_DURATION,
        sample_rate=SAMPLE_RATE,
    )

    file_size_kb = master_output.stat().st_size / 1024.0
    print("\n" + "=" * 80)
    print("SYNTHESIS & ASSEMBLY COMPLETED SUCCESSFULLY!")
    print("=" * 80)
    print(f"Master File : {master_output.name}")
    print(f"File Path   : {master_output}")
    print(f"File Size   : {file_size_kb:.1f} KB")
    print(f"Duration    : {final_duration:.2f} seconds")
    print(f"Sample Rate : {SAMPLE_RATE} Hz (Stereo 2-Channel)")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
