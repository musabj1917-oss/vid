export type V3 = [number, number, number];
export type CamKey = { pos: V3; look: V3; fov: number };

const ease = (x: number) => (x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2);
const mix = (a: V3, b: V3, f: number): V3 => [
  a[0] + (b[0] - a[0]) * f,
  a[1] + (b[1] - a[1]) * f,
  a[2] + (b[2] - a[2]) * f,
];

// Camera swings on an arc around the scene (degrees, 0 = looking down -Z).
export function orbit(r: number, h: number, a0: number, a1: number, look: V3 = [0, 0.3, 0], fov = 34, n = 4): CamKey[] {
  const keys: CamKey[] = [];
  for (let i = 0; i <= n; i++) {
    const a = ((a0 + ((a1 - a0) * i) / n) * Math.PI) / 180;
    keys.push({ pos: [Math.sin(a) * r, h, Math.cos(a) * r], look, fov });
  }
  return keys;
}

// Straight push-in / pull-out, optionally moving the look target and the field of view.
export function push(from: V3, to: V3, look: V3 = [0, 0.3, 0], look2: V3 = look, fov = 34, fov2: number = fov): CamKey[] {
  return [
    { pos: from, look, fov },
    { pos: to, look: look2, fov: fov2 },
  ];
}

// t in 0..1 across the whole shot. Ease in/out over the whole move, linear between keys.
export function sampleCamera(keys: CamKey[], t: number): CamKey {
  if (keys.length === 1) return keys[0];
  const n = keys.length - 1;
  const s = ease(Math.min(Math.max(t, 0), 1)) * n;
  const i = Math.min(Math.floor(s), n - 1);
  const f = s - i;
  const a = keys[i];
  const b = keys[i + 1];
  return { pos: mix(a.pos, b.pos, f), look: mix(a.look, b.look, f), fov: a.fov + (b.fov - a.fov) * f };
}
