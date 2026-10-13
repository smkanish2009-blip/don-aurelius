import math
import os
import random
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import imageio
import imageio_ffmpeg

WIDTH = 1280
HEIGHT = 720
FPS = 30
TOTAL_DURATION = 60.0  # Exactly 1 minute (60 seconds)
TOTAL_FRAMES = int(TOTAL_DURATION * FPS)  # 1800 frames

TEMP_MP4 = "temp_video_60s.mp4"
AUDIO_WAV = "cinematic_soundtrack_60s.wav"
FINAL_MP4 = "don_aurelius_60s_master.mp4"

def get_font(size, bold=False):
    candidates = [
        "C:\\Windows\\Fonts\\segoeui.ttf",
        "C:\\Windows\\Fonts\\arial.ttf",
        "C:\\Windows\\Fonts\\consola.ttf"
    ]
    if bold:
        candidates = [
            "C:\\Windows\\Fonts\\segouib.ttf",
            "C:\\Windows\\Fonts\\arialbd.ttf",
            "C:\\Windows\\Fonts\\consolab.ttf"
        ] + candidates

    for p in candidates:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()

font_hero = get_font(42, bold=True)
font_title = get_font(28, bold=True)
font_sub = get_font(20, bold=False)
font_mono = get_font(16, bold=True)
font_tiny = get_font(13, bold=False)

# 6 Storyboard Scenes (10 seconds each)
SCENES = [
    {
        "id": 1,
        "title": "THE VOLATILITY CRISIS",
        "tag": "MARKET ANOMALY",
        "image": "docs/assets/scene1_chaos.jpg",
        "headline": "MANUAL EXECUTION IS OBSOLETE",
        "script": "Gold market volatility triggers catastrophic drawdowns for manual traders. Lagged indicators and emotional bias destroy capital.",
        "badge": "XAUUSD VOLATILITY DETECTED",
        "color": (255, 75, 75)
    },
    {
        "id": 2,
        "title": "AWAKENING OF DON AURELIUS",
        "tag": "IMPERIAL MATRIX",
        "image": "docs/assets/scene2_reveal.jpg",
        "headline": "CONCEIVED & ARCHITECTED BY SM.KANISH",
        "script": "Enter Don Aurelius — the sovereign autonomous quantitative syndicate engineered to dominate institutional liquidity.",
        "badge": "AUTONOMOUS CORE: ONLINE",
        "color": (240, 199, 94)
    },
    {
        "id": 3,
        "title": "METATRADER 5 CLOUD BRIDGE",
        "tag": "ZERO LATENCY",
        "image": "docs/assets/scene3_mt5_install.jpg",
        "headline": "DIRECT MQL5 SUB-MILLIS TELEMETRY",
        "script": "0.4ms execution gateway direct to Tier-1 liquidity providers. Hardware-locked licensing armor with AES-256 sovereign defense.",
        "badge": "0.4ms FIBER GATEWAY",
        "color": (0, 240, 255)
    },
    {
        "id": 4,
        "title": "PROJECT EAGLE-EYE VISION",
        "tag": "MULTIMODAL AI",
        "image": "docs/assets/scene4_execution_hud.jpg",
        "headline": "COMPUTER VISION PATTERN RECOGNITION",
        "script": "Neural inspection of raw M15 candlestick geometry. +380 Pips locked with mathematical precision and zero indicator lag.",
        "badge": "+380 PIPS LOCKED · 94.2% WIN RATE",
        "color": (0, 255, 136)
    },
    {
        "id": 5,
        "title": "NEURAL WAR ROOM & MOBILE HUD",
        "tag": "24/7 SURVEILLANCE",
        "image": "don_aurelius_phone_texture.png",
        "headline": "SOVEREIGN PORTFOLIO SURVEILLANCE",
        "script": "Monte Carlo 5,000 path simulation per tick. Real-time Telegram bi-directional conversational voice commander with instant kill-switch.",
        "badge": "5,000 PATH MONTE CARLO TWIN",
        "color": (190, 140, 255)
    },
    {
        "id": 6,
        "title": "SOVEREIGN VERIFICATION",
        "tag": "PRIVATE SYNDICATE",
        "image": "docs/assets/scene5_outro_sparkle.jpg",
        "headline": "THE INSTITUTIONAL GOLD STANDARD",
        "script": "Claim your sovereign terminal access. Architected by Commander SM.KANISH. Verified operational on MetaTrader 5.",
        "badge": "VERIFIED SOVEREIGN · SM.KANISH",
        "color": (240, 199, 94)
    }
]

# Pre-load and resize scene images
loaded_images = []
for sc in SCENES:
    if os.path.exists(sc["image"]):
        im = Image.open(sc["image"]).convert("RGBA")
        loaded_images.append(im)
    else:
        # Fallback dark background
        im = Image.new("RGBA", (WIDTH, HEIGHT), (10, 12, 18, 255))
        loaded_images.append(im)

# Particles
random.seed(42)
particles = []
for _ in range(60):
    particles.append({
        'x': random.uniform(0, WIDTH),
        'y': random.uniform(0, HEIGHT),
        'vx': random.uniform(-0.5, 0.5),
        'vy': random.uniform(-0.6, -0.1),
        's': random.uniform(1.5, 3.5),
        'c': random.choice([(240, 199, 94), (0, 240, 255), (0, 255, 136), (255, 255, 255)])
    })

def render_frame(frame_idx):
    t = frame_idx / FPS
    scene_idx = min(5, int(t / 10.0))
    scene_t = (t % 10.0) / 10.0  # 0.0 to 1.0 within scene
    sc = SCENES[scene_idx]
    base_img = loaded_images[scene_idx]

    # Ken Burns pan & zoom
    scale = 1.0 + 0.12 * scene_t
    bw, bh = base_img.size
    crop_w = int(bw / scale)
    crop_h = int(bh / scale)
    
    # Pan direction varies by scene
    pan_x = int((bw - crop_w) * (0.3 + 0.4 * (scene_t if scene_idx % 2 == 0 else (1.0 - scene_t))))
    pan_y = int((bh - crop_h) * (0.2 + 0.3 * scene_t))
    pan_x = max(0, min(bw - crop_w, pan_x))
    pan_y = max(0, min(bh - crop_h, pan_y))

    cropped = base_img.crop((pan_x, pan_y, pan_x + crop_w, pan_y + crop_h))
    frame = cropped.resize((WIDTH, HEIGHT), Image.Resampling.BILINEAR)

    # Cross-dissolve transition at scene start (first 0.6s)
    if scene_idx > 0 and (t % 10.0) < 0.6:
        fade = (t % 10.0) / 0.6
        prev_img = loaded_images[scene_idx - 1]
        prev_frame = prev_img.resize((WIDTH, HEIGHT), Image.Resampling.BILINEAR)
        frame = Image.blend(prev_frame, frame, fade)

    draw = ImageDraw.Draw(frame)

    # 1. Vignette dark borders
    vignette = Image.new('RGBA', (WIDTH, HEIGHT), (0, 0, 0, 0))
    vdraw = ImageDraw.Draw(vignette)
    vdraw.rectangle([0, 0, WIDTH, 90], fill=(0, 0, 0, 160))
    vdraw.rectangle([0, HEIGHT - 180, WIDTH, HEIGHT], fill=(0, 0, 0, 190))
    frame = Image.alpha_composite(frame, vignette)
    draw = ImageDraw.Draw(frame)

    # 2. Floating Ambient Particles
    for p in particles:
        px = (p['x'] + p['vx'] * t * 30) % WIDTH
        py = (p['y'] + p['vy'] * t * 30) % HEIGHT
        alpha = int(120 + 80 * math.sin(t * 4 + px))
        r, g, b = p['c']
        s = p['s']
        draw.ellipse([px - s, py - s, px + s, py + s], fill=(r, g, b, alpha))

    # 3. Top HUD Bar
    # Left chapter badge
    draw.rounded_rectangle([40, 24, 460, 60], radius=8, fill=(10, 14, 24, 230), outline=(240, 199, 94, 180), width=1)
    pulse = (math.sin(t * 8) + 1) / 2
    p_color = sc["color"] if pulse > 0.3 else (100, 100, 100)
    draw.ellipse([54, 36, 64, 46], fill=p_color)
    draw.text((74, 32), f"DON AURELIUS • CH {sc['id']:02d}: {sc['title']}", fill=(240, 245, 255), font=font_mono)

    # Right timecode badge
    draw.rounded_rectangle([WIDTH - 280, 24, WIDTH - 40, 60], radius=8, fill=(10, 14, 24, 230), outline=(0, 240, 255, 180), width=1)
    sec = int(t)
    ms = int((t - sec) * 100)
    draw.text((WIDTH - 265, 32), f"30 FPS • {sec:02d}:{ms:02d} / 60:00 • 1080P", fill=(0, 240, 255), font=font_mono)

    # 4. Lower-Third Glassmorphic Subtitle Card
    card_y = HEIGHT - 165
    draw.rounded_rectangle([40, card_y, WIDTH - 40, HEIGHT - 30], radius=16, fill=(8, 12, 20, 235), outline=(sc["color"][0], sc["color"][1], sc["color"][2], 160), width=1)

    # Color accent bar on left of card
    draw.rounded_rectangle([40, card_y, 48, HEIGHT - 30], radius=4, fill=sc["color"])

    # Badge & Headline
    draw.text((65, card_y + 14), sc["badge"], fill=sc["color"], font=font_mono)
    draw.text((65, card_y + 36), sc["headline"], fill=(255, 255, 255), font=font_title)

    # Explanatory Script line
    draw.text((65, card_y + 76), sc["script"], fill=(200, 215, 235), font=font_sub)

    # 5. Global bottom progress bar (0s to 60s)
    progress_w = int((t / TOTAL_DURATION) * WIDTH)
    draw.rectangle([0, HEIGHT - 4, progress_w, HEIGHT], fill=(240, 199, 94, 255))

    return np.array(frame.convert("RGB"))

def main():
    print(f"Starting 60-Second Master Video Render: {TOTAL_FRAMES} frames @ {FPS} FPS...")
    
    # 1. Render Video Frames
    writer = imageio.get_writer(TEMP_MP4, fps=FPS, codec='libx264', quality=8)
    
    for f in range(TOTAL_FRAMES):
        frame_arr = render_frame(f)
        writer.append_data(frame_arr)
        if (f + 1) % 150 == 0 or f == TOTAL_FRAMES - 1:
            pct = int(((f + 1) / TOTAL_FRAMES) * 100)
            sec = int((f + 1) / FPS)
            print(f"Render progress: {pct}% ({sec:02d}s / 60s)", flush=True)
            
    writer.close()
    print("Video track rendering complete!")

    # 2. Mux with Audio using FFmpeg
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    print(f"Muxing audio track {AUDIO_WAV} with video {TEMP_MP4} using FFmpeg...")
    
    cmd = [
        ffmpeg_exe, "-y",
        "-i", TEMP_MP4,
        "-i", AUDIO_WAV,
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        FINAL_MP4
    ]
    subprocess.run(cmd, check=True)
    print(f"60-SECOND MASTER VIDEO COMPLETE: {FINAL_MP4}")

    # Clean up temp
    if os.path.exists(TEMP_MP4):
        os.remove(TEMP_MP4)

if __name__ == "__main__":
    main()
