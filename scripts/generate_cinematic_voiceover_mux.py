import asyncio
import os
import shutil
import subprocess
import edge_tts
import numpy as np
import soundfile as sf
import imageio_ffmpeg

VOICEOVER_SEGMENTS = [
    (5.0, "Markets fail. The illusion of manual certainty breaks under pressure."),
    (10.0, "Humans hesitate. Emotional bias destroys capital."),
    (15.0, "Gold remains."),
    (20.0, "Introducing Don Aurelius. The sovereign algorithmic gold syndicate, architected by SM Kanish."),
    (39.0, "Eighty-nine point four percent win rate across two thousand one hundred fifty verified trades."),
    (50.0, "Direct sub-millisecond execution. Zero lag. Pure mathematical dominance."),
    (62.0, "Deploy in seconds. A single command connects your terminal directly to the cloud bridge."),
    (72.0, "MetaTrader five cloud telemetry locked. Monte Carlo five thousand paths simulated per tick."),
    (83.0, "Don Aurelius. Claim your sovereign terminal access today.")
]

TOTAL_DURATION = 90.0
SAMPLE_RATE = 48000

async def generate_speech_clips():
    os.makedirs("temp_voice", exist_ok=True)
    clip_files = []
    voice = "en-US-ChristopherNeural"
    
    for idx, (timestamp, text) in enumerate(VOICEOVER_SEGMENTS):
        clip_path = f"temp_voice/clip_{idx:02d}.mp3"
        print(f"[{timestamp}s] Synthesizing voiceover: {text[:40]}...")
        communicate = edge_tts.Communicate(text, voice, rate="-5%", pitch="-2Hz")
        await communicate.save(clip_path)
        clip_files.append((timestamp, clip_path))
        
    return clip_files

def assemble_master_audio(clip_files):
    total_samples = int(TOTAL_DURATION * SAMPLE_RATE)
    voice_track = np.zeros(total_samples, dtype=np.float32)
    
    for timestamp, clip_path in clip_files:
        data, sr = sf.read(clip_path)
        if len(data.shape) > 1:
            data = data.mean(axis=1) # Mono
            
        # Resample if needed
        if sr != SAMPLE_RATE:
            num_samples = int(len(data) * SAMPLE_RATE / sr)
            data = np.interp(
                np.linspace(0, len(data), num_samples, endpoint=False),
                np.arange(len(data)),
                data
            )
            
        start_idx = int(timestamp * SAMPLE_RATE)
        end_idx = min(start_idx + len(data), total_samples)
        available_len = end_idx - start_idx
        
        voice_track[start_idx:end_idx] += data[:available_len] * 1.25
        
    # Save voice track
    voice_wav = "out/voiceover_track_90s.wav"
    sf.write(voice_wav, voice_track, SAMPLE_RATE)
    print(f"Generated {voice_wav}!")
    return voice_wav

def mux_final_master(voice_wav):
    input_video = "out/don_aurelius_nolan_trailer.mp4"
    output_video = "out/Don_Aurelius_Nolan_Trailer_Master.mp4"
    desktop_output = os.path.expanduser(r"C:\Users\LENOVO\Desktop\Don_Aurelius_Nolan_Trailer.mp4")
    
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    
    # Mix original score (input 0 audio) with newly mastered voiceover (input 1 audio)
    # Original score at 0.85, voiceover at 1.4 for pristine clarity
    cmd = [
        ffmpeg_exe, "-y",
        "-i", input_video,
        "-i", voice_wav,
        "-filter_complex",
        "[0:a]volume=0.82[orig];[1:a]volume=1.45[voice];[orig][voice]amix=inputs=2:duration=first:dropout_transition=2[aout]",
        "-map", "0:v",
        "-map", "[aout]",
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "320k",
        "-shortest",
        output_video
    ]
    
    print("Muxing video with dual audio stems via FFmpeg...")
    subprocess.run(cmd, check=True)
    print(f"[SUCCESS] Master trailer compiled to: {output_video}")
    
    # Copy directly to user's Desktop
    shutil.copyfile(output_video, desktop_output)
    print(f"[SUCCESS] Delivered directly to Desktop: {desktop_output}")
    
    # Cleanup temp
    if os.path.exists("temp_voice"):
        shutil.rmtree("temp_voice")

def main():
    print("Starting Christopher Nolan Voiceover & Master Mix Pipeline...")
    clips = asyncio.run(generate_speech_clips())
    voice_wav = assemble_master_audio(clips)
    mux_final_master(voice_wav)
    print("ALL DONE! Master video ready!")

if __name__ == "__main__":
    main()
