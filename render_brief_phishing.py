#!/usr/bin/env python3
"""
render_brief_phishing.py - Rebuild of "How Hackers Phish Your Phone"
Strictly adheres to:
- VIDEO_GUIDELINES.md
- PHISHING_VIDEO_BRIEF.md

Main Object: Realistic smartphone (rounded body, glass screen, camera bump, side buttons,
working lock screen and fake banking UI) filling >60% of the frame. Real lit 3D materials,
perspective camera, warm desk accent, moving parts in every scene.
10 distinct shots cutting every 2-3s across 29.256s audio.
Big bottom-center captions (3-5 words, spoken word gold highlighted, NO paragraph box).
"""

import os
import sys
import json
import math
import shutil
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT_DIR = Path(__file__).resolve().parent
PIPELINE_DIR = ROOT_DIR / ".pipeline"
OUTPUT_DIR = PIPELINE_DIR / "output"
TIMINGS_FILE = PIPELINE_DIR / "phishing_chunks.json"
AUDIO_FILE = PIPELINE_DIR / "phishing_audio.mp3"

FONT_SANS_BOLD = "/data/data/com.termux/files/usr/share/fonts/TTF/DejaVuSans-Bold.ttf"
FONT_MONO_BOLD = "/data/data/com.termux/files/usr/share/fonts/TTF/DejaVuSansMono-Bold.ttf"
if not os.path.exists(FONT_SANS_BOLD):
    FONT_SANS_BOLD = "/system/fonts/Roboto-Regular.ttf"
if not os.path.exists(FONT_MONO_BOLD):
    FONT_MONO_BOLD = FONT_SANS_BOLD

font_hud_tab = ImageFont.truetype(FONT_MONO_BOLD, 18)
font_hud_label = ImageFont.truetype(FONT_MONO_BOLD, 22)
font_hero_num = ImageFont.truetype(FONT_SANS_BOLD, 105)
font_hero_unit = ImageFont.truetype(FONT_SANS_BOLD, 46)
font_hero_label = ImageFont.truetype(FONT_MONO_BOLD, 24)
font_callout_txt = ImageFont.truetype(FONT_MONO_BOLD, 20)
font_caption = ImageFont.truetype(FONT_SANS_BOLD, 46)
font_proof_title = ImageFont.truetype(FONT_SANS_BOLD, 24)
font_proof_body = ImageFont.truetype(FONT_SANS_BOLD, 20)
font_proof_stat = ImageFont.truetype(FONT_MONO_BOLD, 18)
font_cta_btn = ImageFont.truetype(FONT_SANS_BOLD, 44)
font_cta_sub = ImageFont.truetype(FONT_MONO_BOLD, 26)

font_ui_clock = ImageFont.truetype(FONT_SANS_BOLD, 64)
font_ui_date = ImageFont.truetype(FONT_SANS_BOLD, 22)
font_ui_bold = ImageFont.truetype(FONT_SANS_BOLD, 22)
font_ui_reg = ImageFont.truetype(FONT_SANS_BOLD, 18)
font_ui_code = ImageFont.truetype(FONT_MONO_BOLD, 18)
font_ui_btn = ImageFont.truetype(FONT_SANS_BOLD, 24)

W, H = 1080, 1920
FPS = 30

# Colors
C_BG = (12, 14, 22, 255)
C_CYAN = (0, 242, 254, 255)
C_AMBER = (255, 176, 32, 255)
C_GOLD = (255, 215, 0, 255)
C_RED = (255, 45, 85, 255)
C_EMERALD = (16, 185, 129, 255)
C_WHITE = (255, 255, 255, 255)
C_MUTED = (148, 163, 184, 255)

# Shot List Timings (10 distinct scenes across 29.256s)
SHOT_TIMELINE = [
    {"id": 1, "name": "01 HOOK // SMS ALERT", "start": 0.0, "end": 2.8, "dur": 2.8},
    {"id": 2, "name": "02 PULL-BACK // DESK", "start": 2.8, "end": 5.5, "dur": 2.7},
    {"id": 3, "name": "03 TAP // FAKE BANK", "start": 5.5, "end": 8.2, "dur": 2.7},
    {"id": 4, "name": "04 DIVE // CHIP INJECT", "start": 8.2, "end": 11.2, "dur": 3.0},
    {"id": 5, "name": "05 COUNTER // 11.2s", "start": 11.2, "end": 14.0, "dur": 2.8},
    {"id": 6, "name": "06 EXFIL // LAPTOP", "start": 14.0, "end": 17.0, "dur": 3.0},
    {"id": 7, "name": "07 PROOF // VERIZON 91%", "start": 17.0, "end": 20.5, "dur": 3.5},
    {"id": 8, "name": "08 DEFENSE // CLAMP", "start": 20.5, "end": 23.5, "dur": 3.0},
    {"id": 9, "name": "09 RESULT // 0% SAFE", "start": 23.5, "end": 26.2, "dur": 2.7},
    {"id": 10, "name": "10 CTA // @mwd1504", "start": 26.2, "end": 29.256, "dur": 3.056}
]

def get_audio_duration(audio_path):
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(audio_path)
    ]
    try:
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return float(res.stdout.strip())
    except Exception:
        return 29.256

def project_3d(x, y, z, cx=540, cy=960, yaw=0.0, pitch=25.0, zoom=1.0):
    """Perspective projection with camera yaw, pitch, and zoom."""
    yaw_rad = math.radians(yaw)
    pitch_rad = math.radians(pitch)
    x1 = x * math.cos(yaw_rad) - y * math.sin(yaw_rad)
    y1 = x * math.sin(yaw_rad) + y * math.cos(yaw_rad)
    z1 = z
    cos_p = math.cos(pitch_rad)
    sin_p = math.sin(pitch_rad)
    sx = cx + x1 * zoom
    sy = cy + (y1 * sin_p - z1 * cos_p) * zoom
    return (sx, sy)

def draw_hud_tabs(d, active_idx, scene_name):
    """Dynamic top HUD tab bar."""
    d.rounded_rectangle([60, 110, 1020, 195], radius=16, fill=(13, 17, 28, 240), outline=(0, 242, 254, 80), width=2)
    accent = C_AMBER if active_idx in [1, 3, 5, 7] else (C_RED if active_idx in [0, 2, 4] else C_EMERALD)
    d.ellipse([92, 144, 106, 158], fill=accent)
    d.ellipse([88, 140, 110, 162], outline=accent, width=1)
    d.text((124, 138), f"MOBILE THREAT // {scene_name}", font=font_hud_label, fill=(241, 245, 249, 255))

    total_steps = 10
    start_x = 720
    step_w = 24
    step_gap = 5
    for i in range(total_steps):
        sx = start_x + i * (step_w + step_gap)
        is_cur = (i == active_idx)
        c_fill = accent if is_cur else (30, 41, 59, 140)
        c_line = accent if is_cur else (71, 85, 105, 100)
        d.rounded_rectangle([sx, 142, sx + step_w, 164], radius=4, fill=c_fill, outline=c_line, width=1)
        if is_cur:
            d.text((sx + 5, 144), str(i + 1), font=font_hud_tab, fill=(10, 12, 18, 255))

def draw_bottom_captions(d, t, timings_data):
    """Big bottom-center captions, 3-5 words, spoken word gold highlighted, NO paragraph box."""
    if not timings_data:
        return
    active_chunk = None
    for chunk in timings_data:
        if chunk["start"] <= t <= chunk["end"]:
            active_chunk = chunk
            break
        elif t < chunk["start"]:
            if active_chunk is None and t > chunk["start"] - 0.2:
                active_chunk = chunk
                break
    if not active_chunk:
        if t >= timings_data[-1]["start"]:
            active_chunk = timings_data[-1]
        else:
            return

    words = active_chunk["words"]
    word_starts = active_chunk.get("word_starts", [])
    space_w = font_caption.getbbox(" ")[2] - font_caption.getbbox(" ")[0]
    word_metrics = []
    total_w = 0
    for w in words:
        bbox = font_caption.getbbox(w)
        w_w = bbox[2] - bbox[0]
        word_metrics.append((w, w_w))
        total_w += w_w + space_w
    total_w -= space_w

    start_x = (W - total_w) // 2
    y_pos = 1630

    active_word_idx = -1
    for i, w_start in enumerate(word_starts):
        if t >= w_start:
            active_word_idx = i

    cur_x = start_x
    for i, (w, w_w) in enumerate(word_metrics):
        is_active = (i == active_word_idx)
        if is_active:
            for dx, dy in [(-3,0),(3,0),(0,-3),(0,3),(-2,-2),(2,2)]:
                d.text((cur_x + dx, y_pos + dy), w, font=font_caption, fill=(0, 0, 0, 240))
            d.text((cur_x, y_pos), w, font=font_caption, fill=C_GOLD)
            d.rounded_rectangle([cur_x - 2, y_pos + 56, cur_x + w_w + 2, y_pos + 61], radius=2, fill=C_AMBER)
        else:
            d.text((cur_x + 2, y_pos + 2), w, font=font_caption, fill=(0, 0, 0, 180))
            d.text((cur_x, y_pos), w, font=font_caption, fill=C_WHITE)
        cur_x += w_w + space_w

def draw_callout_line(d, start_pt, end_pt, text, accent_color=C_CYAN, align_right=False):
    """Draws a clean pointer line to a sub-part label."""
    d.ellipse([start_pt[0]-4, start_pt[1]-4, start_pt[0]+4, start_pt[1]+4], fill=accent_color)
    d.ellipse([start_pt[0]-8, start_pt[1]-8, start_pt[0]+8, start_pt[1]+8], outline=accent_color, width=1)
    mid_pt = (end_pt[0] - 20 if not align_right else end_pt[0] + 20, end_pt[1])
    d.line([start_pt, mid_pt, end_pt], fill=accent_color, width=2)

    bbox = font_callout_txt.getbbox(text)
    txt_w = bbox[2] - bbox[0]
    box_w = txt_w + 28
    box_h = 38
    bx = end_pt[0] if not align_right else end_pt[0] - box_w
    by = end_pt[1] - 19
    d.rounded_rectangle([bx, by, bx + box_w, by + box_h], radius=8,
                        fill=(15, 20, 32, 230), outline=accent_color, width=1)
    d.text((bx + 14, by + 8), text, font=font_callout_txt, fill=C_WHITE)

def draw_realistic_phone(d, px, py, pw=480, ph=960, radius=52, angle_deg=0.0,
                         screen_content="lockscreen", alert_y=0, alert_pulse=0.0):
    """
    Renders a realistic smartphone with rounded chassis, aluminum frame, side buttons,
    camera bump, speaker slit, and UI screen. Fills >60% of the screen.
    """
    # 1. Soft Multi-Tier Contact Shadows
    for expand, alpha in [(36, 30), (18, 60), (4, 110)]:
        d.rounded_rectangle([px - expand, py - expand + 16, px + pw + expand, py + ph + expand + 16],
                            radius=radius + expand, fill=(5, 7, 14, alpha))

    # 2. Side Buttons
    # Left: Volume buttons
    d.rounded_rectangle([px - 7, py + 220, px, py + 290], radius=3, fill=(100, 115, 145, 255))
    d.rounded_rectangle([px - 7, py + 320, px, py + 390], radius=3, fill=(100, 115, 145, 255))
    # Right: Power button
    d.rounded_rectangle([px + pw, py + 260, px + pw + 7, py + 360], radius=3, fill=(100, 115, 145, 255))

    # 3. Outer Titanium/Aluminum Chassis
    d.rounded_rectangle([px, py, px + pw, py + ph], radius=radius,
                        fill=(38, 44, 60, 255), outline=(90, 105, 135, 255), width=3)

    # 4. Inner Screen Bezel
    d.rounded_rectangle([px + 14, py + 14, px + pw - 14, py + ph - 14], radius=radius - 8,
                        fill=(10, 12, 18, 255), outline=(25, 30, 42, 255), width=2)

    # 5. OLED Screen Surface
    sx, sy, sw, sh = px + 22, py + 22, pw - 44, ph - 44
    d.rounded_rectangle([sx, sy, sx + sw, sy + sh], radius=radius - 14, fill=(14, 18, 28, 255))

    # 6. Top Dynamic Island & Selfie Camera
    d.rounded_rectangle([px + (pw // 2) - 60, py + 30, px + (pw // 2) + 60, py + 62],
                        radius=16, fill=(5, 6, 10, 255))
    d.ellipse([px + (pw // 2) - 40, py + 40, px + (pw // 2) - 26, py + 54], fill=(12, 16, 26, 255))

    # 7. Screen Contents based on shot
    if screen_content == "lockscreen":
        # Time & Date
        d.text((px + (pw // 2) - 80, py + 150), "09:41", font=font_ui_clock, fill=C_WHITE)
        d.text((px + (pw // 2) - 72, py + 235), "Tuesday, Nov 10", font=font_ui_date, fill=C_MUTED)

        # In-Display Fingerprint Sensor Icon at bottom
        fp_x, fp_y = px + (pw // 2), py + ph - 160
        d.ellipse([fp_x - 32, fp_y - 32, fp_x + 32, fp_y + 32], outline=C_CYAN, width=2)
        d.arc([fp_x - 22, fp_y - 22, fp_x + 22, fp_y + 22], start=45, end=315, fill=C_CYAN, width=2)
        d.arc([fp_x - 12, fp_y - 12, fp_x + 12, fp_y + 12], start=45, end=315, fill=C_CYAN, width=2)

        # Incoming Phishing SMS Notification Card (Sliding down)
        card_w = sw - 32
        card_h = 190
        card_x = sx + 16
        card_y = sy + 180 + alert_y

        d.rounded_rectangle([card_x, card_y, card_x + card_w, card_y + card_h], radius=20,
                            fill=(24, 16, 22, 245), outline=C_RED, width=2)

        # App icon & Header
        d.rounded_rectangle([card_x + 16, card_y + 14, card_x + 42, card_y + 40], radius=6, fill=C_RED)
        d.text((card_x + 21, card_y + 16), "💬", font=font_ui_bold)
        d.text((card_x + 52, card_y + 16), "MESSAGES • NOW", font=font_ui_reg, fill=C_MUTED)

        # Message Text
        d.text((card_x + 18, card_y + 52), "CHASE: Suspicious $840 transfer.", font=font_ui_bold, fill=C_WHITE)
        d.text((card_x + 18, card_y + 82), "Action required. Verify account now:", font=font_ui_reg, fill=(226, 232, 240, 255))

        # Glowing Red Malicious Link
        link_border = C_RED if alert_pulse > 0.5 else (255, 120, 140, 255)
        d.rounded_rectangle([card_x + 18, card_y + 120, card_x + card_w - 18, card_y + 166], radius=10,
                            fill=(45, 12, 18, 255), outline=link_border, width=2)
        d.text((card_x + 30, card_y + 130), "chase-fraud-verify.cc/login", font=font_ui_code, fill=C_RED)

    elif screen_content == "fake_bank":
        # Fake Banking Login Screen
        # Blue Header Banner
        d.rounded_rectangle([sx, sy + 70, sx + sw, sy + 160], radius=8, fill=(16, 44, 98, 255))
        d.text((sx + (sw // 2) - 80, sy + 100), "CHASE ONLINE", font=font_ui_bold, fill=C_WHITE)

        # Title
        d.text((sx + 36, sy + 200), "Sign In to Your Account", font=font_ui_bold, fill=C_WHITE)
        d.text((sx + 36, sy + 236), "Security authentication check", font=font_ui_reg, fill=C_MUTED)

        # Input 1: Username
        d.text((sx + 36, sy + 280), "Username / Email", font=font_ui_reg, fill=C_MUTED)
        d.rounded_rectangle([sx + 36, sy + 310, sx + sw - 36, sy + 370], radius=10,
                            fill=(20, 26, 40, 255), outline=C_CYAN, width=1)
        d.text((sx + 50, sy + 326), "alex.rivers@email.com", font=font_ui_reg, fill=C_WHITE)

        # Input 2: Password
        d.text((sx + 36, sy + 400), "Password", font=font_ui_reg, fill=C_MUTED)
        d.rounded_rectangle([sx + 36, sy + 430, sx + sw - 36, sy + 490], radius=10,
                            fill=(20, 26, 40, 255), outline=(71, 85, 105, 255), width=1)
        d.text((sx + 50, sy + 448), "••••••••••••••", font=font_ui_reg, fill=C_WHITE)

        # Sign In Button
        d.rounded_rectangle([sx + 36, sy + 530, sx + sw - 36, sy + 600], radius=12,
                            fill=(18, 90, 210, 255), outline=C_CYAN, width=2)
        d.text((sx + (sw // 2) - 60, sy + 550), "SECURE LOGIN", font=font_ui_btn, fill=C_WHITE)

        # Warning Watermark: "SPOOFED PHISHING DOMAIN"
        d.rounded_rectangle([sx + 36, sy + 630, sx + sw - 36, sy + 680], radius=8,
                            fill=(50, 14, 20, 230), outline=C_RED, width=1)
        d.text((sx + 50, sy + 645), "⚠️ SPOOFED DOMAIN DETECTED", font=font_ui_code, fill=C_RED)

    elif screen_content == "shield_active":
        # Green Protected State
        d.text((px + (pw // 2) - 80, py + 150), "09:41", font=font_ui_clock, fill=C_WHITE)
        card_w = sw - 32
        card_h = 190
        card_x = sx + 16
        card_y = sy + 240

        d.rounded_rectangle([card_x, card_y, card_x + card_w, card_y + card_h], radius=20,
                            fill=(14, 32, 26, 245), outline=C_EMERALD, width=3)
        d.text((card_x + 20, card_y + 24), "🛡️ DEFENSE ACTIVE // BLOCKED", font=font_ui_bold, fill=C_EMERALD)
        d.text((card_x + 20, card_y + 64), "Malicious phishing domain intercepted.", font=font_ui_reg, fill=C_WHITE)
        d.text((card_x + 20, card_y + 94), "Device enclave locked. Zero tokens leaked.", font=font_ui_reg, fill=C_MUTED)
        d.rounded_rectangle([card_x + 20, card_y + 130, card_x + card_w - 20, card_y + 172], radius=8,
                            fill=(20, 52, 42, 255), outline=C_EMERALD, width=1)
        d.text((card_x + 36, card_y + 140), "STATUS: BULLETPROOF", font=font_ui_code, fill=C_EMERALD)

def render_scene_frame(frame_idx, total_frames, timings_data):
    """Renders a single frame according to the 10-shot list from the brief."""
    t = frame_idx / float(FPS)
    total_duration = total_frames / float(FPS)
    progress = min(1.0, max(0.0, t / total_duration))

    # Determine active shot
    active_idx = 0
    for idx, sc in enumerate(SHOT_TIMELINE):
        if sc["start"] <= t <= sc["end"]:
            active_idx = idx
            break
        elif t > sc["end"]:
            active_idx = idx

    current_shot = SHOT_TIMELINE[active_idx]
    shot_dur = current_shot["dur"]
    shot_rel_t = max(0.0, min(1.0, (t - current_shot["start"]) / shot_dur))
    pulse = (math.sin(t * 8.0) + 1.0) * 0.5
    float_z = math.sin(t * 3.4) * 10.0

    im = Image.new('RGBA', (W, H), C_BG)
    d = ImageDraw.Draw(im)

    # Warm desk glow on top-left (Desk lamp ambiance)
    d.ellipse([-100, 200, 1180, 1600], fill=(20, 26, 40, 255))
    d.ellipse([-50, 250, 700, 950], fill=(32, 36, 56, 120))  # Warm lamp pool

    # ------------------ SHOT-BY-SHOT RENDERING ------------------

    if current_shot["id"] == 1:
        # Shot 1: Macro Push-in on Phone as SMS slides in
        # Camera push-in from zoom 1.05 to 1.25
        zoom = 1.05 + shot_rel_t * 0.20
        pw = int(480 * zoom)
        ph = int(960 * zoom)
        px = (W - pw) // 2
        py = int(480 - (shot_rel_t * 40))

        # SMS sliding in
        alert_y = int((1.0 - min(1.0, shot_rel_t * 1.5)) * -140)
        draw_realistic_phone(d, px, py, pw=pw, ph=ph, screen_content="lockscreen",
                             alert_y=alert_y, alert_pulse=pulse)

        # Callouts pointing to parts
        draw_callout_line(d, (px + 60, py + 360 + alert_y), (100, 380), "SMS SPOOF DETECTED", C_RED)
        draw_callout_line(d, (px + pw - 60, py + 410 + alert_y), (980, 430), "MALICIOUS LINK", C_RED, align_right=True)

    elif current_shot["id"] == 2:
        # Shot 2: Pull Back: Phone on Desk, Hand Reaches for It
        zoom = 1.15 - (shot_rel_t * 0.18)
        pw = int(440 * zoom)
        ph = int(880 * zoom)
        px = (W - pw) // 2
        py = 520

        draw_realistic_phone(d, px, py, pw=pw, ph=ph, screen_content="lockscreen", alert_y=0, alert_pulse=pulse)

        # Stylized 3D Hand/Finger reaching down
        finger_x = px + (pw // 2) + 30
        finger_y = py + 380 + int(shot_rel_t * 80)
        # Finger silhouette with warm edge lighting
        d.rounded_rectangle([finger_x - 36, finger_y - 200, finger_x + 36, finger_y],
                            radius=30, fill=(65, 50, 48, 240), outline=C_AMBER, width=2)
        d.ellipse([finger_x - 28, finger_y - 36, finger_x + 28, finger_y + 20],
                  fill=(85, 65, 60, 255), outline=C_GOLD, width=1)

        # Callouts on specific sub-parts
        draw_callout_line(d, (px + (pw // 2), py + ph - 160), (100, 1150), "IN-DISPLAY FINGERPRINT", C_CYAN)
        draw_callout_line(d, (px + pw - 20, py + 260), (980, 780), "TITANIUM CHASSIS", C_AMBER, align_right=True)
        draw_callout_line(d, (px + 40, py + 180), (100, 680), "OLED LOCK SCREEN", C_CYAN)

    elif current_shot["id"] == 3:
        # Shot 3: Thumb taps the link. Screen switches to fake login page
        pw = 500
        ph = 1000
        px = (W - pw) // 2
        py = 460

        draw_realistic_phone(d, px, py, pw=pw, ph=ph, screen_content="fake_bank")

        # Expanding Tap Ripple
        tap_x = px + 120
        tap_y = py + 480
        ripple_r = int((shot_rel_t * 120) % 90)
        d.ellipse([tap_x - ripple_r, tap_y - ripple_r, tap_x + ripple_r, tap_y + ripple_r],
                  outline=C_RED, width=3)

        # Thumb pressing
        d.ellipse([tap_x - 35, tap_y - 35, tap_x + 35, tap_y + 35],
                  fill=(85, 65, 60, 230), outline=C_AMBER, width=2)

        draw_callout_line(d, (tap_x, tap_y), (100, 760), "1-TAP PHISHING TRIGGER", C_RED)
        draw_callout_line(d, (px + pw - 40, py + 560), (980, 880), "FAKE LOGIN PAGE", C_AMBER, align_right=True)

    elif current_shot["id"] == 4:
        # Shot 4: Camera dives through the screen into motherboard chip
        # Teardown internal motherboard PCB view
        d.rounded_rectangle([180, 420, 900, 1480], radius=40,
                            fill=(18, 30, 26, 255), outline=C_CYAN, width=3)

        # Copper Circuit Traces
        for trace_y in range(480, 1420, 70):
            d.line([(220, trace_y), (860, trace_y)], fill=(32, 60, 50, 180), width=2)
        for trace_x in range(240, 840, 90):
            d.line([(trace_x, 460), (trace_x, 1440)], fill=(32, 60, 50, 180), width=2)

        # Central Hardware Enclave Socket
        d.rounded_rectangle([340, 740, 740, 1140], radius=24,
                            fill=(14, 20, 32, 255), outline=C_GOLD, width=3)
        d.text((370, 770), "HARDWARE SECURITY ENCLAVE", font=font_proof_body, fill=C_GOLD)

        # Glowing Trojan Token Chip Sliding into Socket (Moving Part)
        chip_slide = min(180, int(shot_rel_t * 220))
        chip_y = 520 + chip_slide
        d.rounded_rectangle([380, chip_y, 700, chip_y + 160], radius=16,
                            fill=(55, 12, 24, 255), outline=C_RED, width=3)
        d.text((410, chip_y + 40), "TROJAN TOKEN CHIP", font=font_hero_label, fill=C_WHITE)
        d.text((430, chip_y + 90), "[SESSION_STEALER.SO]", font=font_callout_txt, fill=C_RED)

        # Electric Spark Arcs
        if chip_slide > 120:
            for s_i in range(6):
                arc_x = 360 + s_i * 60
                d.line([(arc_x, 900), (arc_x + 10, 915)], fill=C_CYAN, width=3)

        draw_callout_line(d, (380, chip_y + 80), (100, 680), "SUB-PART: ENCLAVE CHIP", C_CYAN)
        draw_callout_line(d, (700, chip_y + 80), (980, 820), "PAYLOAD INJECTED", C_RED, align_right=True)

    elif current_shot["id"] == 5:
        # Shot 5: Big Counter 11.2s counting up over fast orbit of phone
        zoom = 1.05 + shot_rel_t * 0.15
        pw = int(420 * zoom)
        ph = int(840 * zoom)
        px = (W - pw) // 2
        py = 560
        draw_realistic_phone(d, px, py, pw=pw, ph=ph, screen_content="fake_bank")

        # BIG HERO NUMBER: Animated 11.2s Counting Up
        ease = 0.5 - 0.5 * math.cos(shot_rel_t * math.pi)
        cur_sec = ease * 11.2

        card_y = 480
        d.rounded_rectangle([160, card_y, 920, card_y + 250], radius=24,
                            fill=(14, 18, 30, 245), outline=C_RED, width=3)

        # Radial Gauge Arc
        arc_x, arc_y = 300, card_y + 125
        d.ellipse([arc_x - 70, arc_y - 70, arc_x + 70, arc_y + 70], outline=(40, 50, 70, 255), width=8)
        end_angle = int((cur_sec / 11.2) * 260)
        d.arc([arc_x - 70, arc_y - 70, arc_x + 70, arc_y + 70], start=-90, end=-90 + end_angle, fill=C_RED, width=10)

        # Digits fully inside card
        d.text((410, card_y + 40), f"{cur_sec:.1f}s", font=font_hero_num, fill=C_RED)
        d.text((415, card_y + 155), "TIME TO COMPROMISE: 11.2s", font=font_hero_label, fill=C_AMBER)

    elif current_shot["id"] == 6:
        # Shot 6: Data Exfiltrating to Hacker Laptop
        # Left: Phone
        pw, ph = 340, 680
        px, py = 120, 600
        draw_realistic_phone(d, px, py, pw=pw, ph=ph, screen_content="fake_bank")

        # Right: Hacker Laptop
        lx, ly, lw, lh = 580, 720, 420, 300
        # Laptop Screen
        d.rounded_rectangle([lx, ly, lx + lw, ly + lh], radius=14,
                            fill=(10, 16, 24, 255), outline=C_RED, width=2)
        # Terminal code lines
        d.text((lx + 20, ly + 20), "> EXFILTRATION TERMINAL", font=font_ui_code, fill=C_RED)
        d.text((lx + 20, ly + 56), "CONNECT: 192.168.1.44 [OK]", font=font_ui_code, fill=C_CYAN)
        d.text((lx + 20, ly + 90), "DUMPING KEYCHAIN...", font=font_ui_code, fill=C_WHITE)
        d.text((lx + 20, ly + 124), "HARVESTED: 42 COOKIES", font=font_ui_code, fill=C_AMBER)
        # Laptop Keyboard Base
        d.polygon([(lx - 30, ly + lh), (lx + lw + 30, ly + lh),
                   (lx + lw + 10, ly + lh + 50), (lx - 10, ly + lh + 50)],
                  fill=(24, 30, 44, 255), outline=(50, 60, 80, 255))

        # Floating Labeled Data Cubes flying across desk
        data_items = [
            ("🍪 SESSION_COOKIE", 0.0),
            ("🔑 BANK_PWD_HASH", 0.33),
            ("📲 2FA_OTP: 94021", 0.66)
        ]
        for name, off in data_items:
            prog = (shot_rel_t + off) % 1.0
            fly_x = int(px + pw + prog * (lx - px - pw))
            fly_y = int(py + 200 + math.sin(prog * math.pi) * -80)
            d.rounded_rectangle([fly_x - 100, fly_y - 20, fly_x + 100, fly_y + 20], radius=8,
                                fill=(45, 14, 22, 240), outline=C_GOLD, width=1)
            d.text((fly_x - 85, fly_y - 12), name, font=font_proof_stat, fill=C_WHITE)

        draw_callout_line(d, (lx + 200, ly), (980, 640), "HACKER RECEIVER SERVER", C_RED, align_right=True)

    elif current_shot["id"] == 7:
        # Shot 7: PROOF BEAT: Real Verizon DBIR 91% Stat Chart
        card_w = 880
        card_h = 560
        card_x = (W - card_w) // 2
        card_y = 520

        # Glass Proof Card with generous margins
        d.rounded_rectangle([card_x, card_y, card_x + card_w, card_y + card_h], radius=28,
                            fill=(14, 18, 30, 245), outline=C_RED, width=3)

        # Header with Shield Badge
        d.ellipse([card_x + 36, card_y + 36, card_x + 68, card_y + 68], fill=C_RED)
        d.text((card_x + 44, card_y + 40), "🛡️", font=font_ui_bold)
        d.text((card_x + 84, card_y + 40), "VERIZON DATA BREACH REPORT (DBIR)", font=font_proof_title, fill=C_WHITE)

        # 91% Dial Gauge
        dial_cx, dial_cy = card_x + 160, card_y + 210
        d.ellipse([dial_cx - 75, dial_cy - 75, dial_cx + 75, dial_cy + 75], outline=(40, 50, 70, 255), width=8)
        d.arc([dial_cx - 75, dial_cy - 75, dial_cx + 75, dial_cy + 75], start=-90, end=240, fill=C_RED, width=12)
        d.text((dial_cx - 52, dial_cy - 35), "91%", font=font_hero_unit, fill=C_RED)

        # Bar Chart of Attack Vectors
        chart_x = card_x + 280
        d.text((chart_x, card_y + 130), "PRIMARY ATTACK VECTOR", font=font_hero_label, fill=C_AMBER)

        # Bar 1: Phishing 91%
        d.text((chart_x, card_y + 175), "Phishing Links: 91%", font=font_proof_body, fill=C_WHITE)
        d.rounded_rectangle([chart_x, card_y + 205, chart_x + 500, card_y + 225], radius=6, fill=C_RED)

        # Bar 2: Brute Force 5%
        d.text((chart_x, card_y + 245), "Brute Force: 5%", font=font_proof_body, fill=C_MUTED)
        d.rounded_rectangle([chart_x, card_y + 275, chart_x + 30, card_y + 295], radius=6, fill=(71, 85, 105, 255))

        # Bar 3: Zero-Day 4%
        d.text((chart_x, card_y + 315), "System Zero-Day: 4%", font=font_proof_body, fill=C_MUTED)
        d.rounded_rectangle([chart_x, card_y + 345, chart_x + 24, card_y + 365], radius=6, fill=(71, 85, 105, 255))

        # Official Stat Quote Box (Fully inside card)
        d.rounded_rectangle([card_x + 36, card_y + 440, card_x + card_w - 36, card_y + 515], radius=12,
                            fill=(26, 18, 24, 255), outline=C_AMBER, width=1)
        d.text((card_x + 56, card_y + 455), "“91% of cyber breaches start with a phishing message”",
               font=font_proof_stat, fill=C_AMBER)
        d.text((card_x + 56, card_y + 482), "Source: Verizon DBIR & CISA Cyber Defense Report",
               font=font_proof_stat, fill=C_MUTED)

    elif current_shot["id"] == 8:
        # Shot 8: Defense Clamps Over Link and Turns Green
        pw, ph = 480, 960
        px = (W - pw) // 2
        py = 500
        draw_realistic_phone(d, px, py, pw=pw, ph=ph, screen_content="shield_active")

        # Heavy 3D Security Shield Clamp Snapping Down (Moving Part)
        clamp_drop = min(60, int(shot_rel_t * 90))
        clamp_y = py + 260 + clamp_drop
        d.rounded_rectangle([px + 30, clamp_y, px + pw - 30, clamp_y + 70], radius=14,
                            fill=(20, 60, 48, 240), outline=C_EMERALD, width=3)
        d.text((px + 60, clamp_y + 20), "🔒 HARDWARE ACCESS CLAMP DEPLOYED", font=font_proof_body, fill=C_WHITE)

        draw_callout_line(d, (px + 60, clamp_y + 35), (100, 780), "ENCLAVE CLAMP LOCKED", C_EMERALD)
        draw_callout_line(d, (px + pw - 60, py + 480), (980, 920), "MALICIOUS LINK TERMINATED", C_CYAN, align_right=True)

    elif current_shot["id"] == 9:
        # Shot 9: Result 0%, Phone Glowing Safe
        pw, ph = 460, 920
        px = (W - pw) // 2
        py = 520
        draw_realistic_phone(d, px, py, pw=pw, ph=ph, screen_content="shield_active")

        # Luminous Spherical Energy Shield Ring
        shield_r = 320 + pulse * 25
        d.ellipse([540 - shield_r, 960 - shield_r, 540 + shield_r, 960 + shield_r], outline=C_CYAN, width=3)

        # BIG HERO NUMBER: 0% VULNERABILITY
        card_y = 500
        d.rounded_rectangle([180, card_y, 900, card_y + 220], radius=24,
                            fill=(12, 28, 24, 245), outline=C_EMERALD, width=3)
        d.text((240, card_y + 35), "0%", font=font_hero_num, fill=C_EMERALD)
        d.text((450, card_y + 60), "VULNERABILITY", font=font_hero_unit, fill=C_GOLD)
        d.text((245, card_y + 150), "PHONE VAULT IMPERVIOUS TO PHISHING", font=font_hero_label, fill=C_WHITE)

    else:
        # Shot 10: CTA "Stay bulletproof" with @mwd1504
        pw, ph = 420, 840
        px = (W - pw) // 2
        py = 560
        draw_realistic_phone(d, px, py, pw=pw, ph=ph, screen_content="shield_active")

        # 3D Glass CTA Monolith (Centered on Screen)
        cta_y = 520
        d.rounded_rectangle([150, cta_y, 930, cta_y + 300], radius=28,
                            fill=(14, 18, 32, 245), outline=C_GOLD, width=3)

        # Glowing CTA Button Slab
        btn_y = cta_y + 45
        d.rounded_rectangle([190, btn_y, 890, btn_y + 100], radius=20,
                            fill=(16, 185, 129, 235), outline=C_GOLD, width=2)
        btn_bbox = font_cta_btn.getbbox("STAY BULLETPROOF")
        btn_w = btn_bbox[2] - btn_bbox[0]
        d.text(((1080 - btn_w) // 2, btn_y + 26), "STAY BULLETPROOF", font=font_cta_btn, fill=(10, 12, 18, 255))

        # Handle "@mwd1504" + Verified Badge
        handle_str = "@mwd1504"
        h_bbox = font_cta_sub.getbbox(handle_str)
        h_w = h_bbox[2] - h_bbox[0]
        h_x = (1080 - h_w) // 2
        d.text((h_x, cta_y + 175), handle_str, font=font_cta_sub, fill=C_CYAN)

        # Verified badge
        d.ellipse([h_x + h_w + 14, cta_y + 180, h_x + h_w + 34, cta_y + 200], fill=C_CYAN)
        d.text((h_x + h_w + 18, cta_y + 178), "✓", font=font_hud_tab, fill=(10, 12, 18, 255))

        d.text((280, cta_y + 235), "Follow for Mobile Cyber Defense & High-Security Tech",
               font=font_proof_body, fill=C_MUTED)

    # ------------------ TOP HUD TABS & CAPTIONS ------------------
    draw_hud_tabs(d, active_idx, current_shot["name"])
    draw_bottom_captions(d, t, timings_data)

    # Bottom Progress Bar
    d.rounded_rectangle([80, 1780, 1000, 1788], radius=4, fill=(30, 41, 59, 160))
    bar_w = int(920 * progress)
    if bar_w > 0:
        bar_col = C_GOLD if active_idx == 9 else C_CYAN
        d.rounded_rectangle([80, 1780, 80 + bar_w, 1788], radius=4, fill=bar_col)

    return im

def render_final_brief_video():
    output_path = OUTPUT_DIR / "How_Hackers_Phish_Your_Phone.mp4"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(TIMINGS_FILE, "r", encoding="utf-8") as f:
        timings_data = json.load(f)

    total_duration = get_audio_duration(AUDIO_FILE)
    total_frames = int(math.ceil(total_duration * FPS))
    print(f"🎵 Audio Duration: {total_duration:.3f}s")
    print(f"🚀 Rendering {total_frames} frames ({len(SHOT_TIMELINE)} shots, 1080x1920 @ {FPS} FPS)...")

    cmd_ffmpeg = [
        "ffmpeg", "-y",
        "-f", "rawvideo",
        "-pix_fmt", "rgba",
        "-s", f"{W}x{H}",
        "-r", str(FPS),
        "-i", "-",
        "-i", str(AUDIO_FILE),
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        str(output_path)
    ]

    proc = subprocess.Popen(cmd_ffmpeg, stdin=subprocess.PIPE, stderr=subprocess.PIPE)

    try:
        for f in range(total_frames):
            frame_im = render_scene_frame(f, total_frames, timings_data)
            proc.stdin.write(frame_im.tobytes())
            if f % (FPS * 4) == 0:
                print(f"  ⚡ Rendered {f}/{total_frames} frames ({f/total_frames*100:.1f}%)...")
        proc.stdin.close()
    except Exception as e:
        proc.kill()
        print(f"Render pipeline exception: {e}", file=sys.stderr)
        sys.exit(1)

    _, stderr = proc.communicate()
    if proc.returncode != 0:
        print(f"FFmpeg error:\n{stderr.decode('utf-8', errors='ignore')}", file=sys.stderr)
        sys.exit(1)

    out_size = os.path.getsize(output_path)
    print(f"✅ Rendered successfully: {output_path} ({out_size} bytes)")

    # Copy to Download directory
    download_dir = Path("/sdcard/Download")
    if download_dir.exists() and download_dir.is_dir():
        dest = download_dir / "How_Hackers_Phish_Your_Phone.mp4"
        shutil.copyfile(output_path, dest)
        print(f"📲 Synchronized to Downloads: {dest}")

if __name__ == "__main__":
    render_final_brief_video()
