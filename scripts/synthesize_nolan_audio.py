import math
import wave
import struct
import os

SAMPLE_RATE = 44100

def create_wav_file(filename, samples_left, samples_right):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with wave.open(filename, 'w') as wav:
        wav.setnchannels(2)
        wav.setsampwidth(2)
        wav.setframerate(SAMPLE_RATE)
        
        frames = bytearray()
        chunk_size = 4096
        total = len(samples_left)
        
        for i in range(0, total, chunk_size):
            chunk_frames = bytearray()
            end = min(i + chunk_size, total)
            for j in range(i, end):
                l = max(-0.98, min(0.98, samples_left[j]))
                r = max(-0.98, min(0.98, samples_right[j]))
                chunk_frames.extend(struct.pack('<hh', int(l * 32000), int(r * 32000)))
            wav.writeframes(chunk_frames)
    print(f"Generated: {filename} ({len(samples_left)/SAMPLE_RATE:.1f}s)")

def synthesize_braam(duration=4.5):
    total = int(duration * SAMPLE_RATE)
    left = [0.0] * total
    right = [0.0] * total
    
    # Fundamental brass freqs (Low D minor triad)
    freqs = [36.7, 43.65, 55.0, 73.4, 110.0, 146.8]
    
    for i in range(total):
        t = i / SAMPLE_RATE
        # Aggressive exponential envelope
        env = math.exp(-t * 0.9)
        # Pitch bend down slightly at start
        pitch_drop = 1.0 + 0.15 * math.exp(-t * 8.0)
        
        val = 0.0
        for idx, f in enumerate(freqs):
            cur_f = f * pitch_drop
            # Saturated sawtooth approximation
            saw = (2.0 * ((t * cur_f) % 1.0) - 1.0)
            # Add third harmonic for brass growl
            dist = math.tanh(saw * 2.5)
            weight = 1.0 / (idx + 1) ** 0.6
            val += dist * weight
            
        # Sub-bass rumble (32Hz sine)
        sub = math.sin(2 * math.pi * 32.0 * pitch_drop * t) * 0.6 * math.exp(-t * 0.5)
        
        sig = (val * 0.22 + sub) * env
        # Slight stereo chorus offset
        left[i] = sig
        right[i] = sig * (0.95 + 0.05 * math.sin(2 * math.pi * 3.0 * t))
        
    return left, right

def synthesize_tick(duration=90.0):
    total = int(duration * SAMPLE_RATE)
    left = [0.0] * total
    right = [0.0] * total
    
    # 60fps / 120 BPM: main tick every 0.5s, micro tick every 0.25s
    for i in range(total):
        t = i / SAMPLE_RATE
        if t >= 81.0:
            # Cut to dead silence at 81.0s (frame 4860)
            break
            
        # Main tick every 0.5s
        t_sub = t % 0.5
        tick_val = 0.0
        
        # Accelerate ticks in Act IV (60s to 81s): tick every 0.25s or 0.125s
        if t >= 60.0:
            t_fast = t % 0.25
            if t_fast < 0.03:
                decay = math.exp(-t_fast * 180.0)
                click = math.sin(2 * math.pi * 2800.0 * t_fast) * decay
                tick_val += click * 0.35
                
        if t_sub < 0.04:
            decay = math.exp(-t_sub * 120.0)
            # Metal mechanical click (high frequencies)
            click1 = math.sin(2 * math.pi * 3200.0 * t_sub)
            click2 = math.sin(2 * math.pi * 4800.0 * t_sub) * 0.5
            body = math.sin(2 * math.pi * 850.0 * t_sub) * 0.3
            tick_val += (click1 + click2 + body) * decay * 0.45
            
        left[i] = tick_val
        right[i] = tick_val * 0.95
        
    return left, right

def synthesize_orchestral_rise(duration=21.0):
    total = int(duration * SAMPLE_RATE)
    left = [0.0] * total
    right = [0.0] * total
    
    for i in range(total):
        t = i / SAMPLE_RATE
        progress = t / duration  # 0 to 1
        
        # Exponential volume ramp
        vol = progress ** 2.2 * 0.85
        
        # Exponential frequency rise (60Hz to 1200Hz)
        freq1 = 55.0 + 800.0 * (progress ** 2.5)
        freq2 = freq1 * 1.5
        freq3 = freq1 * 2.0
        
        # Detuned oscillators
        tone1 = math.sin(2 * math.pi * freq1 * t)
        tone2 = math.sin(2 * math.pi * freq2 * t + 0.4)
        tone3 = math.sin(2 * math.pi * freq3 * t + 0.8)
        
        # Noise riser
        noise = (math.sin(i * 12345.67) % 1.0 - 0.5) * (progress ** 3.0) * 0.4
        
        val = (tone1 * 0.4 + tone2 * 0.3 + tone3 * 0.3 + noise) * vol
        left[i] = val
        right[i] = val * (0.9 + 0.1 * math.sin(progress * 10))
        
    return left, right

def synthesize_master_score(duration=90.0):
    total = int(duration * SAMPLE_RATE)
    left = [0.0] * total
    right = [0.0] * total
    
    # Generate stems
    tick_l, tick_r = synthesize_tick(duration)
    braam_l, braam_r = synthesize_braam(4.5)
    braam_len = len(braam_l)
    
    # Master composition loop
    for i in range(total):
        t = i / SAMPLE_RATE
        
        # Dead silence drop between 81.0s (frame 4860) and 82.0s
        if 81.0 <= t < 82.0:
            left[i] = 0.0
            right[i] = 0.0
            continue
            
        # Act V (82.0s - 90.0s): Lone sovereign chord & warm chime
        if t >= 82.0:
            t_outro = t - 82.0
            outro_env = math.exp(-t_outro * 0.25) * min(1.0, t_outro * 2.0)
            # Golden D Major chord: 146.8Hz (D3), 185.0Hz (F#3), 220.0Hz (A3), 293.6Hz (D4)
            c1 = math.sin(2 * math.pi * 146.83 * t)
            c2 = math.sin(2 * math.pi * 184.99 * t)
            c3 = math.sin(2 * math.pi * 220.00 * t)
            c4 = math.sin(2 * math.pi * 293.66 * t) * 0.5
            chime = math.sin(2 * math.pi * 1174.66 * t) * math.exp(-t_outro * 1.5) * 0.3
            sig = (c1 * 0.35 + c2 * 0.3 + c3 * 0.25 + c4 * 0.15 + chime) * outro_env * 0.6
            left[i] = sig
            right[i] = sig
            continue
            
        # Base chords for Acts I - IV
        # Act I (0 - 18s): A minor
        # Act II (18 - 36s): D minor
        # Act III (36 - 60s): C major / F major
        # Act IV (60 - 81s): Building riser
        if t < 18.0:
            f_root = 55.0  # A1
            chord = math.sin(2 * math.pi * 110.0 * t) + math.sin(2 * math.pi * 130.81 * t) * 0.8
            sub = math.sin(2 * math.pi * f_root * t) * 0.5
            drone = (chord * 0.25 + sub) * min(1.0, t / 3.0) * 0.35
        elif t < 36.0:
            f_root = 73.4  # D2
            chord = math.sin(2 * math.pi * 146.83 * t) + math.sin(2 * math.pi * 174.61 * t) * 0.8
            sub = math.sin(2 * math.pi * 36.7 * t) * 0.6
            drone = (chord * 0.3 + sub) * 0.4
        elif t < 60.0:
            chord = math.sin(2 * math.pi * 130.81 * t) + math.sin(2 * math.pi * 164.81 * t) * 0.7 + math.sin(2 * math.pi * 196.0 * t) * 0.5
            sub = math.sin(2 * math.pi * 48.99 * t) * 0.65
            drone = (chord * 0.3 + sub) * 0.45
        else: # 60.0 - 81.0 (Act IV)
            p_rise = (t - 60.0) / 21.0
            freq_rise = 65.0 + 900.0 * (p_rise ** 2.2)
            horn = math.sin(2 * math.pi * freq_rise * t) * 0.4
            sub_rise = math.sin(2 * math.pi * (32.0 + 80.0 * p_rise) * t) * 0.5
            drone = (horn + sub_rise) * (p_rise ** 1.8) * 0.65
            
        # Mix tick
        tick = tick_l[i]
        
        # Mix braams at act transitions:
        # Act I -> II transition at 18.0s
        # Act II -> III transition at 36.0s
        # Act III -> IV transition at 60.0s
        braam_sig = 0.0
        for braam_time in [18.0, 36.0, 60.0]:
            diff_samples = i - int(braam_time * SAMPLE_RATE)
            if 0 <= diff_samples < braam_len:
                braam_sig += braam_l[diff_samples] * 0.85
                
        tot = drone + tick + braam_sig
        left[i] = tot
        right[i] = tot * 0.98
        
    return left, right

def main():
    print("Synthesizing Christopher Nolan trailer audio stems...")
    
    # 1. Ticking clock
    tick_l, tick_r = synthesize_tick(90.0)
    create_wav_file("public/audio/ticking_clock_90s.wav", tick_l, tick_r)
    
    # 2. Nolan Braam
    braam_l, braam_r = synthesize_braam(4.5)
    create_wav_file("public/audio/nolan_braam.wav", braam_l, braam_r)
    
    # 3. Orchestral rise (Act IV 21 seconds)
    rise_l, rise_r = synthesize_orchestral_rise(21.0)
    create_wav_file("public/audio/orchestral_rise.wav", rise_l, rise_r)
    
    # 4. Master 90s score
    master_l, master_r = synthesize_master_score(90.0)
    create_wav_file("public/audio/nolan_master_score_90s.wav", master_l, master_r)
    
    print("All Nolan audio stems synthesized successfully!")

if __name__ == "__main__":
    main()
