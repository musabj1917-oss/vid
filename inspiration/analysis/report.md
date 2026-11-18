# Inspiration analysis report

Source: `inspo.mp4` (measured with ffprobe/ffmpeg; frames reviewed by hand).

## Technical
| Item | Value |
|------|-------|
| Resolution | 720 x 1280 (9:16) |
| Frame rate | 30 fps |
| Duration | 91.9 s |
| Video | H.264, yuv420p, about 1.3 Mbps |
| Audio | AAC, 48 kHz, stereo |
| Loudness | -14.1 LUFS integrated, LRA 2.8 LU, true peak -2.4 dBFS |

## Cuts and pacing
- 10 hard cuts at scene threshold 0.3: 6.5, 18.7, 21.9, 24.5, 26.6, 32.7, 52.3, 66.5, 86.3, 88.2 s.
- 32 change events at threshold 0.12 (camera moves count here): new angle about every 4 s.
- Transition seen: white flash (about 0.2 s) at 6.5 s; 18.7 s is a hard cut.

## Colour
- Background: near-black navy, mean about rgb(23,25,34) on dark shots.
- Accent: copper-orange metal, about rgb(160-176, 96-112, 48-64); amber for flat text and X marks.
- Text: white. Viewfinder UI: yellow.

## Audio
- Continuous voiceover-dominant mix. Only two gaps over 0.4 s: 32.2 s and 87.8 s.
- Mean level per 10 s window stays between -15.8 and -18.4 dB (very even).
- Band energy: speech band (around 1.5 kHz) -23.4 dB mean, below 120 Hz -27.3 dB, above 5 kHz -31.2 dB.
- Music bed or impacts: not verified.

## Visual structure (23 frames sampled every 4 s)
1. Hero shot: phone on handlebar mount with viewfinder UI (opening and ending).
2. Macro lens and coil teardown, gyroscope, motor and vibration cutaways.
3. Phone UI close-ups, hand, motorcycle and road wide shots, engine (6,000 RPM).
4. Big-number beats ("6,000 RPM", "1 SEC"), documentation-page proof beat, "NOT THIS" with crossed-out bolt.
5. Return to the hero shot with a closing question and a channel title.

Persistent elements: top HUD bar (status label plus four step dots), bottom-center pill captions with the spoken word underlined, monospace callout labels with leader lines.

## Notes
- Measured values are at 720p; rebuild at 1080x1920.
- Do not copy the source's script, brand name, logo badge or documentation screenshots. Use the style and techniques only.
