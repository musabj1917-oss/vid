// Renders one keyframe (PNG) per shot so the look can be reviewed before any full encode.
import path from 'node:path';
import fs from 'node:fs';
import { bundle } from '@remotion/bundler';
import { renderStill, selectComposition } from '@remotion/renderer';

const gl = process.env.GL || 'swangle';
const scale = Number(process.env.SCALE || 1);
const out = path.resolve(process.env.OUT_DIR || 'out/stills');
fs.mkdirSync(out, { recursive: true });

const serveUrl = await bundle({ entryPoint: path.resolve('src/index.ts') });
const composition = await selectComposition({ serveUrl, id: 'Inspired3D', chromiumOptions: { gl } });
const mids = composition.props.mids;

for (let i = 0; i < mids.length; i++) {
  const output = path.join(out, 'shot_' + String(i + 1).padStart(2, '0') + '.png');
  await renderStill({
    composition,
    serveUrl,
    output,
    frame: mids[i],
    imageFormat: 'png',
    scale,
    chromiumOptions: { gl },
    timeoutInMilliseconds: 180000,
  });
  console.log('rendered', output);
}
