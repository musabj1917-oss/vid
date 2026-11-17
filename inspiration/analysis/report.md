# Inspiration video spec (measured)

- File: `sample.mp4` (15.66 MB)
- Resolution: 720x1280 (vertical 9:16)
- FPS: 30.0
- Duration: 91.9s
- Video codec: h264 (yuv420p)
- Audio: aac (48000 Hz, 2 ch) {'mean_volume_db': '-17.0 dB', 'max_volume_db': '-2.5 dB'}
- Frames extracted: 92 (see `frames/`)

## Dominant colours

- `#15171A` — 4.3% (Deep slate background)
- `#1A1B1F` — 4.2% (Dark metallic shadow)
- `#142032` — 4.1% (Deep midnight navy)
- `#060911` — 4.0% (Obsidian void floor)
- `#303030` — 3.2% (Neutral gray chassis / mount)
- `#292D36` — 2.7% (Dark blue-gray hardware)
- Key accents: `#D4883A` / `#FFB020` (amber/copper voice coil & vibration waves), `#FFFFFF` (crisp white typography & Apple card), `#38BDF8` (waveform telemetry)

## Observed Video Specifications

- **Scene count & cuts**: 38 cuts across 91.9s (~2.4s per scene cut). Continuous visual pacing matching the 2-3s rule.
- **Main object & metaphor**: Hardware teardown of the iPhone camera system (Motorcycle mount -> Exploded lens barrel with copper voice coil and floating glass elements -> Microscopic gimbal gyroscope -> Official Apple Support documentation authority card -> Vibration waveforms -> Rider on motorcycle).
- **Camera moves**: Wide 3D orbital sweeps (35°–60° yaw), continuous push-ins and pull-backs, never static for > 2.5s.
- **Captions**:
  - Font: Clean geometric sans-serif (Inter / SF Pro Display Bold, extra bold weight).
  - Size: Large (~54px), positioned in the lower-third safe zone (`y ≈ 78%–84%`).
  - Container: Frosted dark pill (`rgba(10, 15, 25, 0.85)`) tightly hugging 2 to 4 words.
  - Highlight: Current spoken word emphasized with a solid white highlight underline; non-active words slightly dimmed.
- **Callouts**: Uppercase monospaced micro-labels (`GYROSCOPE`, `HANDLEBARS`, `BUILT TO MOVE`) inside rounded dark tags with thin leader lines.
- **Transitions**: Whip-pan blurs, zoom-blur cuts, and smooth camera momentum across scene boundaries.
- **Audio & Sound Design**: Close-mic voiceover, subtle low-frequency tension synth bed, mechanical vibration hum, whoosh transitions, and normalized loudness.
- **CTA / Ending**: Punchy brand lockup ("AI UNPACKED", "now?") snapping back to the motorcycle mount.
