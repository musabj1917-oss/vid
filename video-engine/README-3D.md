# Inspired3D (Three.js in Remotion)

Real 3D explainer look (metal, glass, copper coils, soft shadows) following `INSPIRATION_SPEC.md`.

## Edit the video
- `src/3d/shots.ts`: the shot list (scene, duration, camera path, captions, callouts, big numbers). The current copy is a PLACEHOLDER topic.
- `src/3d/parts.tsx`: reusable 3D parts. `src/3d/scenes.tsx`: which parts form each scene.
- `src/3d/overlays.tsx`: HUD, pill captions, callouts, big numbers, flash.

## Render (GitHub Actions, workflow `render-3d`)
1. Run with mode `stills` to get one PNG per shot (artifact `keyframes`). Review before anything else.
2. Run with mode `full` for the sharded full render (12 parallel shards, silent video). Software GL is slow, so use `scale` 0.5 for previews.
3. Add `video-engine/public/voiceover3d.mp3` to get audio muxed with loudness normalisation (-14 LUFS).

## Not done yet
- Bloom and depth of field (glow is faked with additive sprites).
- Word-level caption timing from the voiceover (captions use fixed times per shot).
- Hook into `scripts/cloud_pipeline.py` (the cloud pipeline still uses the existing renderers).
