#!/usr/bin/env python3
"""
render_engine.py - Advanced 3D Isometric Motion Graphics Engine for Mobile Shorts/Reels
Features:
1. 11 dynamic scenes cutting every 2-3 seconds across 29 seconds.
2. Continuous 3D camera orbits (yaw), elevation tilts (pitch), push-ins, and pull-backs.
3. Lit 3D objects with depth shading, warm amber/gold accents, glassmorphism, soft shadows.
4. Single continuous metaphor: High-Velocity Website Conversion Pipeline.
5. Bottom-center big captions (3-5 words at a time) with active spoken word highlighted in gold (no box).
6. Massive visual numbers: 68% bounce rate with animated danger arc, 3.8s hot load lag, animated 3.8s -> 0.8s counter.
7. Dedicated Proof Beat: Google PageSpeed 99/100 score + Think With Google 53% stat citation.
8. Shock visual hook in first 2 seconds ("YOUR WEBSITE IS BLEEDING MONEY") & clear CTA ("Book a call" / @mwd1504).
9. Dynamic top HUD tabs updating with every scene.
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
if ROOT_DIR.name == "video-engine":
    ROOT_DIR = ROOT_DIR.parent

PIPELINE_DIR = ROOT_DIR / ".pipeline"
OUTPUT_DIR = PIPELINE_DIR / "output"
SCRIPT_FILE = PIPELINE_DIR / "script.json"
TIMINGS_FILE = PIPELINE_DIR / "word_timings.json"
AUDIO_FILE = ROOT_DIR / "video-engine" / "public" / "audio.mp3"
if not AUDIO_FILE.exists():
    AUDIO_FILE = PIPELINE_DIR / "audio.mp3"

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
font_hero_num = ImageFont.truetype(FONT_SANS_BOLD, 115)
font_hero_unit = ImageFont.truetype(FONT_SANS_BOLD, 52)
font_hero_label = ImageFont.truetype(FONT_MONO_BOLD, 26)
font_callout_txt = ImageFont.truetype(FONT_MONO_BOLD, 22)
font_caption = ImageFont.truetype(FONT_SANS_BOLD, 46)
font_caption_sm = ImageFont.truetype(FONT_SANS_BOLD, 38)
font_proof_title = ImageFont.truetype(FONT_SANS_BOLD, 28)
font_proof_body = ImageFont.truetype(FONT_SANS_BOLD, 22)
font_proof_stat = ImageFont.truetype(FONT_MONO_BOLD, 19)
font_cta_btn = ImageFont.truetype(FONT_SANS_BOLD, 48)
font_cta_sub = ImageFont.truetype(FONT_MONO_BOLD, 28)

W, H = 1080, 1920
FPS = 30

# Colors
C_BG = (10, 12, 18, 255)
C_CYAN = (0, 242, 254, 255)
C_AMBER = (255, 176, 32, 255)
C_GOLD = (255, 215, 0, 255)
C_RED = (255, 45, 85, 255)
C_EMERALD = (16, 185, 129, 255)
C_WHITE = (255, 255, 255, 255)
C_MUTED = (148, 163, 184, 255)

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
        return 29.088

def project_3d(x, y, z, cx=540, cy=960, yaw=45.0, pitch=35.0, zoom=1.0):
    """True 3D projection with dynamic camera yaw, pitch, and zoom."""
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

def draw_soft_shadow(d, bx, by, bw, bd, cx=540, cy=960, yaw=45.0, pitch=35.0, zoom=1.0):
    """Draws multi-tier soft contact shadow on the floor (Z = 0)."""
    for expand, alpha in [(30, 40), (16, 70), (4, 110)]:
        p0 = project_3d(bx - expand, by - expand, 0, cx, cy, yaw, pitch, zoom)
        p1 = project_3d(bx + bw + expand, by - expand, 0, cx, cy, yaw, pitch, zoom)
        p2 = project_3d(bx + bw + expand, by + bd + expand, 0, cx, cy, yaw, pitch, zoom)
        p3 = project_3d(bx - expand, by + bd + expand, 0, cx, cy, yaw, pitch, zoom)
        d.polygon([p0, p1, p2, p3], fill=(4, 6, 12, alpha))

def draw_3d_box(d, bx, by, bz, bw, bd, bh,
                col_top, col_r, col_l, border=None,
                cx=540, cy=960, yaw=45.0, pitch=35.0, zoom=1.0,
                width=2, shadow=False):
    """Draws a lit 3D cuboid with shaded top, right, and left faces."""
    if shadow:
        draw_soft_shadow(d, bx, by, bw, bd, cx, cy, yaw, pitch, zoom)

    p000 = project_3d(bx, by, bz, cx, cy, yaw, pitch, zoom)
    p100 = project_3d(bx + bw, by, bz, cx, cy, yaw, pitch, zoom)
    p110 = project_3d(bx + bw, by + bd, bz, cx, cy, yaw, pitch, zoom)
    p010 = project_3d(bx, by + bd, bz, cx, cy, yaw, pitch, zoom)

    p001 = project_3d(bx, by, bz + bh, cx, cy, yaw, pitch, zoom)
    p101 = project_3d(bx + bw, by, bz + bh, cx, cy, yaw, pitch, zoom)
    p111 = project_3d(bx + bw, by + bd, bz + bh, cx, cy, yaw, pitch, zoom)
    p011 = project_3d(bx, by + bd, bz + bh, cx, cy, yaw, pitch, zoom)

    # Left face (+Y normal)
    d.polygon([p010, p110, p111, p011], fill=col_l, outline=border, width=width)
    # Right face (+X normal)
    d.polygon([p100, p110, p111, p101], fill=col_r, outline=border, width=width)
    # Top face (+Z normal)
    d.polygon([p001, p101, p111, p011], fill=col_top, outline=border, width=width)

    # Optional glass specular edge
    if border and width > 1:
        d.line([p001, p101], fill=(255, 255, 255, 140), width=1)

def draw_iso_callout(d, x_3d, y_3d, z_3d, badge_x, badge_y, text, accent_color,
                     cx=540, cy=960, yaw=45.0, pitch=35.0, zoom=1.0):
    """Draws an angled 3D HUD leader line from 3D space to a glass HUD card."""
    start_pt = project_3d(x_3d, y_3d, z_3d, cx, cy, yaw, pitch, zoom)
    mid_pt = (badge_x - 24, badge_y + 22)
    end_pt = (badge_x, badge_y + 22)

    # 3D anchor point with pulse ring
    d.ellipse([start_pt[0] - 5, start_pt[1] - 5, start_pt[0] + 5, start_pt[1] + 5], fill=accent_color)
    d.ellipse([start_pt[0] - 9, start_pt[1] - 9, start_pt[0] + 9, start_pt[1] + 9], outline=accent_color, width=1)
    d.line([start_pt, mid_pt, end_pt], fill=accent_color, width=2)

    bbox = font_callout_txt.getbbox(text)
    badge_w = max(260, (bbox[2] - bbox[0]) + 36)
    badge_h = 44
    d.rounded_rectangle([badge_x, badge_y, badge_x + badge_w, badge_y + badge_h], radius=10,
                        fill=(15, 20, 32, 230), outline=accent_color, width=2)
    d.text((badge_x + 16, badge_y + 10), text, font=font_callout_txt, fill=(255, 255, 255, 255))

def draw_hud_tabs(d, active_idx, scene_tag):
    """Top dynamic telemetry HUD pill matching inspiration video."""
    pill_w, pill_h = 940, 64
    x1, y1 = (W - pill_w) // 2, 85
    x2, y2 = x1 + pill_w, y1 + pill_h

    # Translucent glass pill
    d.rounded_rectangle([x1, y1, x2, y2], radius=32, fill=(12, 17, 28, 220), outline=(255, 255, 255, 30), width=1)

    # Live Status Dot & Scene Tag
    accent = C_AMBER if active_idx in [1, 3, 5, 7] else (C_RED if active_idx in [0, 2] else C_CYAN)
    d.ellipse([x1 + 24, y1 + 25, x1 + 38, y1 + 39], fill=accent)
    d.text((x1 + 50, y1 + 20), f"• PIPELINE // {scene_tag}", font=font_hud_label, fill=(241, 245, 249, 240))

    # 11 Micro Step Indicators
    total_steps = 11
    step_r = 13
    step_gap = 8
    start_x = x2 - total_steps * (step_r * 2 + step_gap) - 15

    for i in range(total_steps):
        sx = start_x + i * (step_r * 2 + step_gap) + step_r
        sy = y1 + pill_h // 2
        is_cur = (i == active_idx)
        if is_cur:
            d.ellipse([sx - step_r, sy - step_r, sx + step_r, sy + step_r], fill=C_AMBER)
            d.text((sx - 5, sy - 9), str(i + 1), font=font_hud_tab, fill=(10, 14, 22, 255))
        else:
            d.ellipse([sx - step_r, sy - step_r, sx + step_r, sy + step_r], fill=(22, 30, 46, 200), outline=(71, 85, 105, 120), width=1)
            d.text((sx - 5, sy - 9), str(i + 1), font=font_hud_tab, fill=(148, 163, 184, 180))

def draw_bottom_captions(d, t, timings_data):
    """
    Kinetic lower-third captions matching the inspiration video:
    - Frosted dark pill hugging 2-4 words
    - Spoken word highlighted with thick gold underline
    - Lower third safe zone (y ≈ 1620)
    """
    if not timings_data:
        return

    # Find active chunk
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
            d.text((cur_x, text_y), w, font=font_caption, fill=C_WHITE)
            d.line([(cur_x, text_y + 50), (cur_x + w_w, text_y + 50)], fill=C_GOLD, width=4)
        else:
            d.text((cur_x, text_y), w, font=font_caption, fill=(160, 174, 192, 230))
        cur_x += w_w + space_w

def render_frame_image(frame_idx, total_frames, script_data, total_duration, timed_scenes, timings_data):
    """Renders a single 1080x1920 video frame with lit 3D isometric graphics."""
    t = frame_idx / float(FPS)
    progress = min(1.0, max(0.0, t / max(1.0, total_duration)))

    # Determine active scene
    active_idx = 0
    for idx, sc in enumerate(timed_scenes):
        if sc["start"] <= t <= sc["end"]:
            active_idx = idx
            break
        elif t > sc["end"]:
            active_idx = idx

    current_scene = timed_scenes[active_idx]
    v_type = current_scene.get("visual_type", "shock_leak_hook")
    scene_dur = max(0.1, current_scene["end"] - current_scene["start"])
    scene_rel_t = max(0.0, min(1.0, (t - current_scene["start"]) / scene_dur))

    # Base image setup
    im = Image.new('RGBA', (W, H), C_BG)
    d = ImageDraw.Draw(im)

    # Camera kinematics per scene: continuous slow orbit & push/pull
    # Scene-specific camera orbits
    if v_type == "shock_leak_hook":
        # Push-in with yaw orbit 38° -> 48°
        cam_yaw = 38.0 + scene_rel_t * 10.0
        cam_pitch = 34.0 + scene_rel_t * 4.0
        cam_zoom = 1.05 + scene_rel_t * 0.14
        cam_cy = 820
    elif v_type == "hero_bounce_gauge":
        # Dutch angle push-in onto the rupture
        cam_yaw = 48.0 - scene_rel_t * 12.0
        cam_pitch = 38.0 + scene_rel_t * 5.0
        cam_zoom = 1.15 + scene_rel_t * 0.16
        cam_cy = 800
    elif v_type == "pipeline_junction_loss":
        # Orbit shift reveal
        cam_yaw = 36.0 + scene_rel_t * 15.0
        cam_pitch = 45.0 - scene_rel_t * 8.0
        cam_zoom = 1.25 - scene_rel_t * 0.15
        cam_cy = 830
    elif v_type == "hero_load_lag":
        # Push-in on heat valve
        cam_yaw = 50.0 - scene_rel_t * 8.0
        cam_pitch = 32.0 + scene_rel_t * 4.0
        cam_zoom = 1.10 + scene_rel_t * 0.18
        cam_cy = 810
    elif v_type == "exploded_stack_laser":
        # Upward tilt & slow orbit around exploding vertical slabs
        cam_yaw = 42.0 + scene_rel_t * 16.0
        cam_pitch = 28.0 + scene_rel_t * 10.0
        cam_zoom = 1.08 + scene_rel_t * 0.08
        cam_cy = 840
    elif v_type == "clarity_filter":
        # Lateral pan & rotation
        cam_yaw = 58.0 - scene_rel_t * 14.0
        cam_pitch = 36.0
        cam_zoom = 1.16 + scene_rel_t * 0.10
        cam_cy = 820
    elif v_type == "pagespeed_proof_beat":
        # 3D tilt-down onto the proof card
        cam_yaw = 44.0 + math.sin(scene_rel_t * math.pi) * 6.0
        cam_pitch = 30.0 + scene_rel_t * 10.0
        cam_zoom = 1.06 + scene_rel_t * 0.12
        cam_cy = 820
    elif v_type == "gold_value_monolith":
        # Push-in on the illuminated gold slab
        cam_yaw = 40.0 + scene_rel_t * 8.0
        cam_pitch = 36.0
        cam_zoom = 1.12 + scene_rel_t * 0.15
        cam_cy = 810
    elif v_type == "direct_booking_conduit":
        # Split sweep
        cam_yaw = 48.0 - scene_rel_t * 12.0
        cam_pitch = 35.0
        cam_zoom = 1.14 + scene_rel_t * 0.10
        cam_cy = 820
    elif v_type == "hero_speed_countdown":
        # Turbo push-in on big counter
        cam_yaw = 36.0 + scene_rel_t * 10.0
        cam_pitch = 34.0 + scene_rel_t * 4.0
        cam_zoom = 1.15 + scene_rel_t * 0.18
        cam_cy = 800
    else: # cta_reveal_slab
        # Grand pull-back wide reveal
        cam_yaw = 46.0 - scene_rel_t * 14.0
        cam_pitch = 36.0 + scene_rel_t * 6.0
        cam_zoom = 1.25 - scene_rel_t * 0.28
        cam_cy = 830

    # Perspective Grid with warm ambient horizon lighting
    grid_col = (0, 242, 254, 25)
    for gx in range(-600, 700, 120):
        p_start = project_3d(gx, -600, 0, cx=540, cy=cam_cy, yaw=cam_yaw, pitch=cam_pitch, zoom=cam_zoom)
        p_end = project_3d(gx, 600, 0, cx=540, cy=cam_cy, yaw=cam_yaw, pitch=cam_pitch, zoom=cam_zoom)
        d.line([p_start, p_end], fill=grid_col, width=1)
    for gy in range(-600, 700, 120):
        p_start = project_3d(-600, gy, 0, cx=540, cy=cam_cy, yaw=cam_yaw, pitch=cam_pitch, zoom=cam_zoom)
        p_end = project_3d(600, gy, 0, cx=540, cy=cam_cy, yaw=cam_yaw, pitch=cam_pitch, zoom=cam_zoom)
        d.line([p_start, p_end], fill=grid_col, width=1)

    # Subtle floating physics
    float_z = math.sin(t * 3.4) * 12.0
    pulse = (math.sin(t * 8.0) + 1.0) * 0.5

    # ------------------ SCENE-SPECIFIC 3D GEOMETRY ------------------

    if v_type == "shock_leak_hook":
        # Scene 1: Fractured Pipeline with Pulsing Red Emergency Alarms
        # Base Foundation Slab (Obsidian with cyan rim)
        draw_3d_box(d, -220, -220, 10, 440, 440, 30,
                    col_top=(22, 28, 44, 255), col_r=(14, 18, 28, 255), col_l=(10, 14, 22, 255),
                    border=(0, 242, 254, 140), cx=540, cy=cam_cy, yaw=cam_yaw, pitch=cam_pitch, zoom=cam_zoom, shadow=True)

        # Main Pipeline Chamber (Z = 40 to 180)
        draw_3d_box(d, -140, -140, 40, 280, 280, 140,
                    col_top=(32, 42, 64, 255), col_r=(20, 26, 40, 255), col_l=(14, 18, 30, 255),
                    border=(0, 242, 254, 200), cx=540, cy=cam_cy, yaw=cam_yaw, pitch=cam_pitch, zoom=cam_zoom)

        # Red Rupture Fissure (Glowing hot crimson on front edge)
        fissure_color = (255, 30, 70, int(200 + pulse * 55))
        p_f1 = project_3d(140, -80, 120, cx=540, cy=cam_cy, yaw=cam_yaw, pitch=cam_pitch, zoom=cam_zoom)
        p_f2 = project_3d(140, 0, 70, cx=540, cy=cam_cy, yaw=cam_yaw, pitch=cam_pitch, zoom=cam_zoom)
        p_f3 = project_3d(140, 60, 130, cx=540, cy=cam_cy, yaw=cam_yaw, pitch=cam_pitch, zoom=cam_zoom)
        d.line([p_f1, p_f2, p_f3], fill=fissure_color, width=6)

        # Escaping particle drops
        for p_i, p_off in enumerate([(20, 30), (50, 70), (80, 120)]):
            px = 140 + p_off[0] + (scene_rel_t * 60)
            py = p_off[1]
            pz = max(0, 100 - (scene_rel_t * 80) - (p_i * 15))
            pt = project_3d(px, py, pz, cx=540, cy=cam_cy, yaw=cam_yaw, pitch=cam_pitch, zoom=cam_zoom)
            d.ellipse([pt[0]-4, pt[1]-4, pt[0]+4, pt[1]+4], fill=(255, 45, 85, 240))

        # Floating Shock Alert Card
        draw_iso_callout(d, 140, 0, 140, 120, 460, "ALERT: PIPELINE RUPTURED", C_RED,
                         cx=540, cy=cam_cy, yaw=cam_yaw, pitch=cam_pitch, zoom=cam_zoom)
        draw_iso_callout(d, -140, 0, 180, 580, 940, "REVENUE LOSS DETECTED", C_AMBER,
                         cx=540, cy=cam_cy, yaw=cam_yaw, pitch=cam_pitch, zoom=cam_zoom)

        # Big Shock Hook Header at upper screen
        d.rounded_rectangle([100, 360, 980, 430], radius=12, fill=(255, 45, 85, 40), outline=C_RED, width=2)
        d.text((120, 378), "CRITICAL ALERT: CLIENT LEAK IN PROGRESS", font=font_callout_txt, fill=C_RED)

    elif v_type == "hero_bounce_gauge":
        # Scene 2: HERO 68% BOUNCE RATE GAUGE
        # 3D Base Platform
        draw_3d_box(d, -240, -240, 10, 480, 480, 24,
                    col_top=(20, 26, 40, 255), col_r=(12, 16, 26, 255), col_l=(8, 12, 20, 255),
                    border=(71, 85, 105, 150), cx=540, cy=cam_cy, yaw=cam_yaw, pitch=cam_pitch, zoom=cam_zoom, shadow=True)

        # 3D Lit Glass Cylindrical Tank (Obsidian base + Glowing Crimson Core)
        draw_3d_box(d, -160, -160, 34, 320, 320, 120,
                    col_top=(45, 12, 24, 240), col_r=(32, 8, 18, 255), col_l=(22, 6, 14, 255),
                    border=C_RED, cx=540, cy=cam_cy, yaw=cam_yaw, pitch=cam_pitch, zoom=cam_zoom)

        # BIG VISUAL HERO NUMBER: Animated 68%
        ease = 0.5 - 0.5 * math.cos(scene_rel_t * math.pi)
        anim_val = int(ease * 68)
        num_str = f"{anim_val}%"

        # Center Hero HUD Badge for 68%
        badge_y = 500
        d.rounded_rectangle([180, badge_y, 900, badge_y + 240], radius=24,
                            fill=(14, 18, 28, 240), outline=C_RED, width=3)

        # Pulsing Radial Arc
        arc_cx, arc_cy = 340, badge_y + 120
        d.ellipse([arc_cx - 75, arc_cy - 75, arc_cx + 75, arc_cy + 75], outline=(40, 50, 70, 255), width=8)
        # Danger arc
        angle_end = int(240 * (anim_val / 100.0))
        d.arc([arc_cx - 75, arc_cy - 75, arc_cx + 75, arc_cy + 75], start=-90, end=-90 + angle_end, fill=C_RED, width=10)

        # Large Digits
        d.text((460, badge_y + 40), num_str, font=font_hero_num, fill=C_RED)
        d.text((465, badge_y + 155), "BOUNCE RATE DETECTED", font=font_hero_label, fill=C_AMBER)

        # 3D HUD Callout
        draw_iso_callout(d, 160, 0, 154, 560, 960, "LOST PIPELINE: $45K", C_AMBER,
                         cx=540, cy=cam_cy, yaw=cam_yaw, pitch=cam_pitch, zoom=cam_zoom)

    elif v_type == "pipeline_junction_loss":
        # Scene 3: Pipeline Junction with Fluid Leaking into Void
        # Multi-tier Pipeline Junction
        draw_3d_box(d, -260, -180, 20, 200, 360, 70,
                    col_top=(26, 36, 54, 255), col_r=(16, 24, 38, 255), col_l=(10, 16, 28, 255),
                    border=C_CYAN, cx=540, cy=cam_cy, yaw=cam_yaw, pitch=cam_pitch, zoom=cam_zoom, shadow=True)

        # Broken Branch Conduit (Crimson with leaking gap)
        draw_3d_box(d, 40, -180, 20, 220, 160, 60,
                    col_top=(48, 14, 26, 255), col_r=(34, 10, 20, 255), col_l=(24, 6, 14, 255),
                    border=C_RED, cx=540, cy=cam_cy, yaw=cam_yaw, pitch=cam_pitch, zoom=cam_zoom)

        # Gap Laser Sparks
        for s_i in range(5):
            sp_x = 0 + (s_i * 8)
            sp_z = 50 + math.sin(t * 12 + s_i) * 20
            p_sp = project_3d(sp_x, -100, sp_z, cx=540, cy=cam_cy, yaw=cam_yaw, pitch=cam_pitch, zoom=cam_zoom)
            d.ellipse([p_sp[0]-3, p_sp[1]-3, p_sp[0]+3, p_sp[1]+3], fill=C_AMBER)

        draw_iso_callout(d, -160, 0, 90, 100, 460, "DESKTOP FLOW: 32%", C_CYAN,
                         cx=540, cy=cam_cy, yaw=cam_yaw, pitch=cam_pitch, zoom=cam_zoom)
        draw_iso_callout(d, 150, -100, 80, 560, 960, "MOBILE BOUNCE: 68%", C_RED,
                         cx=540, cy=cam_cy, yaw=cam_yaw, pitch=cam_pitch, zoom=cam_zoom)

    elif v_type == "hero_load_lag":
        # Scene 4: HERO 3.8s LOAD LAG (Choked Hot Intake Valve)
        # Base Choked Intake Valve
        draw_3d_box(d, -220, -220, 10, 440, 440, 40,
                    col_top=(38, 20, 24, 255), col_r=(26, 12, 16, 255), col_l=(18, 8, 12, 255),
                    border=C_AMBER, cx=540, cy=cam_cy, yaw=cam_yaw, pitch=cam_pitch, zoom=cam_zoom, shadow=True)

        # Central Valve Cylinder (Hot Crimson / Amber)
        draw_3d_box(d, -130, -130, 50, 260, 260, 120,
                    col_top=(60, 16, 24, 255), col_r=(42, 10, 18, 255), col_l=(30, 8, 14, 255),
                    border=C_RED, cx=540, cy=cam_cy, yaw=cam_yaw, pitch=cam_pitch, zoom=cam_zoom)

        # Thermal Haze Rings (Pulsing Amber 3D Ring)
        ring_r = 170 + pulse * 25
        ring_pts = []
        for deg in range(0, 360, 15):
            rad = math.radians(deg)
            ring_pts.append(project_3d(math.cos(rad) * ring_r, math.sin(rad) * ring_r, 110,
                                       cx=540, cy=cam_cy, yaw=cam_yaw, pitch=cam_pitch, zoom=cam_zoom))
        d.polygon(ring_pts, outline=C_AMBER, width=2)

        # BIG VISUAL HERO NUMBER: 3.8s
        ease = 0.5 - 0.5 * math.cos(scene_rel_t * math.pi)
        cur_sec = 1.0 + ease * 2.8
        badge_y = 500
        d.rounded_rectangle([180, badge_y, 900, badge_y + 240], radius=24,
                            fill=(18, 14, 22, 240), outline=C_RED, width=3)

        d.text((240, badge_y + 40), f"{cur_sec:.1f}s", font=font_hero_num, fill=C_RED)
        d.text((560, badge_y + 70), "LOAD LAG", font=font_hero_unit, fill=C_AMBER)
        d.text((245, badge_y + 155), "DANGER THRESHOLD EXCEEDED (> 2.0s)", font=font_hero_label, fill=C_WHITE)

        draw_iso_callout(d, -130, 0, 170, 100, 940, "STEP 01: KILL LOAD LAG", C_CYAN,
                         cx=540, cy=cam_cy, yaw=cam_yaw, pitch=cam_pitch, zoom=cam_zoom)

    elif v_type == "exploded_stack_laser":
        # Scene 5: Exploded 3D Architectural Slabs with Laser Purge Grid
        # Corner laser guide pillars
        for corner_x, corner_y in [(-200, -200), (200, -200), (200, 200), (-200, 200)]:
            p_b = project_3d(corner_x, corner_y, 10, cx=540, cy=cam_cy, yaw=cam_yaw, pitch=cam_pitch, zoom=cam_zoom)
            p_t = project_3d(corner_x, corner_y, 380, cx=540, cy=cam_cy, yaw=cam_yaw, pitch=cam_pitch, zoom=cam_zoom)
            d.line([p_b, p_t], fill=(0, 242, 254, 120), width=2)

        # Tier 1 (Bottom, Z = 20): Mobile Hardware / OS Layer
        draw_3d_box(d, -190, -190, 20, 380, 380, 32,
                    col_top=(20, 28, 42, 255), col_r=(12, 18, 28, 255), col_l=(8, 12, 20, 255),
                    border=(71, 85, 105, 255), cx=540, cy=cam_cy, yaw=cam_yaw, pitch=cam_pitch, zoom=cam_zoom, shadow=True)

        # Tier 2 (Middle, Z = 150): Bloated JS Scripts (Crimson/Amber undergoing laser slice)
        burn_alpha = int(255 * (1.0 - scene_rel_t * 0.6))
        draw_3d_box(d, -190, -190, 150 + float_z * 0.5, 380, 380, 38,
                    col_top=(55, 12, 26, burn_alpha), col_r=(38, 8, 18, burn_alpha), col_l=(26, 6, 12, burn_alpha),
                    border=C_RED, cx=540, cy=cam_cy, yaw=cam_yaw, pitch=cam_pitch, zoom=cam_zoom)

        # Cyan Laser Slicing Grid across Tier 2
        for lx in range(-180, 190, 60):
            p1 = project_3d(lx, -190, 169 + float_z * 0.5, cx=540, cy=cam_cy, yaw=cam_yaw, pitch=cam_pitch, zoom=cam_zoom)
            p2 = project_3d(lx, 190, 169 + float_z * 0.5, cx=540, cy=cam_cy, yaw=cam_yaw, pitch=cam_pitch, zoom=cam_zoom)
            d.line([p1, p2], fill=C_CYAN, width=2)

        # Tier 3 (Top, Z = 290): Glass Viewport Layer (Clear Cyan)
        draw_3d_box(d, -190, -190, 290 + float_z * 1.2, 380, 380, 28,
                    col_top=(16, 36, 56, 230), col_r=(10, 22, 38, 255), col_l=(8, 16, 26, 255),
                    border=C_CYAN, cx=540, cy=cam_cy, yaw=cam_yaw, pitch=cam_pitch, zoom=cam_zoom)

        draw_iso_callout(d, -190, 0, 290 + float_z * 1.2, 90, 460, "FROZEN DOM: RESOLVED", C_CYAN,
                         cx=540, cy=cam_cy, yaw=cam_yaw, pitch=cam_pitch, zoom=cam_zoom)
        draw_iso_callout(d, 190, 0, 150 + float_z * 0.5, 560, 960, "4.8MB UNUSED JS: PURGED", C_AMBER,
                         cx=540, cy=cam_cy, yaw=cam_yaw, pitch=cam_pitch, zoom=cam_zoom)

    elif v_type == "clarity_filter":
        # Scene 6: Clarity Filter Cylinder (Jargon Filtered -> Instant Value)
        draw_3d_box(d, -220, -220, 20, 440, 440, 36,
                    col_top=(20, 28, 42, 255), col_r=(14, 18, 28, 255), col_l=(10, 14, 20, 255),
                    border=C_CYAN, cx=540, cy=cam_cy, yaw=cam_yaw, pitch=cam_pitch, zoom=cam_zoom, shadow=True)

        # 3D Clarity Dial Needle
        draw_3d_box(d, -140, -140, 56, 280, 280, 40,
                    col_top=(26, 36, 56, 255), col_r=(16, 24, 38, 255), col_l=(12, 18, 28, 255),
                    border=C_AMBER, cx=540, cy=cam_cy, yaw=cam_yaw, pitch=cam_pitch, zoom=cam_zoom)

        # Needle pivoting from Red (Jargon) to Cyan (Clarity)
        angle_deg = 240 - (scene_rel_t * 180)
        rad = math.radians(angle_deg)
        nx = math.cos(rad) * 120
        ny = math.sin(rad) * 120
        p_hub = project_3d(0, 0, 98, cx=540, cy=cam_cy, yaw=cam_yaw, pitch=cam_pitch, zoom=cam_zoom)
        p_tip = project_3d(nx, ny, 98, cx=540, cy=cam_cy, yaw=cam_yaw, pitch=cam_pitch, zoom=cam_zoom)
        d.line([p_hub, p_tip], fill=C_AMBER, width=6)

        draw_iso_callout(d, -140, 0, 96, 90, 480, "STEP 02: 5-SEC CLARITY", C_AMBER,
                         cx=540, cy=cam_cy, yaw=cam_yaw, pitch=cam_pitch, zoom=cam_zoom)
        draw_iso_callout(d, 140, 0, 96, 560, 960, "PURGE CORPORATE JARGON", C_CYAN,
                         cx=540, cy=cam_cy, yaw=cam_yaw, pitch=cam_pitch, zoom=cam_zoom)

    elif v_type == "pagespeed_proof_beat":
        # Scene 7: PROOF BEAT // GOOGLE PAGESPEED 99/100 AUDIT CARD
        # Floating 3D Glass Certificate Base
        card_z = 80 + float_z
        draw_3d_box(d, -260, -200, card_z, 520, 400, 24,
                    col_top=(16, 24, 38, 245), col_r=(10, 16, 28, 255), col_l=(8, 12, 20, 255),
                    border=C_CYAN, cx=540, cy=cam_cy, yaw=cam_yaw, pitch=cam_pitch, zoom=cam_zoom, shadow=True)

        # Screen-space Overlay Glass Certificate for Ultra Sharp Legibility
        overlay_y = 480
        d.rounded_rectangle([120, overlay_y, 960, overlay_y + 360], radius=24,
                            fill=(14, 18, 30, 245), outline=C_EMERALD, width=3)

        # Google Colored Dots Icon
        dot_colors = [(66, 133, 244), (234, 67, 53), (251, 188, 5), (52, 168, 83)]
        for dot_i, col in enumerate(dot_colors):
            d.ellipse([160 + dot_i * 22, overlay_y + 36, 174 + dot_i * 22, overlay_y + 50], fill=col)

        d.text((260, overlay_y + 30), "GOOGLE PAGESPEED INSIGHTS", font=font_proof_title, fill=C_WHITE)

        # 99/100 Score Dial
        d.ellipse([170, overlay_y + 110, 310, overlay_y + 250], outline=(30, 41, 59, 255), width=8)
        d.arc([170, overlay_y + 110, 310, overlay_y + 250], start=-90, end=260, fill=C_EMERALD, width=10)
        d.text((200, overlay_y + 140), "99", font=font_hero_unit, fill=C_EMERALD)
        d.text((208, overlay_y + 200), "/ 100", font=font_proof_body, fill=C_MUTED)

        # Stats Column
        d.text((360, overlay_y + 115), "CORE WEB VITALS: PASSED", font=font_hero_label, fill=C_EMERALD)
        d.text((360, overlay_y + 155), "• Largest Contentful Paint (LCP): 0.8s", font=font_proof_body, fill=C_WHITE)
        d.text((360, overlay_y + 195), "• Cumulative Layout Shift (CLS): 0.00", font=font_proof_body, fill=C_WHITE)

        # Proof Stat Citation Box
        d.rounded_rectangle([150, overlay_y + 280, 930, overlay_y + 335], radius=10,
                            fill=(20, 28, 44, 255), outline=C_AMBER, width=1)
        d.text((170, overlay_y + 295), "“53% of mobile visits are abandoned if pages take >3s”",
               font=font_proof_stat, fill=C_AMBER)
        d.text((700, overlay_y + 295), "[Think With Google]", font=font_proof_stat, fill=C_MUTED)

    elif v_type == "gold_value_monolith":
        # Scene 8: Gold Illuminated Above-the-Fold Monolith
        draw_3d_box(d, -220, -220, 10, 440, 440, 30,
                    col_top=(26, 32, 48, 255), col_r=(18, 22, 34, 255), col_l=(12, 16, 26, 255),
                    border=C_CYAN, cx=540, cy=cam_cy, yaw=cam_yaw, pitch=cam_pitch, zoom=cam_zoom, shadow=True)

        # Warm Amber / Gold Hero Slab
        slab_z = 40 + float_z
        draw_3d_box(d, -180, -140, slab_z, 360, 280, 160,
                    col_top=(60, 44, 18, 255), col_r=(44, 30, 12, 255), col_l=(30, 20, 8, 255),
                    border=C_AMBER, cx=540, cy=cam_cy, yaw=cam_yaw, pitch=cam_pitch, zoom=cam_zoom)

        # Specular Gold Rim
        draw_iso_callout(d, -180, 0, slab_z + 160, 90, 480, "ABOVE THE FOLD: < 5 WORDS", C_AMBER,
                         cx=540, cy=cam_cy, yaw=cam_yaw, pitch=cam_pitch, zoom=cam_zoom)
        draw_iso_callout(d, 180, 0, slab_z + 80, 560, 960, "INSTANT VALUE PROPOSITION", C_CYAN,
                         cx=540, cy=cam_cy, yaw=cam_yaw, pitch=cam_pitch, zoom=cam_zoom)

    elif v_type == "direct_booking_conduit":
        # Scene 9: Direct 1-Tap Booking Conduit (Split Comparison)
        # Left Monolith: 1-Tap Direct Superconductor (Emerald / Cyan)
        draw_3d_box(d, -280, -140, 20, 220, 280, 160 + float_z,
                    col_top=(14, 48, 40, 255), col_r=(10, 34, 28, 255), col_l=(8, 24, 20, 255),
                    border=C_EMERALD, cx=540, cy=cam_cy, yaw=cam_yaw, pitch=cam_pitch, zoom=cam_zoom, shadow=True)

        # Right Monolith: Legacy Form Friction (Crimson)
        draw_3d_box(d, 60, -140, 20, 220, 280, 240 - float_z,
                    col_top=(50, 14, 26, 255), col_r=(36, 10, 18, 255), col_l=(24, 6, 14, 255),
                    border=C_RED, cx=540, cy=cam_cy, yaw=cam_yaw, pitch=cam_pitch, zoom=cam_zoom, shadow=True)

        # Central Laser Divider
        p_div1 = project_3d(0, -200, 0, cx=540, cy=cam_cy, yaw=cam_yaw, pitch=cam_pitch, zoom=cam_zoom)
        p_div2 = project_3d(0, 200, 0, cx=540, cy=cam_cy, yaw=cam_yaw, pitch=cam_pitch, zoom=cam_zoom)
        p_div3 = project_3d(0, 0, 320, cx=540, cy=cam_cy, yaw=cam_yaw, pitch=cam_pitch, zoom=cam_zoom)
        d.line([p_div1, p_div2], fill=C_CYAN, width=2)
        d.line([p_div1, p_div3], fill=C_CYAN, width=3)

        draw_iso_callout(d, -170, 0, 180 + float_z, 90, 480, "1-TAP: 0.8s (+120%)", C_EMERALD,
                         cx=540, cy=cam_cy, yaw=cam_yaw, pitch=cam_pitch, zoom=cam_zoom)
        draw_iso_callout(d, 170, 0, 260 - float_z, 560, 960, "LEGACY FORM: 3.8s (-68%)", C_RED,
                         cx=540, cy=cam_cy, yaw=cam_yaw, pitch=cam_pitch, zoom=cam_zoom)

    elif v_type == "hero_speed_countdown":
        # Scene 10: HERO COUNTER 3.8s -> 0.8s OVERDRIVE
        # Base Foundation
        draw_3d_box(d, -220, -220, 10, 440, 440, 36,
                    col_top=(16, 40, 36, 255), col_r=(10, 28, 24, 255), col_l=(8, 20, 18, 255),
                    border=C_EMERALD, cx=540, cy=cam_cy, yaw=cam_yaw, pitch=cam_pitch, zoom=cam_zoom, shadow=True)

        # Sealed Reinforcement Conduit (Gold Clamps)
        draw_3d_box(d, -150, -150, 46, 300, 300, 120,
                    col_top=(22, 52, 44, 255), col_r=(14, 38, 30, 255), col_l=(10, 26, 22, 255),
                    border=C_GOLD, cx=540, cy=cam_cy, yaw=cam_yaw, pitch=cam_pitch, zoom=cam_zoom)

        # BIG VISUAL HERO NUMBER: 3.8s ticking down to 0.8s
        ease = 0.5 - 0.5 * math.cos(scene_rel_t * math.pi)
        current_speed = 3.8 - (ease * 3.0)  # 3.8 down to 0.8
        badge_y = 500
        d.rounded_rectangle([160, badge_y, 920, badge_y + 240], radius=24,
                            fill=(12, 24, 22, 245), outline=C_EMERALD, width=3)

        # Dynamic number display
        d.text((220, badge_y + 40), f"{current_speed:.1f}s", font=font_hero_num, fill=C_EMERALD)
        d.text((540, badge_y + 60), "➔ 0.8s TURBO", font=font_hero_unit, fill=C_GOLD)
        d.text((225, badge_y + 155), "INBOUND QUALIFIED CONVERSIONS: +120%", font=font_hero_label, fill=C_WHITE)

        # Green turbo particle sparks
        for p_i in range(8):
            angle = (t * 6.0) + (p_i * 0.785)
            pr = 180 + math.sin(t * 10 + p_i) * 30
            px = math.cos(angle) * pr
            py = math.sin(angle) * pr
            p_pt = project_3d(px, py, 110, cx=540, cy=cam_cy, yaw=cam_yaw, pitch=cam_pitch, zoom=cam_zoom)
            d.ellipse([p_pt[0]-4, p_pt[1]-4, p_pt[0]+4, p_pt[1]+4], fill=C_EMERALD)

        draw_iso_callout(d, 0, 0, 166, 560, 960, "ALL LEAKS SEALED", C_GOLD,
                         cx=540, cy=cam_cy, yaw=cam_yaw, pitch=cam_pitch, zoom=cam_zoom)

    else: # cta_reveal_slab
        # Scene 11: PULL-BACK REVEAL & CTA SLAB
        # Grand Overview of Sealed Gold/Cyan Pipeline
        draw_3d_box(d, -320, -240, 10, 640, 480, 40,
                    col_top=(20, 28, 44, 255), col_r=(14, 18, 30, 255), col_l=(10, 14, 22, 255),
                    border=C_GOLD, cx=540, cy=cam_cy, yaw=cam_yaw, pitch=cam_pitch, zoom=cam_zoom, shadow=True)

        draw_3d_box(d, -220, -160, 50, 440, 320, 100,
                    col_top=(24, 38, 58, 255), col_r=(16, 26, 40, 255), col_l=(12, 18, 30, 255),
                    border=C_CYAN, cx=540, cy=cam_cy, yaw=cam_yaw, pitch=cam_pitch, zoom=cam_zoom)

        # 3D Floating Glass CTA Monolith (Centered on Screen)
        cta_y = 520
        d.rounded_rectangle([150, cta_y, 930, cta_y + 300], radius=28,
                            fill=(14, 18, 32, 245), outline=C_GOLD, width=3)

        # Glowing CTA Button Slab
        btn_y = cta_y + 45
        d.rounded_rectangle([200, btn_y, 880, btn_y + 100], radius=20,
                            fill=(16, 185, 129, 235), outline=C_GOLD, width=2)
        # Center "BOOK A CALL"
        btn_bbox = font_cta_btn.getbbox("BOOK A CALL")
        btn_w = btn_bbox[2] - btn_bbox[0]
        d.text(((1080 - btn_w) // 2, btn_y + 24), "BOOK A CALL", font=font_cta_btn, fill=(10, 12, 18, 255))

        # Handle "@mwd1504" + Verified Badge
        handle_str = "@mwd1504"
        h_bbox = font_cta_sub.getbbox(handle_str)
        h_w = h_bbox[2] - h_bbox[0]
        h_x = (1080 - h_w) // 2
        d.text((h_x, cta_y + 175), handle_str, font=font_cta_sub, fill=C_CYAN)

        # Verified badge circle
        d.ellipse([h_x + h_w + 14, cta_y + 180, h_x + h_w + 34, cta_y + 200], fill=C_CYAN)
        d.text((h_x + h_w + 18, cta_y + 178), "✓", font=font_hud_tab, fill=(10, 12, 18, 255))

        d.text((250, cta_y + 235), "Fix Your Website Pipeline // Double Inbound Leads",
               font=font_proof_body, fill=C_MUTED)

    # ------------------ HUD TABS & CAPTIONS ------------------
    # Dynamic top HUD Tabs
    scene_tag = current_scene.get("tag", "PIPELINE OS")
    draw_hud_tabs(d, active_idx, scene_tag)

    # Safe-Zone Captions: 3-5 words at a time, big, bottom-center, with spoken word highlighted
    draw_bottom_captions(d, t, timings_data)

    # Bottom Continuous Progress Indicator (y: 1780)
    d.rounded_rectangle([80, 1780, 1000, 1788], radius=4, fill=(30, 41, 59, 160))
    bar_w = int(920 * progress)
    if bar_w > 0:
        bar_col = C_GOLD if active_idx == 10 else C_CYAN
        d.rounded_rectangle([80, 1780, 80 + bar_w, 1788], radius=4, fill=bar_col)

    return im

def render_final(output_path=None):
    if output_path is None:
        output_path = OUTPUT_DIR / "final.mp4"
    else:
        output_path = Path(output_path)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    if not SCRIPT_FILE.exists():
        print(f"Error: {SCRIPT_FILE} not found.", file=sys.stderr)
        sys.exit(1)

    with open(SCRIPT_FILE, "r", encoding="utf-8") as f:
        script_data = json.load(f)

    timings_data = []
    if TIMINGS_FILE.exists():
        with open(TIMINGS_FILE, "r", encoding="utf-8") as f:
            timings_data = json.load(f)

    if not AUDIO_FILE.exists():
        print(f"Error: {AUDIO_FILE} not found.", file=sys.stderr)
        sys.exit(1)

    total_duration = get_audio_duration(AUDIO_FILE)
    print(f"🎵 Audio duration: {total_duration:.2f}s")

    scenes = script_data.get("scenes", [])
    raw_total = sum(s.get("duration", 2.5) for s in scenes) or 1.0
    current_t = 0.0
    timed_scenes = []

    for sc in scenes:
        dur = (sc.get("duration", 2.5) / raw_total) * total_duration
        timed_scenes.append({
            "id": sc.get("id", 1),
            "tag": sc.get("tag", "SCENE"),
            "text": sc.get("text", ""),
            "visual_type": sc.get("visual_type", "shock_leak_hook"),
            "hud_callout": sc.get("hud_callout", ""),
            "metric_val": sc.get("metric_val", ""),
            "start": current_t,
            "end": current_t + dur
        })
        current_t += dur

    total_frames = int(math.ceil(total_duration * FPS))
    print(f"🚀 Rendering {total_frames} frames ({len(timed_scenes)} scenes, 1080x1920 @ {FPS} FPS) with Lit 3D Engine...")

    cmd_ffmpeg = [
        "ffmpeg", "-y",
        "-f", "rawvideo",
        "-pix_fmt", "rgba",
        "-s", f"{W}x{H}",
        "-r", str(FPS),
        "-i", "-",
        "-i", str(AUDIO_FILE),
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
            frame_im = render_frame_image(f, total_frames, script_data, total_duration, timed_scenes, timings_data)
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

    # Copy to Download directory if on Android
    download_dir = Path("/sdcard/Download")
    if download_dir.exists() and download_dir.is_dir():
        dest = download_dir / "final.mp4"
        shutil.copyfile(output_path, dest)
        print(f"📲 Synchronized to Downloads: {dest}")

if __name__ == "__main__":
    out_arg = sys.argv[1] if len(sys.argv) > 1 else None
    render_final(out_arg)
