#!/usr/bin/env python3
"""
test_brief_shots.py - Test and preview all 10 shots from PHISHING_VIDEO_BRIEF.md
"""

import os
import math
from PIL import Image, ImageDraw, ImageFont

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
font_caption = ImageFont.truetype(FONT_SANS_BOLD, 44)
font_proof_title = ImageFont.truetype(FONT_SANS_BOLD, 26)
font_proof_body = ImageFont.truetype(FONT_SANS_BOLD, 21)
font_proof_stat = ImageFont.truetype(FONT_MONO_BOLD, 18)
font_cta_btn = ImageFont.truetype(FONT_SANS_BOLD, 44)
font_cta_sub = ImageFont.truetype(FONT_MONO_BOLD, 26)
font_ui_time = ImageFont.truetype(FONT_SANS_BOLD, 36)
font_ui_sm = ImageFont.truetype(FONT_MONO_BOLD, 16)
font_ui_bold = ImageFont.truetype(FONT_SANS_BOLD, 22)

W, H = 1080, 1920

# Colors
C_BG = (12, 14, 22, 255)
C_DESK = (20, 24, 36, 255)
C_CYAN = (0, 242, 254, 255)
C_AMBER = (255, 176, 32, 255)
C_GOLD = (255, 215, 0, 255)
C_RED = (255, 45, 85, 255)
C_EMERALD = (16, 185, 129, 255)
C_WHITE = (255, 255, 255, 255)
C_MUTED = (148, 163, 184, 255)

def project_perspective(x, y, z, cx=540, cy=960, yaw=0.0, pitch=25.0, zoom=1.0, fov=800.0):
    """
    True 3D perspective camera projection.
    yaw: camera rotation around Y/Z axis in degrees
    pitch: tilt elevation in degrees
    """
    yaw_rad = math.radians(yaw)
    pitch_rad = math.radians(pitch)

    # Yaw rotation
    x1 = x * math.cos(yaw_rad) - y * math.sin(yaw_rad)
    y1 = x * math.sin(yaw_rad) + y * math.cos(yaw_rad)
    z1 = z

    # Pitch tilt
    cos_p = math.cos(pitch_rad)
    sin_p = math.sin(pitch_rad)
    y2 = y1 * cos_p - z1 * sin_p
    z2 = y1 * sin_p + z1 * cos_p

    # Perspective division
    dist = fov + y2 * 0.4
    if dist < 10:
        dist = 10
    scale = (fov / dist) * zoom

    sx = cx + x1 * scale
    sy = cy - z2 * scale
    return (sx, sy)

print("Project perspective defined.")
