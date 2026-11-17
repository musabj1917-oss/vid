# Inspiration spec — fill from `inspiration/analysis/report.md`

> Do not guess these. Measure them from the sample video, then build to them.

## Measured (from analyzer)
- Resolution / FPS / Duration: _pending sample video_
- Scene cuts: _pending_
- Dominant colours: _pending_
- Audio (music / SFX / voiceover): _pending_

## To observe by watching
- [ ] Main object / single metaphor:
- [ ] Camera moves per scene (orbit / push / pull / tilt):
- [ ] Transitions between scenes:
- [ ] Caption font / size / position / highlight:
- [ ] Callout style (if any):
- [ ] Background + accent colours:
- [ ] Big-number / proof-beat style:
- [ ] CTA + end card:
- [ ] Sound design (music, whooshes, impacts):

## Current renderer vs inspiration (scorecard)
| Criterion | Current (PIL v2) | Inspiration | Gap action |
|-----------|------------------|-------------|------------|
| 3D materials (glass/metal/glow) | Flat fills + outline | _TBD_ | _TBD_ |
| Camera movement range | 6–12° yaw, near-static | _TBD_ | _TBD_ |
| Screen/UI texture sharpness | 480×1000, blurry warp | _TBD_ | _TBD_ |
| Typography | DejaVu Bold | _TBD_ | _TBD_ |
| Background depth | Flat + grid | _TBD_ | _TBD_ |
| Transitions | Hard cuts | _TBD_ | _TBD_ |
| Sound design | Single mp3 | _TBD_ | _TBD_ |
| Encoding | veryfast, no CRF | _TBD_ | _TBD_ |

## Render path decision
- [ ] Real 3D needed → Three.js in `video-engine/` (Remotion) for hero objects
- [ ] 2D motion graphics sufficient → fix PIL renderer per DIAGNOSIS.md
