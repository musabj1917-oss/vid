import React, { useMemo } from 'react';
import * as THREE from 'three';
import { M, glowTexture } from './materials';

const PI = Math.PI;
type V3 = [number, number, number];

function roundedRect(w: number, h: number, r: number): THREE.Shape {
  const s = new THREE.Shape();
  const x = -w / 2;
  const y = -h / 2;
  s.moveTo(x + r, y);
  s.lineTo(x + w - r, y);
  s.quadraticCurveTo(x + w, y, x + w, y + r);
  s.lineTo(x + w, y + h - r);
  s.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
  s.lineTo(x + r, y + h);
  s.quadraticCurveTo(x, y + h, x, y + h - r);
  s.lineTo(x, y + r);
  s.quadraticCurveTo(x, y, x + r, y);
  return s;
}

function screenGeometry(w: number, h: number, r: number): THREE.ShapeGeometry {
  const g = new THREE.ShapeGeometry(roundedRect(w, h, r), 12);
  const p = g.attributes.position;
  const uv = g.attributes.uv;
  for (let i = 0; i < p.count; i++) uv.setXY(i, (p.getX(i) + w / 2) / w, (p.getY(i) + h / 2) / h);
  uv.needsUpdate = true;
  return g;
}

function rr(g: CanvasRenderingContext2D, x: number, y: number, w: number, h: number, r: number) {
  g.beginPath();
  g.moveTo(x + r, y);
  g.arcTo(x + w, y, x + w, y + h, r);
  g.arcTo(x + w, y + h, x, y + h, r);
  g.arcTo(x, y + h, x, y, r);
  g.arcTo(x, y, x + w, y, r);
  g.closePath();
}

function makeSiteTexture(): THREE.CanvasTexture {
  const W = 1024;
  const H = 2336;
  const c = document.createElement('canvas');
  c.width = W;
  c.height = H;
  const g = c.getContext('2d')!;
  const bg = g.createLinearGradient(0, 0, 0, H);
  bg.addColorStop(0, '#0d1220');
  bg.addColorStop(1, '#1a2036');
  g.fillStyle = bg;
  g.fillRect(0, 0, W, H);
  g.fillStyle = '#ffffff';
  g.font = 'bold 46px monospace';
  g.fillText('9:41', 90, 130);
  g.fillStyle = '#FFB020';
  rr(g, 80, 230, 76, 76, 20);
  g.fill();
  g.fillStyle = '#8f98ad';
  for (let i = 0; i < 3; i++) {
    rr(g, 560 + i * 140, 256, 100, 22, 11);
    g.fill();
  }
  g.fillStyle = '#ffffff';
  g.font = 'bold 128px sans-serif';
  g.fillText('Your site', 80, 600);
  g.fillText('feels fast.', 80, 745);
  g.fillStyle = '#9aa3b8';
  g.font = '46px sans-serif';
  g.fillText('Built to turn visitors', 80, 850);
  g.fillText('into customers.', 80, 915);
  g.fillStyle = '#FFB020';
  rr(g, 80, 1010, 540, 160, 40);
  g.fill();
  g.fillStyle = '#0A0C12';
  g.font = 'bold 58px sans-serif';
  g.fillText('Get started', 150, 1112);
  for (let i = 0; i < 3; i++) {
    const y = 1290 + i * 330;
    g.fillStyle = '#212944';
    rr(g, 80, y, 864, 290, 36);
    g.fill();
    g.fillStyle = '#FFB020';
    rr(g, 120, y + 40, 150, 150, 28);
    g.fill();
    g.fillStyle = '#c9d0e4';
    rr(g, 310, y + 60, 520, 28, 14);
    g.fill();
    g.fillStyle = '#6c7794';
    rr(g, 310, y + 120, 400, 22, 11);
    g.fill();
    rr(g, 310, y + 170, 460, 22, 11);
    g.fill();
  }
  const tex = new THREE.CanvasTexture(c);
  tex.colorSpace = THREE.SRGBColorSpace;
  tex.anisotropy = 8;
  return tex;
}

function makeSensorTexture(): THREE.CanvasTexture {
  const c = document.createElement('canvas');
  c.width = 256;
  c.height = 256;
  const g = c.getContext('2d')!;
  g.fillStyle = '#05070b';
  g.fillRect(0, 0, 256, 256);
  for (let y = 0; y < 32; y++) {
    for (let x = 0; x < 32; x++) {
      const k = (x + y * 2) % 3;
      g.fillStyle = k === 0 ? '#b03030' : k === 1 ? '#2f9a48' : '#2e56b8';
      g.fillRect(x * 8, y * 8, 7, 7);
    }
  }
  const tex = new THREE.CanvasTexture(c);
  tex.colorSpace = THREE.SRGBColorSpace;
  tex.magFilter = THREE.NearestFilter;
  return tex;
}

export const Glow: React.FC<{ position: V3; color?: string; size?: number; opacity?: number }> = ({
  position,
  color = '#FFB020',
  size = 2,
  opacity = 0.8,
}) => (
  <sprite position={position} scale={[size, size, 1]}>
    <spriteMaterial
      map={glowTexture()}
      color={color}
      blending={THREE.AdditiveBlending}
      transparent
      depthWrite={false}
      opacity={opacity}
    />
  </sprite>
);

export const Floor: React.FC<{ y?: number }> = ({ y = -2.6 }) => (
  <group position={[0, y, 0]}>
    <mesh rotation={[-PI / 2, 0, 0]} receiveShadow material={M.floor}>
      <planeGeometry args={[60, 60]} />
    </mesh>
    <gridHelper args={[60, 60, '#27303f', '#151a24']} position={[0, 0.005, 0]} />
  </group>
);

export const RoadStreaks: React.FC<{ f: number; y?: number; speed?: number }> = ({ f, y = -3.1, speed = 0.35 }) => {
  const items = [];
  for (let i = 0; i < 36; i++) {
    const side = i % 2 === 0 ? -1 : 1;
    const x = side * (2.2 + ((i * 7) % 5) * 0.9);
    const z = ((i * 1.9 + f * speed) % 40) - 28;
    items.push(
      <mesh key={i} position={[x, y + 0.05 + ((i * 3) % 4) * 0.35, z]} material={i % 3 === 0 ? M.amber : M.white}>
        <boxGeometry args={[0.04, 0.04, 1.1]} />
      </mesh>,
    );
  }
  return <group>{items}</group>;
};

export const Coil: React.FC<{ r?: number; n?: number; h?: number; f: number; shake?: number }> = ({
  r = 1,
  n = 16,
  h = 1,
  f,
  shake = 0,
}) => {
  const rings = [];
  for (let i = 0; i < n; i++) {
    const y = (i / (n - 1) - 0.5) * h;
    const wob = Math.sin(f * 0.6 + i * 0.7) * 0.015 * shake;
    rings.push(
      <mesh key={i} position={[wob, y, 0]} rotation={[PI / 2 + 0.04, 0, 0]} castShadow material={M.copper}>
        <torusGeometry args={[r, 0.035, 12, 72]} />
      </mesh>,
    );
  }
  return <group>{rings}</group>;
};

export const GlassBarrel: React.FC<{ r?: number; h?: number }> = ({ r = 0.9, h = 1.5 }) => (
  <group>
    <mesh material={M.glass}>
      <cylinderGeometry args={[r, r, h, 72, 1, true]} />
    </mesh>
    {[0.35, -0.05, -0.4].map((y, i) => (
      <mesh key={'d' + i} position={[0, y, 0]} material={M.glass}>
        <cylinderGeometry args={[r * 0.92, r * 0.92, 0.06, 72]} />
      </mesh>
    ))}
    {[h / 2, -h / 2].map((y, i) => (
      <mesh key={'o' + i} position={[0, y, 0]} rotation={[PI / 2, 0, 0]} castShadow material={M.rubber}>
        <torusGeometry args={[r * 1.02, 0.06, 16, 72]} />
      </mesh>
    ))}
  </group>
);

export const Sensor: React.FC<{ y?: number }> = ({ y = -1.0 }) => {
  const tex = useMemo(() => makeSensorTexture(), []);
  return (
    <group position={[0, y, 0]}>
      <mesh castShadow receiveShadow material={M.steel}>
        <boxGeometry args={[2.6, 0.12, 2.6]} />
      </mesh>
      <mesh position={[0, 0.07, 0]} rotation={[-PI / 2, 0, 0]}>
        <planeGeometry args={[1.5, 1.5]} />
        <meshStandardMaterial map={tex} emissiveMap={tex} emissive='#ffffff' emissiveIntensity={0.3} roughness={0.5} metalness={0.2} />
      </mesh>
    </group>
  );
};

export const Clamps: React.FC = () => (
  <group>
    {[-1.5, 1.5].map((x, i) => (
      <mesh key={i} position={[x, -0.2, 0]} castShadow material={M.steel}>
        <boxGeometry args={[0.45, 1.6, 1.1]} />
      </mesh>
    ))}
  </group>
);

export const Cage: React.FC<{ w?: number; h?: number; d?: number; y?: number }> = ({ w = 4.4, h = 3.4, d = 3.4, y = 0 }) => {
  const geo = useMemo(() => new THREE.EdgesGeometry(new THREE.BoxGeometry(w, h, d)), [w, h, d]);
  return (
    <lineSegments geometry={geo} position={[0, y, 0]}>
      <lineBasicMaterial color='#7c8cab' transparent opacity={0.35} />
    </lineSegments>
  );
};

export const Gyro: React.FC<{ f: number }> = ({ f }) => (
  <group>
    <mesh rotation={[f * 0.012, f * 0.02, 0]} material={M.chrome}>
      <torusGeometry args={[1.35, 0.035, 16, 96]} />
    </mesh>
    <mesh rotation={[PI / 2, 0, f * 0.035]} castShadow material={M.copper}>
      <torusGeometry args={[0.95, 0.05, 16, 96]} />
    </mesh>
    <mesh rotation={[f * 0.05, PI / 2, 0]} material={M.chrome}>
      <torusGeometry args={[0.65, 0.03, 16, 96]} />
    </mesh>
    <mesh castShadow material={M.chrome}>
      <sphereGeometry args={[0.38, 48, 48]} />
    </mesh>
    <Glow position={[0, 0, 0]} size={2.6} opacity={0.25} />
  </group>
);

export const Engine: React.FC<{ f: number }> = ({ f }) => {
  const pistons = [-1.1, 0, 1.1].map((x, i) => {
    const ph = f * 0.32 + i * 2.1;
    const y = 0.15 + Math.sin(ph) * 0.38;
    const fire = Math.pow(Math.max(0, Math.sin(ph + 0.6)), 6);
    return (
      <group key={i} position={[x, 0, 0]}>
        <mesh position={[0, 0.2, 0]} material={M.glass}>
          <cylinderGeometry args={[0.4, 0.4, 1.7, 48, 1, true]} />
        </mesh>
        <mesh position={[0, y, 0]} castShadow material={M.chrome}>
          <cylinderGeometry args={[0.34, 0.34, 0.42, 48]} />
        </mesh>
        <mesh position={[0, y - 0.65, 0]} castShadow material={M.steel}>
          <cylinderGeometry args={[0.06, 0.06, 0.9, 16]} />
        </mesh>
        <Glow position={[0, 0.95, 0]} size={1.6 + fire * 1.6} opacity={0.15 + fire * 0.75} />
      </group>
    );
  });
  return (
    <group position={[0, 0.2, 0]}>
      {pistons}
      <mesh position={[0, -1.05, 0]} rotation={[0, 0, PI / 2]} castShadow material={M.chrome}>
        <cylinderGeometry args={[0.1, 0.1, 3.6, 24]} />
      </mesh>
      <mesh position={[0, -1.35, 0]} castShadow receiveShadow material={M.dark}>
        <boxGeometry args={[3.8, 0.4, 1.2]} />
      </mesh>
      <mesh position={[0, 1.25, 0]} castShadow material={M.dark}>
        <boxGeometry args={[3.8, 0.25, 1.2]} />
      </mesh>
    </group>
  );
};

export const Bolt: React.FC<{ f: number }> = ({ f }) => {
  const threads = [];
  for (let i = 0; i < 14; i++) {
    threads.push(
      <mesh key={i} position={[0, -0.15 - i * 0.12, 0]} rotation={[PI / 2, 0, 0]} material={M.chrome}>
        <torusGeometry args={[0.31, 0.035, 10, 40]} />
      </mesh>,
    );
  }
  return (
    <group position={[0, 0.4, 0]} rotation={[0.15, f * 0.012, 0]}>
      <mesh position={[0, 0.7, 0]} castShadow material={M.chrome}>
        <cylinderGeometry args={[0.62, 0.62, 0.38, 6]} />
      </mesh>
      <mesh position={[0, 0.45, 0]} material={M.steel}>
        <cylinderGeometry args={[0.55, 0.55, 0.08, 48]} />
      </mesh>
      <mesh position={[0, -0.7, 0]} castShadow material={M.steel}>
        <cylinderGeometry args={[0.29, 0.29, 1.9, 32]} />
      </mesh>
      {threads}
    </group>
  );
};

export const Phone: React.FC = () => {
  const body = useMemo(() => {
    const g = new THREE.ExtrudeGeometry(roundedRect(1.12, 2.4, 0.17), {
      depth: 0.09,
      bevelEnabled: true,
      bevelThickness: 0.025,
      bevelSize: 0.025,
      bevelSegments: 5,
      curveSegments: 20,
    });
    g.translate(0, 0, -0.045);
    return g;
  }, []);
  const screen = useMemo(() => screenGeometry(1.0, 2.28, 0.14), []);
  const tex = useMemo(() => makeSiteTexture(), []);
  const lenses: [number, number][] = [
    [-0.14, 0.14],
    [-0.14, -0.14],
    [0.14, 0],
  ];
  return (
    <group>
      <mesh geometry={body} castShadow material={M.chrome} />
      <mesh geometry={screen} position={[0, 0, 0.074]}>
        <meshStandardMaterial map={tex} emissiveMap={tex} emissive='#ffffff' emissiveIntensity={0.7} roughness={0.35} metalness={0} />
      </mesh>
      <mesh position={[0, 1.05, 0.078]} rotation={[0, 0, PI / 2]} material={M.rubber}>
        <capsuleGeometry args={[0.045, 0.2, 4, 12]} />
      </mesh>
      <group position={[-0.24, 0.78, -0.07]} rotation={[0, PI, 0]}>
        <mesh material={M.dark}>
          <boxGeometry args={[0.58, 0.58, 0.05]} />
        </mesh>
        {lenses.map(([x, y], i) => (
          <group key={i} position={[x, y, 0.04]} rotation={[PI / 2, 0, 0]}>
            <mesh material={M.chrome}>
              <cylinderGeometry args={[0.115, 0.115, 0.05, 40]} />
            </mesh>
            <mesh position={[0, 0.03, 0]} material={M.rubber}>
              <cylinderGeometry args={[0.085, 0.085, 0.02, 40]} />
            </mesh>
            <mesh position={[0, 0.045, 0]} material={M.glass}>
              <cylinderGeometry args={[0.07, 0.07, 0.01, 40]} />
            </mesh>
          </group>
        ))}
      </group>
    </group>
  );
};

export const PulseRings: React.FC<{ f: number }> = ({ f }) => {
  const geos = useMemo(
    () =>
      [1, 2, 3, 4].map((k) => {
        const w = 1.12 + 0.18 * k;
        const h = 2.4 + 0.18 * k;
        const r = 0.2 + 0.05 * k;
        const outer = roundedRect(w, h, r);
        outer.holes.push(roundedRect(w - 0.03, h - 0.03, r - 0.01));
        return new THREE.ShapeGeometry(outer, 24);
      }),
    [],
  );
  return (
    <group position={[0, 0, -0.1]}>
      {geos.map((g, i) => {
        const k = i + 1;
        const s = 1 + 0.025 * Math.sin(f * 0.35 - k);
        return (
          <mesh key={i} geometry={g} position={[0, 0, -0.01 * k]} scale={[s, s, 1]}>
            <meshBasicMaterial color='#FFB020' transparent opacity={0.9 - 0.18 * k} depthWrite={false} />
          </mesh>
        );
      })}
    </group>
  );
};

export const Mount: React.FC<{ f: number }> = ({ f }) => {
  const bob = Math.sin(f * 0.5) * 0.01;
  return (
    <group position={[0, bob, 0]}>
      <mesh position={[0, 0, -0.16]} castShadow material={M.dark}>
        <boxGeometry args={[1.0, 2.1, 0.1]} />
      </mesh>
      {[-0.62, 0.62].map((x, i) => (
        <mesh key={i} position={[x, 0, 0]} castShadow material={M.dark}>
          <boxGeometry args={[0.1, 0.9, 0.22]} />
        </mesh>
      ))}
      {[1.12, -1.12].map((y, i) => (
        <mesh key={'t' + i} position={[0, y, 0]} castShadow material={M.dark}>
          <boxGeometry args={[0.5, 0.1, 0.2]} />
        </mesh>
      ))}
      <mesh position={[0, -1.35, -0.2]} castShadow material={M.chrome}>
        <sphereGeometry args={[0.24, 48, 48]} />
      </mesh>
      <mesh position={[0, -1.95, -0.2]} castShadow material={M.chrome}>
        <cylinderGeometry args={[0.07, 0.07, 1.2, 24]} />
      </mesh>
      <mesh position={[0, -2.45, -0.2]} rotation={[0, 0, PI / 2]} castShadow material={M.chrome}>
        <cylinderGeometry args={[0.11, 0.11, 9, 32]} />
      </mesh>
      <mesh position={[0, -2.45, -0.2]} castShadow material={M.dark}>
        <boxGeometry args={[0.5, 0.45, 0.45]} />
      </mesh>
    </group>
  );
};
