import math
import wave
import struct

def generate_cinematic_audio(output_wav="cinematic_soundtrack_60s.wav", duration=60.0, sample_rate=44100):
    total_samples = int(duration * sample_rate)
    print(f"Generating {duration}s cinematic audio track ({total_samples} samples)...")

    # Open wave file
    with wave.open(output_wav, 'w') as wav:
        wav.setnchannels(2)  # Stereo
        wav.setsampwidth(2)  # 16-bit
        wav.setframerate(sample_rate)

        frames = bytearray()
        
        # Chord progression across 6 scenes (each scene is 10s)
        # Frequencies: [Root, Minor Third, Fifth]
        chords = [
            (110.0, 130.81, 164.81),  # A minor (Scene 1: Tension)
            (146.83, 174.61, 220.0),  # D minor (Scene 2: Power)
            (130.81, 164.81, 196.0),  # C major (Scene 3: Clarity)
            (164.81, 196.0, 246.94),  # E minor (Scene 4: Execution)
            (146.83, 174.61, 220.0),  # D minor (Scene 5: High stakes)
            (110.0, 138.59, 164.81)   # A major (Scene 6: Sovereign Victory)
        ]

        # Chunk writing for efficiency
        chunk_size = 4096
        for i in range(0, total_samples, chunk_size):
            chunk_frames = bytearray()
            current_chunk_size = min(chunk_size, total_samples - i)
            
            for j in range(current_chunk_size):
                sample_idx = i + j
                t = sample_idx / sample_rate
                
                # Active scene (0 to 5)
                scene_idx = min(5, int(t / 10.0))
                scene_t = t % 10.0
                f1, f2, f3 = chords[scene_idx]

                # 1. Deep Sub Bass (f1 / 2) with subtle pulse
                sub_freq = f1 / 2.0
                sub_wave = math.sin(2 * math.pi * sub_freq * t)
                sub_amp = 0.28 * (0.8 + 0.2 * math.sin(2 * math.pi * 0.5 * t))

                # 2. Atmospheric Synth Pad (Chords with slow chorus)
                pad1 = math.sin(2 * math.pi * f1 * t + 0.3 * math.sin(2 * math.pi * 0.2 * t))
                pad2 = math.sin(2 * math.pi * f2 * t)
                pad3 = math.sin(2 * math.pi * f3 * t + 0.2 * math.sin(2 * math.pi * 0.3 * t))
                pad_wave = (pad1 + pad2 + pad3) / 3.0
                pad_amp = 0.22

                # 3. High-tech HUD Arpeggio / Beeps (every 0.5s)
                arp_notes = [f1 * 2, f2 * 2, f3 * 2, f1 * 4]
                arp_idx = int(t * 4) % len(arp_notes)
                arp_freq = arp_notes[arp_idx]
                arp_env = math.exp(-6.0 * (t % 0.25))
                arp_wave = math.sin(2 * math.pi * arp_freq * t) * arp_env * 0.08

                # 4. Cinematic Scene Transition Riser / Swoosh (at the end of each 10s scene: 8.5s - 10s)
                swoosh_wave = 0.0
                if scene_t > 8.0:
                    rise_p = (scene_t - 8.0) / 2.0
                    sweep_freq = 150.0 + 800.0 * (rise_p ** 2)
                    swoosh_wave = math.sin(2 * math.pi * sweep_freq * t) * (rise_p * 0.18)

                # Total mixed sample
                mixed = (sub_wave * sub_amp) + (pad_wave * pad_amp) + arp_wave + swoosh_wave
                
                # Global fade in (first 1s) and fade out (last 2s)
                if t < 1.0:
                    mixed *= t
                elif t > duration - 2.0:
                    mixed *= max(0.0, (duration - t) / 2.0)

                # Clip & convert to 16-bit signed integer (-32768 to 32767)
                mixed = max(-0.95, min(0.95, mixed))
                left_int = int(mixed * 30000)
                # Stereo widening with slight phase offset
                right_int = int(max(-0.95, min(0.95, mixed * 0.95 + arp_wave * 0.05)) * 30000)

                chunk_frames.extend(struct.pack('<hh', left_int, right_int))
            
            wav.writeframes(chunk_frames)

    print(f"Successfully generated {output_wav}!")

if __name__ == "__main__":
    generate_cinematic_audio()
