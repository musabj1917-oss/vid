#!/usr/bin/env python3
"""
render_chatgpt_sample.py - "How ChatGPT Actually Works Inside"
Sample video demonstrating the 3D pipeline on a new topic.

Strictly follows VIDEO_GUIDELINES.md:
- ONE metaphor: a glowing AI processing stack (transformer block tower)
- 10 scenes, cuts every 2-3s, 10+ visible cuts
- Truly 3D objects: transformer blocks, attention heads, token chips, neural pathways
- Moving parts every scene
- Proof beat: OpenAI paper citation
- CTA: @mwd1504
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
AUDIO_FILE = PIPELINE_DIR / "audio.mp3"

FONT_SANS_BOLD = "/data/data/com.termux/files/usr/share/fonts/TTF/DejaVuSans-Bold.ttf"
FONT_MONO_BOLD = "/data/data/com.termux/files/usr/share/fonts/TTF/DejaVuSansMono-Bold.ttf"
if not os.path.exists(FONT_SANS_BOLD):
    FONT_SANS_BOLD = "/system/fonts/Roboto-Regular.ttf"
if not os.path.exists(FONT_MONO_BOLD):
    FONT_MONO_BOLD = FONT_SANS_BOLD

font_hud_label = ImageFont.truetype(FONT_MONO_BOLD, 22)
font_hud_tab   = ImageFont.truetype(FONT_MONO_BOLD, 15)
font_hero_num  = ImageFont.truetype(FONT_SANS_BOLD, 92)
font_stat_num  = ImageFont.truetype(FONT_SANS_BOLD, 48)
font_hero_lbl  = ImageFont.truetype(FONT_MONO_BOLD, 22)
font_callout   = ImageFont.truetype(FONT_MONO_BOLD, 18)
font_caption   = ImageFont.truetype(FONT_SANS_BOLD, 46)
font_body      = ImageFont.truetype(FONT_SANS_BOLD, 22)
font_code      = ImageFont.truetype(FONT_MONO_BOLD, 18)
font_cta_btn   = ImageFont.truetype(FONT_SANS_BOLD, 42)
font_cta_sub   = ImageFont.truetype(FONT_MONO_BOLD, 26)
font_sm        = ImageFont.truetype(FONT_SANS_BOLD, 17)

W, H = 1080, 1920
FPS  = 30

C_BG      = (8, 10, 18, 255)
C_CYAN    = (0, 220, 255, 255)
C_VIOLET  = (140, 80, 255, 255)
C_AMBER   = (255, 176, 32, 255)
C_GOLD    = (255, 215, 0, 255)
C_GREEN   = (16, 220, 130, 255)
C_RED     = (255, 60, 90, 255)
C_WHITE   = (255, 255, 255, 255)
C_MUTED   = (140, 155, 175, 255)
C_PINK    = (255, 80, 180, 255)

SHOT_TIMELINE = [
    {"id": 1,  "name": "01 HOOK // TOKEN IN",    "start": 0.0,   "end": 2.8,   "dur": 2.8},
    {"id": 2,  "name": "02 TEARDOWN // STACK",   "start": 2.8,   "end": 5.6,   "dur": 2.8},
    {"id": 3,  "name": "03 EMBED // VECTORS",    "start": 5.6,   "end": 8.4,   "dur": 2.8},
    {"id": 4,  "name": "04 ATTENTION // HEADS",  "start": 8.4,   "end": 11.2,  "dur": 2.8},
    {"id": 5,  "name": "05 COUNTER // 96 LAYERS","start": 11.2,  "end": 14.0,  "dur": 2.8},
    {"id": 6,  "name": "06 FFN // NEURONS",      "start": 14.0,  "end": 17.0,  "dur": 3.0},
    {"id": 7,  "name": "07 PROOF // GPT-4 PAPER","start": 17.0,  "end": 20.5,  "dur": 3.5},
    {"id": 8,  "name": "08 SOFTMAX // NEXT TOKEN","start":20.5,  "end": 23.5,  "dur": 3.0},
    {"id": 9,  "name": "09 OUTPUT // WORD GEN",  "start": 23.5,  "end": 26.2,  "dur": 2.7},
    {"id": 10, "name": "10 CTA // @mwd1504",     "start": 26.2,  "end": 29.088,"dur": 2.888},
]

VOICEOVER_CHUNKS = [
    {"start": 0.0,   "end": 2.8,   "words": ["Your", "words", "enter", "as"], "word_starts": [0.0, 0.7, 1.4, 2.1]},
    {"start": 2.8,   "end": 5.6,   "words": ["tokens", "through", "96", "layers"], "word_starts": [2.8, 3.5, 4.2, 4.9]},
    {"start": 5.6,   "end": 8.4,   "words": ["each", "word", "becomes", "a"], "word_starts": [5.6, 6.3, 7.0, 7.7]},
    {"start": 8.4,   "end": 11.2,  "words": ["high-dimensional", "vector", "in", "space"], "word_starts": [8.4, 9.1, 9.8, 10.5]},
    {"start": 11.2,  "end": 14.0,  "words": ["attention", "heads", "scan", "context"], "word_starts": [11.2, 11.9, 12.6, 13.3]},
    {"start": 14.0,  "end": 17.0,  "words": ["96", "parallel", "processors", "fire"], "word_starts": [14.0, 14.75, 15.5, 16.25]},
    {"start": 17.0,  "end": 20.5,  "words": ["feed-forward", "networks", "refine", "meaning"], "word_starts": [17.0, 17.9, 18.8, 19.7]},
    {"start": 20.5,  "end": 23.5,  "words": ["softmax", "picks", "the", "next"], "word_starts": [20.5, 21.25, 22.0, 22.75]},
    {"start": 23.5,  "end": 26.2,  "words": ["token", "word", "by", "word"], "word_starts": [23.5, 24.2, 24.9, 25.6]},
    {"start": 26.2,  "end": 29.088,"words": ["Follow", "@mwd1504", "for", "more"], "word_starts": [26.2, 26.9, 27.6, 28.3]},
]

def get_audio_duration(audio_path):
    cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration",
           "-of", "default=noprint_wrappers=1:nokey=1", str(audio_path)]
    try:
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return float(res.stdout.strip())
    except Exception:
        return 29.088

def project_3d(x, y, z, cx=540, cy=960, yaw=0.0, pitch=20.0, roll=0.0, zoom=1.0, fov=900.0):
    yr = math.radians(yaw); pr = math.radians(pitch); rr = math.radians(roll)
    x1 = x*math.cos(yr) + z*math.sin(yr); y1 = y; z1 = -x*math.sin(yr) + z*math.cos(yr)
    x2 = x1; y2 = y1*math.cos(pr) - z1*math.sin(pr); z2 = y1*math.sin(pr) + z1*math.cos(pr)
    x3 = x2*math.cos(rr) - y2*math.sin(rr); y3 = x2*math.sin(rr) + y2*math.cos(rr); z3 = z2
    dist = max(40, fov - z3)
    s = (fov / dist) * zoom
    return (cx + x3*s, cy + y3*s)

def draw_hud(d, active_idx, scene_name, t):
    accent = C_VIOLET if active_idx % 2 == 0 else C_CYAN
    d.rounded_rectangle([50, 85, 1030, 175], radius=16,
                        fill=(10, 12, 22, 240), outline=(*accent[:3], 80), width=2)
    # Pulsing dot
    pulse = (math.sin(t * 6) + 1) * 0.5
    dot_col = tuple(int(c * (0.5 + pulse * 0.5)) for c in accent[:3]) + (255,)
    d.ellipse([82, 118, 98, 134], fill=dot_col)
    d.text((112, 118), f"GPT CORE // {scene_name}", font=font_hud_label, fill=(230, 240, 255, 255))
    # Step indicators
    for i in range(10):
        sx = 730 + i * 29
        is_cur = (i == active_idx)
        fill = accent if is_cur else (28, 35, 55, 160)
        outl = accent if is_cur else (60, 75, 100, 100)
        d.rounded_rectangle([sx, 120, sx+24, 142], radius=4, fill=fill, outline=outl, width=1)
        if is_cur:
            d.text((sx+6, 122), str(i+1), font=font_hud_tab, fill=(8, 10, 20, 255))

def draw_captions(d, t):
    active = None
    for chunk in VOICEOVER_CHUNKS:
        if chunk["start"] <= t <= chunk["end"]:
            active = chunk; break
        elif t < chunk["start"] and abs(t - chunk["start"]) < 0.2:
            active = chunk; break
    if not active:
        if t >= VOICEOVER_CHUNKS[-1]["start"]:
            active = VOICEOVER_CHUNKS[-1]
        else:
            return
    words = active["words"]; word_starts = active.get("word_starts", [])
    sp_w = font_caption.getbbox(" ")[2] - font_caption.getbbox(" ")[0]
    metrics = [(w, font_caption.getbbox(w)[2] - font_caption.getbbox(w)[0]) for w in words]
    total_w = sum(m[1] for m in metrics) + sp_w * (len(metrics) - 1)
    cur_x = (W - total_w) // 2; y_pos = 1640
    active_wi = -1
    for i, ws in enumerate(word_starts):
        if t >= ws: active_wi = i
    for i, (w, ww) in enumerate(metrics):
        is_a = (i == active_wi)
        if is_a:
            for dx, dy in [(-2,0),(2,0),(0,-2),(0,2)]:
                d.text((cur_x+dx, y_pos+dy), w, font=font_caption, fill=(0,0,0,220))
            d.text((cur_x, y_pos), w, font=font_caption, fill=C_GOLD)
            d.rounded_rectangle([cur_x-2, y_pos+56, cur_x+ww+2, y_pos+61], radius=2, fill=C_AMBER)
        else:
            d.text((cur_x+2, y_pos+2), w, font=font_caption, fill=(0,0,0,160))
            d.text((cur_x, y_pos), w, font=font_caption, fill=C_WHITE)
        cur_x += ww + sp_w

def draw_callout(d, target, box_center, text, accent=None):
    if accent is None: accent = C_CYAN
    d.ellipse([target[0]-4, target[1]-4, target[0]+4, target[1]+4], fill=accent)
    d.ellipse([target[0]-8, target[1]-8, target[0]+8, target[1]+8], outline=accent, width=1)
    bbox = font_callout.getbbox(text)
    bw = bbox[2]-bbox[0]+26; bh = 36
    bx = box_center[0]-bw//2; by = box_center[1]-bh//2
    edge_x = bx+bw if target[0] > bx+bw//2 else bx
    mid_x = (target[0]+edge_x)//2
    d.line([target, (mid_x, box_center[1]), (edge_x, box_center[1])], fill=accent, width=2)
    d.rounded_rectangle([bx, by, bx+bw, by+bh], radius=8, fill=(12,15,28,240), outline=accent, width=1)
    d.text((bx+13, by+8), text, font=font_callout, fill=C_WHITE)

def draw_transformer_block(d, cx, cy, w, h, depth, yaw, pitch, zoom, color=None, label=""):
    """Draw a lit 3D hardware accelerator / transformer module with depth shading and circuit details."""
    if color is None: color = C_VIOLET
    hw, hh, hd = w/2, h/2, depth/2
    corners = [(-hw,-hh,hd),(hw,-hh,hd),(hw,hh,hd),(-hw,hh,hd),
               (-hw,-hh,-hd),(hw,-hh,-hd),(hw,hh,-hd),(-hw,hh,-hd)]
    pts = [project_3d(x+cx, y+cy, z, 540, 960, yaw, pitch, 0.0, zoom) for x,y,z in corners]
    r,g,b = color[:3]

    # Contact shadow under block
    sh_pts = [project_3d(x+cx, y+cy+25, -hd-15, 540, 960, yaw, pitch, 0.0, zoom)
              for x,y in [(-hw-20,-hh), (hw+20,-hh), (hw+20,hh+20), (-hw-20,hh+20)]]
    d.polygon(sh_pts, fill=(4, 6, 14, 160))

    # Back face
    d.polygon([pts[4],pts[5],pts[6],pts[7]], fill=(r//6, g//6, b//6, 220), outline=(*color[:3],50), width=1)
    # Bottom face
    d.polygon([pts[3],pts[2],pts[6],pts[7]], fill=(r//5, g//5, b//5+8, 240), outline=(*color[:3],80), width=1)
    # Right face
    d.polygon([pts[1],pts[5],pts[6],pts[2]], fill=(r//4+10, g//4+10, b//4+10, 240), outline=(*color[:3],90), width=1)
    # Left face
    d.polygon([pts[0],pts[4],pts[7],pts[3]], fill=(r//5+5, g//5+5, b//5+12, 240), outline=(*color[:3],70), width=1)
    # Top face
    d.polygon([pts[0],pts[1],pts[5],pts[4]], fill=(min(255, r//2+40), min(255, g//2+40), min(255, b//2+40), 250), outline=(*color[:3],160), width=2)
    # Front face
    d.polygon([pts[0],pts[1],pts[2],pts[3]], fill=(20, 24, 40, 245), outline=color, width=3)

    p0, p1, p2, p3 = pts[0], pts[1], pts[2], pts[3]
    # Gold edge contacts on left rail
    for frac in [0.2, 0.35, 0.5, 0.65, 0.8]:
        lx = p0[0] + (p3[0] - p0[0]) * frac
        ly = p0[1] + (p3[1] - p0[1]) * frac
        d.line([(lx+8, ly), (lx+28, ly)], fill=C_GOLD, width=3)

    # Status LED cluster on right
    for frac, led_col in [(0.25, C_GREEN), (0.45, C_CYAN), (0.65, C_AMBER)]:
        rx = p1[0] + (p2[0] - p1[0]) * frac
        ry = p1[1] + (p2[1] - p1[1]) * frac
        d.ellipse([rx-18, ry-5, rx-8, ry+5], fill=led_col)

    # Label on front face
    if label:
        mx = (p0[0]+p1[0]+p2[0]+p3[0])/4
        my = (p0[1]+p1[1]+p2[1]+p3[1])/4
        bbox = font_callout.getbbox(label)
        lw = bbox[2]-bbox[0]
        d.rounded_rectangle([mx-lw//2-14, my-16, mx+lw//2+14, my+18], radius=6,
                            fill=(14, 18, 32, 220), outline=(*color[:3], 120), width=1)
        d.text((mx-lw//2, my-10), label, font=font_callout, fill=C_WHITE)

def draw_token_chip(d, x, y, label="TOKEN", color=None, size=70):
    """Draw a labeled silicon token chip."""
    if color is None: color = C_CYAN
    half = size//2
    d.rounded_rectangle([x-half, y-half, x+half, y+half], radius=10,
                        fill=(14,18,32,255), outline=color, width=2)
    # Glow inner
    d.rounded_rectangle([x-half+4, y-half+4, x+half-4, y+half-4], radius=7,
                        fill=(20,26,45,255), outline=(*color[:3],100), width=1)
    # Pins
    for px_off in [-22, -8, 8, 22]:
        d.rectangle([x+px_off-3, y-half-7, x+px_off+3, y-half], fill=(190,210,230,255))
        d.rectangle([x+px_off-3, y+half, x+px_off+3, y+half+7], fill=(190,210,230,255))
    bbox = font_hud_tab.getbbox(label)
    lw = bbox[2]-bbox[0]
    d.text((x-lw//2, y-9), label, font=font_hud_tab, fill=color)

def draw_attention_head(d, cx, cy, radius, angle_offset, label, t, color=None):
    """Draw a rotating attention head cylinder with arc sweeps."""
    if color is None: color = C_VIOLET
    # Outer ring
    d.ellipse([cx-radius, cy-radius, cx+radius, cy+radius], outline=(*color[:3],60), width=3)
    # Sweeping arc
    sweep = int(((t * 90 + angle_offset) % 360))
    d.arc([cx-radius, cy-radius, cx+radius, cy+radius], start=sweep, end=sweep+120, fill=color, width=4)
    # Inner dot
    d.ellipse([cx-8, cy-8, cx+8, cy+8], fill=color)
    # Label
    bbox = font_sm.getbbox(label)
    lw = bbox[2]-bbox[0]
    d.text((cx-lw//2, cy+radius+8), label, font=font_sm, fill=color)

def draw_neural_beam(d, x1, y1, x2, y2, progress, color=None, width=3):
    """Animated data beam along a path."""
    if color is None: color = C_CYAN
    # Static backbone
    d.line([(x1,y1),(x2,y2)], fill=(*color[:3],50), width=1)
    # Moving segment
    px = x1 + (x2-x1)*progress
    py = y1 + (y2-y1)*progress
    head_len = 0.15
    hx = x1 + (x2-x1)*max(0,progress-head_len)
    hy = y1 + (y2-y1)*max(0,progress-head_len)
    d.line([(int(hx),int(hy)),(int(px),int(py))], fill=color, width=width)
    # Particle dot
    d.ellipse([px-5, py-5, px+5, py+5], fill=color)

def draw_progress_bar(d, t, total, active_idx):
    progress = min(1.0, t / max(1.0, total))
    d.rounded_rectangle([80, 1790, 1000, 1798], radius=4, fill=(25,32,52,160))
    bar_w = int(920 * progress)
    if bar_w > 0:
        col = C_GOLD if active_idx == 9 else C_VIOLET
        d.rounded_rectangle([80, 1790, 80+bar_w, 1798], radius=4, fill=col)

# ─────────────────────────── AMBIENT BACKGROUND ───────────────────────────

def draw_bg(im, t, yaw, pitch, zoom):
    d = ImageDraw.Draw(im)
    # Radial spotlight
    spot = Image.new("RGBA", (W,H), (0,0,0,0))
    sd = ImageDraw.Draw(spot)
    sd.ellipse([-200,300,1280,1680], fill=(18,22,45,120))
    sd.ellipse([80,480,1000,1440], fill=(26,30,60,80))
    im.alpha_composite(spot)
    d = ImageDraw.Draw(im)
    # Grid
    gc = (20,30,55,70)
    for gy in range(300, 1700, 110):
        d.line([(40,gy),(1040,gy)], fill=gc, width=1)
    for gx in range(80, 1040, 130):
        d.line([(gx,290),(gx,1700)], fill=gc, width=1)
    # Animated diagonal accent lines
    phase = (t * 40) % 220
    for i in range(5):
        ox = int(phase + i*220)
        d.line([(ox,290),(ox+180,1700)], fill=(30,45,90,30), width=1)

# ───────────────────────────── SCENE RENDERS ──────────────────────────────

def render_frame(frame_idx, total_frames, total_duration):
    t = frame_idx / float(FPS)
    progress = min(1.0, t / max(1.0, total_duration))

    active_idx = 0
    for idx, sc in enumerate(SHOT_TIMELINE):
        if sc["start"] <= t <= sc["end"]: active_idx = idx; break
        elif t > sc["end"]: active_idx = idx

    shot = SHOT_TIMELINE[active_idx]
    shot_dur = shot["dur"]
    relt = max(0.0, min(1.0, (t - shot["start"]) / shot_dur))
    pulse = (math.sin(t * 7.0) + 1.0) * 0.5
    pulse2 = (math.sin(t * 4.5 + 1.2) + 1.0) * 0.5

    im = Image.new("RGBA", (W,H), C_BG)
    yaw = 0.0; pitch = 20.0; zoom = 1.0  # defaults

    # ── Scene 1: HOOK — Token chip macro push-in ──────────────────────────
    if shot["id"] == 1:
        yaw   = -8.0 + relt*6.0
        pitch = 18.0 - relt*5.0
        zoom  = 1.18 + relt*0.22
        draw_bg(im, t, yaw, pitch, zoom)
        d = ImageDraw.Draw(im)

        # Giant glowing processor block
        draw_transformer_block(d, 0, 40, 520, 920, 70, yaw, pitch, zoom,
                               color=C_VIOLET, label="GPT-4 SILICON ENCLAVE")

        # Token chip entering smoothly from y=220 down to y=520
        chip_y = int(220 + relt * 300)
        draw_token_chip(d, 540, chip_y, "\"Hello\"", C_CYAN, size=94)
        # Glowing neural beam into processor
        beam_prog = min(1.0, relt * 1.3)
        draw_neural_beam(d, 540, chip_y+50, 540, 680, beam_prog, C_CYAN, 4)

        # Non-overlapping precision callouts
        draw_callout(d, (720, 780), (880, 480), "175B PARAMETERS", C_VIOLET)
        draw_callout(d, (360, 840), (160, 500), "TOKENIZER LAYER", C_CYAN)

        # Shock hook banner
        d.rounded_rectangle([80, 1480, 1000, 1550], radius=14,
                            fill=(30,20,55,210), outline=C_VIOLET, width=2)
        d.text((120, 1497), "⚡ 175 BILLION WEIGHTS — IN ONE FORWARD PASS", font=font_callout, fill=C_VIOLET)

    # ── Scene 2: TEARDOWN — Transformer stack exploded ───────────────────
    elif shot["id"] == 2:
        yaw   = 28.0 - relt*16.0
        pitch = 30.0 - relt*8.0
        zoom  = 1.08 + relt*0.12
        draw_bg(im, t, yaw, pitch, zoom)
        d = ImageDraw.Draw(im)

        # Stack of 5 transformer blocks sliding apart (filling >60% frame)
        block_colors = [C_VIOLET, C_CYAN, C_PINK, C_VIOLET, C_CYAN]
        block_labels = [
            "01 EMBED // INPUT",
            "02 MULTI-HEAD ATTENTION",
            "03 FEED-FORWARD (FFN)",
            "04 LAYER NORM // RESIDUAL",
            "05 SOFTMAX // OUTPUT"
        ]
        base_y = 660
        for i, (col, lbl) in enumerate(zip(block_colors, block_labels)):
            sep = relt * 35 * i
            block_cy = base_y + i * 140 + sep
            draw_transformer_block(d, 0, block_cy-960, 540, 100, 38, yaw, pitch, zoom,
                                   color=col, label=lbl)

        # Precision callouts pointing to distinct blocks
        draw_callout(d, (720, 520), (880, 400), "96 LAYERS DEEP", C_VIOLET)
        draw_callout(d, (340, 800), (160, 680), "RESIDUAL STREAM", C_CYAN)
        draw_callout(d, (720, 1060), (880, 940), "ATTENTION HEADS", C_PINK)

    # ── Scene 3: EMBED — Token → vector in high-dim space ────────────────
    elif shot["id"] == 3:
        yaw   = -20.0 + relt*14.0
        pitch = 42.0 + relt*8.0
        zoom  = 1.12 + relt*0.14
        draw_bg(im, t, yaw, pitch, zoom)
        d = ImageDraw.Draw(im)

        # Embedding matrix: grid of glowing dots
        grid_x, grid_y = 540, 870
        cols_n, rows_n = 12, 16
        dot_spacing = 68
        total_grid_w = (cols_n-1)*dot_spacing
        total_grid_h = (rows_n-1)*dot_spacing
        for row in range(rows_n):
            for col in range(cols_n):
                dx = grid_x - total_grid_w//2 + col*dot_spacing
                dy = grid_y - total_grid_h//2 + row*dot_spacing
                # Animated brightness wave
                wave = (math.sin(t*4 + col*0.5 + row*0.3) + 1)*0.5
                heat = int(80 + wave * 170)
                r_col = (heat//3, heat//4, heat, 200) if col % 3 != 0 else (heat, heat//5, heat//2, 200)
                d.ellipse([dx-5, dy-5, dx+5, dy+5], fill=r_col)

        # Highlighted vector column (token being embedded)
        active_col = int((relt * 0.8) * cols_n) % cols_n
        for row in range(rows_n):
            dx = grid_x - total_grid_w//2 + active_col*dot_spacing
            dy = grid_y - total_grid_h//2 + row*dot_spacing
            d.ellipse([dx-9, dy-9, dx+9, dy+9], fill=C_GOLD)
            d.ellipse([dx-5, dy-5, dx+5, dy+5], fill=C_WHITE)

        # Token chip above grid
        draw_token_chip(d, 540, 460, "\"Hello\"", C_CYAN, size=78)
        # Beam from token to highlighted column
        draw_neural_beam(d, 540, 500, grid_x-total_grid_w//2+active_col*dot_spacing, grid_y-total_grid_h//2, relt, C_GOLD, 3)

        draw_callout(d, (540, 820), (170, 600), "12,288-DIM VECTOR", C_GOLD)
        draw_callout(d, (820, 950), (900, 700), "POSITION ENCODING", C_CYAN)

    # ── Scene 4: ATTENTION — Multi-head attention rings ───────────────────
    elif shot["id"] == 4:
        yaw   = 15.0 - relt*20.0
        pitch = 25.0 + relt*5.0
        zoom  = 1.08 + relt*0.16
        draw_bg(im, t, yaw, pitch, zoom)
        d = ImageDraw.Draw(im)

        # Central query box
        d.rounded_rectangle([380, 790, 700, 920], radius=16,
                            fill=(22,16,46,245), outline=C_VIOLET, width=3)
        d.text((430, 820), "QUERY", font=font_hud_label, fill=C_VIOLET)
        d.text((415, 855), "\"Hello\" context", font=font_sm, fill=C_MUTED)

        # 8 attention heads arranged in arc
        head_configs = [
            (280,  620, 68, 0,    "H1"),
            (430,  540, 60, 45,   "H2"),
            (600,  520, 65, 90,   "H3"),
            (760,  570, 62, 135,  "H4"),
            (820,  720, 68, 180,  "H5"),
            (770,  880, 60, 225,  "H6"),
            (620,  980, 65, 270,  "H7"),
            (340,  970, 62, 315,  "H8"),
        ]
        head_colors = [C_VIOLET, C_CYAN, C_PINK, C_VIOLET, C_CYAN, C_GREEN, C_VIOLET, C_CYAN]
        for (hx, hy, hr, ang, hlbl), hcol in zip(head_configs, head_colors):
            draw_attention_head(d, hx, hy, hr, ang, hlbl, t, hcol)
            # Beam from each head to central query
            beam_p = (relt + ang/360) % 1.0
            draw_neural_beam(d, hx, hy, 540, 855, beam_p, (*hcol[:3], 180), 2)

        draw_callout(d, (280, 620), (160, 400), "96 HEADS TOTAL", C_VIOLET)
        draw_callout(d, (820, 720), (900, 500), "PARALLEL SCAN", C_CYAN)

    # ── Scene 5: COUNTER — 96 layers stat ─────────────────────────────────
    elif shot["id"] == 5:
        yaw   = -35.0 + relt*70.0
        pitch = 30.0
        zoom  = 1.02
        draw_bg(im, t, yaw, pitch, zoom)
        d = ImageDraw.Draw(im)

        # Counter card in upper HUD zone (never covers main object)
        card_y = 210
        d.rounded_rectangle([140, card_y, 940, card_y+220], radius=24,
                            fill=(14,12,30,245), outline=C_VIOLET, width=3)
        # Radial sweep gauge
        arc_cx, arc_cy = 280, card_y+110
        d.ellipse([arc_cx-75, arc_cy-75, arc_cx+75, arc_cy+75], outline=(40,30,70,255), width=8)
        sweep = int(min(1.0, relt*1.4) * 260)
        d.arc([arc_cx-75, arc_cy-75, arc_cx+75, arc_cy+75], start=-90, end=-90+sweep, fill=C_VIOLET, width=10)
        # Icon in arc center
        d.text((arc_cx-16, arc_cy-16), "⚡", font=font_hud_label, fill=C_GOLD)

        # Big counter number and label (zero overlap)
        d.text((410, card_y+30), "96", font=font_hero_num, fill=C_VIOLET)
        d.text((580, card_y+55), "LAYERS", font=font_hud_label, fill=C_AMBER)
        d.text((415, card_y+145), "TRANSFORMER DEPTH: 96 LAYERS", font=font_hero_lbl, fill=C_WHITE)

        # Orbiting transformer stack below
        draw_transformer_block(d, 0, 100, 480, 800, 50, yaw, pitch, zoom, C_VIOLET, "GPT-4 ENCLAVE")
        draw_callout(d, (540, 1200), (880, 700), "1 PASS = 96 TRANSFORMS", C_VIOLET)

    # ── Scene 6: FFN — Feed-forward neuron layer ───────────────────────────
    elif shot["id"] == 6:
        yaw   = 12.0 + relt*14.0
        pitch = 22.0 - relt*6.0
        zoom  = 1.05 + relt*0.12
        draw_bg(im, t, yaw, pitch, zoom)
        d = ImageDraw.Draw(im)

        # FFN: two-layer neural network visualization
        # Input layer (left)
        in_nodes  = [(200, 480), (200, 640), (200, 800), (200, 960), (200, 1120)]
        # Hidden layer (middle) — 4x wider in GPT-4
        hid_nodes = [(540, 380), (540, 560), (540, 740), (540, 920), (540, 1100), (540, 1280)]
        # Output layer (right)
        out_nodes = [(880, 480), (880, 640), (880, 800), (880, 960), (880, 1120)]

        # Draw connections with animated beams
        for i, inp in enumerate(in_nodes):
            for j, hid in enumerate(hid_nodes):
                alpha = int(30 + 20 * math.sin(t*3 + i + j))
                d.line([inp, hid], fill=(140,80,255,alpha), width=1)
        for i, hid in enumerate(hid_nodes):
            for j, out in enumerate(out_nodes):
                alpha = int(30 + 20 * math.sin(t*3 + i + j + 2))
                d.line([hid, out], fill=(0,200,255,alpha), width=1)

        # Moving data beams
        for i, inp in enumerate(in_nodes):
            for j, hid in enumerate(hid_nodes[:2]):
                bp = (relt + (i*0.2 + j*0.1)) % 1.0
                draw_neural_beam(d, inp[0], inp[1], hid[0], hid[1], bp, C_VIOLET, 2)
        for i, hid in enumerate(hid_nodes[:3]):
            for j, out in enumerate(out_nodes[:2]):
                bp = (relt + (i*0.15 + j*0.1) + 0.3) % 1.0
                draw_neural_beam(d, hid[0], hid[1], out[0], out[1], bp, C_CYAN, 2)

        # Node circles
        for nx, ny in in_nodes:
            glow = int(140 + pulse*115)
            d.ellipse([nx-20, ny-20, nx+20, ny+20], fill=(glow//3,glow//6,glow,230), outline=C_VIOLET, width=2)
        for nx, ny in hid_nodes:
            glow = int(140 + pulse2*115)
            d.ellipse([nx-24, ny-24, nx+24, ny+24], fill=(glow//4,glow//5,glow//2+40,230), outline=C_PINK, width=2)
        for nx, ny in out_nodes:
            glow = int(100 + pulse*155)
            d.ellipse([nx-20, ny-20, nx+20, ny+20], fill=(glow//5,glow//3,glow//2,230), outline=C_CYAN, width=2)

        draw_callout(d, (200, 640), (140, 390), "INPUT: d=12288", C_VIOLET)
        draw_callout(d, (880, 640), (900, 380), "OUTPUT: d=12288", C_CYAN)
        draw_callout(d, (540, 560), (600, 320), "HIDDEN: d=49152", C_PINK)

    # ── Scene 7: PROOF — GPT-4 technical report ───────────────────────────
    elif shot["id"] == 7:
        yaw   = -18.0 + relt*10.0
        pitch = 20.0
        zoom  = 0.94
        draw_bg(im, t, yaw, pitch, zoom)
        d = ImageDraw.Draw(im)

        # Faint block in background
        draw_transformer_block(d, 150, 80, 360, 600, 44, yaw+15, pitch+10, zoom*0.75, C_VIOLET)

        # Proof card
        cw, ch = 880, 600
        cx2, cy2 = (W-cw)//2, 400
        d.rounded_rectangle([cx2, cy2, cx2+cw, cy2+ch], radius=28,
                            fill=(12,14,28,248), outline=C_VIOLET, width=3)

        # Header
        d.text((cx2+40, cy2+36), "📄 GPT-4 TECHNICAL REPORT", font=font_body, fill=C_WHITE)
        d.text((cx2+40, cy2+68), "OpenAI  •  arXiv:2303.08774  •  2023", font=font_sm, fill=C_MUTED)
        d.line([(cx2+40, cy2+100), (cx2+cw-40, cy2+100)], fill=(*C_VIOLET[:3],80), width=1)

        # Key stats in 3 distinct cards (zero overlap guaranteed)
        col_w = 244
        for i, (val, lbl, col) in enumerate([
            ("175B+", "Parameters (est.)", C_VIOLET),
            ("96",    "Transformer Layers", C_CYAN),
            ("12,288","Model Dimension d", C_PINK)
        ]):
            box_x = cx2 + 40 + i * (col_w + 34)
            box_y = cy2 + 130
            d.rounded_rectangle([box_x, box_y, box_x + col_w, box_y + 140], radius=16,
                                fill=(18, 22, 44, 230), outline=(*col[:3], 140), width=2)
            d.text((box_x + 20, box_y + 24), val, font=font_stat_num, fill=col)
            d.text((box_x + 20, box_y + 90), lbl, font=font_sm, fill=C_MUTED)

        # Quote box
        d.rounded_rectangle([cx2+36, cy2+430, cx2+cw-36, cy2+555], radius=12,
                            fill=(22,18,45,255), outline=C_AMBER, width=1)
        quote = '"GPT-4 is a large multimodal model... achieves human-level'
        quote2 = 'performance on various professional and academic benchmarks"'
        d.text((cx2+56, cy2+452), quote,  font=font_sm, fill=C_AMBER)
        d.text((cx2+56, cy2+480), quote2, font=font_sm, fill=C_AMBER)
        d.text((cx2+56, cy2+512), "— OpenAI GPT-4 Technical Report, 2023", font=font_sm, fill=C_MUTED)

    # ── Scene 8: SOFTMAX — Probability distribution next token ────────────
    elif shot["id"] == 8:
        yaw   = 20.0 - relt*25.0
        pitch = 28.0 + relt*4.0
        zoom  = 1.10 + relt*0.08
        draw_bg(im, t, yaw, pitch, zoom)
        d = ImageDraw.Draw(im)

        # Token candidates with animated probability bars
        tokens = [
            ("world",  0.42, C_GOLD),
            ("there",  0.26, C_CYAN),
            ("GPT",    0.15, C_VIOLET),
            ("friend", 0.10, C_GREEN),
            ("AI",     0.07, C_PINK),
        ]
        bar_x, bar_y = 160, 440
        bar_max_w = 700
        d.rounded_rectangle([130, 400, 950, 1200], radius=20,
                            fill=(12,15,30,240), outline=C_VIOLET, width=2)
        d.text((bar_x, 418), "SOFTMAX OUTPUT — NEXT TOKEN PROBABILITIES", font=font_sm, fill=C_VIOLET)
        for i, (tok, prob, col) in enumerate(tokens):
            ty = bar_y + i * 140
            # Animated bar fill
            anim_w = int(bar_max_w * prob * min(1.0, relt * 2.5))
            d.rounded_rectangle([bar_x, ty, bar_x+bar_max_w, ty+90], radius=10,
                                fill=(20,25,45,200), outline=(*col[:3],60), width=1)
            if anim_w > 0:
                d.rounded_rectangle([bar_x, ty, bar_x+anim_w, ty+90], radius=10, fill=(*col[:3],200))
            # Token label
            d.text((bar_x+16, ty+22), f'"{tok}"', font=font_hud_label, fill=C_WHITE)
            # Probability
            prob_str = f"{prob*100:.0f}%"
            bbox = font_hero_lbl.getbbox(prob_str)
            pw = bbox[2]-bbox[0]
            d.text((bar_x+bar_max_w-pw-10, ty+28), prob_str, font=font_hero_lbl, fill=col)

        # Winning token highlight
        draw_callout(d, (bar_x+int(bar_max_w*0.42)//2, bar_y+45), (160, 300), "WINNER: \"world\"", C_GOLD)
        draw_callout(d, (bar_x+bar_max_w, bar_y+500), (900, 320), "ARGMAX SELECTION", C_VIOLET)

    # ── Scene 9: OUTPUT — Word-by-word generation ─────────────────────────
    elif shot["id"] == 9:
        yaw   = 18.0 - relt*22.0
        pitch = 24.0
        zoom  = 1.08 + relt*0.10
        draw_bg(im, t, yaw, pitch, zoom)
        d = ImageDraw.Draw(im)

        # Output stream
        generated = ["Hello", "world!", "This", "is", "GPT-4"]
        full_shown = int(relt * len(generated) * 1.3)

        # Terminal-style output box
        term_x, term_y, term_w, term_h = 100, 460, 880, 520
        d.rounded_rectangle([term_x, term_y, term_x+term_w, term_y+term_h], radius=18,
                            fill=(8,12,22,255), outline=C_GREEN, width=3)
        d.rounded_rectangle([term_x+6, term_y+6, term_x+term_w-6, term_y+28], radius=12,
                            fill=(14,20,38,255), outline=(30,40,60,255), width=1)
        d.text((term_x+16, term_y+8), "● ● ●  GPT-4 OUTPUT STREAM", font=font_sm, fill=C_MUTED)

        # Prompt line
        d.text((term_x+24, term_y+52), "> prompt: \"Say hello to the world\"", font=font_code, fill=C_MUTED)
        d.line([(term_x+24, term_y+88), (term_x+term_w-24, term_y+88)], fill=(*C_GREEN[:3],50), width=1)

        # Generated words appearing one by one
        cur_x = term_x + 24
        cur_y = term_y + 112
        for i, word in enumerate(generated):
            if i >= full_shown: break
            is_latest = (i == full_shown-1)
            col = C_GOLD if is_latest else C_WHITE
            d.text((cur_x, cur_y), word, font=font_hud_label, fill=col)
            bbox = font_hud_label.getbbox(word)
            cur_x += bbox[2]-bbox[0] + 14

        # Blinking cursor
        if int(t * 3) % 2 == 0:
            d.rectangle([cur_x, cur_y, cur_x+3, cur_y+28], fill=C_GREEN)

        # Token count meter
        token_count = int(relt * 892)
        d.text((term_x+24, term_y+term_h-100), f"TOKENS GENERATED: {token_count}", font=font_code, fill=C_CYAN)
        d.text((term_x+24, term_y+term_h-68),  "LATENCY: 0.014s / TOKEN",           font=font_code, fill=C_MUTED)
        d.text((term_x+24, term_y+term_h-36),  "TEMP: 0.7  TOP-P: 0.95  MAX: 4096", font=font_code, fill=C_MUTED)

        draw_callout(d, (term_x+440, term_y+112), (880, 350), "AUTOREGRESSIVE OUT", C_GREEN)
        draw_callout(d, (term_x+24, term_y+term_h-80), (160, 300), "SUB-WORD TOKENS", C_CYAN)

    # ── Scene 10: CTA ──────────────────────────────────────────────────────
    else:
        yaw   = 15.0 - relt*18.0
        pitch = 22.0
        zoom  = 1.02
        draw_bg(im, t, yaw, pitch, zoom)
        d = ImageDraw.Draw(im)

        # Faint block backdrop
        draw_transformer_block(d, 0, 100, 440, 850, 50, yaw, pitch, zoom, C_VIOLET)

        # CTA card in upper frame
        cta_y = 215
        d.rounded_rectangle([140, cta_y, 940, cta_y+280], radius=28,
                            fill=(12,14,30,245), outline=C_GOLD, width=3)

        btn_y = cta_y + 36
        d.rounded_rectangle([180, btn_y, 900, btn_y+92], radius=18,
                            fill=(16, 220, 130, 255), outline=C_GOLD, width=3)
        label_str = "FOLLOW FOR AI BREAKDOWNS"
        bbox = font_cta_btn.getbbox(label_str)
        bw = bbox[2]-bbox[0]
        d.text(((W-bw)//2, btn_y+24), label_str, font=font_cta_btn, fill=(10, 14, 24, 255))

        h_str = "@mwd1504"
        hb = font_cta_sub.getbbox(h_str)
        hx = (W-(hb[2]-hb[0]))//2
        d.text((hx, cta_y+152), h_str, font=font_cta_sub, fill=C_CYAN)
        # Verified badge
        d.ellipse([hx+(hb[2]-hb[0])+14, cta_y+157, hx+(hb[2]-hb[0])+34, cta_y+177], fill=C_CYAN)
        d.text((hx+(hb[2]-hb[0])+18, cta_y+155), "✓", font=font_hud_tab, fill=(8,10,20,255))

        sub = "New AI & Tech Deep-Dives Every Week"
        sb = font_body.getbbox(sub)
        d.text(((W-(sb[2]-sb[0]))//2, cta_y+218), sub, font=font_body, fill=C_MUTED)

    # ── Shared HUD, captions, progress ────────────────────────────────────
    d = ImageDraw.Draw(im)
    draw_hud(d, active_idx, shot["name"], t)
    draw_captions(d, t)
    draw_progress_bar(d, t, total_duration, active_idx)

    return im.convert("RGBA")

# ─────────────────────────── RENDER ENTRY POINT ───────────────────────────

def render_keyframe_previews():
    kf_dir = PIPELINE_DIR / "keyframes"
    kf_dir.mkdir(parents=True, exist_ok=True)
    total_duration = get_audio_duration(AUDIO_FILE)
    total_frames = int(math.ceil(total_duration * FPS))
    print("📸 Generating ChatGPT sample keyframes...")
    for sc in SHOT_TIMELINE:
        mid_t = sc["start"] + sc["dur"] * 0.5
        f_idx = min(total_frames-1, int(mid_t * FPS))
        frame = render_frame(f_idx, total_frames, total_duration)
        out = kf_dir / f"chatgpt_shot_{sc['id']}.png"
        frame.save(out)
        print(f"  ✓ {out}")

def render_final_video():
    out_path = OUTPUT_DIR / "ChatGPT_How_It_Works.mp4"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    total_duration = get_audio_duration(AUDIO_FILE)
    total_frames = int(math.ceil(total_duration * FPS))
    print(f"🎵 Audio: {total_duration:.3f}s")
    print(f"🚀 Rendering {total_frames} frames (10 shots, {W}x{H} @ {FPS}fps)...")

    cmd = [
        "ffmpeg", "-y",
        "-f", "rawvideo", "-pix_fmt", "rgba",
        "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
        "-i", str(AUDIO_FILE),
        "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-shortest",
        str(out_path)
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)

    try:
        for f in range(total_frames):
            frame_im = render_frame(f, total_frames, total_duration)
            proc.stdin.write(frame_im.tobytes())
            if f % (FPS * 3) == 0:
                print(f"  ⚡ {f}/{total_frames} ({f/total_frames*100:.1f}%)...")
        proc.stdin.close()
    except Exception as e:
        proc.kill()
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    _, stderr = proc.communicate()
    if proc.returncode != 0:
        print(f"FFmpeg:\n{stderr.decode('utf-8', errors='ignore')}", file=sys.stderr)
        sys.exit(1)

    size = os.path.getsize(out_path)
    print(f"✅ Rendered: {out_path} ({size:,} bytes)")

    dl = Path("/sdcard/Download")
    if dl.exists():
        dest = dl / "ChatGPT_How_It_Works.mp4"
        shutil.copyfile(out_path, dest)
        print(f"📲 Synced to Downloads: {dest}")

if __name__ == "__main__":
    if "--keyframes" in sys.argv:
        render_keyframe_previews()
    else:
        render_keyframe_previews()
        render_final_video()
