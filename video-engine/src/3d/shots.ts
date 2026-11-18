// TOPIC: PLACEHOLDER (website speed). Replace captions, callouts and numbers with your own script.
// The look, camera work, HUD, captions and pacing follow INSPIRATION_SPEC.md.
// Do not reuse the inspiration video's script, brand name or screenshots.
import { orbit, push } from './camera';
import type { CamKey } from './camera';

export const FPS = 30;

export type SceneId = 'hero' | 'coil' | 'gyro' | 'engine' | 'bolt' | 'mount' | 'lens' | 'screen';
export type Caption = { text: string; hi?: string; at: number }; // at = seconds from shot start
export type Callout = { text: string; from: [number, number]; to: [number, number]; at?: number }; // percent of frame
export type Shot = {
  scene: SceneId;
  dur: number;
  cam: CamKey[];
  step: 1 | 2 | 3 | 4;
  status: string;
  caps: Caption[];
  flashIn?: boolean;
  callout?: Callout;
  big?: { value: string; sub?: string };
  headline?: string;
  cross?: boolean;
  title?: string;
};

const S = (
  scene: SceneId,
  dur: number,
  cam: CamKey[],
  step: 1 | 2 | 3 | 4,
  status: string,
  caps: Caption[],
  extra: Partial<Shot> = {},
): Shot => ({ scene, dur, cam, step, status, caps, ...extra });

const FAST = 'SPEED: FAST';
const SLOW = 'SPEED: SLOW';
const C = (text: string, at: number, hi?: string): Caption => ({ text, at, hi });

export const SHOTS: Shot[] = [
  S('hero', 4.5, push([0.6, -0.2, 8], [0.2, -0.4, 6.2], [0, -0.45, 0], [0, -0.45, 0], 34, 34), 1, FAST, [C('Your website is a machine.', 0, 'machine'), C('Is it running well?', 2.3, 'well')]),
  S('lens', 4, push([1.3, 1.6, 3.4], [0.55, 0.9, 1.5], [0.24, 0.78, 0], [0.24, 0.78, 0], 30, 30), 1, FAST, [C('Every part has a job.', 0, 'job'), C('Visitors feel each one.', 2.1, 'feel')], { flashIn: true, callout: { text: 'IMAGES', from: [22, 30], to: [52, 46], at: 0.6 } }),
  S('coil', 4.5, orbit(6.5, 1.8, -35, 5, [0, 0.1, 0], 34), 1, FAST, [C('This coil is your page speed.', 0, 'speed'), C('Tight and fast.', 2.6, 'fast')], { callout: { text: 'PAGE SPEED', from: [70, 22], to: [52, 44], at: 0.5 } }),
  S('gyro', 4, orbit(5.6, 0.4, -20, 25, [0, 0, 0], 36), 1, FAST, [C('This keeps layouts steady.', 0, 'steady'), C('No jumping around.', 2.2, 'jumping')], { callout: { text: 'LAYOUT', from: [28, 24], to: [47, 42], at: 0.5 } }),
  S('coil', 4, push([3.5, 0.6, 4.2], [1.2, 0.5, 2.6], [0, 0.2, 0], [0, 0.2, 0], 30, 26), 1, SLOW, [C('Add heavy images...', 0, 'heavy'), C('...and it starts to shake.', 2.0, 'shake')]),
  S('mount', 4, push([2.2, -0.6, 5.5], [0.9, -1.5, 3.2], [0, -1.5, -0.2], [0, -1.5, -0.2], 34, 32), 2, SLOW, [C('Small flaws travel up.', 0, 'travel'), C('Straight to your visitor.', 2.0, 'visitor')], { callout: { text: 'YOUR VISITOR', from: [24, 22], to: [52, 34], at: 0.8 } }),
  S('engine', 4.5, orbit(6, 1.1, -30, 15, [0, 0.2, 0], 34), 2, FAST, [C('Traffic is the engine.', 0, 'engine'), C('More traffic, more load.', 2.4, 'load')], { callout: { text: 'TRAFFIC', from: [68, 26], to: [52, 46], at: 0.5 } }),
  S('screen', 4, push([1.8, 0.4, 4.8], [0.3, 0.2, 3.0], [0, 0.1, 0], [0, 0.1, 0], 34, 30), 2, FAST, [C('The visitor sees it all.', 0, 'sees'), C('In a blink.', 2.3, 'blink')]),
  S('hero', 4, orbit(7, 0.3, -18, 14, [0, -0.5, 0], 34), 2, FAST, [C('Most sites never check.', 0, 'check'), C('They just hope.', 2.2, 'hope')]),
  S('gyro', 4, push([0, 0.2, 7], [0.3, 0.1, 3.8], [0, 0, 0], [0, 0, 0], 34, 34), 2, SLOW, [C('Layout shifts cost trust.', 0, 'trust'), C('Visitors notice.', 2.2, 'notice')]),
  S('engine', 4.5, push([2.4, 0.6, 5.5], [0, 0.3, 4.0], [0, 0.2, 0], [0, 0.2, 0], 34, 34), 2, SLOW, [C('Three seconds.', 0, 'Three'), C('That is all you get.', 2.3, 'all')], { big: { value: '3 SEC', sub: 'TO KEEP A VISITOR' } }),
  S('coil', 4, orbit(6.2, 0.4, 40, -10, [0, 0.2, 0], 34), 3, FAST, [C('Speed is built in.', 0, 'built'), C('Not bolted on.', 2.1, 'bolted')]),
  S('mount', 4, orbit(4.8, -0.9, -40, 10, [0, -1.4, -0.2], 32), 3, FAST, [C('Strong foundations hold.', 0, 'foundations'), C('Under real traffic.', 2.2, 'real')], { callout: { text: 'FOUNDATION', from: [24, 24], to: [48, 42], at: 0.6 } }),
  S('lens', 4, push([-1.2, 1.4, 3.2], [0.6, 1.0, 1.7], [0.24, 0.78, 0], [0.24, 0.78, 0], 32, 28), 3, FAST, [C('Clear design shows.', 0, 'Clear'), C('Messy design blurs.', 2.1, 'blurs')], { flashIn: true }),
  S('screen', 4, push([-0.5, 0.2, 5.2], [0.4, 0.3, 3.6], [0, 0.1, 0], [0, 0.1, 0], 34, 30), 3, SLOW, [C('One second of delay.', 0, 'delay'), C('Costs real sales.', 2.2, 'sales')], { big: { value: '1 SEC', sub: 'OF DELAY' } }),
  S('bolt', 4.5, push([2.6, 0.9, 5.6], [0.4, 0.5, 4.6], [0, 0.4, 0], [0, 0.4, 0], 34, 34), 3, SLOW, [C('Not a quick patch.', 0, 'patch'), C('Patches fail later.', 2.4, 'fail')], { headline: 'NOT THIS', cross: true }),
  S('coil', 4, push([-2.5, 2.2, 5.5], [0.5, 1.0, 3.4], [0, 0.2, 0], [0, 0.2, 0], 34, 30), 3, FAST, [C('Tune the whole system.', 0, 'whole'), C('Part by part.', 2.1, 'part')]),
  S('gyro', 4, orbit(4.6, 0.8, 60, 10, [0, 0, 0], 32), 4, FAST, [C('Test on real phones.', 0, 'real'), C('Not just your laptop.', 2.0, 'laptop')]),
  S('engine', 4, orbit(5.2, 0.2, 25, -25, [0, 0.2, 0], 34), 4, FAST, [C('Plan for the busy days.', 0, 'busy'), C('Not the quiet ones.', 2.1, 'quiet')]),
  S('mount', 4.5, push([-2.4, -0.8, 4.8], [0, -1.7, 3.4], [0, -1.2, -0.2], [0, -1.5, -0.2], 34, 32), 4, FAST, [C('Build it to hold.', 0, 'hold'), C('Then it keeps working.', 2.3, 'working')]),
  S('screen', 4, orbit(4.4, 0.3, -25, 10, [0, 0, 0], 34), 4, FAST, [C('A fast site feels easy.', 0, 'easy'), C('Visitors stay.', 2.2, 'stay')]),
  S('hero', 5.5, push([0.3, -0.3, 6.4], [0, -0.45, 7.8], [0, -0.45, 0], [0, -0.45, 0], 34, 34), 4, FAST, [C('Is your website running well?', 0, 'running'), C('Let us check it.', 2.8, 'check')], { title: 'MWD' }),
];

export const SHOT_FRAMES: number[] = SHOTS.map((s) => Math.round(s.dur * FPS));
export const SHOT_STARTS: number[] = SHOT_FRAMES.reduce<number[]>((acc, n, i) => {
  acc.push(i === 0 ? 0 : acc[i - 1] + SHOT_FRAMES[i - 1]);
  return acc;
}, []);
export const TOTAL_FRAMES: number = SHOT_STARTS[SHOT_STARTS.length - 1] + SHOT_FRAMES[SHOT_FRAMES.length - 1];
export const SHOT_MIDS: number[] = SHOT_STARTS.map((s, i) => s + Math.floor(SHOT_FRAMES[i] * 0.6));

export function locate(frame: number): { i: number; shot: Shot; local: number; total: number } {
  let i = SHOT_STARTS.length - 1;
  while (i > 0 && frame < SHOT_STARTS[i]) i--;
  return { i, shot: SHOTS[i], local: frame - SHOT_STARTS[i], total: SHOT_FRAMES[i] };
}
