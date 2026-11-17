# Inspiration spec — measured from `sample.mp4`

> Measured and observed from `inspiration/sample.mp4` (and `inspiration/analysis/report.json`).

## Measured (from analyzer)
- Resolution / FPS / Duration: `720x1280` (native vertical 9:16), `30.0 fps`, `91.90s`
- Scene cuts: 38 distinct scene/angle cuts (average 2.41s per cut)
- Dominant colours:
  - Deep obsidian slate: `#060911` (4.0%), `#15171A` (4.3%), `#1A1B1F` (4.2%)
  - Dark midnight navy/shadow: `#142032` (4.1%), `#292D36` (2.7%)
  - Neutral dark tone: `#303030` (3.2%)
  - Accents in scene: Amber/copper coils `#D4883A` / `#FFB020`, alert red `#EF4444`, doc white `#FFFFFF` / `#F8FAFC`
- Audio (music / SFX / voiceover):
  - Codec: AAC (HE-AAC), 48000 Hz, 2 ch stereo
  - Loudness: Mean volume `-17.0 dB`, Max peak `-2.5 dB`
  - Elements: Close-mic dry voiceover + ambient tech tension synth bed + mechanical vibration SFX + camera whoosh transitions + card snap sound

## To observe by watching
- [x] **Main object / single metaphor**: Physical hardware teardown of the iPhone camera system under vibration stress (Motorcycle handlebar mount -> Camera lens assembly with voice coil & magnet actuators -> Microscopic gyroscope gimbal -> Official Apple documentation proof card -> Dual frequency waveforms -> Mannequin rider on motorcycle).
- [x] **Camera moves per scene (orbit / push / pull / tilt)**:
  - Scene 1–3: Wide 3D orbit around motorcycle handlebar push-in to camera screen (yaw rotation 45°, pitch 15°).
  - Scene 4–6: Macro push-in directly inside the camera lens barrel, showing floating glass elements and copper coil.
  - Scene 7–9: 3D gimbal gyroscope rotation (continuous 360° yaw/roll on dark IC substrate).
  - Scene 10–12: 3D perspective tilt on the floating Apple Support documentation card.
  - Scene 13+: Profile tracking shot of rider/motorcycle, followed by side-by-side waveform teardown. Continuous dynamic motion; camera never holds static for > 2.5s.
- [x] **Transitions between scenes**:
  - Seamless motion-matched camera cuts
  - Whip-pan directional blurs
  - Subtle focal depth shifts / light exposure flashes across cuts
- [x] **Caption font / size / position / highlight**:
  - Font: Geometric sans-serif (Inter / SF Pro Display Bold, extra bold weight, ~54px).
  - Layout: Tight translucent dark pill (`rgba(10, 15, 25, 0.85)`) hugging 2 to 4 words at a time.
  - Position: Lower-third (`y ≈ 78%–84%`), strictly above platform UI safe zones.
  - Highlight: Current spoken word is underscored with a solid white highlight underline; non-active words slightly dimmed (`#9CA3AF`).
- [x] **Callout style**:
  - Uppercase monospaced micro-labels (`GYROSCOPE`, `HANDLEBARS`, `BUILT TO MOVE`, `SMALLER ENGINE`) inside sleek translucent dark pills with 1px border.
  - Thin leader lines terminating in precise circular anchor points on the target geometry.
- [x] **Background + accent colours**:
  - Background: Deep obsidian/slate gradient (`#060911` to `#142032`) with 3D environment depth.
  - Accents: Warm amber/copper gold (`#FFB020` / `#D4883A`) for energy coils and vibration harmonics; electric cyan (`#38BDF8`) for telemetry; pure white (`#FFFFFF`) for typography.
  - Top Telemetry HUD: Translucent pill with glowing status dot (`• ENGINE ON` / `• ENGINE OFF`) and stage progress indicators `(1) (3) (4) (2)` with active amber fill.
- [x] **Big-number / proof-beat style**:
  - Dual frequency waveforms: `HAND 10 / SECOND` (cyan smooth wave) vs `ENGINE 200 / SECOND` (orange rapid vibration coil).
  - Authority Proof Beat: High-contrast 3D floating document card (`support.apple.com`) with authentic typography, drop shadow, and a soft yellow highlighter marker over the critical evidence statement.
- [x] **CTA + end card**:
  - Fast snap-back to the hero device mounted on the bike with branding ("AI UNPACKED", "now?").
- [x] **Sound design (music, whooshes, impacts)**:
  - Multi-track mix: Voiceover ducking background music by -6dB; directional whooshes synced to camera transitions; subtle low-frequency drone on problem states; mechanical click on callouts.

## Current renderer vs inspiration (scorecard)
| Criterion | Current (PIL v2) | Inspiration | Gap action |
|-----------|------------------|-------------|------------|
| 3D materials (glass/metal/glow) | Flat fills + cyan outline | Realistic PBR reflections, specular highlights, glass refraction, glow halos | Implement multi-layer shaded geometry: specular highlight maps, lighting gradients, glass sheen layers, and glow halos |
| Camera movement range | 6–12° yaw, near-static | 30–60° orbit, deep push-ins, continuous drift | Increase camera trajectory to 35–65° dynamic orbit, 1.0x to 1.8x continuous push-in/pull-back |
| Screen/UI texture sharpness | 480×1000, blurry warp | Crisp high-res textures, sharp vector text & icons | Render all UI/screen textures at native 1080×1920 or 2x supersampling (1440×2560) before warping with high-quality BICUBIC/LANCZOS interpolation |
| Typography | DejaVu Bold | Modern geometric sans (Inter / SF Pro Display Bold) | Integrate Inter / modern geometric sans font; add fallback chain; eliminate tofu with drawn vector icons |
| Background depth | Flat + grid | Rich dark gradient `#060911` with radial lighting & ambient particles | Add multi-stop radial lighting gradients, dynamic depth dust/particles, and realistic drop/contact shadows |
| Transitions | Hard cuts | Whip-pans, focal zoom-cuts, exposure flashes | Add 3–5 frame motion-blur/whip-pan or white flash transition buffers between scenes |
| Sound design | Single mp3 | Multi-layer VO + music ducking + whoosh SFX + loudness normalization | Add ffmpeg multi-track audio filter graph with loudnorm (target I=-16 LUFS, TP=-1.5 dB) + transition whooshes |
| Encoding | veryfast, no CRF | High quality tuned H.264 (CRF 18–20, yuv420p) | Set ffmpeg `-crf 19 -preset medium -pix_fmt yuv420p` |

## Render path decision
- [ ] Real 3D needed → Three.js in `video-engine/` (Remotion) for hero objects
- [x] High-Fidelity 2D/2.5D Motion Graphics + Procedural 3D Engine in Python (`render_brief_phishing_v2.py` / `render_engine.py`):
  - **Reason**: The production workflow must run in headless CI environments (GitHub Actions) without requiring full Chromium/Puppeteer/GPU dependencies, while remaining 100% portable on Termux. By upgrading the renderer with:
    1. High-res supersampled texture rendering (2x resolution with LANCZOS/BICUBIC filtering)
    2. Ray-marched / shaded multi-tone specular surfaces, metallic chrome gradients, glass refraction highlights, and soft multi-pass gaussian contact shadows
    3. Modern typography (Inter / SF Pro with vector icon fallbacks to eliminate tofu)
    4. Continuous 30°–60° camera orbit and push-in trajectories (no static holds)
    5. Scene-to-scene whip-pan / exposure flash transitions
    6. Multi-layer audio mixing with SFX and loudness normalization (CRF 19, YUV420p)
  - This closes every defect identified in `DIAGNOSIS.md` (items 1–16) while ensuring reliable execution across Termux and GitHub Actions cloud automation.
