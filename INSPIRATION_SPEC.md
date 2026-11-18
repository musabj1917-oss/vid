# Inspiration spec (filled from `inspiration/analysis/report.md`)

> Measured = from ffmpeg/ffprobe. Observed = from 23 frames sampled every 4 s plus close-ups at cuts, end card and opening.
> Not verified = could not be checked without listening or scrubbing the full video.

## Measured (from analyzer)
- Resolution / FPS / Duration: 720x1280, 30 fps, 91.9 s, H.264 yuv420p ~1.3 Mbps
- Scene cuts: 10 hard cuts at scene threshold 0.3 (6.5, 18.7, 21.9, 24.5, 26.6, 32.7, 52.3, 66.5, 86.3, 88.2 s). 32 events at threshold 0.12, mostly camera moves. New angle about every 4 s.
- Dominant colours: near-black navy backgrounds (mean about rgb(23,25,34) on dark shots); copper-orange metal (about rgb(160-176, 96-112, 48-64)); flat amber for text and X marks; white text; yellow viewfinder box and "VIDEO" label.
- Audio: AAC 48 kHz stereo, -14.1 LUFS integrated, LRA 2.8 LU, true peak -2.4 dBFS. Continuous: only two gaps over 0.4 s (32.2 s and 87.8 s), both at scene changes. Energy sits mostly in the speech band.

## Observed by watching
- [x] Main object / single metaphor: an iPhone's camera internals (glass lens barrel wrapped in copper coil, gyroscope, mount ball joint) driven by a motorcycle engine. One consistent world, parts shown as cutaway "teardown" objects.
- [x] Camera moves per scene: continuous. Slow push-ins, orbits and tilts on hero objects, macro close-ups on lenses and coils, wide pulls to the motorcycle and road. Field of view changes between wide and macro. Rarely static.
- [x] Transitions between scenes: mostly hard cuts that land on a new angle of the same object; one white-flash transition (about 0.2 s) at 6.5 s from a macro lens shot. Other transitions not verified.
- [x] Caption font / size / position / highlight: bold white heavy grotesque, 2-5 words at a time, bottom-center about 70% down the frame, inside a dark translucent rounded pill. The spoken word is underlined in white (not gold) and other words dim slightly.
- [x] Callout style: small monospace labels in capitals ("MAIN LENS", "GYROSCOPE", "ENGINE") with thin leader lines to the part. Amber labels with a dark chip in some shots.
- [x] Background + accent colours: obsidian navy (#0A0C14 range) with a soft light gradient and environment reflections; copper/amber accent; yellow for the viewfinder UI.
- [x] Big-number / proof-beat style: very large white heavy numerals with a small caption ("6,000 RPM", "1 SEC"); amber "NOT THIS" headline above an object crossed out with an amber X; proof beat is a close-up of a documentation page with the key sentence highlighted. The glass element is the lens barrel, not the proof.
- [x] CTA + end card: bookends the opening. The same hero shot (phone on handlebar mount) returns with a question as the final caption and a channel title in heavy white caps at the top. No separate end card.
- [ ] Sound design (music, whooshes, impacts): NOT VERIFIED. Voiceover dominates. Whether there is a music bed or impacts needs a listen.
- Persistent UI: top HUD bar with a status label (ENGINE ON / OFF) and four step dots that fill in as the video progresses. Small brand badge top right in the opening.

## Current renderer vs inspiration (scorecard)
| Criterion | Current (PIL v2) | Inspiration | Gap action |
|-----------|------------------|-------------|------------|
| 3D materials (glass/metal/glow) | Flat fills + outline | Real PBR: chrome, glass with refraction, emissive copper coils, soft shadows, bloom, depth of field | Three.js with MeshPhysicalMaterial (transmission), environment lighting; bloom and DOF still to add |
| Camera movement range | 6-12 deg yaw, near-static | Continuous push / orbit / tilt, wide to macro | Keyframed camera paths per shot, moving every frame, varied FOV |
| Screen/UI texture sharpness | 480x1000, blurry warp | Crisp phone UI, readable at 720p | UI textures drawn at 1024x2336 with anisotropic filtering |
| Typography | DejaVu Bold | Heavy grotesque captions, monospace callouts | Archivo Black and JetBrains Mono via @remotion/google-fonts |
| Background depth | Flat + grid | Lit environment, reflections, light cones, depth blur | Environment map, fog, floor with reflections, road streaks |
| Transitions | Hard cuts | Hard cuts on new angles, rare white flash | Hard cuts plus occasional flash |
| Sound design | Single mp3 | Voiceover-led, loud (-14 LUFS), continuous | Voiceover plus loudnorm to -14 LUFS (music/SFX to be decided) |
| Encoding | veryfast, no CRF | 720p about 1.3 Mbps | 1080x1920, libx264 CRF 18, yuv420p, loudnorm |

## Render path decision
- [x] Real 3D needed -> Three.js in `video-engine/` (Remotion) for hero objects
- [ ] 2D motion graphics sufficient -> fix PIL renderer per DIAGNOSIS.md

Evidence: glass refraction, specular chrome, emissive coils with bloom and depth of field cannot be faked with flat 2D drawing.

## Open decisions
- Target length: about 92 s (decided).
- Shot length: 3-5 s per angle with continuous motion, which gives roughly 20-25 shots (the inspiration does not cut every 2-3 s).
- Use the style and technique, not the source's script, branding or screenshots.
