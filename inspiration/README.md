# Inspiration Video Intake

Drop your sample / inspiration video here.

## How to add it
1. Put the video file in this folder, e.g. `inspiration/sample.mp4`
   (`.mp4`, `.mov`, `.webm` all work — `.mp4` is preferred).
2. Tell me in chat: **"sample video added"** (and the filename if it isn't `sample.mp4`).
3. If you have them, also add:
   - The voiceover script / narration text (as `.txt`)
   - The topic of the video
   - Whether you want the SAME topic rebuilt, or your own topic in the same style

## What happens next
I will run:

```bash
python3 scripts/analyze_inspiration.py
```

That extracts resolution, fps, duration, scene cuts, colour palette,
caption style and audio info into `inspiration/analysis/report.md`,
then I rebuild the renderer to match that spec as closely as possible.

## If the video file is too large to upload
Upload 5–10 screenshots instead (one per scene), named `shot_01.png`,
`shot_02.png`, … plus a screen recording of the audio if you can.
The analyzer works with images too.
