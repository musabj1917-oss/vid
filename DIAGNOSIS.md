# Why the current video is not up to standard

Audited `render_brief_phishing_v2.py` (the main phishing renderer) against
`VIDEO_GUIDELINES.md` / `VIDEO_QUALITY_GUIDELINES.md`, and rendered its
10 keyframes to look at them directly (`.pipeline/keyframes_preview/`).

## Root cause (the big one)

**The renderer is 2D vector drawing (PIL `ImageDraw`), not 3D.**
Every "3D" object is flat-shaded polygons with a cyan outline. PIL cannot
produce PBR materials, specular highlights, glass reflections, soft shadows,
depth of field, motion blur or bloom — which is exactly what makes
inspiration videos look premium. No amount of tuning PIL closes that gap;
matching a real-3D inspiration video requires a real 3D path
(Three.js / Remotion 3D, or Blender) for the hero objects.

## Specific failures found in the rendered frames

| # | Problem | Evidence |
|---|---------|----------|
| 1 | Flat materials, no glass/metal/glow | Phone is a dark fill + cyan stroke; no reflection or specular anywhere |
| 2 | Scene 4 is fully flat 2D | Battery = empty black box, PCB = green grid — breaks the "lit 3D geometry, no flat-fill shapes" rule |
| 3 | Screen text overflows its card | Shot 1: "Tap here to verify your account immediate" is clipped at the card edge |
| 4 | Emoji render as tofu boxes | 🔋 / 🛡️ / ⚠️ show as `□` — DejaVu has no emoji glyphs |
| 5 | Screen textures are blurry | 480×1000 texture perspective-warped full-frame with BILINEAR; text smears when the phone is large |
| 6 | Camera barely moves | Yaw changes of 6–12° and zoom 1.22→1.42 over ~3s = near-static; guidelines demand constant orbit/push/pull |
| 7 | No transitions | Hard cuts only — no whip-pan, zoom-blur or light-flash between scenes |
| 8 | Empty background | Flat `#0A0C12` + faint grid + two ellipses; large voids in shots 4 & 7 |
| 9 | Hand is a brown rounded rectangle | Shot 2 "hand" reads as a capsule, not a hand — breaks the scale-cue rule |
| 10 | Cluttered HUD | Top "MOBILE THREAT // 01 HOOK" bar + 10 progress squares compete with the hero object; inspiration videos are clean |
| 11 | Dated typography | DejaVu Sans Bold everywhere; inspiration standard is a modern geometric sans (Inter / Montserrat / Poppins ExtraBold) |
| 12 | Callout lines cross screen text | Shots 1 & 6: leader lines pass through SMS/laptop text |
| 13 | No sound design | Single mp3 muxed in; no SFX, no music ducking, no loudness normalisation |
| 14 | Weak compression | `libx264 -preset veryfast`, no CRF/2-pass tuning → artefacts on gradients |
| 15 | Not portable | Fonts hardcoded to Termux/Android paths (`/data/data/com.termux/...`, `/system/fonts/...`) — crashes on Linux. Fixed in v2 (see below) |
| 16 | Missing inputs | Renderer needs `.pipeline/phishing_chunks.json` + `phishing_audio.mp3`, neither in the repo — cannot render as committed |

## What was fixed this session

- `render_brief_phishing_v2.py`: font lookup now falls back to Linux
  DejaVu paths (`/usr/share/fonts/truetype/dejavu/...`) and raises a clear
  error instead of crashing on a missing file.

## What matching an inspiration video requires

1. Measure the sample: `python3 scripts/analyze_inspiration.py`
2. Decide the render path from the measurement:
   - If the inspiration is real 3D → rebuild hero objects in Three.js
     (inside the existing Remotion `video-engine/`) with PBR materials,
     environment lighting, soft shadows and bloom; keep PIL only for
     2D overlays (captions, callouts).
   - If the inspiration is 2D motion graphics → keep PIL but fix
     items 3–14 above (font, emoji, texture resolution, camera range,
     transitions, background depth, sound design, encoding).
3. Re-render keyframes first, compare side-by-side, then full video.
