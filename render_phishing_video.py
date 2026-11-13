#!/usr/bin/env python3
"""
render_phishing_video.py - 3D Isometric Motion Graphics Video:
Topic: "How Hackers Infiltrate Phones Through Phishing"
Strictly adheres to VIDEO_QUALITY_GUIDELINES.md:
- ONE central metaphor: Smartphone Bank Vault & Mechanical Security Strongroom
- Teardown sub-parts, moving mechanical tumblers, optical data conduits, clamping jaws
- 11 rapid scenes (cuts every 2-3s)
- Continuous 3D camera orbits, push-ins, pull-backs
- Lit 3D geometry with 3-tone shading, specular highlights, soft contact shadows
- Big bottom captions with active spoken word highlighted in gold (no paragraph box)
- Hero numbers (12s breach countdown, 91% Verizon DBIR stat)
- Verified proof beat
- Shock hook (0-2s) & clear CTA (@mwd1504)
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
SCRIPT_FILE = PIPELINE_DIR / "phishing_script.json"
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
font_hero_num = ImageFont.truetype(FONT_SANS_BOLD, 115)
font_hero_unit = ImageFont.truetype(FONT_SANS_BOLD, 52)
font_hero_label = ImageFont.truetype(FONT_MONO_BOLD, 26)
font_callout_txt = ImageFont.truetype(FONT_MONO_BOLD, 22)
font_caption = ImageFont.truetype(FONT_SANS_BOLD, 46)
font_proof_title = ImageFont.truetype(FONT_SANS_BOLD, 28)
font_proof_body = ImageFont.truetype(FONT_SANS_BOLD, 22)
font_proof_stat = ImageFont.truetype(FONT_MONO_BOLD, 19)
font_cta_btn = ImageFont.truetype(FONT_SANS_BOLD, 46)
font_cta_sub = ImageFont.truetype(FONT_MONO_BOLD, 28)

W, H = 1080, 1920
FPS = 30

# Color Palette: Deep Obsidian + Warm Amber + Cyan + Crimson + Emerald
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
        return 29.256

def project_3d(x, y, z, cx=540, cy=960, yaw=45.0, pitch=35.0, zoom=1.0):
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
    for expand, alpha in [(32, 40), (16, 70), (4, 110)]:
        p0 = project_3d(bx - expand, by - expand, 0, cx, cy, yaw, pitch, zoom)
        p1 = project_3d(bx + bw + expand, by - expand, 0, cx, cy, yaw, pitch, zoom)
        p2 = project_3d(bx + bw + expand, by + bd + expand, 0, cx, cy, yaw, pitch, zoom)
        p3 = project_3d(bx - expand, by + bd + expand, 0, cx, cy, yaw, pitch, zoom)
        d.polygon([p0, p1, p2, p3], fill=(4, 6, 12, alpha))

def draw_3d_box(d, bx, by, bz, bw, bd, bh,
                col_top, col_r, col_l, border=None,
                cx=540, cy=960, yaw=45.0, pitch=35.0, zoom=1.0,
                width=2, shadow=False):
    if shadow:
        draw_soft_shadow(d, bx, by, bw, bd, cx, cy, yaw, pitch, zoom)

    p010 = project_3d(bx, by + bd, bz, cx, cy, yaw, pitch, zoom)
    p110 = project_3d(bx + bw, by + bd, bz, cx, cy, yaw, pitch, zoom)
    p100 = project_3d(bx + bw, by, bz, cx, cy, yaw, pitch, zoom)

    p001 = project_3d(bx, by, bz + bh, cx, cy, yaw, pitch, zoom)
    p101 = project_3d(bx + bw, by, bz + bh, cx, cy, yaw, pitch, zoom)
    p111 = project_3d(bx + bw, by + bd, bz + bh, cx, cy, yaw, pitch, zoom)
    p011 = project_3d(bx, by + bd, bz + bh, cx, cy, yaw, pitch, zoom)

    d.polygon([p010, p110, p111, p011], fill=col_l, outline=border, width=width)
    d.polygon([p100, p110, p111, p101], fill=col_r, outline=border, width=width)
    d.polygon([p001, p101, p111, p011], fill=col_top, outline=border, width=width)
    if border and width > 1:
        d.line([p001, p101], fill=(255, 255, 255, 140), width=1)

def draw_3d_cylinder(d, cx_3d, cy_3d, cz, radius, height, col_top, col_side, border=None,
                     cx=540, cy=960, yaw=45.0, pitch=35.0, zoom=1.0, segments=16):
    pts_bot = []
    pts_top = []
    for i in range(segments):
        deg = (360.0 / segments) * i
        rad = math.radians(deg)
        x = cx_3d + math.cos(rad) * radius
        y = cy_3d + math.sin(rad) * radius
        pts_bot.append(project_3d(x, y, cz, cx, cy, yaw, pitch, zoom))
        pts_top.append(project_3d(x, y, cz + height, cx, cy, yaw, pitch, zoom))

    # Draw side quads
    for i in range(segments):
        nxt = (i + 1) % segments
        quad = [pts_bot[i], pts_bot[nxt], pts_top[nxt], pts_top[i]]
        d.polygon(quad, fill=col_side, outline=border, width=1)

    # Draw top cap
    d.polygon(pts_top, fill=col_top, outline=border, width=2)

def draw_iso_callout(d, x_3d, y_3d, z_3d, badge_x, badge_y, text, accent_color,
                     cx=540, cy=960, yaw=45.0, pitch=35.0, zoom=1.0):
    start_pt = project_3d(x_3d, y_3d, z_3d, cx, cy, yaw, pitch, zoom)
    mid_pt = (badge_x - 24, badge_y + 22)
    end_pt = (badge_x, badge_y + 22)

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
    d.rounded_rectangle([60, 110, 1020, 195], radius=16, fill=(13, 17, 28, 235), outline=(0, 242, 254, 70), width=2)

    accent = C_AMBER if active_idx in [1, 3, 5, 7] else (C_RED if active_idx in [0, 4, 6] else C_CYAN)
    d.ellipse([92, 144, 106, 158], fill=accent)
    d.ellipse([88, 140, 110, 162], outline=accent, width=1)

    tag_text = f"VAULT SECURITY // {scene_tag}"
    d.text((124, 138), tag_text, font=font_hud_label, fill=(241, 245, 249, 255))

    total_steps = 11
    start_x = 680
    step_w = 26
    step_gap = 4
    for i in range(total_steps):
        sx = start_x + i * (step_w + step_gap)
        is_cur = (i == active_idx)
        c_fill = accent if is_cur else (30, 41, 59, 140)
        c_line = accent if is_cur else (71, 85, 105, 100)
        d.rounded_rectangle([sx, 142, sx + step_w, 164], radius=4, fill=c_fill, outline=c_line, width=1)
        if is_cur:
            txt_num = str(i + 1)
            d.text((sx + 5, 144), txt_num, font=font_hud_tab, fill=(10, 12, 18, 255))

def draw_bottom_captions(d, t, timings_data):
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

def render_phishing_frame(frame_idx, total_frames, script_data, total_duration, timed_scenes, timings_data):
    t = frame_idx / float(FPS)
    progress = min(1.0, max(0.0, t / max(1.0, total_duration)))

    active_idx = 0
    for idx, sc in enumerate(timed_scenes):
        if sc["start"] <= t <= sc["end"]:
            active_idx = idx
            break
        elif t > sc["end"]:
            active_idx = idx

    current_scene = timed_scenes[active_idx]
    v_type = current_scene.get("visual_type", "vault_perimeter_alert")
    scene_dur = max(0.1, current_scene["end"] - current_scene["start"])
    scene_rel_t = max(0.0, min(1.0, (t - current_scene["start"]) / scene_dur))

    im = Image.new('RGBA', (W, H), C_BG)
    d = ImageDraw.Draw(im)

    # Continuous Camera Kinematics per Scene
    if v_type == "vault_perimeter_alert":
        cam_yaw = 36.0 + scene_rel_t * 12.0
        cam_pitch = 34.0 + scene_rel_t * 5.0
        cam_zoom = 1.05 + scene_rel_t * 0.15
        cam_cy = 820
    elif v_type == "phone_chassis_teardown":
        cam_yaw = 48.0 - scene_rel_t * 14.0
        cam_pitch = 42.0 - scene_rel_t * 8.0
        cam_zoom = 1.15 + scene_rel_t * 0.12
        cam_cy = 830
    elif v_type == "auth_tumbler_lock":
        cam_yaw = 34.0 + scene_rel_t * 15.0
        cam_pitch = 35.0
        cam_zoom = 1.20 + scene_rel_t * 0.10
        cam_cy = 810
    elif v_type == "trojan_keycard_open":
        cam_yaw = 52.0 - scene_rel_t * 10.0
        cam_pitch = 32.0 + scene_rel_t * 6.0
        cam_zoom = 1.16 + scene_rel_t * 0.15
        cam_cy = 820
    elif v_type == "malware_conduit_inject":
        cam_yaw = 40.0 + scene_rel_t * 16.0
        cam_pitch = 28.0 + scene_rel_t * 10.0
        cam_zoom = 1.12 + scene_rel_t * 0.10
        cam_cy = 840
    elif v_type == "hero_breach_timer":
        cam_yaw = 50.0 - scene_rel_t * 12.0
        cam_pitch = 36.0
        cam_zoom = 1.15 + scene_rel_t * 0.18
        cam_cy = 800
    elif v_type == "credential_exfil_stream":
        cam_yaw = 36.0 + scene_rel_t * 14.0
        cam_pitch = 34.0 + scene_rel_t * 6.0
        cam_zoom = 1.14 + scene_rel_t * 0.12
        cam_cy = 820
    elif v_type == "verizon_proof_beat":
        cam_yaw = 44.0 + math.sin(scene_rel_t * math.pi) * 6.0
        cam_pitch = 30.0 + scene_rel_t * 10.0
        cam_zoom = 1.06 + scene_rel_t * 0.12
        cam_cy = 820
    elif v_type == "titanium_security_clamp":
        cam_yaw = 48.0 - scene_rel_t * 10.0
        cam_pitch = 36.0
        cam_zoom = 1.18 + scene_rel_t * 0.10
        cam_cy = 810
    elif v_type == "impervious_shield_lock":
        cam_yaw = 38.0 + scene_rel_t * 12.0
        cam_pitch = 34.0 + scene_rel_t * 4.0
        cam_zoom = 1.15 + scene_rel_t * 0.16
        cam_cy = 810
    else: # cta_reveal_phishing
        cam_yaw = 46.0 - scene_rel_t * 14.0
        cam_pitch = 36.0 + scene_rel_t * 6.0
        cam_zoom = 1.25 - scene_rel_t * 0.28
        cam_cy = 830

    # Ground Blueprint Grid with Warm Accent
    grid_col = (0, 242, 254, 25)
    for gx in range(-600, 700, 120):
        p_start = project_3d(gx, -600, 0, cx=540, cy=cam_cy, yaw=cam_yaw, pitch=cam_pitch, zoom=cam_zoom)
        p_end = project_3d(gx, 600, 0, cx=540, cy=cam_cy, yaw=cam_yaw, pitch=cam_pitch, zoom=cam_zoom)
        d.line([p_start, p_end], fill=grid_col, width=1)
    for gy in range(-600, 700, 120):
        p_start = project_3d(-600, gy, 0, cx=540, cy=cam_cy, yaw=cam_yaw, pitch=cam_pitch, zoom=cam_zoom)
        p_end = project_3d(600, gy, 0, cx=540, cy=cam_cy, yaw=cam_yaw, pitch=cam_pitch, zoom=cam_zoom)
        d.line([p_start, p_end], fill=grid_col, width=1)

    float_z = math.sin(t * 3.4) * 12.0
    pulse = (math.sin(t * 8.0) + 1.0) * 0.5

    # ------------------ SCENE-SPECIFIC 3D GEOMETRY ------------------

    if v_type == "vault_perimeter_alert":
        # Scene 1: Smartphone Vault with Shocking Incoming Phishing SMS Alarm
        # 3D Smartphone Chassis (Titanium rim + Obsidian OLED glass)
        draw_3d_box(d, -180, -280, 20, 360, 560, 36,
                    col_top=(24, 32, 48, 255), col_r=(15, 20, 32, 255), col_l=(10, 14, 24, 255),
                    border=(0, 242, 254, 180), cx=540, cy=cam_cy, yaw=cam_yaw, pitch=cam_pitch, zoom=cam_zoom, shadow=True)

        # OLED Screen Plate with glowing red alert strobe
        draw_3d_box(d, -160, -260, 56, 320, 520, 10,
                    col_top=(38, 12, 22, 255), col_r=(26, 8, 16, 255), col_l=(18, 6, 12, 255),
                    border=C_RED, cx=540, cy=cam_cy, yaw=cam_yaw, pitch=cam_pitch, zoom=cam_zoom)

        # Floating Decoy Phishing SMS Notification Card (Golden/Red Trojan Bait)
        card_z = 120 + float_z
        draw_3d_box(d, -140, -140, card_z, 280, 220, 24,
                    col_top=(45, 18, 14, 245), col_r=(32, 12, 10, 255), col_l=(22, 8, 6, 255),
                    border=C_AMBER, cx=540, cy=cam_cy, yaw=cam_yaw, pitch=cam_pitch, zoom=cam_zoom)

        draw_iso_callout(d, -140, 0, card_z + 24, 100, 460, "SPOOFED SMS: BANK ALERT", C_RED,
                         cx=540, cy=cam_cy, yaw=cam_yaw, pitch=cam_pitch, zoom=cam_zoom)
        draw_iso_callout(d, 140, 0, card_z + 24, 580, 940, "MALICIOUS LINK EMBEDDED", C_AMBER,
                         cx=540, cy=cam_cy, yaw=cam_yaw, pitch=cam_pitch, zoom=cam_zoom)

        # Top Shock Hook Banner
        d.rounded_rectangle([100, 360, 980, 430], radius=12, fill=(255, 45, 85, 40), outline=C_RED, width=2)
        d.text((130, 378), "⚠️ INCOMING ATTACK: 1 TAP DRAINS ENTIRE PHONE", font=font_callout_txt, fill=C_RED)

    elif v_type == "phone_chassis_teardown":
        # Scene 2: Product Teardown of the Smartphone Vault into 3 Labeled Sub-Parts
        # Sub-Part 1: Bottom Core Enclave Silicon (Obsidian/Cyan)
        draw_3d_box(d, -170, -220, 20, 340, 440, 30,
                    col_top=(20, 28, 42, 255), col_r=(12, 18, 28, 255), col_l=(8, 12, 20, 255),
                    border=C_CYAN, cx=540, cy=cam_cy, yaw=cam_yaw, pitch=cam_pitch, zoom=cam_zoom, shadow=True)

        # Sub-Part 2: Middle Mechanical Tumbler Lock Plate (Sliding up with float)
        draw_3d_box(d, -170, -220, 130 + float_z * 0.6, 340, 440, 32,
                    col_top=(44, 34, 18, 255), col_r=(30, 22, 12, 255), col_l=(20, 14, 8, 255),
                    border=C_AMBER, cx=540, cy=cam_cy, yaw=cam_yaw, pitch=cam_pitch, zoom=cam_zoom)

        # Sub-Part 3: Top Biometric Sensor Glass Viewport
        draw_3d_box(d, -170, -220, 250 + float_z * 1.3, 340, 440, 26,
                    col_top=(16, 34, 52, 230), col_r=(10, 22, 34, 255), col_l=(8, 16, 24, 255),
                    border=C_CYAN, cx=540, cy=cam_cy, yaw=cam_yaw, pitch=cam_pitch, zoom=cam_zoom)

        # Teardown Leader Callouts
        draw_iso_callout(d, -170, 0, 250 + float_z * 1.3, 90, 460, "PART 01: BIOMETRIC SENSOR", C_CYAN,
                         cx=540, cy=cam_cy, yaw=cam_yaw, pitch=cam_pitch, zoom=cam_zoom)
        draw_iso_callout(d, 170, 0, 130 + float_z * 0.6, 560, 960, "PART 02: AUTH TUMBLER LOCK", C_AMBER,
                         cx=540, cy=cam_cy, yaw=cam_yaw, pitch=cam_pitch, zoom=cam_zoom)

    elif v_type == "auth_tumbler_lock":
        # Scene 3: Rotating Mechanical Cipher Tumbler Lock
        draw_3d_box(d, -220, -220, 20, 440, 440, 36,
                    col_top=(22, 30, 46, 255), col_r=(14, 20, 30, 255), col_l=(10, 14, 22, 255),
                    border=C_CYAN, cx=540, cy=cam_cy, yaw=cam_yaw, pitch=cam_pitch, zoom=cam_zoom, shadow=True)

        # 3D Rotating Vault Tumbler Cylinder
        rot_deg = (t * 120.0) % 360
        draw_3d_cylinder(d, 0, 0, 56, radius=130, height=50,
                         col_top=(36, 48, 72, 255), col_side=(24, 32, 50, 255), border=C_AMBER,
                         cx=540, cy=cam_cy, yaw=cam_yaw + rot_deg * 0.1, pitch=cam_pitch, zoom=cam_zoom)

        # Radial Tumbler Dial Ticks
        for tick_d in range(0, 360, 30):
            rad = math.radians(tick_d + rot_deg)
            tx1 = math.cos(rad) * 90
            ty1 = math.sin(rad) * 90
            tx2 = math.cos(rad) * 120
            ty2 = math.sin(rad) * 120
            pt1 = project_3d(tx1, ty1, 107, cx=540, cy=cam_cy, yaw=cam_yaw, pitch=cam_pitch, zoom=cam_zoom)
            pt2 = project_3d(tx2, ty2, 107, cx=540, cy=cam_cy, yaw=cam_yaw, pitch=cam_pitch, zoom=cam_zoom)
            d.line([pt1, pt2], fill=C_GOLD, width=3)

        draw_iso_callout(d, -130, 0, 90, 90, 480, "HARDWARE CIPHER: LOCKED", C_CYAN,
                         cx=540, cy=cam_cy, yaw=cam_yaw, pitch=cam_pitch, zoom=cam_zoom)
        draw_iso_callout(d, 130, 0, 90, 560, 960, "PASSWORD CANNOT BE CRACKED", C_AMBER,
                         cx=540, cy=cam_cy, yaw=cam_yaw, pitch=cam_pitch, zoom=cam_zoom)

    elif v_type == "trojan_keycard_open":
        # Scene 4: Trojan Fake Authentication Keycard Sliding into Lock
        draw_3d_box(d, -220, -220, 20, 440, 440, 36,
                    col_top=(26, 32, 48, 255), col_r=(16, 22, 34, 255), col_l=(12, 16, 24, 255),
                    border=C_CYAN, cx=540, cy=cam_cy, yaw=cam_yaw, pitch=cam_pitch, zoom=cam_zoom, shadow=True)

        # Vault Door Sliding Open (Moving Part)
        door_slide = scene_rel_t * 140
        draw_3d_box(d, -200 + door_slide, -180, 56, 180, 360, 50,
                    col_top=(45, 20, 24, 255), col_r=(32, 12, 16, 255), col_l=(22, 8, 12, 255),
                    border=C_RED, cx=540, cy=cam_cy, yaw=cam_yaw, pitch=cam_pitch, zoom=cam_zoom)

        # Deceptive Gold Phishing Token Inserting
        draw_3d_box(d, -60, -80, 110, 120, 160, 18,
                    col_top=(60, 45, 14, 255), col_r=(42, 30, 10, 255), col_l=(28, 20, 6, 255),
                    border=C_GOLD, cx=540, cy=cam_cy, yaw=cam_yaw, pitch=cam_pitch, zoom=cam_zoom)

        draw_iso_callout(d, 0, 0, 128, 90, 480, "VICTIM TAPS LINK: AUTHORIZED", C_AMBER,
                         cx=540, cy=cam_cy, yaw=cam_yaw, pitch=cam_pitch, zoom=cam_zoom)
        draw_iso_callout(d, -180 + door_slide, 0, 106, 560, 960, "VAULT DOOR UNLOCKED", C_RED,
                         cx=540, cy=cam_cy, yaw=cam_yaw, pitch=cam_pitch, zoom=cam_zoom)

    elif v_type == "malware_conduit_inject":
        # Scene 5: Crimson Optical Conduit Injecting Malicious Payload
        draw_3d_box(d, -200, -200, 20, 400, 400, 40,
                    col_top=(20, 26, 40, 255), col_r=(14, 18, 28, 255), col_l=(10, 12, 20, 255),
                    border=C_CYAN, cx=540, cy=cam_cy, yaw=cam_yaw, pitch=cam_pitch, zoom=cam_zoom, shadow=True)

        # Central Operating System Core Enclave
        draw_3d_box(d, -120, -120, 60, 240, 240, 80,
                    col_top=(48, 14, 24, 255), col_r=(34, 10, 16, 255), col_l=(24, 6, 12, 255),
                    border=C_RED, cx=540, cy=cam_cy, yaw=cam_yaw, pitch=cam_pitch, zoom=cam_zoom)

        # Malicious data particles streaming through conduit
        for p_i in range(8):
            dist = (t * 220 + p_i * 35) % 240
            pt = project_3d(-180 + dist, 0, 110, cx=540, cy=cam_cy, yaw=cam_yaw, pitch=cam_pitch, zoom=cam_zoom)
            d.ellipse([pt[0]-5, pt[1]-5, pt[0]+5, pt[1]+5], fill=C_RED)

        draw_iso_callout(d, -120, 0, 140, 90, 460, "BACKGROUND TOKEN INJECTED", C_RED,
                         cx=540, cy=cam_cy, yaw=cam_yaw, pitch=cam_pitch, zoom=cam_zoom)
        draw_iso_callout(d, 120, 0, 140, 560, 960, "OS PRIVILEGES GRANTED", C_AMBER,
                         cx=540, cy=cam_cy, yaw=cam_yaw, pitch=cam_pitch, zoom=cam_zoom)

    elif v_type == "hero_breach_timer":
        # Scene 6: HERO 12s BREACH SPEED COUNTDOWN
        draw_3d_box(d, -220, -220, 10, 440, 440, 40,
                    col_top=(36, 18, 24, 255), col_r=(24, 12, 16, 255), col_l=(16, 8, 12, 255),
                    border=C_RED, cx=540, cy=cam_cy, yaw=cam_yaw, pitch=cam_pitch, zoom=cam_zoom, shadow=True)

        # BIG VISUAL HERO NUMBER: 12s Timer Sweeping
        ease = 0.5 - 0.5 * math.cos(scene_rel_t * math.pi)
        cur_sec = max(0.8, 12.0 - (ease * 11.2))

        badge_y = 500
        d.rounded_rectangle([180, badge_y, 900, badge_y + 240], radius=24,
                            fill=(18, 14, 22, 240), outline=C_RED, width=3)

        d.text((240, badge_y + 40), f"{cur_sec:.1f}s", font=font_hero_num, fill=C_RED)
        d.text((580, badge_y + 70), "BREACH SPEED", font=font_hero_unit, fill=C_AMBER)
        d.text((245, badge_y + 155), "FULL CREDENTIAL HARVEST IN 12 SECONDS", font=font_hero_label, fill=C_WHITE)

        draw_iso_callout(d, -130, 0, 160, 100, 940, "AUTOMATED BOT EXFILTRATION", C_RED,
                         cx=540, cy=cam_cy, yaw=cam_yaw, pitch=cam_pitch, zoom=cam_zoom)

    elif v_type == "credential_exfil_stream":
        # Scene 7: Exfiltrating Private Tokens & Session Cookies
        draw_3d_box(d, -200, -200, 20, 400, 400, 36,
                    col_top=(26, 32, 46, 255), col_r=(16, 22, 32, 255), col_l=(12, 16, 24, 255),
                    border=C_CYAN, cx=540, cy=cam_cy, yaw=cam_yaw, pitch=cam_pitch, zoom=cam_zoom, shadow=True)

        # 3 Floating Stolen Credential Cubes (2FA tokens, Session Keys)
        for c_i, c_offset in enumerate([-90, 0, 90]):
            cube_z = 90 + math.sin(t * 6.0 + c_i) * 18
            draw_3d_box(d, c_offset - 35, -35, cube_z, 70, 70, 50,
                        col_top=(54, 40, 16, 255), col_r=(38, 28, 10, 255), col_l=(26, 18, 8, 255),
                        border=C_GOLD, cx=540, cy=cam_cy, yaw=cam_yaw, pitch=cam_pitch, zoom=cam_zoom)

        draw_iso_callout(d, -90, 0, 140, 90, 460, "2FA SESSION TOKENS: COPIED", C_AMBER,
                         cx=540, cy=cam_cy, yaw=cam_yaw, pitch=cam_pitch, zoom=cam_zoom)
        draw_iso_callout(d, 90, 0, 140, 560, 960, "BANKING PASSWORDS EXFILTRATED", C_RED,
                         cx=540, cy=cam_cy, yaw=cam_yaw, pitch=cam_pitch, zoom=cam_zoom)

    elif v_type == "verizon_proof_beat":
        # Scene 8: PROOF BEAT // VERIZON DBIR 91% STAT CERTIFICATE
        card_z = 80 + float_z
        draw_3d_box(d, -260, -200, card_z, 520, 400, 24,
                    col_top=(16, 24, 38, 245), col_r=(10, 16, 28, 255), col_l=(8, 12, 20, 255),
                    border=C_RED, cx=540, cy=cam_cy, yaw=cam_yaw, pitch=cam_pitch, zoom=cam_zoom, shadow=True)

        # Glass Certificate Screen Card
        overlay_y = 480
        d.rounded_rectangle([120, overlay_y, 960, overlay_y + 360], radius=24,
                            fill=(14, 18, 30, 245), outline=C_RED, width=3)

        # Shield Icon
        d.ellipse([160, overlay_y + 36, 188, overlay_y + 64], fill=C_RED)
        d.text((210, overlay_y + 35), "VERIZON DATA BREACH REPORT (DBIR)", font=font_proof_title, fill=C_WHITE)

        # 91% Score Dial
        d.ellipse([170, overlay_y + 110, 310, overlay_y + 250], outline=(40, 50, 70, 255), width=8)
        d.arc([170, overlay_y + 110, 310, overlay_y + 250], start=-90, end=240, fill=C_RED, width=10)
        d.text((195, overlay_y + 140), "91%", font=font_hero_unit, fill=C_RED)

        # Stat Column
        d.text((360, overlay_y + 115), "CYBER BREACH VECTOR: PHISHING", font=font_hero_label, fill=C_AMBER)
        d.text((360, overlay_y + 155), "• 91% of cyber attacks start with 1 link", font=font_proof_body, fill=C_WHITE)
        d.text((360, overlay_y + 195), "• Credential theft via spoofed landing pages", font=font_proof_body, fill=C_WHITE)

        # Proof Source Box
        d.rounded_rectangle([150, overlay_y + 280, 930, overlay_y + 335], radius=10,
                            fill=(26, 18, 24, 255), outline=C_RED, width=1)
        d.text((170, overlay_y + 295), "“91% of all cyber breaches start with a phishing message”",
               font=font_proof_stat, fill=C_AMBER)
        d.text((720, overlay_y + 295), "[Verizon DBIR & CISA]", font=font_proof_stat, fill=C_MUTED)

    elif v_type == "titanium_security_clamp":
        # Scene 9: Visibly Showing the Fix: Heavy Titanium Security Clamps Slam Shut
        draw_3d_box(d, -220, -220, 20, 440, 440, 36,
                    col_top=(20, 36, 44, 255), col_r=(12, 24, 30, 255), col_l=(8, 16, 22, 255),
                    border=C_CYAN, cx=540, cy=cam_cy, yaw=cam_yaw, pitch=cam_pitch, zoom=cam_zoom, shadow=True)

        # Clamping Jaws Slamming Down over the Breach Conduit (Moving Part)
        clamp_drop = min(90.0, scene_rel_t * 120.0)
        draw_3d_box(d, -180, -120, 220 - clamp_drop, 360, 240, 50,
                    col_top=(24, 52, 48, 255), col_r=(16, 38, 34, 255), col_l=(10, 26, 22, 255),
                    border=C_EMERALD, cx=540, cy=cam_cy, yaw=cam_yaw, pitch=cam_pitch, zoom=cam_zoom)

        draw_iso_callout(d, -180, 0, 220 - clamp_drop + 50, 90, 480, "HARDWARE CLAMP DEPLOYED", C_EMERALD,
                         cx=540, cy=cam_cy, yaw=cam_yaw, pitch=cam_pitch, zoom=cam_zoom)
        draw_iso_callout(d, 180, 0, 220 - clamp_drop + 50, 560, 960, "BREACH CONDUIT TERMINATED", C_CYAN,
                         cx=540, cy=cam_cy, yaw=cam_yaw, pitch=cam_pitch, zoom=cam_zoom)

    elif v_type == "impervious_shield_lock":
        # Scene 10: Impervious Shield Active, Vulnerability 0%
        draw_3d_box(d, -220, -220, 20, 440, 440, 40,
                    col_top=(18, 44, 38, 255), col_r=(12, 30, 26, 255), col_l=(8, 22, 18, 255),
                    border=C_EMERALD, cx=540, cy=cam_cy, yaw=cam_yaw, pitch=cam_pitch, zoom=cam_zoom, shadow=True)

        # Luminous Blue/Cyan Energy Shield Ring
        shield_r = 180 + pulse * 20
        ring_pts = []
        for deg in range(0, 360, 15):
            rad = math.radians(deg)
            ring_pts.append(project_3d(math.cos(rad) * shield_r, math.sin(rad) * shield_r, 120,
                                       cx=540, cy=cam_cy, yaw=cam_yaw, pitch=cam_pitch, zoom=cam_zoom))
        d.polygon(ring_pts, outline=C_CYAN, width=3)

        badge_y = 500
        d.rounded_rectangle([180, badge_y, 900, badge_y + 240], radius=24,
                            fill=(12, 26, 24, 245), outline=C_EMERALD, width=3)

        d.text((240, badge_y + 40), "0%", font=font_hero_num, fill=C_EMERALD)
        d.text((450, badge_y + 70), "VULNERABILITY", font=font_hero_unit, fill=C_GOLD)
        d.text((245, badge_y + 155), "UNVERIFIED ACCESS LINKS BLOCKED", font=font_hero_label, fill=C_WHITE)

    else: # cta_reveal_phishing
        # Scene 11: Cinematic Pull-Back Reveal of Secure Vault Fortress & CTA
        draw_3d_box(d, -320, -240, 10, 640, 480, 40,
                    col_top=(20, 32, 48, 255), col_r=(14, 22, 34, 255), col_l=(10, 16, 24, 255),
                    border=C_CYAN, cx=540, cy=cam_cy, yaw=cam_yaw, pitch=cam_pitch, zoom=cam_zoom, shadow=True)

        cta_y = 520
        d.rounded_rectangle([150, cta_y, 930, cta_y + 300], radius=28,
                            fill=(14, 18, 32, 245), outline=C_GOLD, width=3)

        btn_y = cta_y + 45
        d.rounded_rectangle([190, btn_y, 890, btn_y + 100], radius=20,
                            fill=(16, 185, 129, 235), outline=C_GOLD, width=2)
        btn_bbox = font_cta_btn.getbbox("STAY BULLETPROOF")
        btn_w = btn_bbox[2] - btn_bbox[0]
        d.text(((1080 - btn_w) // 2, btn_y + 24), "STAY BULLETPROOF", font=font_cta_btn, fill=(10, 12, 18, 255))

        handle_str = "@mwd1504"
        h_bbox = font_cta_sub.getbbox(handle_str)
        h_w = h_bbox[2] - h_bbox[0]
        h_x = (1080 - h_w) // 2
        d.text((h_x, cta_y + 175), handle_str, font=font_cta_sub, fill=C_CYAN)

        d.ellipse([h_x + h_w + 14, cta_y + 180, h_x + h_w + 34, cta_y + 200], fill=C_CYAN)
        d.text((h_x + h_w + 18, cta_y + 178), "✓", font=font_hud_tab, fill=(10, 12, 18, 255))

        d.text((280, cta_y + 235), "Follow for Mobile Cyber Defense & High-Security Tech",
               font=font_proof_body, fill=C_MUTED)

    # Dynamic top HUD Tabs
    scene_tag = current_scene.get("tag", "VAULT SECURITY")
    draw_hud_tabs(d, active_idx, scene_tag)

    # Safe-Zone Captions: 3-5 words at a time, big, bottom-center, active word highlighted in gold
    draw_bottom_captions(d, t, timings_data)

    # Bottom Progress Bar
    d.rounded_rectangle([80, 1780, 1000, 1788], radius=4, fill=(30, 41, 59, 160))
    bar_w = int(920 * progress)
    if bar_w > 0:
        bar_col = C_GOLD if active_idx == 10 else C_CYAN
        d.rounded_rectangle([80, 1780, 80 + bar_w, 1788], radius=4, fill=bar_col)

    return im

def render_phishing_final():
    output_path = OUTPUT_DIR / "phishing_breach.mp4"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(SCRIPT_FILE, "r", encoding="utf-8") as f:
        script_data = json.load(f)

    with open(TIMINGS_FILE, "r", encoding="utf-8") as f:
        timings_data = json.load(f)

    total_duration = get_audio_duration(AUDIO_FILE)
    print(f"🎵 Phishing Audio duration: {total_duration:.2f}s")

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
            "visual_type": sc.get("visual_type", "vault_perimeter_alert"),
            "hud_callout": sc.get("hud_callout", ""),
            "metric_val": sc.get("metric_val", ""),
            "start": current_t,
            "end": current_t + dur
        })
        current_t += dur

    total_frames = int(math.ceil(total_duration * FPS))
    print(f"🚀 Rendering {total_frames} frames ({len(timed_scenes)} scenes, 1080x1920 @ {FPS} FPS)...")

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
            frame_im = render_phishing_frame(f, total_frames, script_data, total_duration, timed_scenes, timings_data)
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
    render_phishing_final()
