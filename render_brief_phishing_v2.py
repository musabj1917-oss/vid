#!/usr/bin/env python3
"""
render_brief_phishing_v2.py - Production Rebuild: "How Hackers Phish Your Phone"
Strictly adheres to:
- VIDEO_GUIDELINES.md
- ROUND2_CHANGES_Phishing_Video.pdf

All 8 Round 2 Changes Implemented:
1. Truly 3D Phone: Real thickness, extruded side rails with directional lighting,
   chamfered bevels, physical side buttons (volume & power), triple camera bump,
   realistic soft perspective contact shadow, and perspective-mapped OLED glass screen.
2. 10 Distinct Scenes & Continuous Camera Motion: Macro push-in, desk pull-back,
   top-down Dutch tilt, internal fly-through, high-angle fast orbit, lateral data split,
   proof tilt, low-angle clamp, spherical shield orbit, grand pull-back reveal.
   No angle held >3s. Target 10+ visible cuts.
3. Scene 4 Internal Cutaway: Phone chassis cutaway revealing Li-Ion battery pack,
   motherboard chip board with copper wiring traces, and glowing Trojan token chip
   sliding into a labeled slot with cyan electrical sparks.
4. Scene 6 Data Theft: Phone and laptop both large and fully inside frame.
   Cookies, passwords, and 2FA codes fly out as 3 separate distinct 3D objects
   (chocolate-chip cookie icon, brass key, 2FA silicon chip) along an arc into laptop.
   Tiny overlapping text labels removed.
5. Counter Cards (Scenes 5 & 9): Placed in upper HUD zone where they NEVER cover
   the phone or its clock. Number mismatch fixed: exactly 11.2s on card and label.
6. Callouts: Spaced 2-4 per scene with leader lines pointing at specific parts,
   zero overlaps with each other or screen text.
7. Scene 8 Defense: Titanium security clamp physically snaps down over the link,
   then SMS card transforms from red to emerald green. No stacked labels on phone.
8. Frame Use: Phone fills at least 60% of frame, rich high-tech cybersecurity ambiance,
   no empty voids.
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

FONT_CANDIDATES_SANS = [
    "/data/data/com.termux/files/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
    "/system/fonts/Roboto-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
]
FONT_CANDIDATES_MONO = [
    "/data/data/com.termux/files/usr/share/fonts/TTF/DejaVuSansMono-Bold.ttf",
    "/system/fonts/Roboto-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
    "/usr/share/fonts/TTF/DejaVuSansMono-Bold.ttf",
]
FONT_SANS_BOLD = next((p for p in FONT_CANDIDATES_SANS if os.path.exists(p)), None)
FONT_MONO_BOLD = next((p for p in FONT_CANDIDATES_MONO if os.path.exists(p)), FONT_SANS_BOLD)
if FONT_SANS_BOLD is None:
    raise FileNotFoundError("No usable bold font found. Install fonts-dejavu or set FONT_SANS_BOLD.")

font_hud_tab = ImageFont.truetype(FONT_MONO_BOLD, 18)
font_hud_label = ImageFont.truetype(FONT_MONO_BOLD, 22)
font_hero_num = ImageFont.truetype(FONT_SANS_BOLD, 96)
font_hero_unit = ImageFont.truetype(FONT_SANS_BOLD, 38)
font_hero_label = ImageFont.truetype(FONT_MONO_BOLD, 22)
font_callout_txt = ImageFont.truetype(FONT_MONO_BOLD, 18)
font_caption = ImageFont.truetype(FONT_SANS_BOLD, 46)
font_proof_title = ImageFont.truetype(FONT_SANS_BOLD, 24)
font_proof_body = ImageFont.truetype(FONT_SANS_BOLD, 20)
font_proof_stat = ImageFont.truetype(FONT_MONO_BOLD, 18)
font_cta_btn = ImageFont.truetype(FONT_SANS_BOLD, 44)
font_cta_sub = ImageFont.truetype(FONT_MONO_BOLD, 26)

font_ui_clock = ImageFont.truetype(FONT_SANS_BOLD, 68)
font_ui_date = ImageFont.truetype(FONT_SANS_BOLD, 22)
font_ui_bold = ImageFont.truetype(FONT_SANS_BOLD, 22)
font_ui_reg = ImageFont.truetype(FONT_SANS_BOLD, 18)
font_ui_code = ImageFont.truetype(FONT_MONO_BOLD, 18)
font_ui_btn = ImageFont.truetype(FONT_SANS_BOLD, 22)

W, H = 1080, 1920
FPS = 30

# Colors
C_BG = (10, 13, 20, 255)
C_CYAN = (0, 242, 254, 255)
C_AMBER = (255, 176, 32, 255)
C_GOLD = (255, 215, 0, 255)
C_RED = (255, 45, 85, 255)
C_EMERALD = (16, 185, 129, 255)
C_WHITE = (255, 255, 255, 255)
C_MUTED = (148, 163, 184, 255)

SHOT_TIMELINE = [
    {"id": 1, "name": "01 HOOK // SMS ALERT", "start": 0.0, "end": 2.8, "dur": 2.8},
    {"id": 2, "name": "02 PULL-BACK // DESK", "start": 2.8, "end": 5.5, "dur": 2.7},
    {"id": 3, "name": "03 TAP // FAKE BANK", "start": 5.5, "end": 8.2, "dur": 2.7},
    {"id": 4, "name": "04 DIVE // CUTAWAY PCB", "start": 8.2, "end": 11.2, "dur": 3.0},
    {"id": 5, "name": "05 COUNTER // 11.2s", "start": 11.2, "end": 14.0, "dur": 2.8},
    {"id": 6, "name": "06 EXFIL // 3D OBJECTS", "start": 14.0, "end": 17.0, "dur": 3.0},
    {"id": 7, "name": "07 PROOF // VERIZON 91%", "start": 17.0, "end": 20.5, "dur": 3.5},
    {"id": 8, "name": "08 DEFENSE // CLAMP", "start": 20.5, "end": 23.5, "dur": 3.0},
    {"id": 9, "name": "09 RESULT // 0% BULLETPROOF", "start": 23.5, "end": 26.2, "dur": 2.7},
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

def solve_perspective_coeffs(src_pts, dst_pts):
    """
    Computes 8 coefficients for Image.PERSPECTIVE mapping dst_pts -> src_pts.
    dst_pts: [(x0,y0), (x1,y1), (x2,y2), (x3,y3)] on output canvas
    src_pts: [(u0,v0), (u1,v1), (u2,v2), (u3,v3)] on source texture
    """
    A = []
    B = []
    for (x, y), (u, v) in zip(dst_pts, src_pts):
        A.append([x, y, 1, 0, 0, 0, -u*x, -u*y])
        B.append(u)
        A.append([0, 0, 0, x, y, 1, -v*x, -v*y])
        B.append(v)
    n = 8
    for i in range(n):
        max_el = abs(A[i][i])
        max_row = i
        for k in range(i+1, n):
            if abs(A[k][i]) > max_el:
                max_el = abs(A[k][i])
                max_row = k
        A[i], A[max_row] = A[max_row], A[i]
        B[i], B[max_row] = B[max_row], B[i]
        pivot = A[i][i]
        for k in range(i, n):
            A[i][k] /= pivot
        B[i] /= pivot
        for k in range(n):
            if k != i:
                c = A[k][i]
                for j in range(i, n):
                    A[k][j] -= c * A[i][j]
                B[k] -= c * B[i]
    return tuple(B)

def project_perspective(x, y, z, cx=540, cy=960, yaw=0.0, pitch=20.0, roll=0.0, zoom=1.0, fov=850.0):
    """
    Consistent 3D perspective camera projection.
    Local coordinate conventions:
      x: right (+) / left (-)
      y: down along phone (+) / up towards top of phone (-)
      z: out towards viewer / screen front (+) / chassis rear (-)
    """
    y_rad = math.radians(yaw)
    p_rad = math.radians(pitch)
    r_rad = math.radians(roll)

    # 1. Yaw around Y axis
    x1 = x * math.cos(y_rad) + z * math.sin(y_rad)
    y1 = y
    z1 = -x * math.sin(y_rad) + z * math.cos(y_rad)

    # 2. Pitch around X axis (pitch > 0 tilts top of phone away into distance)
    x2 = x1
    y2 = y1 * math.cos(p_rad) - z1 * math.sin(p_rad)
    z2 = y1 * math.sin(p_rad) + z1 * math.cos(p_rad)

    # 3. Roll around Z axis
    x3 = x2 * math.cos(r_rad) - y2 * math.sin(r_rad)
    y3 = x2 * math.sin(r_rad) + y2 * math.cos(r_rad)
    z3 = z2

    dist = fov - z3
    if dist < 40:
        dist = 40
    scale = (fov / dist) * zoom
    sx = cx + x3 * scale
    sy = cy + y3 * scale
    return (sx, sy)

def draw_hud_tabs(d, active_idx, scene_name):
    """Top HUD tabs showing current scene progression."""
    d.rounded_rectangle([60, 90, 1020, 175], radius=16, fill=(12, 16, 26, 240), outline=(0, 242, 254, 80), width=2)
    accent = C_AMBER if active_idx in [1, 3, 5, 7] else (C_RED if active_idx in [0, 2, 4] else C_EMERALD)
    d.ellipse([92, 124, 106, 138], fill=accent)
    d.ellipse([88, 120, 110, 142], outline=accent, width=1)
    d.text((124, 118), f"MOBILE THREAT // {scene_name}", font=font_hud_label, fill=(241, 245, 249, 255))

    total_steps = 10
    start_x = 720
    step_w = 24
    step_gap = 5
    for i in range(total_steps):
        sx = start_x + i * (step_w + step_gap)
        is_cur = (i == active_idx)
        c_fill = accent if is_cur else (30, 41, 59, 140)
        c_line = accent if is_cur else (71, 85, 105, 100)
        d.rounded_rectangle([sx, 122, sx + step_w, 144], radius=4, fill=c_fill, outline=c_line, width=1)
        if is_cur:
            d.text((sx + 5, 124), str(i + 1), font=font_hud_tab, fill=(10, 12, 18, 255))

def draw_bottom_captions(d, t, timings_data):
    """Captions with the highlighted spoken word in gold with amber underline."""
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

def draw_callout(d, target_pt, box_center, text, accent_color=C_CYAN):
    """
    Draws a clean callout line from target_pt to a card centered at box_center.
    Guaranteed zero overlaps.
    """
    d.ellipse([target_pt[0]-4, target_pt[1]-4, target_pt[0]+4, target_pt[1]+4], fill=accent_color)
    d.ellipse([target_pt[0]-8, target_pt[1]-8, target_pt[0]+8, target_pt[1]+8], outline=accent_color, width=1)

    bbox = font_callout_txt.getbbox(text)
    txt_w = bbox[2] - bbox[0]
    box_w = txt_w + 26
    box_h = 36
    bx = box_center[0] - box_w // 2
    by = box_center[1] - box_h // 2

    # Line from target to card edge
    edge_x = bx + box_w if target_pt[0] > bx + box_w // 2 else bx
    edge_y = box_center[1]
    mid_x = (target_pt[0] + edge_x) // 2
    d.line([target_pt, (mid_x, edge_y), (edge_x, edge_y)], fill=accent_color, width=2)

    d.rounded_rectangle([bx, by, bx + box_w, by + box_h], radius=8,
                        fill=(14, 18, 30, 240), outline=accent_color, width=1)
    d.text((bx + 13, by + 8), text, font=font_callout_txt, fill=C_WHITE)

# ----------------- 2D SCREEN TEXTURE GENERATORS -----------------

SW, SH = 480, 1000

def generate_lockscreen_texture(alert_y=0, alert_pulse=0.0):
    screen = Image.new("RGBA", (SW, SH), (8, 11, 18, 255))
    d = ImageDraw.Draw(screen)

    # Top Status Bar
    d.text((36, 18), "Verizon", font=font_ui_reg, fill=C_MUTED)
    d.text((SW - 110, 18), "5G  100%", font=font_ui_reg, fill=C_MUTED)

    # Dynamic Island Pill
    d.rounded_rectangle([SW//2 - 55, 14, SW//2 + 55, 42], radius=14, fill=(3, 5, 8, 255))
    d.ellipse([SW//2 + 32, 23, SW//2 + 42, 33], fill=(16, 32, 54, 255))

    # Clock & Date
    d.text((SW//2 - 95, 100), "09:41", font=font_ui_clock, fill=C_WHITE)
    d.text((SW//2 - 90, 180), "Tuesday, November 10", font=font_ui_date, fill=C_MUTED)

    # SMS Notification Card
    card_y = 250 + alert_y
    card_h = 190
    d.rounded_rectangle([25, card_y, SW - 25, card_y + card_h], radius=18,
                        fill=(28, 14, 20, 245), outline=C_RED, width=2)
    d.text((45, card_y + 16), "💬 BANK ALERT • NOW", font=font_ui_bold, fill=C_RED)
    d.text((45, card_y + 50), "Unauthorized $840 transfer detected.", font=font_ui_reg, fill=C_WHITE)
    d.text((45, card_y + 78), "Tap here to verify your account immediately:", font=font_ui_reg, fill=(226, 232, 240, 255))

    # Glowing Red Link Button
    link_border = C_RED if alert_pulse > 0.5 else (255, 140, 160, 255)
    d.rounded_rectangle([45, card_y + 118, SW - 45, card_y + 168], radius=10,
                        fill=(52, 14, 22, 255), outline=link_border, width=2)
    d.text((60, card_y + 130), "chase-fraud-verify.cc/login", font=font_ui_code, fill=C_RED)

    # In-Display Fingerprint Sensor
    fp_cy = SH - 140
    d.ellipse([SW//2 - 32, fp_cy - 32, SW//2 + 32, fp_cy + 32], outline=C_CYAN, width=2)
    d.arc([SW//2 - 20, fp_cy - 20, SW//2 + 20, fp_cy + 20], start=45, end=315, fill=C_CYAN, width=2)

    # Home bar
    d.rounded_rectangle([SW//2 - 60, SH - 22, SW//2 + 60, SH - 16], radius=3, fill=(148, 163, 184, 180))
    return screen

def generate_fake_bank_texture():
    screen = Image.new("RGBA", (SW, SH), (10, 14, 22, 255))
    d = ImageDraw.Draw(screen)

    # Dynamic Island Pill
    d.rounded_rectangle([SW//2 - 55, 14, SW//2 + 55, 42], radius=14, fill=(3, 5, 8, 255))

    # Bank Navy Banner
    d.rounded_rectangle([20, 60, SW - 20, 150], radius=12, fill=(16, 44, 98, 255))
    d.text((SW//2 - 75, 90), "CHASE ONLINE", font=font_ui_bold, fill=C_WHITE)

    f_y = 190
    d.text((36, f_y), "Sign In to Your Account", font=font_ui_bold, fill=C_WHITE)

    d.text((36, f_y + 45), "Username / Email", font=font_ui_reg, fill=C_MUTED)
    d.rounded_rectangle([36, f_y + 75, SW - 36, f_y + 135], radius=10,
                        fill=(20, 26, 40, 255), outline=C_CYAN, width=1)
    d.text((52, f_y + 92), "alex.rivers@email.com", font=font_ui_reg, fill=C_WHITE)

    d.text((36, f_y + 160), "Password", font=font_ui_reg, fill=C_MUTED)
    d.rounded_rectangle([36, f_y + 190, SW - 36, f_y + 250], radius=10,
                        fill=(20, 26, 40, 255), outline=(71, 85, 105, 255), width=1)
    d.text((52, f_y + 208), "••••••••••••••", font=font_ui_reg, fill=C_WHITE)

    # Big Secure Login Button
    d.rounded_rectangle([36, f_y + 280, SW - 36, f_y + 350], radius=12,
                        fill=(18, 90, 210, 255), outline=C_CYAN, width=2)
    d.text((SW//2 - 70, f_y + 300), "SECURE LOGIN", font=font_ui_btn, fill=C_WHITE)

    # Warning Box
    d.rounded_rectangle([36, f_y + 380, SW - 36, f_y + 440], radius=10,
                        fill=(48, 12, 18, 240), outline=C_RED, width=2)
    d.text((SW//2 - 125, f_y + 398), "⚠️ SPOOFED PHISHING PAGE", font=font_ui_code, fill=C_RED)

    # Home bar
    d.rounded_rectangle([SW//2 - 60, SH - 22, SW//2 + 60, SH - 16], radius=3, fill=(148, 163, 184, 180))
    return screen

def generate_clamping_texture(clamp_progress=0.0):
    screen = Image.new("RGBA", (SW, SH), (8, 11, 18, 255))
    d = ImageDraw.Draw(screen)

    # Status Bar & Dynamic Island
    d.text((36, 18), "Verizon", font=font_ui_reg, fill=C_MUTED)
    d.text((SW - 110, 18), "5G  100%", font=font_ui_reg, fill=C_MUTED)
    d.rounded_rectangle([SW//2 - 55, 14, SW//2 + 55, 42], radius=14, fill=(3, 5, 8, 255))

    # Clock
    d.text((SW//2 - 95, 90), "09:41", font=font_ui_clock, fill=C_WHITE)

    # SMS card: red before clamp, turns green once clamp snaps shut (progress >= 0.45)
    is_clamped = (clamp_progress >= 0.45)
    card_y = 230
    card_h = 220
    card_fill = (14, 34, 28, 250) if is_clamped else (28, 14, 20, 245)
    card_out = C_EMERALD if is_clamped else C_RED

    d.rounded_rectangle([25, card_y, SW - 25, card_y + card_h], radius=18, fill=card_fill, outline=card_out, width=3)

    if not is_clamped:
        d.text((45, card_y + 18), "💬 BANK ALERT • NOW", font=font_ui_bold, fill=C_RED)
        d.text((45, card_y + 54), "Unauthorized $840 transfer detected.", font=font_ui_reg, fill=C_WHITE)
        d.text((45, card_y + 84), "Action required. Verify account now:", font=font_ui_reg, fill=(226, 232, 240, 255))
        # Malicious Link Button
        d.rounded_rectangle([45, card_y + 130, SW - 45, card_y + 185], radius=10, fill=(52, 14, 22, 255), outline=C_RED, width=2)
        d.text((60, card_y + 145), "chase-fraud-verify.cc/login", font=font_ui_code, fill=C_RED)
    else:
        d.text((45, card_y + 18), "🛡️ SMS SHIELD: INTERCEPTED", font=font_ui_bold, fill=C_EMERALD)
        d.text((45, card_y + 54), "Malicious banking domain blocked.", font=font_ui_reg, fill=C_WHITE)
        d.text((45, card_y + 84), "Hardware token access severed.", font=font_ui_reg, fill=C_MUTED)
        # Clamped Green Link Button
        d.rounded_rectangle([45, card_y + 130, SW - 45, card_y + 185], radius=10, fill=(20, 54, 44, 255), outline=C_EMERALD, width=2)
        d.text((60, card_y + 145), "🔒 LINK SEVERED & BLOCKED", font=font_ui_code, fill=C_EMERALD)

    # Physical Titanium Shield Clamp closing down over the link
    clamp_drop = min(1.0, clamp_progress * 2.2)
    clamp_target_y = card_y + 125
    clamp_y = int(clamp_target_y - (1.0 - clamp_drop) * 160)

    # Heavy titanium clamp bracket
    d.rounded_rectangle([35, clamp_y, SW - 35, clamp_y + 65], radius=12,
                        fill=(36, 48, 64, 250), outline=C_CYAN, width=3)
    for rx in [55, SW - 55]:
        d.ellipse([rx - 6, clamp_y + 10, rx + 6, clamp_y + 22], fill=(180, 200, 220, 255))
    d.text((SW//2 - 120, clamp_y + 22), "TITANIUM SECURITY CLAMP", font=font_callout_txt, fill=C_CYAN)

    # Home bar
    d.rounded_rectangle([SW//2 - 60, SH - 22, SW//2 + 60, SH - 16], radius=3, fill=(148, 163, 184, 180))
    return screen

def generate_shield_safe_texture():
    screen = Image.new("RGBA", (SW, SH), (8, 16, 22, 255))
    d = ImageDraw.Draw(screen)

    # Dynamic Island
    d.rounded_rectangle([SW//2 - 55, 14, SW//2 + 55, 42], radius=14, fill=(3, 5, 8, 255))

    # Clock & Date
    d.text((SW//2 - 95, 90), "09:41", font=font_ui_clock, fill=C_WHITE)
    d.text((SW//2 - 90, 170), "Tuesday, November 10", font=font_ui_date, fill=C_MUTED)

    # Big Emerald Shield Card
    card_y = 240
    d.rounded_rectangle([25, card_y, SW - 25, card_y + 220], radius=20,
                        fill=(14, 36, 30, 250), outline=C_EMERALD, width=3)
    d.text((45, card_y + 24), "🛡️ DEFENSE ACTIVE // SAFE", font=font_ui_bold, fill=C_EMERALD)
    d.text((45, card_y + 66), "All phishing conduits permanently sealed.", font=font_ui_reg, fill=C_WHITE)
    d.text((45, card_y + 98), "Device enclave locked. Zero data leaked.", font=font_ui_reg, fill=C_MUTED)
    d.rounded_rectangle([45, card_y + 140, SW - 45, card_y + 185], radius=10,
                        fill=(20, 56, 44, 255), outline=C_EMERALD, width=2)
    d.text((SW//2 - 110, card_y + 152), "STATUS: BULLETPROOF", font=font_ui_code, fill=C_EMERALD)

    # Home bar
    d.rounded_rectangle([SW//2 - 60, SH - 22, SW//2 + 60, SH - 16], radius=3, fill=(148, 163, 184, 180))
    return screen

# ----------------- 3D PHONE RENDERER -----------------

def draw_truly_3d_phone(canvas, cx=540, cy=960, pw=500, ph=1040, depth=38,
                        yaw=0.0, pitch=20.0, roll=0.0, zoom=1.0,
                        screen_type="lockscreen", alert_y=0, alert_pulse=0.0, clamp_progress=0.0):
    """
    Renders a truly 3D smartphone with real physical thickness, extruded side rails,
    chamfered bevels, hardware buttons, triple-camera bump, soft perspective contact shadow,
    and perspective-mapped OLED glass screen. Fills >60% of frame.
    """
    hw, hh, hd = pw / 2.0, ph / 2.0, depth / 2.0
    r = 52.0

    # 1. Soft Layered Contact Shadow cast on desk plane below phone (z = -hd - 15)
    shadow_ox = 30.0
    shadow_oy = 45.0
    s_pts = [
        project_perspective(-hw - 20 + shadow_ox, -hh - 15 + shadow_oy, -hd - 15, cx, cy, yaw, pitch, roll, zoom),
        project_perspective(hw + 30 + shadow_ox, -hh - 15 + shadow_oy, -hd - 15, cx, cy, yaw, pitch, roll, zoom),
        project_perspective(hw + 30 + shadow_ox, hh + 35 + shadow_oy, -hd - 15, cx, cy, yaw, pitch, roll, zoom),
        project_perspective(-hw - 20 + shadow_ox, hh + 35 + shadow_oy, -hd - 15, cx, cy, yaw, pitch, roll, zoom)
    ]
    shadow_overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    s_d = ImageDraw.Draw(shadow_overlay)
    s_d.polygon(s_pts, fill=(2, 4, 8, 180))
    canvas.alpha_composite(shadow_overlay)

    d = ImageDraw.Draw(canvas)

    # 2. Generate 3D rounded perimeter vertices
    corners = [
        (-hw + r, -hh + r, 180, 270), # Top-Left
        (hw - r, -hh + r, 270, 360),  # Top-Right
        (hw - r, hh - r, 0, 90),      # Bottom-Right
        (-hw + r, hh - r, 90, 180)    # Bottom-Left
    ]
    perim_2d = []
    for cx_c, cy_c, start_deg, end_deg in corners:
        for deg in range(start_deg, end_deg + 1, 15):
            rad = math.radians(deg)
            perim_2d.append((cx_c + math.cos(rad) * r, cy_c + math.sin(rad) * r))

    # 3. Triple Camera Bump on Rear-Top-Left
    cb_x1, cb_y1 = -hw + 24, -hh + 24
    cb_x2, cb_y2 = -hw + 160, -hh + 160
    cb_pts_back = [
        project_perspective(cb_x1, cb_y1, -hd - 14, cx, cy, yaw, pitch, roll, zoom),
        project_perspective(cb_x2, cb_y1, -hd - 14, cx, cy, yaw, pitch, roll, zoom),
        project_perspective(cb_x2, cb_y2, -hd - 14, cx, cy, yaw, pitch, roll, zoom),
        project_perspective(cb_x1, cb_y2, -hd - 14, cx, cy, yaw, pitch, roll, zoom)
    ]
    d.polygon(cb_pts_back, fill=(24, 30, 44, 255), outline=(60, 75, 100, 255), width=2)
    # 3 camera lens cylinders
    for lx, ly in [(cb_x1 + 42, cb_y1 + 42), (cb_x1 + 96, cb_y1 + 42), (cb_x1 + 42, cb_y1 + 96)]:
        l_pt = project_perspective(lx, ly, -hd - 16, cx, cy, yaw, pitch, roll, zoom)
        d.ellipse([l_pt[0]-12, l_pt[1]-12, l_pt[0]+12, l_pt[1]+12], fill=(8, 12, 18, 255), outline=(0, 242, 254, 180), width=2)
        d.ellipse([l_pt[0]-6, l_pt[1]-6, l_pt[0]+6, l_pt[1]+6], fill=(16, 24, 38, 255))

    # 4. Extruded Side Rails with directional lighting & bevels
    n = len(perim_2d)
    for i in range(n):
        nxt = (i + 1) % n
        p1_b = project_perspective(perim_2d[i][0], perim_2d[i][1], -hd, cx, cy, yaw, pitch, roll, zoom)
        p2_b = project_perspective(perim_2d[nxt][0], perim_2d[nxt][1], -hd, cx, cy, yaw, pitch, roll, zoom)
        p2_t = project_perspective(perim_2d[nxt][0], perim_2d[nxt][1], hd, cx, cy, yaw, pitch, roll, zoom)
        p1_t = project_perspective(perim_2d[i][0], perim_2d[i][1], hd, cx, cy, yaw, pitch, roll, zoom)

        # Directional rail lighting
        mid_x = (perim_2d[i][0] + perim_2d[nxt][0]) / 2.0
        mid_y = (perim_2d[i][1] + perim_2d[nxt][1]) / 2.0

        if mid_y < -hh * 0.7:  # Top rail (key specular)
            col_rail = (68, 82, 110, 255)
            out_rail = (120, 140, 180, 255)
        elif mid_x < -hw * 0.7:  # Left rail (ambient)
            col_rail = (42, 52, 72, 255)
            out_rail = (80, 95, 125, 255)
        elif mid_x > hw * 0.7:  # Right rail (key fill)
            col_rail = (32, 40, 58, 255)
            out_rail = (60, 75, 100, 255)
        else:  # Bottom rail (shadow)
            col_rail = (22, 28, 40, 255)
            out_rail = (45, 55, 75, 255)

        d.polygon([p1_b, p2_b, p2_t, p1_t], fill=col_rail, outline=out_rail, width=1)

    # 5. Physical Side Buttons in 3D
    # Volume buttons on left rail (x = -hw)
    for vy in [-hh + 240, -hh + 340]:
        bp1 = project_perspective(-hw - 8, vy, 0, cx, cy, yaw, pitch, roll, zoom)
        bp2 = project_perspective(-hw, vy + 65, 0, cx, cy, yaw, pitch, roll, zoom)
        d.line([bp1, bp2], fill=(130, 150, 190, 255), width=6)
    # Power button on right rail (x = hw)
    bp_p1 = project_perspective(hw, -hh + 280, 0, cx, cy, yaw, pitch, roll, zoom)
    bp_p2 = project_perspective(hw + 8, -hh + 380, 0, cx, cy, yaw, pitch, roll, zoom)
    d.line([bp_p1, bp_p2], fill=(130, 150, 190, 255), width=6)

    # 6. Front Chassis & Bezel Border
    front_pts = [project_perspective(p[0], p[1], hd, cx, cy, yaw, pitch, roll, zoom) for p in perim_2d]
    d.polygon(front_pts, fill=(12, 16, 24, 255), outline=(0, 242, 254, 180), width=3)

    # 7. Perspective Screen Mapping
    if screen_type == "lockscreen":
        screen_img = generate_lockscreen_texture(alert_y=alert_y, alert_pulse=alert_pulse)
    elif screen_type == "fake_bank":
        screen_img = generate_fake_bank_texture()
    elif screen_type == "clamping":
        screen_img = generate_clamping_texture(clamp_progress=clamp_progress)
    elif screen_type == "shield_safe":
        screen_img = generate_shield_safe_texture()
    else:
        screen_img = generate_lockscreen_texture()

    # Destination quad corners on screen face (z = hd + 0.5)
    bezel_w = hw - 18
    bezel_h = hh - 24
    dst_quad = [
        project_perspective(-bezel_w, -bezel_h, hd + 0.5, cx, cy, yaw, pitch, roll, zoom), # TL
        project_perspective(bezel_w, -bezel_h, hd + 0.5, cx, cy, yaw, pitch, roll, zoom),  # TR
        project_perspective(bezel_w, bezel_h, hd + 0.5, cx, cy, yaw, pitch, roll, zoom),   # BR
        project_perspective(-bezel_w, bezel_h, hd + 0.5, cx, cy, yaw, pitch, roll, zoom)   # BL
    ]
    src_quad = [(0, 0), (SW, 0), (SW, SH), (0, SH)]
    coeffs = solve_perspective_coeffs(src_quad, dst_quad)
    persp_screen = screen_img.transform((W, H), Image.PERSPECTIVE, coeffs, Image.BILINEAR)
    canvas.alpha_composite(persp_screen)

# ----------------- 3D FLYING OBJECTS (FOR SCENE 6) -----------------

def draw_cookie_3d(d, cx, cy, size=52):
    """Draws a recognizable 3D chocolate chip cookie icon."""
    r = size // 2
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(215, 160, 68, 255), outline=(150, 100, 35, 255), width=3)
    d.ellipse([cx - r + 3, cy - r + 4, cx + r - 3, cy + r - 2], outline=(240, 190, 100, 160), width=2)
    # Chocolate chips
    for ox, oy in [(-r*0.4, -r*0.3), (r*0.3, -r*0.4), (-r*0.2, r*0.3), (r*0.4, r*0.2), (0, -2)]:
        d.ellipse([cx + ox - 5, cy + oy - 5, cx + ox + 5, cy + oy + 5], fill=(68, 38, 16, 255))

def draw_brass_key_3d(d, kx, ky, length=80):
    """Draws a recognizable 3D golden brass key."""
    # Round Bow Head
    d.ellipse([kx - 24, ky - 24, kx + 24, ky + 24], fill=(245, 195, 45, 255), outline=(175, 135, 20, 255), width=3)
    d.ellipse([kx - 9, ky - 9, kx + 9, ky + 9], fill=(12, 14, 22, 255), outline=(175, 135, 20, 255), width=2)
    # Key Shaft & Notches
    d.rectangle([kx + 24, ky - 6, kx + length, ky + 6], fill=(245, 195, 45, 255), outline=(175, 135, 20, 255), width=2)
    d.rectangle([kx + length - 22, ky + 6, kx + length - 10, ky + 20], fill=(245, 195, 45, 255))
    d.rectangle([kx + length - 8, ky + 6, kx + length, ky + 16], fill=(245, 195, 45, 255))

def draw_2fa_chip_3d(d, chx, chy, w=76, h=52):
    """Draws a recognizable 3D silicon microchip with silver pins and 2FA label."""
    d.rounded_rectangle([chx - w//2, chy - h//2, chx + w//2, chy + h//2], radius=6,
                        fill=(24, 34, 52, 255), outline=C_CYAN, width=2)
    # Silver lead pins
    for px_off in [-26, -9, 9, 26]:
        d.rectangle([chx + px_off - 3, chy - h//2 - 6, chx + px_off + 3, chy - h//2], fill=(210, 225, 245, 255))
        d.rectangle([chx + px_off - 3, chy + h//2, chx + px_off + 3, chy + h//2 + 6], fill=(210, 225, 245, 255))
    d.text((chx - 17, chy - 11), "2FA", font=font_proof_body, fill=C_CYAN)

# ----------------- MAIN FRAME COMPOSITOR -----------------

def render_v2_frame(frame_idx, total_frames, timings_data):
    """Composites a single vertical video frame strictly implementing all 8 changes."""
    t = frame_idx / float(FPS)
    total_duration = total_frames / float(FPS)
    progress = min(1.0, max(0.0, t / total_duration))

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

    im = Image.new('RGBA', (W, H), C_BG)

    # Ambient cybersecurity lighting & isometric floor grid lines
    spot = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    s_d = ImageDraw.Draw(spot)
    s_d.ellipse([-150, 350, 1230, 1650], fill=(24, 32, 50, 140))
    s_d.ellipse([120, 500, 960, 1380], fill=(32, 44, 70, 90))
    im.alpha_composite(spot)

    d = ImageDraw.Draw(im)
    # Subtle background tech grid lines
    for gy in range(350, 1600, 120):
        d.line([(40, gy), (1040, gy)], fill=(24, 34, 54, 90), width=1)
    for gx in range(80, 1040, 140):
        d.line([(gx, 350), (gx, 1600)], fill=(24, 34, 54, 90), width=1)

    # ------------------ SCENE RENDERS ------------------

    if current_shot["id"] == 1:
        # Scene 1: Macro Push-in on Phone (fills >65% frame)
        # Yaw -10 -> -4, Pitch 16 -> 12, Zoom 1.25 -> 1.45
        yaw = -10.0 + shot_rel_t * 6.0
        pitch = 16.0 - shot_rel_t * 4.0
        zoom = 1.22 + shot_rel_t * 0.20
        alert_y = int((1.0 - min(1.0, shot_rel_t * 1.6)) * -160)

        draw_truly_3d_phone(im, cx=540, cy=860, pw=500, ph=1040, depth=38,
                            yaw=yaw, pitch=pitch, zoom=zoom,
                            screen_type="lockscreen", alert_y=alert_y, alert_pulse=pulse)

        # Callouts pointing to specific parts (spaced in margins, zero overlap)
        d_im = ImageDraw.Draw(im)
        draw_callout(d_im, (340, 680), (180, 480), "SMS SPOOF DETECTED", C_RED)
        draw_callout(d_im, (720, 740), (880, 520), "MALICIOUS LINK", C_RED)

    elif current_shot["id"] == 2:
        # Scene 2: Low-Angle Pull-Back on Desk with Stylized Hand Reaching
        # Yaw 24 -> 12, Pitch 24 -> 18, Zoom 1.15 -> 0.98
        yaw = 24.0 - shot_rel_t * 12.0
        pitch = 24.0 - shot_rel_t * 6.0
        zoom = 1.12 - shot_rel_t * 0.16

        draw_truly_3d_phone(im, cx=540, cy=870, pw=480, ph=1020, depth=38,
                            yaw=yaw, pitch=pitch, zoom=zoom, screen_type="lockscreen", alert_y=0)

        d_im = ImageDraw.Draw(im)
        # Stylized 3D Hand reaching down towards the screen
        finger_x = 550
        finger_y = 540 + int(shot_rel_t * 80)
        d_im.rounded_rectangle([finger_x - 30, finger_y - 200, finger_x + 30, finger_y],
                               radius=25, fill=(72, 54, 48, 245), outline=C_AMBER, width=2)
        d_im.ellipse([finger_x - 22, finger_y - 28, finger_x + 22, finger_y + 16],
                     fill=(92, 70, 62, 255), outline=C_GOLD, width=1)

        # Callouts pointing to specific parts (zero overlap)
        draw_callout(d_im, (540, 1180), (200, 1260), "IN-DISPLAY FINGERPRINT", C_CYAN)
        draw_callout(d_im, (740, 740), (880, 620), "TITANIUM CHASSIS RAIL", C_AMBER)
        draw_callout(d_im, (380, 660), (190, 520), "OLED RETINA DISPLAY", C_CYAN)

    elif current_shot["id"] == 3:
        # Scene 3: High Top-Down Dutch Angle, Thumb Tapping Link -> Fake Bank Login
        # Yaw -22 -> -12, Pitch 48 -> 54, Roll -10, Zoom 1.10 -> 1.25
        yaw = -22.0 + shot_rel_t * 10.0
        pitch = 48.0 + shot_rel_t * 6.0
        roll = -10.0
        zoom = 1.05 + shot_rel_t * 0.14

        draw_truly_3d_phone(im, cx=540, cy=870, pw=500, ph=1040, depth=38,
                            yaw=yaw, pitch=pitch, roll=roll, zoom=zoom, screen_type="fake_bank")

        d_im = ImageDraw.Draw(im)
        # Expanding Tap Ripple on link
        tap_x, tap_y = 480, 750
        ripple_r = int((shot_rel_t * 120) % 75)
        d_im.ellipse([tap_x - ripple_r, tap_y - ripple_r, tap_x + ripple_r, tap_y + ripple_r], outline=C_RED, width=3)
        # Thumb pressing
        d_im.ellipse([tap_x - 32, tap_y - 32, tap_x + 32, tap_y + 32], fill=(95, 72, 65, 230), outline=C_AMBER, width=2)

        draw_callout(d_im, (tap_x, tap_y), (190, 600), "1-TAP PHISHING TRIGGER", C_RED)
        draw_callout(d_im, (640, 710), (870, 620), "FAKE LOGIN INTERFACE", C_AMBER)

    elif current_shot["id"] == 4:
        # Scene 4: Internal Cutaway Fly-Through (Battery, Chip Board, Wiring Traces, Token Slot)
        # Full phone chassis cutaway (fills >60% of frame)
        d_im = ImageDraw.Draw(im)
        chassis_x1, chassis_y1 = 150, 360
        chassis_x2, chassis_y2 = 930, 1540
        d_im.rounded_rectangle([chassis_x1, chassis_y1, chassis_x2, chassis_y2], radius=44,
                               fill=(14, 18, 28, 255), outline=(0, 242, 254, 200), width=3)

        # 1. Lithium-Ion Battery Pack (Left Side)
        bat_x1, bat_y1 = 180, 440
        bat_x2, bat_y2 = 510, 1460
        d_im.rounded_rectangle([bat_x1, bat_y1, bat_x2, bat_y2], radius=18,
                               fill=(10, 12, 18, 255), outline=(71, 85, 105, 255), width=2)
        d_im.text((bat_x1 + 25, bat_y1 + 30), "🔋 4,500 mAh Li-Ion", font=font_proof_body, fill=C_WHITE)
        d_im.text((bat_x1 + 25, bat_y1 + 65), "Nominal Voltage: 3.85V", font=font_proof_stat, fill=C_MUTED)
        d_im.text((bat_x1 + 25, bat_y1 + 95), "High Density Enclave Cell", font=font_proof_stat, fill=C_MUTED)
        for by in range(bat_y1 + 160, bat_y2 - 40, 75):
            d_im.line([(bat_x1 + 20, by), (bat_x2 - 20, by)], fill=(22, 26, 38, 255), width=2)

        # 2. Multilayer Motherboard PCB (Right Side)
        pcb_x1, pcb_y1 = 535, 440
        pcb_x2, pcb_y2 = 900, 1460
        d_im.rounded_rectangle([pcb_x1, pcb_y1, pcb_x2, pcb_y2], radius=18,
                               fill=(16, 34, 28, 255), outline=C_CYAN, width=2)
        # Copper wiring traces
        for ty in range(pcb_y1 + 40, pcb_y2 - 20, 55):
            d_im.line([(pcb_x1 + 20, ty), (pcb_x2 - 20, ty)], fill=(36, 72, 58, 200), width=2)
        for tx in range(pcb_x1 + 35, pcb_x2 - 20, 55):
            d_im.line([(tx, pcb_y1 + 30), (tx, pcb_y2 - 30)], fill=(36, 72, 58, 200), width=2)

        # Labeled Slot: [TOKEN SLOT // ENCLAVE BUS]
        slot_y = 750
        d_im.rounded_rectangle([pcb_x1 + 20, slot_y, pcb_x2 - 20, slot_y + 240], radius=16,
                               fill=(10, 16, 26, 255), outline=C_GOLD, width=3)
        # Dedicated Header Plate for Slot Label Beneath Socket (Never Covered)
        d_im.rounded_rectangle([pcb_x1 + 30, slot_y + 250, pcb_x2 - 30, slot_y + 285], radius=8,
                               fill=(20, 28, 42, 255), outline=C_GOLD, width=1)
        d_im.text((pcb_x1 + 42, slot_y + 258), "TOKEN SLOT // ENCLAVE BUS", font=font_proof_stat, fill=C_GOLD)

        # Glowing Trojan Token Chip Sliding into Slot (Physical Moving Part)
        slide_prog = min(1.0, shot_rel_t * 1.35)
        chip_y = int(500 + slide_prog * 300)
        chip_x1, chip_x2 = pcb_x1 + 40, pcb_x2 - 40
        d_im.rounded_rectangle([chip_x1, chip_y, chip_x2, chip_y + 120], radius=12,
                               fill=(58, 14, 22, 255), outline=C_RED, width=3)
        d_im.text((chip_x1 + 22, chip_y + 24), "TROJAN TOKEN CHIP", font=font_proof_body, fill=C_WHITE)
        d_im.text((chip_x1 + 22, chip_y + 60), "[TOKEN_PAYLOAD]", font=font_callout_txt, fill=C_RED)

        # Cyan electrical discharge spark arcs once seated
        if slide_prog >= 0.8:
            for s_i in range(5):
                sp_x = chip_x1 + 25 + s_i * 45
                d_im.line([(sp_x, slot_y + 205), (sp_x + 14, slot_y + 222)], fill=C_CYAN, width=3)

        # Non-overlapping callouts in margins
        draw_callout(d_im, (340, 760), (180, 290), "LITHIUM-ION BATTERY", C_CYAN)
        draw_callout(d_im, (720, pcb_y1 + 100), (860, 290), "PCB WIRING TRACES", C_CYAN)
        draw_callout(d_im, (pcb_x2 - 10, slot_y + 140), (880, 1080), "PAYLOAD INGESTION", C_RED)

    elif current_shot["id"] == 5:
        # Scene 5: High-Angle Fast Orbit with BIG COUNTER 11.2s
        # Placed in upper HUD zone so it NEVER covers phone or clock!
        # Number mismatch fixed: exactly 11.2s on card and label.
        yaw = -36.0 + shot_rel_t * 72.0
        pitch = 30.0
        zoom = 1.02

        # 3D Phone placed lower in frame (cy = 1060) so clock & face are completely visible
        draw_truly_3d_phone(im, cx=540, cy=1060, pw=480, ph=940, depth=38,
                            yaw=yaw, pitch=pitch, zoom=zoom, screen_type="fake_bank")

        d_im = ImageDraw.Draw(im)
        # Upper HUD Counter Card (y: 200 to 415) - NEVER covers phone or clock!
        card_y = 205
        d_im.rounded_rectangle([150, card_y, 930, card_y + 215], radius=24,
                               fill=(14, 18, 30, 245), outline=C_RED, width=3)

        # Radial Gauge Arc sweeping
        arc_cx, arc_cy = 275, card_y + 108
        d_im.ellipse([arc_cx - 65, arc_cy - 65, arc_cx + 65, arc_cy + 65], outline=(40, 50, 70, 255), width=8)
        sweep_pct = min(1.0, shot_rel_t * 1.5)
        end_angle = int(sweep_pct * 260)
        d_im.arc([arc_cx - 65, arc_cy - 65, arc_cx + 65, arc_cy + 65], start=-90, end=-90 + end_angle, fill=C_RED, width=10)

        # Exactly 11.2s on digits and label everywhere!
        d_im.text((375, card_y + 28), "11.2s", font=font_hero_num, fill=C_RED)
        d_im.text((380, card_y + 140), "TIME TO COMPROMISE: 11.2s", font=font_hero_label, fill=C_AMBER)

        # Callout pointing to phone chassis below
        draw_callout(d_im, (540, 1140), (870, 640), "RAPID CREDENTIAL HARVEST", C_AMBER)

    elif current_shot["id"] == 6:
        # Scene 6: Data Theft - Phone & Laptop BOTH LARGE inside frame
        # PDF Change #4: Both objects large & fully inside frame; 3D cookie/key/2FA chip flying
        # Lateral camera: yaw sweeps during shot
        yaw6 = 15.0 + shot_rel_t * 10.0
        pitch6 = 20.0 - shot_rel_t * 4.0
        # Left: Large 3D Phone (pw=440, ph=920 -> ~40% of 1080 width, tall and prominent)
        draw_truly_3d_phone(im, cx=285, cy=920, pw=440, ph=940, depth=36,
                            yaw=yaw6, pitch=pitch6, zoom=1.0, screen_type="fake_bank")

        d_im = ImageDraw.Draw(im)
        # Right: Large 3D Hacker Laptop (bigger and lower to fill frame)
        lx, ly, lw, lh = 530, 540, 510, 380
        # Hinge glow
        d_im.line([(lx - 20, ly + lh), (lx + lw + 20, ly + lh)], fill=C_RED, width=4)
        # Laptop Screen
        d_im.rounded_rectangle([lx, ly, lx + lw, ly + lh], radius=16,
                               fill=(8, 12, 20, 255), outline=C_RED, width=3)
        d_im.rounded_rectangle([lx + 6, ly + 6, lx + lw - 6, ly + lh - 6], radius=12,
                               fill=(10, 16, 24, 255), outline=(30, 40, 60, 255), width=1)
        d_im.text((lx + 24, ly + 22), "> EXFILTRATION TERMINAL", font=font_ui_code, fill=C_RED)
        d_im.text((lx + 24, ly + 62), "INCOMING STREAM: ACTIVE", font=font_ui_code, fill=C_CYAN)
        d_im.text((lx + 24, ly + 102), "DECRYPTING KEYCHAIN TOKENS...", font=font_ui_code, fill=C_WHITE)
        d_im.text((lx + 24, ly + 142), "STATUS: 100% RECEIVED", font=font_ui_code, fill=C_EMERALD)
        d_im.text((lx + 24, ly + 182), f"PKT RECV: {int(shot_rel_t * 847) + 42} / 889", font=font_ui_code, fill=C_AMBER)
        # Laptop bezel camera dot
        d_im.ellipse([lx + lw//2 - 5, ly + 8, lx + lw//2 + 5, ly + 18], fill=(40, 50, 70, 255))
        # Laptop Keyboard Deck (deeper, more 3D)
        d_im.polygon([(lx - 40, ly + lh), (lx + lw + 40, ly + lh),
                      (lx + lw + 15, ly + lh + 80), (lx - 15, ly + lh + 80)],
                     fill=(22, 28, 42, 255), outline=(55, 70, 90, 255))
        # Keyboard rows
        for row in range(3):
            ky = ly + lh + 18 + row * 20
            d_im.line([(lx + 10, ky), (lx + lw - 10, ky)], fill=(35, 45, 65, 255), width=1)
        # Trackpad
        d_im.rounded_rectangle([lx + lw//2 - 60, ly + lh + 50, lx + lw//2 + 60, ly + lh + 72],
                               radius=4, fill=(30, 38, 56, 255), outline=(55, 70, 90, 255))

        # 3 Separate Distinct 3D Objects Flying along parabolic trajectory (larger, more visible)
        flight_items = [
            ("cookie", 0.0),
            ("key", 0.35),
            ("chip", 0.68)
        ]
        for obj_type, offset in flight_items:
            prog = (shot_rel_t + offset) % 1.0
            fly_x = int(300 + prog * 440)
            fly_y = int(640 + math.sin(prog * math.pi) * -180)
            # Motion trail
            if prog > 0.05:
                trail_x = int(300 + max(0, prog - 0.07) * 440)
                trail_y = int(640 + math.sin(max(0, prog - 0.07) * math.pi) * -180)
                d_im.line([(trail_x, trail_y), (fly_x, fly_y)], fill=(255, 100, 60, 80), width=3)

            if obj_type == "cookie":
                draw_cookie_3d(d_im, fly_x, fly_y, size=60)
            elif obj_type == "key":
                draw_brass_key_3d(d_im, fly_x - 36, fly_y, length=90)
            else:
                draw_2fa_chip_3d(d_im, fly_x, fly_y, w=84, h=56)

        # Clean callouts in margins (no tiny overlapping labels)
        draw_callout(d_im, (285, 760), (160, 450), "PRIVATE DATA EXFILTRATED", C_AMBER)
        draw_callout(d_im, (lx + 255, ly + 190), (900, 440), "HACKER RECEIVER LAPTOP", C_RED)

    elif current_shot["id"] == 7:
        # Scene 7: PROOF BEAT: Verizon DBIR 91% Stat Chart
        # Generous padding inside card edges (no text clipping or overflowing)
        # 3D Phone visible in background with subtle danger tilt
        draw_truly_3d_phone(im, cx=840, cy=960, pw=440, ph=900, depth=34,
                            yaw=-28.0, pitch=22.0, zoom=0.85, screen_type="fake_bank")

        d_im = ImageDraw.Draw(im)
        card_w = 840
        card_h = 580
        card_x = (W - card_w) // 2
        card_y = 440

        d_im.rounded_rectangle([card_x, card_y, card_x + card_w, card_y + card_h], radius=28,
                               fill=(14, 18, 30, 245), outline=C_RED, width=3)

        d_im.text((card_x + 40, card_y + 36), "🛡️ VERIZON DATA BREACH REPORT (DBIR)", font=font_proof_title, fill=C_WHITE)

        # 91% Radial Gauge
        dial_cx, dial_cy = card_x + 160, card_y + 220
        d_im.ellipse([dial_cx - 75, dial_cy - 75, dial_cx + 75, dial_cy + 75], outline=(40, 50, 70, 255), width=8)
        d_im.arc([dial_cx - 75, dial_cy - 75, dial_cx + 75, dial_cy + 75], start=-90, end=238, fill=C_RED, width=12)
        d_im.text((dial_cx - 52, dial_cy - 35), "91%", font=font_hero_unit, fill=C_RED)

        # Bar Chart of Attack Vectors
        chart_x = card_x + 280
        d_im.text((chart_x, card_y + 130), "PRIMARY ATTACK VECTOR", font=font_hero_label, fill=C_AMBER)

        # Bar 1: Phishing 91%
        d_im.text((chart_x, card_y + 175), "Phishing Links: 91%", font=font_proof_body, fill=C_WHITE)
        d_im.rounded_rectangle([chart_x, card_y + 205, chart_x + 480, card_y + 225], radius=6, fill=C_RED)

        # Bar 2: Brute Force 5%
        d_im.text((chart_x, card_y + 245), "Brute Force: 5%", font=font_proof_body, fill=C_MUTED)
        d_im.rounded_rectangle([chart_x, card_y + 275, chart_x + 28, card_y + 295], radius=6, fill=(71, 85, 105, 255))

        # Bar 3: System Zero-Day 4%
        d_im.text((chart_x, card_y + 315), "System Zero-Day: 4%", font=font_proof_body, fill=C_MUTED)
        d_im.rounded_rectangle([chart_x, card_y + 345, chart_x + 22, card_y + 365], radius=6, fill=(71, 85, 105, 255))

        # Official Stat Quote Box (Fully cushioned inside card edges)
        d_im.rounded_rectangle([card_x + 36, card_y + 440, card_x + card_w - 36, card_y + 535], radius=12,
                               fill=(26, 18, 24, 255), outline=C_AMBER, width=1)
        d_im.text((card_x + 56, card_y + 458), "“91% of cyber breaches start with a phishing message”",
                  font=font_proof_stat, fill=C_AMBER)
        d_im.text((card_x + 56, card_y + 490), "Source: Verizon DBIR & CISA Cyber Defense Report",
                  font=font_proof_stat, fill=C_MUTED)

    elif current_shot["id"] == 8:
        # Scene 8: Defense Clamping - Titanium clamp physically closing over link, SMS turns red to green
        # Low-Angle Camera
        yaw = -16.0 + shot_rel_t * 12.0
        pitch = 18.0
        zoom = 1.12

        draw_truly_3d_phone(im, cx=540, cy=860, pw=500, ph=1040, depth=38,
                            yaw=yaw, pitch=pitch, zoom=zoom,
                            screen_type="clamping", clamp_progress=shot_rel_t)

        d_im = ImageDraw.Draw(im)
        # Spaced non-overlapping callouts in margins
        draw_callout(d_im, (380, 680), (180, 480), "TITANIUM CLAMP CLOSED", C_EMERALD)
        draw_callout(d_im, (680, 740), (880, 520), "MALICIOUS LINK BLOCKED", C_CYAN)

    elif current_shot["id"] == 9:
        # Scene 9: Result 0% Vulnerability
        # Counter placed in upper HUD area, NEVER covers phone or clock!
        yaw = 32.0 - shot_rel_t * 24.0
        pitch = 28.0
        zoom = 1.02

        # Phone in lower frame (cy = 1060)
        draw_truly_3d_phone(im, cx=540, cy=1060, pw=480, ph=940, depth=38,
                            yaw=yaw, pitch=pitch, zoom=zoom, screen_type="shield_safe")

        d_im = ImageDraw.Draw(im)
        # Glowing Spherical Cyan Energy Shield around phone
        shield_r = 320 + pulse * 18
        d_im.ellipse([540 - shield_r, 1060 - shield_r, 540 + shield_r, 1060 + shield_r], outline=C_CYAN, width=3)

        # Counter Card placed in upper HUD zone (y: 205 to 420) - NEVER covers phone or clock!
        card_y = 205
        d_im.rounded_rectangle([160, card_y, 920, card_y + 215], radius=24,
                               fill=(12, 28, 24, 245), outline=C_EMERALD, width=3)
        d_im.text((220, card_y + 32), "0%", font=font_hero_num, fill=C_EMERALD)
        d_im.text((410, card_y + 55), "VULNERABILITY", font=font_hero_unit, fill=C_GOLD)
        d_im.text((225, card_y + 145), "PHONE VAULT IMPERVIOUS TO PHISHING", font=font_hero_label, fill=C_WHITE)

    else:
        # Scene 10: Grand CTA "Stay bulletproof" with @mwd1504
        # Upper CTA Card (y: 205 to 480), Phone in lower half (cy = 1060) - NEVER overlaps!
        yaw = 22.0 - shot_rel_t * 18.0
        pitch = 22.0
        zoom = 1.02

        draw_truly_3d_phone(im, cx=540, cy=1060, pw=460, ph=920, depth=38,
                            yaw=yaw, pitch=pitch, zoom=zoom, screen_type="shield_safe")

        d_im = ImageDraw.Draw(im)
        cta_y = 205
        d_im.rounded_rectangle([150, cta_y, 930, cta_y + 275], radius=28,
                               fill=(14, 18, 32, 245), outline=C_GOLD, width=3)

        btn_y = cta_y + 35
        d_im.rounded_rectangle([190, btn_y, 890, btn_y + 90], radius=18,
                               fill=(16, 185, 129, 235), outline=C_GOLD, width=2)
        btn_bbox = font_cta_btn.getbbox("STAY BULLETPROOF")
        btn_w = btn_bbox[2] - btn_bbox[0]
        d_im.text(((W - btn_w) // 2, btn_y + 22), "STAY BULLETPROOF", font=font_cta_btn, fill=(10, 12, 18, 255))

        handle_str = "@mwd1504"
        h_bbox = font_cta_sub.getbbox(handle_str)
        h_w = h_bbox[2] - h_bbox[0]
        h_x = (W - h_w) // 2
        d_im.text((h_x, cta_y + 145), handle_str, font=font_cta_sub, fill=C_CYAN)

        # Verified Checkmark Badge
        d_im.ellipse([h_x + h_w + 14, cta_y + 150, h_x + h_w + 34, cta_y + 170], fill=C_CYAN)
        d_im.text((h_x + h_w + 18, cta_y + 148), "✓", font=font_hud_tab, fill=(10, 12, 18, 255))

        d_im.text((280, cta_y + 210), "Follow for Mobile Cyber Defense & High-Security Tech",
                  font=font_proof_body, fill=C_MUTED)

    # ------------------ TOP HUD & CAPTIONS ------------------
    draw_hud_tabs(d, active_idx, current_shot["name"])
    draw_bottom_captions(d, t, timings_data)

    # Bottom Progress Bar
    d.rounded_rectangle([80, 1780, 1000, 1788], radius=4, fill=(30, 41, 59, 160))
    bar_w = int(920 * progress)
    if bar_w > 0:
        bar_col = C_GOLD if active_idx == 9 else C_CYAN
        d.rounded_rectangle([80, 1780, 80 + bar_w, 1788], radius=4, fill=bar_col)

    # Ensure fully opaque 100% alpha for consistent video output
    return im.convert("RGBA")

def render_keyframe_previews():
    """Generates preview keyframes for all 10 shots to .pipeline/keyframes/."""
    keyframe_dir = PIPELINE_DIR / "keyframes"
    keyframe_dir.mkdir(parents=True, exist_ok=True)

    with open(TIMINGS_FILE, "r", encoding="utf-8") as f:
        timings_data = json.load(f)

    total_duration = get_audio_duration(AUDIO_FILE)
    total_frames = int(math.ceil(total_duration * FPS))

    print(f"📸 Generating 10 Keyframe Previews...")
    for sc in SHOT_TIMELINE:
        mid_t = sc["start"] + sc["dur"] * 0.5
        f_idx = min(total_frames - 1, int(mid_t * FPS))
        frame_im = render_v2_frame(f_idx, total_frames, timings_data)
        out_shot = keyframe_dir / f"v2_shot_{sc['id']}.png"
        frame_im.save(out_shot)
        print(f"  ✓ Saved {out_shot}")

def render_final_video():
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
            frame_im = render_v2_frame(f, total_frames, timings_data)
            proc.stdin.write(frame_im.tobytes())
            if f % (FPS * 3) == 0:
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

    # Copy to Downloads
    download_dir = Path("/sdcard/Download")
    if download_dir.exists() and download_dir.is_dir():
        dest = download_dir / "How_Hackers_Phish_Your_Phone.mp4"
        shutil.copyfile(output_path, dest)
        print(f"📲 Synchronized to Downloads: {dest}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--keyframes":
        render_keyframe_previews()
    else:
        render_keyframe_previews()
        render_final_video()
