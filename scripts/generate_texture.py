from PIL import Image, ImageDraw, ImageFont
import os

W, H = 946, 2046
img = Image.new('RGBA', (W, H), (6, 8, 14, 255))
draw = ImageDraw.Draw(img)

try:
    font_large = ImageFont.truetype("arialbd.ttf", 56)
    font_title = ImageFont.truetype("arialbd.ttf", 36)
    font_sub = ImageFont.truetype("arial.ttf", 26)
    font_small = ImageFont.truetype("arial.ttf", 22)
    font_mono = ImageFont.truetype("consola.ttf", 24)
    font_hero = ImageFont.truetype("arialbd.ttf", 74)
except:
    font_large = font_title = font_sub = font_small = font_mono = font_hero = ImageFont.load_default()

# 1. Subtle grid lines
for y in range(0, H, 80):
    draw.line([(0, y), (W, y)], fill=(18, 26, 42, 180), width=1)
for x in range(0, W, 80):
    draw.line([(x, 0), (x, H)], fill=(18, 26, 42, 180), width=1)

# 2. Status bar
draw.text((60, 42), "09:41", fill=(255, 255, 255, 240), font=font_sub)
draw.text((W - 190, 42), "5G  ● 100%", fill=(255, 255, 255, 240), font=font_sub)

# 3. Header Card with Golden Eagle
reveal_path = r"C:\Users\LENOVO\.gemini\antigravity\brain\05ba38eb-d86d-4cbb-835f-a82e19cb8a53\don_aurelius_reveal_1790938583644.jpg"
if os.path.exists(reveal_path):
    reveal_img = Image.open(reveal_path)
    rw, rh = reveal_img.size
    eagle_crop = reveal_img.crop((rw//2 - 240, rh//2 - 270, rw//2 + 240, rh//2 + 90))
    eagle_crop = eagle_crop.resize((240, 180), Image.Resampling.LANCZOS)
    img.paste(eagle_crop, (W//2 - 120, 100))

draw.text((W//2, 310), "DON AURELIUS", fill=(240, 199, 94, 255), font=font_large, anchor="mm")
draw.text((W//2, 360), "QUANTUM AI WAR ROOM", fill=(0, 240, 255, 255), font=font_sub, anchor="mm")
draw.text((W//2, 400), "COMMANDER: SM.KANISH", fill=(210, 225, 245, 255), font=font_mono, anchor="mm")

# 4. Hero Profit Card
card_y1 = 440
card_y2 = 740
draw.rounded_rectangle([(40, card_y1), (W - 40, card_y2)], radius=24, fill=(12, 18, 30, 245), outline=(240, 199, 94, 200), width=2)

draw.text((70, 470), "XAUUSD LIVE PERFORMANCE", fill=(160, 180, 200, 255), font=font_small)
draw.text((W - 70, 470), "● ACTIVE MQL5", fill=(0, 255, 136, 255), font=font_small, anchor="rt")

draw.text((70, 530), "+$48,920.00", fill=(0, 255, 136, 255), font=font_hero)
draw.text((70, 620), "+380 Pips Locked · 94.2% Win Rate", fill=(240, 199, 94, 255), font=font_title)

draw.text((70, 685), "Risk Armor: Quarter-Kelly (1.0% Max Cap)", fill=(180, 200, 220, 255), font=font_sub)
draw.text((W - 70, 685), "Latency: 0.4ms", fill=(0, 240, 255, 255), font=font_mono, anchor="rt")

# 5. Trading HUD Chart
hud_path = r"C:\Users\LENOVO\.gemini\antigravity\brain\05ba38eb-d86d-4cbb-835f-a82e19cb8a53\trade_execution_hud_1790938648395.jpg"
if os.path.exists(hud_path):
    hud_img = Image.open(hud_path)
    hw, hh = hud_img.size
    chart_crop = hud_img.crop((70, 40, hw - 70, hh - 40))
    chart_crop = chart_crop.resize((W - 80, 600), Image.Resampling.LANCZOS)
    img.paste(chart_crop, (40, 770))
    draw.rounded_rectangle([(40, 770), (W - 40, 1370)], radius=24, outline=(0, 240, 255, 160), width=2)

# 6. Active AI Modules List Card
m_y1 = 1400
m_y2 = 1860
draw.rounded_rectangle([(40, m_y1), (W - 40, m_y2)], radius=24, fill=(12, 18, 30, 245), outline=(50, 70, 110, 220), width=2)

draw.text((70, 1435), "AUTONOMOUS SUB-SYSTEMS", fill=(240, 199, 94, 255), font=font_title)

modules = [
    ("● Project Eagle-Eye", "Computer Vision pattern recognition (100% active)", (0, 255, 136)),
    ("● Quantum Twin", "5,000 Monte Carlo path simulations per tick", (0, 240, 255)),
    ("● Crisis Sentinel", "Real-time geopolitical news filter & kill-switch", (255, 200, 80)),
    ("● Sovereign Vault", "Hardware-locked AES-256 licensing defense", (190, 150, 255))
]

for idx, (m_title, m_desc, m_color) in enumerate(modules):
    curr_y = 1500 + idx * 85
    draw.text((70, curr_y), m_title, fill=m_color, font=font_title)
    draw.text((70, curr_y + 42), m_desc, fill=(160, 185, 210, 255), font=font_sub)

# 7. Bottom Navigation Bar / CTA
draw.rounded_rectangle([(50, 1890), (W - 50, 1980)], radius=45, fill=(240, 199, 94, 255))
draw.text((W//2, 1935), "VERIFIED SOVEREIGN · SM.KANISH", fill=(8, 10, 16, 255), font=font_title, anchor="mm")

draw.rounded_rectangle([(W//2 - 100, 2015), (W//2 + 100, 2023)], radius=4, fill=(255, 255, 255, 180))

output_path = r"C:\Users\LENOVO\.gemini\antigravity\scratch\xauusd-ai-bot\don_aurelius_phone_texture.png"
img.save(output_path, "PNG")
print(f"Updated texture successfully!")
