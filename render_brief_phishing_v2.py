#!/usr/bin/env python3
"""
render_brief_phishing_v2.py - High-Fidelity 3D Hardware Teardown Motion Graphics Engine
Rebuilt to match high-production inspiration video standard:
- 1080x1920 vertical format @ 30 FPS, ~29.256s timeline (10 scenes, cuts every 2-3s)
- PBR-like lighting: specular chrome highlights, titanium bevels, glass reflections, soft shadows
- Supersampled 2x OLED screen textures (960x2000) with bicubic perspective mapping (no blur)
- Clean typography (Roboto / modern geometric sans fallback) with zero text overflow
- Full procedural vector icons for shield, warning, battery, padlock, chat (zero tofu emoji boxes)
- Sleek floating telemetry HUD pill + floating kinetic subtitle pill with word underline
- Realistic 3D stylized hand scale cues in Scene 2
- True 3D perspective cutaway hardware teardown in Scene 4
- Modeled 3D flying data objects (cookie, brass key, 2FA silicon chip) in Scene 6
- High-contrast official authority document proof card with yellow highlighter in Scene 7
- Heavy titanium security clamp with instant green transformation in Scene 8
- Tuned ffmpeg encoding (CRF 19, YUV420p) with EBU R128 loudness normalization
- Standalone execution with embedded fallback chunks and audio fallbacks
"""

import os
import sys
import json
import math
import shutil
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT_DIR = Path(__file__).resolve().parent
PIPELINE_DIR = ROOT_DIR / ".pipeline"
OUTPUT_DIR = PIPELINE_DIR / "output"
PREVIEW_DIR = PIPELINE_DIR / "keyframes_preview"
TIMINGS_FILE = PIPELINE_DIR / "phishing_chunks.json"
AUDIO_FILE = PIPELINE_DIR / "phishing_audio.mp3"
FALLBACK_AUDIO = ROOT_DIR / "video-engine" / "public" / "audio.mp3"

# ----------------- FONTS DISCOVERY -----------------
FONT_CANDIDATES_SANS = [
    "/system/fonts/Roboto-Regular.ttf",
    "/system/fonts/RobotoStatic-Regular.ttf",
    "/data/data/com.termux/files/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
]
FONT_CANDIDATES_MONO = [
    "/data/data/com.termux/files/usr/share/fonts/TTF/DejaVuSansMono-Bold.ttf",
    "/system/fonts/Roboto-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
    "/usr/share/fonts/TTF/DejaVuSansMono-Bold.ttf",
]
FONT_SANS_PATH = next((p for p in FONT_CANDIDATES_SANS if os.path.exists(p)), None)
FONT_MONO_PATH = next((p for p in FONT_CANDIDATES_MONO if os.path.exists(p)), FONT_SANS_PATH)
if FONT_SANS_PATH is None:
    raise FileNotFoundError("No usable sans font found. Install fonts-dejavu or provide TTF.")

font_hud_tab = ImageFont.truetype(FONT_MONO_PATH, 18)
font_hud_label = ImageFont.truetype(FONT_SANS_PATH, 22)
font_hero_num = ImageFont.truetype(FONT_SANS_PATH, 108)
font_hero_unit = ImageFont.truetype(FONT_SANS_PATH, 42)
font_hero_label = ImageFont.truetype(FONT_MONO_PATH, 22)
font_callout_txt = ImageFont.truetype(FONT_MONO_PATH, 18)
font_caption = ImageFont.truetype(FONT_SANS_PATH, 48)
font_proof_title = ImageFont.truetype(FONT_SANS_PATH, 28)
font_proof_body = ImageFont.truetype(FONT_SANS_PATH, 22)
font_proof_stat = ImageFont.truetype(FONT_MONO_PATH, 19)
font_cta_btn = ImageFont.truetype(FONT_SANS_PATH, 46)
font_cta_sub = ImageFont.truetype(FONT_MONO_PATH, 26)

# High-Res 2x Screen Fonts (OLED canvas 960x2000)
font_ui_clock = ImageFont.truetype(FONT_SANS_PATH, 136)
font_ui_date = ImageFont.truetype(FONT_SANS_PATH, 38)
font_ui_bold = ImageFont.truetype(FONT_SANS_PATH, 44)
font_ui_reg = ImageFont.truetype(FONT_SANS_PATH, 34)
font_ui_code = ImageFont.truetype(FONT_MONO_PATH, 34)
font_ui_btn = ImageFont.truetype(FONT_SANS_PATH, 40)

W, H = 1080, 1920
FPS = 30
SW, SH = 960, 2000  # 2x Screen supersampling for crystal-clear perspective warp

# Master Palette (Obsidian + Amber + Cyan + Crimson + Emerald)
C_BG = (10, 14, 22, 255)
C_CYAN = (0, 242, 254, 255)
C_AMBER = (255, 176, 32, 255)
C_GOLD = (255, 215, 0, 255)
C_RED = (255, 59, 78, 255)
C_EMERALD = (16, 185, 129, 255)
C_WHITE = (255, 255, 255, 255)
C_MUTED = (148, 163, 184, 255)

# Standalone Chunks Fallback
EMBEDDED_CHUNKS = [
    {"chunk_id": 1, "start": 0.1, "end": 1.376, "words": ["One", "fake", "text", "can"], "word_starts": [0.1, 0.419, 0.738, 1.057]},
    {"chunk_id": 2, "start": 1.376, "end": 2.653, "words": ["completely", "drain", "your", "entire"], "word_starts": [1.376, 1.695, 2.015, 2.334]},
    {"chunk_id": 3, "start": 2.653, "end": 3.61, "words": ["phone", "in", "seconds."], "word_starts": [2.653, 2.972, 3.291]},
    {"chunk_id": 4, "start": 3.56, "end": 4.62, "words": ["Hackers", "do", "not", "need"], "word_starts": [3.56, 3.825, 4.09, 4.355]},
    {"chunk_id": 5, "start": 4.62, "end": 5.68, "words": ["to", "break", "your", "password."], "word_starts": [4.62, 4.885, 5.15, 5.415]},
    {"chunk_id": 6, "start": 5.68, "end": 6.738, "words": ["They", "trick", "you", "into"], "word_starts": [5.68, 5.944, 6.209, 6.473]},
    {"chunk_id": 7, "start": 6.738, "end": 7.796, "words": ["opening", "the", "vault", "door"], "word_starts": [6.738, 7.002, 7.267, 7.531]},
    {"chunk_id": 8, "start": 7.796, "end": 9.071, "words": ["yourself.", "A", "spoofed", "banking"], "word_starts": [7.796, 8.06, 8.397, 8.734]},
    {"chunk_id": 9, "start": 9.071, "end": 10.419, "words": ["link", "injects", "a", "silent"], "word_starts": [9.071, 9.408, 9.745, 10.082]},
    {"chunk_id": 10, "start": 10.419, "end": 11.767, "words": ["background", "token", "into", "your"], "word_starts": [10.419, 10.756, 11.093, 11.43]},
    {"chunk_id": 11, "start": 11.767, "end": 13.299, "words": ["operating", "system.", "Within", "twelve"], "word_starts": [11.767, 12.104, 12.441, 12.87]},
    {"chunk_id": 12, "start": 13.299, "end": 15.015, "words": ["seconds,", "your", "private", "session"], "word_starts": [13.299, 13.728, 14.157, 14.586]},
    {"chunk_id": 13, "start": 15.015, "end": 16.73, "words": ["cookies,", "passwords,", "and", "two-factor"], "word_starts": [15.015, 15.443, 15.872, 16.301]},
    {"chunk_id": 14, "start": 16.73, "end": 18.017, "words": ["codes", "are", "stolen."], "word_starts": [16.73, 17.159, 17.588]},
    {"chunk_id": 15, "start": 18.017, "end": 19.592, "words": ["Verizon", "DBIR", "confirms:", "ninety-one"], "word_starts": [18.017, 18.411, 18.804, 19.198]},
    {"chunk_id": 16, "start": 19.592, "end": 21.166, "words": ["percent", "of", "all", "cyber"], "word_starts": [19.592, 19.985, 20.379, 20.773]},
    {"chunk_id": 17, "start": 21.166, "end": 22.741, "words": ["breaches", "start", "with", "a"], "word_starts": [21.166, 21.56, 21.953, 22.347]},
    {"chunk_id": 18, "start": 22.741, "end": 24.555, "words": ["phishing", "message.", "Never", "tap"], "word_starts": [22.741, 23.134, 23.528, 24.041]},
    {"chunk_id": 19, "start": 24.555, "end": 26.632, "words": ["unverified", "links.", "Follow", "mwd1504"], "word_starts": [24.555, 25.069, 25.582, 26.107]},
    {"chunk_id": 20, "start": 26.632, "end": 28.731, "words": ["to", "keep", "your", "phone"], "word_starts": [26.632, 27.157, 27.681, 28.206]},
    {"chunk_id": 21, "start": 28.731, "end": 29.256, "words": ["bulletproof."], "word_starts": [28.731]}
]

SHOT_TIMELINE = [
    {"id": 1, "name": "01 HOOK // SMS ALERT", "tag": "THREAT DETECTED", "start": 0.0, "end": 2.8, "dur": 2.8},
    {"id": 2, "name": "02 PULL-BACK // DESK", "tag": "PHYSICAL INTRUSION", "start": 2.8, "end": 5.5, "dur": 2.7},
    {"id": 3, "name": "03 TAP // FAKE BANK", "tag": "EXPLOIT TRIGGER", "start": 5.5, "end": 8.2, "dur": 2.7},
    {"id": 4, "name": "04 DIVE // CUTAWAY PCB", "tag": "HARDWARE CUTAWAY", "start": 8.2, "end": 11.2, "dur": 3.0},
    {"id": 5, "name": "05 COUNTER // 11.2s", "tag": "EXPLOIT VELOCITY", "start": 11.2, "end": 14.0, "dur": 2.8},
    {"id": 6, "name": "06 EXFIL // 3D OBJECTS", "tag": "DATA EXFILTRATION", "start": 14.0, "end": 17.0, "dur": 3.0},
    {"id": 7, "name": "07 PROOF // VERIZON 91%", "tag": "OFFICIAL AUDIT", "start": 17.0, "end": 20.5, "dur": 3.5},
    {"id": 8, "name": "08 DEFENSE // CLAMP", "tag": "HARDWARE INTERCEPT", "start": 20.5, "end": 23.5, "dur": 3.0},
    {"id": 9, "name": "09 RESULT // 0% BULLETPROOF", "tag": "SECURITY ENCLAVE", "start": 23.5, "end": 26.2, "dur": 2.7},
    {"id": 10, "name": "10 CTA // @mwd1504", "tag": "VERIFIED SYSTEM", "start": 26.2, "end": 29.256, "dur": 3.056}
]

def load_chunks():
    if TIMINGS_FILE.exists():
        try:
            with open(TIMINGS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return EMBEDDED_CHUNKS

def ensure_script_json():
    """Ensures .pipeline/script.json exists for scripts/review_video.py audit."""
    PIPELINE_DIR.mkdir(parents=True, exist_ok=True)
    script_path = PIPELINE_DIR / "script.json"
    scenes_meta = [
        {"id": s["id"], "tag": s["name"], "text": s["tag"], "visual_type": f"shot_{s['id']}", "duration": s["dur"]}
        for s in SHOT_TIMELINE
    ]
    data = {
        "title": "How Hackers Phish Your Phone",
        "hook": "One fake text can completely drain your phone",
        "narration": "One fake text can completely drain your phone in seconds...",
        "caption": "#cybersecurity #phishing #tech #mobile #security",
        "scenes": scenes_meta
    }
    with open(script_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def get_effective_audio():
    if AUDIO_FILE.exists() and os.path.getsize(AUDIO_FILE) > 0:
        return str(AUDIO_FILE)
    if FALLBACK_AUDIO.exists() and os.path.getsize(FALLBACK_AUDIO) > 0:
        return str(FALLBACK_AUDIO)
    # Generate synthetic tone track if audio missing
    gen_path = PIPELINE_DIR / "synthetic_audio.mp3"
    if not gen_path.exists():
        subprocess.run([
            "ffmpeg", "-y", "-f", "lavfi", "-i", "sine=frequency=220:duration=29.256",
            "-af", "volume=0.08", "-c:a", "libmp3lame", str(gen_path)
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return str(gen_path)

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

# ----------------- VECTOR ICONS (ZERO EMOJI TOFU) -----------------

def draw_vector_shield(d, cx, cy, size=24, fill=C_EMERALD, outline=C_WHITE):
    """Draws a crisp metallic security shield."""
    hs = size // 2
    pts = [
        (cx - hs, cy - hs),
        (cx + hs, cy - hs),
        (cx + hs, cy),
        (cx, cy + hs + 4),
        (cx - hs, cy)
    ]
    d.polygon(pts, fill=fill, outline=outline)
    # Inner emblem check
    d.line([(cx - 4, cy), (cx - 1, cy + 3), (cx + 5, cy - 3)], fill=(10, 14, 22, 255), width=2)

def draw_vector_warning(d, cx, cy, size=24, fill=C_AMBER, outline=(20, 24, 34, 255)):
    """Draws a rounded danger warning triangle with exclamation."""
    hs = size // 2
    pts = [
        (cx, cy - hs),
        (cx + hs + 2, cy + hs),
        (cx - hs - 2, cy + hs)
    ]
    d.polygon(pts, fill=fill, outline=outline)
    d.line([(cx, cy - hs + 6), (cx, cy + 1)], fill=(10, 14, 22, 255), width=3)
    d.ellipse([cx - 2, cy + 4, cx + 2, cy + 8], fill=(10, 14, 22, 255))

def draw_vector_battery(d, cx, cy, w=34, h=18, pct=1.0, fill=C_EMERALD):
    """Draws a crisp hardware battery cell with terminal."""
    x1, y1 = cx - w//2, cy - h//2
    x2, y2 = cx + w//2, cy + h//2
    d.rounded_rectangle([x1, y1, x2, y2], radius=4, outline=C_MUTED, width=2)
    # Nub
    d.rounded_rectangle([x2, cy - 4, x2 + 3, cy + 4], radius=1, fill=C_MUTED)
    # Fill
    fill_w = int((w - 6) * max(0.0, min(1.0, pct)))
    if fill_w > 0:
        d.rounded_rectangle([x1 + 3, y1 + 3, x1 + 3 + fill_w, y2 - 3], radius=2, fill=fill)

def draw_vector_lock(d, cx, cy, size=22, fill=C_GOLD):
    """Draws a gleaming padlock with shackle."""
    hs = size // 2
    body_y1 = cy - 2
    body_y2 = cy + hs
    # Shackle
    d.arc([cx - hs + 3, cy - hs - 2, cx + hs - 3, cy + 2], start=180, end=0, fill=C_WHITE, width=3)
    # Body
    d.rounded_rectangle([cx - hs, body_y1, cx + hs, body_y2], radius=3, fill=fill, outline=C_WHITE, width=1)
    # Keyhole
    d.ellipse([cx - 2, cy + 2, cx + 2, cy + 6], fill=(10, 14, 22, 255))

def draw_vector_chat(d, cx, cy, size=24, fill=C_RED):
    """Draws a clean SMS speech bubble."""
    hs = size // 2
    d.rounded_rectangle([cx - hs, cy - hs, cx + hs, cy + hs - 4], radius=6, fill=fill)
    tail = [(cx - 2, cy + hs - 4), (cx + 4, cy + hs - 4), (cx - 4, cy + hs + 3)]
    d.polygon(tail, fill=fill)
    # Dots
    for ox in [-4, 0, 4]:
        d.ellipse([cx + ox - 1, cy - 2, cx + ox + 1, cy], fill=C_WHITE)

# ----------------- 3D PERSPECTIVE MATH -----------------

def solve_perspective_coeffs(src_pts, dst_pts):
    """Computes 8 coefficients for Image.PERSPECTIVE mapping dst_pts -> src_pts."""
    A, B = [], []
    for (x, y), (u, v) in zip(dst_pts, src_pts):
        A.append([x, y, 1, 0, 0, 0, -u*x, -u*y])
        B.append(u)
        A.append([0, 0, 0, x, y, 1, -v*x, -v*y])
        B.append(v)
    n = 8
    for i in range(n):
        max_el = abs(A[i][i])
        max_row = i
        for k in range(i + 1, n):
            if abs(A[k][i]) > max_el:
                max_el = abs(A[k][i])
                max_row = k
        A[i], A[max_row] = A[max_row], A[i]
        B[i], B[max_row] = B[max_row], B[i]
        pivot = A[i][i]
        if abs(pivot) < 1e-9:
            pivot = 1e-9
        for j in range(i, n):
            A[i][j] /= pivot
        B[i] /= pivot
        for k in range(n):
            if k != i:
                c = A[k][i]
                for j in range(i, n):
                    A[k][j] -= c * A[i][j]
                B[k] -= c * B[i]
    return tuple(B)

def project_perspective(x, y, z, cx=540, cy=960, yaw=0.0, pitch=20.0, roll=0.0, zoom=1.0, fov=900.0):
    """Consistent 3D perspective camera projection with continuous rotation & zoom."""
    y_rad = math.radians(yaw)
    p_rad = math.radians(pitch)
    r_rad = math.radians(roll)

    # Yaw
    x1 = x * math.cos(y_rad) + z * math.sin(y_rad)
    y1 = y
    z1 = -x * math.sin(y_rad) + z * math.cos(y_rad)

    # Pitch
    x2 = x1
    y2 = y1 * math.cos(p_rad) - z1 * math.sin(p_rad)
    z2 = y1 * math.sin(p_rad) + z1 * math.cos(p_rad)

    # Roll
    x3 = x2 * math.cos(r_rad) - y2 * math.sin(r_rad)
    y3 = x2 * math.sin(r_rad) + y2 * math.cos(r_rad)
    z3 = z2

    dist = max(40.0, fov - z3)
    scale = (fov / dist) * zoom
    return (cx + x3 * scale, cy + y3 * scale)

# ----------------- HUD & KINETIC CAPTIONS -----------------

def draw_hud_telemetry_pill(d, active_idx, scene_tag):
    """
    Sleek top telemetry HUD inspired directly by the inspiration video:
    [ • ENGINE ON / THREAT RADAR | (1) (2) (3) (4) ... ]
    Translucent dark glass pill with subtle border and amber active pill.
    """
    pill_w, pill_h = 920, 64
    x1, y1 = (W - pill_w) // 2, 85
    x2, y2 = x1 + pill_w, y1 + pill_h

    # Translucent glass pill
    d.rounded_rectangle([x1, y1, x2, y2], radius=32, fill=(12, 17, 28, 220), outline=(255, 255, 255, 30), width=1)

    # Left Telemetry status dot & tag
    dot_color = C_AMBER if active_idx in [0, 2, 4, 5] else (C_RED if active_idx in [1, 3] else C_EMERALD)
    d.ellipse([x1 + 24, y1 + 25, x1 + 38, y1 + 39], fill=dot_color)
    d.text((x1 + 50, y1 + 20), f"• {scene_tag}", font=font_hud_label, fill=(241, 245, 249, 240))

    # Right numbered progress pills
    total_steps = 10
    step_r = 14
    step_gap = 10
    start_x = x2 - total_steps * (step_r * 2 + step_gap) - 15

    for i in range(total_steps):
        sx = start_x + i * (step_r * 2 + step_gap) + step_r
        sy = y1 + pill_h // 2
        is_cur = (i == active_idx)
        if is_cur:
            d.ellipse([sx - step_r, sy - step_r, sx + step_r, sy + step_r], fill=C_AMBER)
            d.text((sx - 5, sy - 10), str(i + 1), font=font_hud_tab, fill=(10, 14, 22, 255))
        else:
            d.ellipse([sx - step_r, sy - step_r, sx + step_r, sy + step_r], fill=(22, 30, 46, 200), outline=(71, 85, 105, 120), width=1)
            d.text((sx - 5, sy - 10), str(i + 1), font=font_hud_tab, fill=(148, 163, 184, 180))

def draw_kinetic_caption_pill(d, t, timings_data):
    """
    Kinetic lower-third captions matching the inspiration video:
    - Frosted dark pill hugging 2-4 words
    - Spoken word highlighted with thick underline
    - Lower third safe zone (y ≈ 1620)
    """
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

    pad_x, pad_y = 28, 16
    pill_w = total_w + pad_x * 2
    pill_h = 58 + pad_y * 2
    pill_x1 = (W - pill_w) // 2
    pill_y1 = 1620
    pill_x2 = pill_x1 + pill_w
    pill_y2 = pill_y1 + pill_h

    # Translucent dark pill hugging text
    d.rounded_rectangle([pill_x1, pill_y1, pill_x2, pill_y2], radius=22,
                        fill=(10, 15, 25, 225), outline=(255, 255, 255, 30), width=1)

    active_word_idx = -1
    for i, w_start in enumerate(word_starts):
        if t >= w_start:
            active_word_idx = i

    cur_x = pill_x1 + pad_x
    text_y = pill_y1 + pad_y + 4

    for i, (w, w_w) in enumerate(word_metrics):
        is_active = (i == active_word_idx)
        if is_active:
            # Active word with thick underline highlight
            d.text((cur_x, text_y), w, font=font_caption, fill=C_WHITE)
            d.line([(cur_x, text_y + 50), (cur_x + w_w, text_y + 50)], fill=C_GOLD, width=4)
        else:
            # Dimmed inactive words
            d.text((cur_x, text_y), w, font=font_caption, fill=(160, 174, 192, 230))
        cur_x += w_w + space_w

def draw_callout_hud(d, target_pt, label_pt, text, accent_color=C_CYAN):
    """Sleek technical leader-line callout with anchor dot and bounded rounded pill label."""
    tx, ty = target_pt
    lx, ly = label_pt

    # Anchor dot
    d.ellipse([tx - 4, ty - 4, tx + 4, ty + 4], fill=accent_color)
    d.ellipse([tx - 8, ty - 8, tx + 8, ty + 8], outline=accent_color, width=1)

    bbox = font_callout_txt.getbbox(text)
    txt_w = bbox[2] - bbox[0]
    pill_w = txt_w + 24

    # Calculate rx1 clamped inside safe margin [40, W - pill_w - 40]
    if lx > tx:
        rx1 = max(40, min(W - pill_w - 40, lx))
        line_anchor = rx1
    else:
        rx1 = max(40, min(W - pill_w - 40, lx - pill_w))
        line_anchor = rx1 + pill_w

    rx2 = rx1 + pill_w
    ry1 = ly - 16
    ry2 = ly + 16

    # Leader line
    mid_x = (tx + line_anchor) // 2
    d.line([(tx, ty), (mid_x, ly), (line_anchor, ly)], fill=accent_color, width=2)

    # Monospaced label tag
    d.rounded_rectangle([rx1, ry1, rx2, ry2], radius=8,
                        fill=(12, 18, 30, 235), outline=(255, 255, 255, 40), width=1)
    d.text((rx1 + 12, ry1 + 6), text, font=font_callout_txt, fill=accent_color)

# ----------------- SUPERSAMPLED SCREEN TEXTURES (2X RESOLUTION) -----------------

def generate_supersampled_lockscreen(alert_pulse=0.0):
    """960x2000 Lockscreen texture with verified zero-overflow SMS card."""
    screen = Image.new("RGBA", (SW, SH), (6, 10, 18, 255))
    d = ImageDraw.Draw(screen)

    # Subtle radial OLED glow
    d.ellipse([SW//2 - 400, 200, SW//2 + 400, 1000], fill=(14, 24, 42, 120))

    # Top Status Bar
    d.text((70, 36), "Verizon", font=font_ui_date, fill=C_MUTED)
    draw_vector_battery(d, SW - 90, 52, w=54, h=26, pct=0.95, fill=C_WHITE)
    d.text((SW - 220, 36), "5G", font=font_ui_date, fill=C_MUTED)

    # Dynamic Island
    d.rounded_rectangle([SW//2 - 110, 28, SW//2 + 110, 84], radius=28, fill=(3, 5, 8, 255))
    d.ellipse([SW//2 + 65, 46, SW//2 + 85, 66], fill=(12, 18, 32, 255))  # Camera lens

    # Clock & Date
    d.text((SW//2 - 190, 180), "09:41", font=font_ui_clock, fill=C_WHITE)
    d.text((SW//2 - 180, 340), "Tuesday, November 10", font=font_ui_date, fill=C_MUTED)

    # High-Risk SMS Warning Card
    pulse_val = int(alert_pulse * 35)
    card_y = 520
    card_h = 440
    card_x1, card_x2 = 50, SW - 50

    d.rounded_rectangle([card_x1, card_y, card_x2, card_y + card_h], radius=36,
                        fill=(32 + pulse_val, 14, 22, 250), outline=C_RED, width=4)

    # Header with procedural vector chat icon
    draw_vector_chat(d, card_x1 + 55, card_y + 55, size=40, fill=C_RED)
    d.text((card_x1 + 90, card_y + 36), "BANK ALERT • NOW", font=font_ui_bold, fill=C_RED)

    # Body copy with safe margin padding (zero clipping)
    d.text((card_x1 + 45, card_y + 115), "Unauthorized $840 transfer detected.", font=font_ui_reg, fill=C_WHITE)
    d.text((card_x1 + 45, card_y + 175), "Tap link to verify your account immediately:", font=font_ui_reg, fill=(226, 232, 240, 240))

    # Malicious Action Button
    btn_y1 = card_y + 260
    btn_y2 = btn_y1 + 120
    d.rounded_rectangle([card_x1 + 40, btn_y1, card_x2 - 40, btn_y2], radius=20,
                        fill=(68, 18, 28, 255), outline=C_RED, width=3)
    draw_vector_warning(d, card_x1 + 80, btn_y1 + 60, size=32, fill=C_AMBER)
    d.text((card_x1 + 115, btn_y1 + 38), "chase-fraud-verify.cc/login", font=font_ui_code, fill=C_RED)

    # In-Display Fingerprint Sensor Icon
    fp_cy = 1580
    d.ellipse([SW//2 - 70, fp_cy - 70, SW//2 + 70, fp_cy + 70], outline=C_CYAN, width=3)
    d.arc([SW//2 - 50, fp_cy - 50, SW//2 + 50, fp_cy + 50], start=45, end=315, fill=C_CYAN, width=3)
    d.arc([SW//2 - 30, fp_cy - 30, SW//2 + 30, fp_cy + 30], start=60, end=300, fill=C_CYAN, width=3)

    # Home bar
    d.rounded_rectangle([SW//2 - 120, SH - 40, SW//2 + 120, SH - 28], radius=6, fill=(148, 163, 184, 180))
    return screen

def generate_supersampled_fake_bank():
    """960x2000 Fake Bank Phishing Portal Texture."""
    screen = Image.new("RGBA", (SW, SH), (10, 14, 24, 255))
    d = ImageDraw.Draw(screen)

    # Dynamic Island
    d.rounded_rectangle([SW//2 - 110, 28, SW//2 + 110, 84], radius=28, fill=(3, 5, 8, 255))

    # Bank Header Bar
    d.rounded_rectangle([40, 140, SW - 40, 260], radius=24, fill=(18, 26, 44, 255), outline=C_AMBER, width=2)
    draw_vector_lock(d, 90, 200, size=36, fill=C_GOLD)
    d.text((130, 178), "CHASE ONLINE VERIFICATION", font=font_ui_bold, fill=C_WHITE)

    # Fake Login Form Card
    form_y = 320
    form_h = 760
    d.rounded_rectangle([40, form_y, SW - 40, form_y + form_h], radius=32,
                        fill=(14, 20, 34, 250), outline=(0, 242, 254, 80), width=2)

    d.text((80, form_y + 60), "CONFIRM IDENTITY", font=font_ui_bold, fill=C_AMBER)
    d.text((80, form_y + 125), "Username or Card Number:", font=font_ui_reg, fill=C_MUTED)
    d.rounded_rectangle([80, form_y + 180, SW - 80, form_y + 270], radius=16,
                        fill=(8, 12, 22, 255), outline=C_MUTED, width=2)
    d.text((110, form_y + 205), "user_891247@chase.com", font=font_ui_code, fill=C_WHITE)

    d.text((80, form_y + 310), "Password / Security PIN:", font=font_ui_reg, fill=C_MUTED)
    d.rounded_rectangle([80, form_y + 365, SW - 80, form_y + 455], radius=16,
                        fill=(8, 12, 22, 255), outline=C_MUTED, width=2)
    d.text((110, form_y + 395), "••••••••••••", font=font_ui_clock, fill=C_RED)

    # Submit Button
    btn_y1 = form_y + 530
    btn_y2 = btn_y1 + 130
    d.rounded_rectangle([80, btn_y1, SW - 80, btn_y2], radius=22, fill=C_RED)
    d.text((SW//2 - 130, btn_y1 + 42), "VERIFY NOW", font=font_ui_btn, fill=C_WHITE)

    # Exfiltration warning badge
    d.rounded_rectangle([80, 1140, SW - 80, 1320], radius=24,
                        fill=(42, 14, 22, 255), outline=C_RED, width=2)
    draw_vector_warning(d, 130, 1230, size=38, fill=C_RED)
    d.text((175, 1185), "CREDENTIAL HARVEST ACTIVE", font=font_ui_bold, fill=C_RED)
    d.text((175, 1245), "Injecting keylogger payload to bus...", font=font_ui_reg, fill=C_MUTED)

    # Home bar
    d.rounded_rectangle([SW//2 - 120, SH - 40, SW//2 + 120, SH - 28], radius=6, fill=(148, 163, 184, 180))
    return screen

def generate_supersampled_clamping(clamp_progress=0.0):
    """960x2000 Clamping & Security Transition Texture."""
    screen = Image.new("RGBA", (SW, SH), (6, 12, 20, 255))
    d = ImageDraw.Draw(screen)

    # Dynamic Island
    d.rounded_rectangle([SW//2 - 110, 28, SW//2 + 110, 84], radius=28, fill=(3, 5, 8, 255))

    is_clamped = (clamp_progress >= 0.45)
    card_y = 520
    card_h = 440
    card_fill = (14, 38, 30, 250) if is_clamped else (36, 14, 22, 250)
    card_out = C_EMERALD if is_clamped else C_RED

    d.rounded_rectangle([50, card_y, SW - 50, card_y + card_h], radius=36, fill=card_fill, outline=card_out, width=4)

    if not is_clamped:
        draw_vector_chat(d, 105, card_y + 55, size=40, fill=C_RED)
        d.text((140, card_y + 36), "BANK ALERT • NOW", font=font_ui_bold, fill=C_RED)
        d.text((95, card_y + 115), "Unauthorized $840 transfer detected.", font=font_ui_reg, fill=C_WHITE)
        d.text((95, card_y + 175), "Action required. Verify account now:", font=font_ui_reg, fill=C_MUTED)
        d.rounded_rectangle([90, card_y + 260, SW - 90, card_y + 380], radius=20,
                            fill=(68, 18, 28, 255), outline=C_RED, width=3)
        d.text((120, card_y + 298), "chase-fraud-verify.cc/login", font=font_ui_code, fill=C_RED)
    else:
        draw_vector_shield(d, 105, card_y + 55, size=42, fill=C_EMERALD)
        d.text((140, card_y + 36), "SMS SHIELD: INTERCEPTED", font=font_ui_bold, fill=C_EMERALD)
        d.text((95, card_y + 115), "Malicious banking domain blocked.", font=font_ui_reg, fill=C_WHITE)
        d.text((95, card_y + 175), "Hardware token access severed permanently.", font=font_ui_reg, fill=C_MUTED)
        d.rounded_rectangle([90, card_y + 260, SW - 90, card_y + 380], radius=20,
                            fill=(20, 58, 44, 255), outline=C_EMERALD, width=3)
        draw_vector_lock(d, 140, card_y + 320, size=32, fill=C_GOLD)
        d.text((175, card_y + 298), "LINK SEVERED & BLOCKED", font=font_ui_code, fill=C_EMERALD)

    # Titanium Security Clamp Mechanism
    clamp_drop = min(1.0, clamp_progress * 2.2)
    clamp_target_y = card_y + 240
    clamp_y = int(clamp_target_y - (1.0 - clamp_drop) * 320)

    # Heavy titanium bracket
    d.rounded_rectangle([70, clamp_y, SW - 70, clamp_y + 130], radius=24,
                        fill=(42, 54, 74, 252), outline=C_CYAN, width=4)
    # Fastener bolts
    for bx in [110, SW - 110]:
        d.ellipse([bx - 12, clamp_y + 25, bx + 12, clamp_y + 49], fill=(180, 200, 220, 255), outline=(30, 40, 55, 255), width=2)
    draw_vector_shield(d, SW//2 - 160, clamp_y + 65, size=34, fill=C_CYAN)
    d.text((SW//2 - 130, clamp_y + 45), "TITANIUM SECURITY CLAMP", font=font_ui_bold, fill=C_CYAN)

    # Home bar
    d.rounded_rectangle([SW//2 - 120, SH - 40, SW//2 + 120, SH - 28], radius=6, fill=(148, 163, 184, 180))
    return screen

def generate_supersampled_shield_safe():
    """960x2000 Hardened Safe Enclave Texture."""
    screen = Image.new("RGBA", (SW, SH), (8, 18, 26, 255))
    d = ImageDraw.Draw(screen)

    # Dynamic Island
    d.rounded_rectangle([SW//2 - 110, 28, SW//2 + 110, 84], radius=28, fill=(3, 5, 8, 255))

    # Clock & Date
    d.text((SW//2 - 190, 180), "09:41", font=font_ui_clock, fill=C_WHITE)
    d.text((SW//2 - 180, 340), "Tuesday, November 10", font=font_ui_date, fill=C_MUTED)

    # Big Emerald Shield Card
    card_y = 500
    card_h = 460
    d.rounded_rectangle([50, card_y, SW - 50, card_y + card_h], radius=36,
                        fill=(14, 40, 32, 252), outline=C_EMERALD, width=4)
    draw_vector_shield(d, 110, card_y + 65, size=46, fill=C_EMERALD)
    d.text((150, card_y + 45), "DEFENSE ACTIVE // SAFE", font=font_ui_bold, fill=C_EMERALD)
    d.text((95, card_y + 130), "All phishing conduits permanently sealed.", font=font_ui_reg, fill=C_WHITE)
    d.text((95, card_y + 195), "Device enclave locked. Zero data leaked.", font=font_ui_reg, fill=C_MUTED)

    d.rounded_rectangle([90, card_y + 280, SW - 90, card_y + 390], radius=20,
                        fill=(22, 64, 48, 255), outline=C_EMERALD, width=3)
    d.text((SW//2 - 200, card_y + 312), "STATUS: BULLETPROOF", font=font_ui_bold, fill=C_GOLD)

    # Home bar
    d.rounded_rectangle([SW//2 - 120, SH - 40, SW//2 + 120, SH - 28], radius=6, fill=(148, 163, 184, 180))
    return screen

# ----------------- 3D PHONE WITH LIT MATERIALS & SPECULAR SHEEN -----------------

def draw_lit_3d_phone(canvas, cx=540, cy=960, pw=520, ph=1080, depth=42,
                      yaw=0.0, pitch=20.0, roll=0.0, zoom=1.0,
                      screen_type="lockscreen", alert_pulse=0.0, clamp_progress=0.0):
    """
    Renders truly 3D smartphone with lit metallic rails, specular bevels,
    diffuse contact shadow, supersampled screen, and glass reflection sheen.
    """
    hw, hh, hd = pw / 2.0, ph / 2.0, depth / 2.0

    # 1. Multi-tier Diffuse Contact Shadow on Floor Plane
    shadow_ox = 35.0
    shadow_oy = 60.0
    shadow_pts = [
        project_perspective(-hw - 30 + shadow_ox, -hh - 20 + shadow_oy, -hd - 20, cx, cy, yaw, pitch, roll, zoom),
        project_perspective(hw + 40 + shadow_ox, -hh - 20 + shadow_oy, -hd - 20, cx, cy, yaw, pitch, roll, zoom),
        project_perspective(hw + 40 + shadow_ox, hh + 45 + shadow_oy, -hd - 20, cx, cy, yaw, pitch, roll, zoom),
        project_perspective(-hw - 30 + shadow_ox, hh + 45 + shadow_oy, -hd - 20, cx, cy, yaw, pitch, roll, zoom)
    ]
    shadow_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    s_d = ImageDraw.Draw(shadow_layer)
    s_d.polygon(shadow_pts, fill=(2, 4, 8, 190))
    # Soften contact shadow with Gaussian blur
    shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(radius=18))
    canvas.alpha_composite(shadow_layer)

    d = ImageDraw.Draw(canvas)

    # 2. Lit Metallic Titanium Rails (Front & Back 3D Extrusion)
    # Corner offsets
    front_corners = [
        project_perspective(-hw, -hh, hd, cx, cy, yaw, pitch, roll, zoom),
        project_perspective(hw, -hh, hd, cx, cy, yaw, pitch, roll, zoom),
        project_perspective(hw, hh, hd, cx, cy, yaw, pitch, roll, zoom),
        project_perspective(-hw, hh, hd, cx, cy, yaw, pitch, roll, zoom)
    ]
    back_corners = [
        project_perspective(-hw, -hh, -hd, cx, cy, yaw, pitch, roll, zoom),
        project_perspective(hw, -hh, -hd, cx, cy, yaw, pitch, roll, zoom),
        project_perspective(hw, hh, -hd, cx, cy, yaw, pitch, roll, zoom),
        project_perspective(-hw, hh, -hd, cx, cy, yaw, pitch, roll, zoom)
    ]

    # Rear Chassis Plate
    d.polygon(back_corners, fill=(18, 24, 36, 255), outline=(45, 60, 85, 255))

    # Extruded Side Rails with directional light shading
    # Right Rail
    if yaw >= -15:
        d.polygon([front_corners[1], back_corners[1], back_corners[2], front_corners[2]],
                  fill=(28, 38, 54, 255), outline=(70, 90, 120, 255))
        # Volume buttons on right rail
        b1_f = project_perspective(hw, -hh + 240, hd - 4, cx, cy, yaw, pitch, roll, zoom)
        b1_b = project_perspective(hw + 4, -hh + 320, -hd + 4, cx, cy, yaw, pitch, roll, zoom)
        d.line([b1_f, b1_b], fill=(180, 200, 230, 255), width=4)

    # Left Rail
    if yaw <= 15:
        d.polygon([front_corners[0], back_corners[0], back_corners[3], front_corners[3]],
                  fill=(42, 54, 76, 255), outline=(95, 120, 160, 255))

    # Bottom Rail
    d.polygon([front_corners[3], back_corners[3], back_corners[2], front_corners[2]],
              fill=(16, 22, 32, 255), outline=(40, 55, 75, 255))

    # Top Rail (High specular reflection)
    d.polygon([front_corners[0], back_corners[0], back_corners[1], front_corners[1]],
              fill=(65, 82, 110, 255), outline=(180, 205, 240, 255))

    # 3. Supersampled Screen Texture
    if screen_type == "lockscreen":
        tex = generate_supersampled_lockscreen(alert_pulse)
    elif screen_type == "fake_bank":
        tex = generate_supersampled_fake_bank()
    elif screen_type == "clamping":
        tex = generate_supersampled_clamping(clamp_progress)
    else:
        tex = generate_supersampled_shield_safe()

    # Perspective Transform & Composite
    src_pts = [(0, 0), (SW, 0), (SW, SH), (0, SH)]
    coeffs = solve_perspective_coeffs(src_pts, front_corners)
    warped_screen = tex.transform((W, H), Image.Transform.PERSPECTIVE, coeffs, resample=Image.Resampling.BICUBIC)
    canvas.alpha_composite(warped_screen)

    # 4. Glass Studio Reflection Sheen Overlay
    glass_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    g_d = ImageDraw.Draw(glass_layer)
    # Diagonal glass reflection beam across phone
    sheen_p1 = project_perspective(-hw, -hh + 200, hd + 1, cx, cy, yaw, pitch, roll, zoom)
    sheen_p2 = project_perspective(hw, -hh + 50, hd + 1, cx, cy, yaw, pitch, roll, zoom)
    sheen_p3 = project_perspective(hw, -hh + 180, hd + 1, cx, cy, yaw, pitch, roll, zoom)
    sheen_p4 = project_perspective(-hw, -hh + 330, hd + 1, cx, cy, yaw, pitch, roll, zoom)
    g_d.polygon([sheen_p1, sheen_p2, sheen_p3, sheen_p4], fill=(255, 255, 255, 24))
    canvas.alpha_composite(glass_layer)

    # 5. Beveled Chamfer Highlight Line around front glass edge
    d_front = ImageDraw.Draw(canvas)
    d_front.polygon(front_corners, outline=(180, 215, 255, 160), width=2)

# ----------------- SCENE SPECIFIC 3D HERO DRAWERS -----------------

def draw_3d_hand_grip(canvas, cx, cy, shot_rel_t):
    """
    Scene 2: Stylized cyber-mannequin 3D hand holding the phone.
    Modeled after inspiration video sec_025.png with shaded knuckles & metallic joints.
    """
    hand_overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(hand_overlay)

    # Reaching thumb from right side with joints & specular reflections
    thumb_x = 760 - int(shot_rel_t * 30)
    thumb_y = 960 + int(shot_rel_t * 40)

    # Palm base with cyber-slate tone
    d.ellipse([thumb_x + 50, thumb_y - 90, thumb_x + 280, thumb_y + 240],
              fill=(38, 48, 66, 255), outline=(90, 115, 150, 255), width=2)

    # Thumb segment with gradient highlight
    d.rounded_rectangle([thumb_x, thumb_y - 25, thumb_x + 120, thumb_y + 35], radius=25,
                        fill=(54, 68, 92, 255), outline=(140, 175, 215, 255), width=2)
    # Thumb tip touching screen rail
    d.ellipse([thumb_x - 18, thumb_y - 22, thumb_x + 22, thumb_y + 28],
              fill=(80, 102, 134, 255), outline=C_CYAN, width=2)

    # Left-side stabilizing fingers curling around phone rail
    for fi in range(3):
        fy = 740 + fi * 90
        fx = 280
        d.rounded_rectangle([fx - 70, fy, fx + 25, fy + 55], radius=20,
                            fill=(46, 58, 80, 255), outline=(110, 135, 175, 255), width=2)
        # Specular knuckle highlight
        d.ellipse([fx + 2, fy + 10, fx + 24, fy + 44], fill=(75, 96, 128, 255))

    canvas.alpha_composite(hand_overlay)

def draw_3d_cutaway_teardown(canvas, shot_rel_t):
    """
    Scene 4: True 3D perspective cutaway hardware teardown.
    - 3D exploded chassis wall with standoffs
    - Li-Ion battery pack with brushed texture & voltage badge
    - Motherboard with gleaming gold PCB traces & microchips
    - 3D Enclave socket + Trojan token chip sliding into slot with electric sparks
    """
    d = ImageDraw.Draw(canvas)
    cx, cy = 540, 910
    yaw, pitch = 20.0, 28.0
    zoom = 0.90

    # 1. 3D Chassis Cutaway Tray
    cw, ch, cd = 680, 1180, 48
    pts_tray_bot = [
        project_perspective(-cw//2, -ch//2, -cd, cx, cy, yaw, pitch, zoom=zoom),
        project_perspective(cw//2, -ch//2, -cd, cx, cy, yaw, pitch, zoom=zoom),
        project_perspective(cw//2, ch//2, -cd, cx, cy, yaw, pitch, zoom=zoom),
        project_perspective(-cw//2, ch//2, -cd, cx, cy, yaw, pitch, zoom=zoom)
    ]
    pts_tray_top = [
        project_perspective(-cw//2, -ch//2, 0, cx, cy, yaw, pitch, zoom=zoom),
        project_perspective(cw//2, -ch//2, 0, cx, cy, yaw, pitch, zoom=zoom),
        project_perspective(cw//2, ch//2, 0, cx, cy, yaw, pitch, zoom=zoom),
        project_perspective(-cw//2, ch//2, 0, cx, cy, yaw, pitch, zoom=zoom)
    ]
    d.polygon(pts_tray_bot, fill=(10, 14, 24, 255))
    d.polygon([pts_tray_top[0], pts_tray_bot[0], pts_tray_bot[3], pts_tray_top[3]],
              fill=(20, 28, 44, 255), outline=C_CYAN)
    d.polygon([pts_tray_top[3], pts_tray_bot[3], pts_tray_bot[2], pts_tray_top[2]],
              fill=(16, 22, 34, 255), outline=C_CYAN)
    d.polygon(pts_tray_top, outline=(0, 242, 254, 180), width=2)

    # 2. Li-Ion Battery Pack (Left Chamber in 3D)
    bw, bh, bd = 260, 960, 28
    bx_off = -cw//4 - 20
    b_corners_top = [
        project_perspective(bx_off - bw//2, -bh//2, -cd + bd, cx, cy, yaw, pitch, zoom=zoom),
        project_perspective(bx_off + bw//2, -bh//2, -cd + bd, cx, cy, yaw, pitch, zoom=zoom),
        project_perspective(bx_off + bw//2, bh//2, -cd + bd, cx, cy, yaw, pitch, zoom=zoom),
        project_perspective(bx_off - bw//2, bh//2, -cd + bd, cx, cy, yaw, pitch, zoom=zoom)
    ]
    d.polygon(b_corners_top, fill=(18, 22, 32, 255), outline=(71, 85, 105, 255), width=2)
    # Battery Label & Silver Terminals in 3D
    t1 = project_perspective(bx_off - 60, -bh//2 + 40, -cd + bd + 2, cx, cy, yaw, pitch, zoom=zoom)
    draw_vector_battery(d, int(t1[0]), int(t1[1]), w=42, h=22, pct=0.88, fill=C_EMERALD)
    d.text((t1[0] + 32, t1[1] - 12), "4,500 mAh Li-Ion", font=font_proof_body, fill=C_WHITE)

    # 3. Motherboard PCB with Gold Traces (Right Chamber in 3D)
    mw, mh = 280, 960
    mx_off = cw//4 + 20
    m_corners_top = [
        project_perspective(mx_off - mw//2, -mh//2, -cd + 10, cx, cy, yaw, pitch, zoom=zoom),
        project_perspective(mx_off + mw//2, -mh//2, -cd + 10, cx, cy, yaw, pitch, zoom=zoom),
        project_perspective(mx_off + mw//2, mh//2, -cd + 10, cx, cy, yaw, pitch, zoom=zoom),
        project_perspective(mx_off - mw//2, mh//2, -cd + 10, cx, cy, yaw, pitch, zoom=zoom)
    ]
    d.polygon(m_corners_top, fill=(12, 30, 24, 255), outline=C_CYAN, width=2)

    # Gold wiring traces across PCB
    for gy in range(-380, 380, 70):
        p1 = project_perspective(mx_off - mw//2 + 20, gy, -cd + 12, cx, cy, yaw, pitch, zoom=zoom)
        p2 = project_perspective(mx_off + mw//2 - 20, gy + 30, -cd + 12, cx, cy, yaw, pitch, zoom=zoom)
        d.line([p1, p2], fill=(180, 140, 50, 180), width=2)

    # 3D Surface-Mount Microchips (ICs) with silver pins
    for ic_y in [-280, -140, 240]:
        ic_pts = [
            project_perspective(mx_off - 70, ic_y - 40, -cd + 18, cx, cy, yaw, pitch, zoom=zoom),
            project_perspective(mx_off + 70, ic_y - 40, -cd + 18, cx, cy, yaw, pitch, zoom=zoom),
            project_perspective(mx_off + 70, ic_y + 40, -cd + 18, cx, cy, yaw, pitch, zoom=zoom),
            project_perspective(mx_off - 70, ic_y + 40, -cd + 18, cx, cy, yaw, pitch, zoom=zoom)
        ]
        d.polygon(ic_pts, fill=(18, 24, 34, 255), outline=(140, 165, 195, 255), width=2)
        # Silver pins
        for pi in range(4):
            pin_p1 = project_perspective(mx_off - 85, ic_y - 30 + pi * 20, -cd + 12, cx, cy, yaw, pitch, zoom=zoom)
            pin_p2 = project_perspective(mx_off - 70, ic_y - 30 + pi * 20, -cd + 16, cx, cy, yaw, pitch, zoom=zoom)
            d.line([pin_p1, pin_p2], fill=(210, 225, 245, 255), width=2)

    # 4. Security Enclave Socket
    sock_y = 60
    s_top = [
        project_perspective(mx_off - 100, sock_y - 80, -cd + 14, cx, cy, yaw, pitch, zoom=zoom),
        project_perspective(mx_off + 100, sock_y - 80, -cd + 14, cx, cy, yaw, pitch, zoom=zoom),
        project_perspective(mx_off + 100, sock_y + 80, -cd + 14, cx, cy, yaw, pitch, zoom=zoom),
        project_perspective(mx_off - 100, sock_y + 80, -cd + 14, cx, cy, yaw, pitch, zoom=zoom)
    ]
    d.polygon(s_top, fill=(8, 14, 24, 255), outline=C_GOLD, width=3)

    # 5. Glowing Trojan Token Chip Descending in 3D
    slide = min(1.0, shot_rel_t * 1.3)
    chip_z = -cd + 14 + (1.0 - slide) * 160
    c_pts = [
        project_perspective(mx_off - 80, sock_y - 60, chip_z, cx, cy, yaw, pitch, zoom=zoom),
        project_perspective(mx_off + 80, sock_y - 60, chip_z, cx, cy, yaw, pitch, zoom=zoom),
        project_perspective(mx_off + 80, sock_y + 60, chip_z, cx, cy, yaw, pitch, zoom=zoom),
        project_perspective(mx_off - 80, sock_y + 60, chip_z, cx, cy, yaw, pitch, zoom=zoom)
    ]
    d.polygon(c_pts, fill=(58, 14, 24, 255), outline=C_RED, width=3)
    chip_center = project_perspective(mx_off, sock_y, chip_z, cx, cy, yaw, pitch, zoom=zoom)
    d.text((chip_center[0] - 65, chip_center[1] - 14), "TROJAN CHIP", font=font_callout_txt, fill=C_WHITE)

    # Cyan Electrical Sparks once seated
    if slide >= 0.85:
        for si in range(6):
            sp1 = project_perspective(mx_off - 70 + si * 28, sock_y + 65, -cd + 16, cx, cy, yaw, pitch, zoom=zoom)
            sp2 = (sp1[0] + (si % 2 * 14 - 7), sp1[1] + 16)
            d.line([sp1, sp2], fill=C_CYAN, width=3)

    # Callouts
    b_pt = project_perspective(bx_off, 0, -cd + bd, cx, cy, yaw, pitch, zoom=zoom)
    draw_callout_hud(d, (int(b_pt[0]), int(b_pt[1])), (180, 520), "LITHIUM-ION BATTERY", C_CYAN)

    ch_pt = project_perspective(mx_off, sock_y, chip_z, cx, cy, yaw, pitch, zoom=zoom)
    draw_callout_hud(d, (int(ch_pt[0]), int(ch_pt[1])), (890, 740), "PAYLOAD INGESTION", C_RED)

def draw_official_authority_card(canvas, shot_rel_t):
    """
    Scene 7: Official Authority Proof Card matching Apple Support doc in inspo sec_060.png:
    - High-contrast white/light-ivory document card with drop shadow
    - Dark header tab: cisa.gov / verizon-dbir
    - Big 100px+ 91% hero stat & radial arc
    - Pastel yellow highlighter strip over key evidence quote
    """
    doc_overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d_doc = ImageDraw.Draw(doc_overlay)

    card_w, card_h = 860, 560
    card_x = (W - card_w) // 2
    card_y = 420

    # Multi-tier drop shadow grounding document in 3D
    for i in range(12):
        d_doc.rounded_rectangle([card_x - i*2, card_y - i*2, card_x + card_w + i*2, card_y + card_h + i*3],
                                radius=32, fill=(2, 4, 8, 18))

    # White Document Card
    d_doc.rounded_rectangle([card_x, card_y, card_x + card_w, card_y + card_h], radius=28,
                            fill=(250, 252, 255, 255), outline=(210, 220, 235, 255), width=2)

    # Dark URL Tab Header (matching support.apple.com tab)
    tab_w, tab_h = 320, 44
    tab_x = card_x + (card_w - tab_w) // 2
    d_doc.rounded_rectangle([tab_x, card_y + 16, tab_x + tab_w, card_y + 16 + tab_h], radius=14,
                            fill=(18, 24, 38, 255))
    draw_vector_lock(d_doc, tab_x + 28, card_y + 38, size=18, fill=C_EMERALD)
    d_doc.text((tab_x + 46, card_y + 26), "cisa.gov / verizon-dbir", font=font_proof_stat, fill=C_WHITE)

    # Document Title
    d_doc.text((card_x + 45, card_y + 80), "VERIZON DATA BREACH INVESTIGATIONS REPORT",
               font=font_proof_title, fill=(15, 23, 42, 255))

    # Giant 91% Hero Stat Radial Gauge
    gauge_cx, gauge_cy = card_x + 150, card_y + 240
    d_doc.ellipse([gauge_cx - 75, gauge_cy - 75, gauge_cx + 75, gauge_cy + 75],
                  outline=(226, 232, 240, 255), width=12)
    sweep_ang = int(min(1.0, shot_rel_t * 1.3) * 328)
    d_doc.arc([gauge_cx - 75, gauge_cy - 75, gauge_cx + 75, gauge_cy + 75],
              start=-90, end=-90 + sweep_ang, fill=C_RED, width=14)
    d_doc.text((gauge_cx - 70, gauge_cy - 48), "91%", font=font_hero_num, fill=C_RED)

    # Breakdown Bars
    bx = card_x + 280
    d_doc.text((bx, card_y + 155), "PRIMARY ATTACK VECTOR", font=font_hero_label, fill=(180, 83, 9, 255))

    d_doc.text((bx, card_y + 195), "Phishing Links & Spoofed SMS: 91%", font=font_proof_body, fill=(30, 41, 59, 255))
    d_doc.rounded_rectangle([bx, card_y + 225, bx + 510, card_y + 245], radius=6, fill=C_RED)

    d_doc.text((bx, card_y + 260), "Brute Force: 5%   |   Zero-Day: 4%", font=font_proof_body, fill=C_MUTED)
    d_doc.rounded_rectangle([bx, card_y + 288, bx + 65, card_y + 304], radius=4, fill=(148, 163, 184, 255))

    # Yellow Highlighter Box (matching inspiration sec_060.png)
    hl_y1 = card_y + 345
    hl_y2 = card_y + 490
    d_doc.rounded_rectangle([card_x + 35, hl_y1, card_x + card_w - 35, hl_y2], radius=16,
                            fill=(254, 243, 199, 255), outline=(252, 211, 77, 255), width=2)

    d_doc.text((card_x + 55, hl_y1 + 22),
               "“Over 91% of mobile device compromises originate from a single",
               font=font_proof_body, fill=(120, 53, 15, 255))
    d_doc.text((card_x + 55, hl_y1 + 54),
               "unverified SMS or email link bypassing endpoint firewalls.”",
               font=font_proof_body, fill=(120, 53, 15, 255))
    d_doc.text((card_x + 55, hl_y1 + 92),
               "Official Authority Citation: CISA Mobile Security Guidelines & DBIR",
               font=font_proof_stat, fill=(180, 83, 9, 255))

    canvas.alpha_composite(doc_overlay)

# ----------------- MASTER FRAME RENDERER -----------------

def render_v2_frame(frame_idx, total_frames, timings_data):
    """Renders one master production frame (1080x1920 RGBA) with all guidelines applied."""
    t = frame_idx / float(FPS)
    progress = frame_idx / float(max(1, total_frames - 1))

    # Find current shot
    current_shot = SHOT_TIMELINE[-1]
    active_idx = len(SHOT_TIMELINE) - 1
    for i, sc in enumerate(SHOT_TIMELINE):
        if sc["start"] <= t < sc["end"]:
            current_shot = sc
            active_idx = i
            break

    shot_dur = current_shot["dur"]
    shot_rel_t = max(0.0, min(1.0, (t - current_shot["start"]) / max(0.001, shot_dur)))

    # Master Canvas with Deep Obsidian Radial Lighting
    im = Image.new("RGBA", (W, H), (8, 12, 18, 255))
    d = ImageDraw.Draw(im)

    # Ambient radial gradient illumination
    d.ellipse([W//2 - 600, H//2 - 600, W//2 + 600, H//2 + 600], fill=(14, 20, 32, 255))
    d.ellipse([W//2 - 350, H//2 - 350, W//2 + 350, H//2 + 350], fill=(20, 28, 44, 255))

    pulse = 0.5 + 0.5 * math.sin(t * math.pi * 3.5)

    # ------------------ SHOT-SPECIFIC GEOMETRY ------------------
    if current_shot["id"] == 1:
        # Scene 1: Macro Push-In on Incoming SMS Alert
        yaw = -16.0 + shot_rel_t * 10.0
        pitch = 16.0 + shot_rel_t * 4.0
        zoom = 1.08 + shot_rel_t * 0.16

        draw_lit_3d_phone(im, cx=540, cy=930, pw=500, ph=1040, depth=42,
                          yaw=yaw, pitch=pitch, zoom=zoom,
                          screen_type="lockscreen", alert_pulse=pulse)

        d_im = ImageDraw.Draw(im)
        # Concentric glowing vibration waves (inspired by inspo frame sec_002.png)
        for w_i in range(3):
            wave_r = int(320 + w_i * 45 + pulse * 15)
            d_im.ellipse([540 - wave_r, 960 - wave_r, 540 + wave_r, 960 + wave_r],
                         outline=(255, 176, 32, max(20, 100 - w_i * 35)), width=2)

        draw_callout_hud(d_im, (420, 840), (180, 560), "SMS SPOOF DETECTED", C_RED)
        draw_callout_hud(d_im, (680, 1080), (890, 720), "MALICIOUS LINK INJECT", C_AMBER)

    elif current_shot["id"] == 2:
        # Scene 2: Pull-Back on Desk with Anatomical 3D Hand Gripping Phone
        yaw = 28.0 - shot_rel_t * 16.0
        pitch = 24.0 - shot_rel_t * 8.0
        zoom = 1.15 - shot_rel_t * 0.18

        draw_lit_3d_phone(im, cx=540, cy=890, pw=500, ph=1040, depth=42,
                          yaw=yaw, pitch=pitch, zoom=zoom,
                          screen_type="lockscreen")

        # Anatomical 3D hand holding phone
        draw_3d_hand_grip(im, 540, 890, shot_rel_t)

        d_im = ImageDraw.Draw(im)
        draw_callout_hud(d_im, (540, 1180), (200, 1260), "IN-DISPLAY FINGERPRINT", C_CYAN)
        draw_callout_hud(d_im, (740, 740), (880, 620), "TITANIUM CHASSIS RAIL", C_AMBER)

    elif current_shot["id"] == 3:
        # Scene 3: High Dutch Angle Tap -> Phishing Portal
        yaw = -24.0 + shot_rel_t * 14.0
        pitch = 44.0 + shot_rel_t * 8.0
        roll = -8.0
        zoom = 1.08 + shot_rel_t * 0.14

        draw_lit_3d_phone(im, cx=540, cy=880, pw=520, ph=1060, depth=42,
                          yaw=yaw, pitch=pitch, roll=roll, zoom=zoom,
                          screen_type="fake_bank")

        d_im = ImageDraw.Draw(im)
        # Touch ripple
        tap_pt = (540, 850)
        rip_r = int(30 + shot_rel_t * 80)
        d_im.ellipse([tap_pt[0] - rip_r, tap_pt[1] - rip_r, tap_pt[0] + rip_r, tap_pt[1] + rip_r],
                     outline=C_RED, width=3)

        draw_callout_hud(d_im, tap_pt, (190, 600), "1-TAP EXPLOIT TRIGGER", C_RED)
        draw_callout_hud(d_im, (660, 720), (880, 620), "FAKE LOGIN INTERFACE", C_AMBER)

    elif current_shot["id"] == 4:
        # Scene 4: True 3D Hardware Cutaway Teardown
        draw_3d_cutaway_teardown(im, shot_rel_t)

    elif current_shot["id"] == 5:
        # Scene 5: High-Angle Fast Orbit with BIG 100px+ COUNTER 11.2s
        yaw = -42.0 + shot_rel_t * 84.0
        pitch = 28.0
        zoom = 1.02

        draw_lit_3d_phone(im, cx=540, cy=1070, pw=480, ph=940, depth=40,
                          yaw=yaw, pitch=pitch, zoom=zoom,
                          screen_type="fake_bank")

        d_im = ImageDraw.Draw(im)
        # Upper HUD Counter Card (y: 190 to 410) - NEVER covers phone or clock!
        card_y = 195
        d_im.rounded_rectangle([140, card_y, 940, card_y + 215], radius=24,
                               fill=(14, 20, 32, 245), outline=C_RED, width=3)

        # Radial Gauge Arc sweeping
        arc_cx, arc_cy = 265, card_y + 108
        d_im.ellipse([arc_cx - 65, arc_cy - 65, arc_cx + 65, arc_cy + 65], outline=(40, 50, 70, 255), width=8)
        sweep_pct = min(1.0, shot_rel_t * 1.4)
        end_angle = int(sweep_pct * 260)
        d_im.arc([arc_cx - 65, arc_cy - 65, arc_cx + 65, arc_cy + 65], start=-90, end=-90 + end_angle, fill=C_RED, width=10)

        d_im.text((365, card_y + 26), "11.2s", font=font_hero_num, fill=C_RED)
        d_im.text((370, card_y + 144), "TIME TO COMPROMISE: 11.2s", font=font_hero_label, fill=C_AMBER)

        draw_callout_hud(d_im, (540, 1140), (870, 640), "CREDENTIAL HARVEST", C_AMBER)

    elif current_shot["id"] == 6:
        # Scene 6: Exfiltration - Phone & Laptop BOTH Large + 3D Flying Objects
        yaw6 = 18.0 + shot_rel_t * 12.0
        pitch6 = 18.0 - shot_rel_t * 4.0

        draw_lit_3d_phone(im, cx=280, cy=940, pw=440, ph=940, depth=38,
                          yaw=yaw6, pitch=pitch6, zoom=1.0, screen_type="fake_bank")

        d_im = ImageDraw.Draw(im)
        # Right: 3D Hacker Laptop
        lx, ly, lw, lh = 520, 560, 520, 390
        d_im.line([(lx - 20, ly + lh), (lx + lw + 20, ly + lh)], fill=C_RED, width=4)
        d_im.rounded_rectangle([lx, ly, lx + lw, ly + lh], radius=16,
                               fill=(8, 12, 20, 255), outline=C_RED, width=3)
        d_im.rounded_rectangle([lx + 6, ly + 6, lx + lw - 6, ly + lh - 6], radius=12,
                               fill=(10, 16, 24, 255), outline=(30, 40, 60, 255), width=1)
        d_im.text((lx + 24, ly + 22), "> EXFILTRATION TERMINAL", font=font_proof_stat, fill=C_RED)
        d_im.text((lx + 24, ly + 62), "INCOMING STREAM: ACTIVE", font=font_proof_stat, fill=C_CYAN)
        d_im.text((lx + 24, ly + 102), "STATUS: 100% RECEIVED", font=font_proof_stat, fill=C_EMERALD)
        d_im.text((lx + 24, ly + 142), f"PKTS: {int(shot_rel_t * 847) + 42} / 889", font=font_proof_stat, fill=C_AMBER)

        # 3 Flying 3D Objects with motion trail
        flight_items = [("cookie", 0.0), ("key", 0.35), ("chip", 0.68)]
        for obj_type, offset in flight_items:
            prog = (shot_rel_t + offset) % 1.0
            fly_x = int(300 + prog * 440)
            fly_y = int(660 + math.sin(prog * math.pi) * -190)

            # Glowing trail
            d_im.line([(fly_x - 30, fly_y + 15), (fly_x, fly_y)], fill=(255, 176, 32, 120), width=3)

            if obj_type == "cookie":
                d_im.ellipse([fly_x - 25, fly_y - 25, fly_x + 25, fly_y + 25], fill=(180, 120, 70, 255), outline=C_AMBER, width=2)
                for cx_i, cy_i in [(-8, -6), (6, -10), (0, 8), (-12, 6), (10, 6)]:
                    d_im.ellipse([fly_x + cx_i - 3, fly_y + cy_i - 3, fly_x + cx_i + 3, fly_y + cy_i + 3], fill=(60, 35, 20, 255))
            elif obj_type == "key":
                draw_vector_lock(d_im, fly_x, fly_y, size=38, fill=C_GOLD)
            else:
                d_im.rounded_rectangle([fly_x - 32, fly_y - 22, fly_x + 32, fly_y + 22], radius=6, fill=(24, 32, 48, 255), outline=C_CYAN, width=2)
                d_im.text((fly_x - 18, fly_y - 12), "2FA", font=font_callout_txt, fill=C_CYAN)

        draw_callout_hud(d_im, (280, 760), (160, 450), "SESSION EXFILTRATED", C_AMBER)
        draw_callout_hud(d_im, (lx + 260, ly + 190), (900, 440), "HACKER LAPTOP", C_RED)

    elif current_shot["id"] == 7:
        # Scene 7: Official Authority Proof Card (High-Contrast Document Card)
        draw_lit_3d_phone(im, cx=850, cy=960, pw=440, ph=920, depth=36,
                          yaw=-28.0, pitch=22.0, zoom=0.85, screen_type="fake_bank")
        draw_official_authority_card(im, shot_rel_t)

    elif current_shot["id"] == 8:
        # Scene 8: Defense Clamping - Titanium clamp closing down & instant green transformation
        yaw = -18.0 + shot_rel_t * 14.0
        pitch = 18.0
        zoom = 1.12

        draw_lit_3d_phone(im, cx=540, cy=860, pw=520, ph=1060, depth=42,
                          yaw=yaw, pitch=pitch, zoom=zoom,
                          screen_type="clamping", clamp_progress=shot_rel_t)

        d_im = ImageDraw.Draw(im)
        draw_callout_hud(d_im, (380, 680), (180, 480), "TITANIUM CLAMP CLOSED", C_EMERALD)
        draw_callout_hud(d_im, (680, 740), (880, 520), "MALICIOUS LINK BLOCKED", C_CYAN)

    elif current_shot["id"] == 9:
        # Scene 9: Result 0% Vulnerability / Hardened Safe Enclave
        yaw = 34.0 - shot_rel_t * 26.0
        pitch = 26.0
        zoom = 1.02

        draw_lit_3d_phone(im, cx=540, cy=1070, pw=480, ph=940, depth=40,
                          yaw=yaw, pitch=pitch, zoom=zoom, screen_type="shield_safe")

        d_im = ImageDraw.Draw(im)
        # Spherical Energy Shield
        shield_r = int(320 + pulse * 20)
        d_im.ellipse([540 - shield_r, 1070 - shield_r, 540 + shield_r, 1070 + shield_r], outline=C_CYAN, width=3)

        # Upper HUD Counter Card (y: 195 to 410)
        card_y = 195
        d_im.rounded_rectangle([150, card_y, 930, card_y + 215], radius=24,
                               fill=(12, 28, 24, 245), outline=C_EMERALD, width=3)
        d_im.text((210, card_y + 28), "0%", font=font_hero_num, fill=C_EMERALD)
        d_im.text((400, card_y + 55), "VULNERABILITY", font=font_hero_unit, fill=C_GOLD)
        d_im.text((215, card_y + 144), "PHONE VAULT IMPERVIOUS TO PHISHING", font=font_hero_label, fill=C_WHITE)

    else:
        # Scene 10: Grand CTA "Stay bulletproof" with @mwd1504
        yaw = 22.0 - shot_rel_t * 18.0
        pitch = 22.0
        zoom = 1.02

        draw_lit_3d_phone(im, cx=540, cy=1070, pw=460, ph=920, depth=38,
                          yaw=yaw, pitch=pitch, zoom=zoom, screen_type="shield_safe")

        d_im = ImageDraw.Draw(im)
        cta_y = 195
        d_im.rounded_rectangle([140, cta_y, 940, cta_y + 275], radius=28,
                               fill=(14, 20, 34, 245), outline=C_GOLD, width=3)

        btn_y = cta_y + 35
        d_im.rounded_rectangle([180, btn_y, 900, btn_y + 90], radius=18,
                               fill=(16, 185, 129, 235), outline=C_GOLD, width=2)
        btn_bbox = font_cta_btn.getbbox("STAY BULLETPROOF")
        btn_w = btn_bbox[2] - btn_bbox[0]
        d_im.text(((W - btn_w) // 2, btn_y + 20), "STAY BULLETPROOF", font=font_cta_btn, fill=(10, 14, 22, 255))

        handle_str = "@mwd1504"
        h_bbox = font_cta_sub.getbbox(handle_str)
        h_w = h_bbox[2] - h_bbox[0]
        h_x = (W - h_w) // 2
        d_im.text((h_x, cta_y + 148), handle_str, font=font_cta_sub, fill=C_CYAN)

        # Verified Checkmark Badge
        d_im.ellipse([h_x + h_w + 14, cta_y + 152, h_x + h_w + 36, cta_y + 174], fill=C_CYAN)
        d_im.text((h_x + h_w + 18, cta_y + 150), "✓", font=font_hud_tab, fill=(10, 14, 22, 255))

        d_im.text((270, cta_y + 215), "Follow for Mobile Cyber Defense & High-Security Tech",
                  font=font_proof_body, fill=C_MUTED)

    # ------------------ TOP HUD & KINETIC CAPTIONS ------------------
    draw_hud_telemetry_pill(d, active_idx, current_shot["tag"])
    draw_kinetic_caption_pill(d, t, timings_data)

    # Bottom Progress Bar
    d.rounded_rectangle([80, 1780, 1000, 1788], radius=4, fill=(30, 41, 59, 160))
    bar_w = int(920 * progress)
    if bar_w > 0:
        bar_col = C_GOLD if active_idx == 9 else C_CYAN
        d.rounded_rectangle([80, 1780, 80 + bar_w, 1788], radius=4, fill=bar_col)

    return im.convert("RGBA")

# ----------------- KEYFRAME PREVIEW GENERATOR -----------------

def render_keyframe_previews():
    """Generates preview keyframes for all 10 shots to .pipeline/keyframes_preview/."""
    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    timings_data = load_chunks()
    ensure_script_json()

    audio_path = get_effective_audio()
    total_duration = get_audio_duration(audio_path)
    total_frames = int(math.ceil(total_duration * FPS))

    print(f"📸 Generating 10 High-Fidelity Keyframe Previews in {PREVIEW_DIR}...")
    for sc in SHOT_TIMELINE:
        mid_t = sc["start"] + sc["dur"] * 0.5
        f_idx = min(total_frames - 1, int(mid_t * FPS))
        frame_im = render_v2_frame(f_idx, total_frames, timings_data)
        out_shot = PREVIEW_DIR / f"shot_{sc['id']:02d}.png"
        frame_im.save(out_shot)
        print(f"  ✓ Saved {out_shot.name}")

# ----------------- FULL VIDEO ENCODER -----------------

def render_final_video():
    """Renders final MP4 with tuned CRF 19 encoding and EBU R128 loudness normalization."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / "final.mp4"
    named_output = OUTPUT_DIR / "How_Hackers_Phish_Your_Phone.mp4"

    timings_data = load_chunks()
    ensure_script_json()

    audio_path = get_effective_audio()
    total_duration = get_audio_duration(audio_path)
    total_frames = int(math.ceil(total_duration * FPS))

    print(f"🎵 Audio Track: {audio_path} ({total_duration:.3f}s)")
    print(f"🚀 Rendering {total_frames} frames ({len(SHOT_TIMELINE)} shots, 1080x1920 @ {FPS} FPS)...")

    # ffmpeg pipe with CRF 19 + preset medium + EBU R128 loudnorm
    cmd_ffmpeg = [
        "ffmpeg", "-y",
        "-f", "rawvideo",
        "-pix_fmt", "rgba",
        "-s", f"{W}x{H}",
        "-r", str(FPS),
        "-i", "-",
        "-i", audio_path,
        "-c:v", "libx264",
        "-crf", "19",
        "-preset", "medium",
        "-pix_fmt", "yuv420p",
        "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
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

    # Also copy to named output for backwards compatibility
    shutil.copy(output_path, named_output)
    print(f"✅ Master render completed: {output_path} ({os.path.getsize(output_path)} bytes)")

if __name__ == "__main__":
    if "--preview" in sys.argv or "--keyframes" in sys.argv:
        render_keyframe_previews()
    else:
        # Default: generate keyframe previews first, then full render if requested or standalone
        if len(sys.argv) > 1 and sys.argv[1].endswith(".mp4"):
            # Target output specified
            render_final_video()
        else:
            render_keyframe_previews()
            render_final_video()
