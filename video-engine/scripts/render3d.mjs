// Renders one shard (a frame range) of the Inspired3D composition. Shards are joined by the workflow.
import path from 'node:path';
import fs from 'node:fs';
import { bundle } from '@remotion/bundler';
import { renderMedia, selectComposition } from '@remotion/renderer';

const gl = process.env.GL || 'swangle';
const scale = Number(process.env.SCALE || 1);
const shards = Number(process.env.SHARDS || 1);
const shard = Number(process.env.SHARD || 0);
const out = path.resolve(process.env.OUT_DIR || 'out/parts');
fs.mkdirSync(out, { recursive: true });

const serveUrl = await bundle({ entryPoint: path.resolve('src/index.ts') });
const composition = await selectComposition({ serveUrl, id: 'Inspired3D', chromiumOptions: { gl } });

const total = composition.durationInFrames;
const per = Math.ceil(total / shards);
const start = shard * per;
const end = Math.min(total - 1, start + per - 1);
if (start > end) {
  console.log('Nothing to render for shard', shard);
  process.exit(0);
}

await renderMedia({
  composition,
  serveUrl,
  codec: 'h264',
  crf: 18,
  pixelFormat: 'yuv420p',
  outputLocation: path.join(out, 'part_' + String(shard).padStart(2, '0') + '.mp4'),
  frameRange: [start, end],
  muted: true,
  scale,
  concurrency: Number(process.env.CONCURRENCY || 2),
  chromiumOptions: { gl },
  timeoutInMilliseconds: 180000,
  onProgress: ({ renderedFrames }) => {
    if (renderedFrames % 30 === 0) console.log('shard', shard, 'frames', renderedFrames, '/', end - start + 1);
  },
});
console.log('done shard', shard, 'frames', start, '-', end);
