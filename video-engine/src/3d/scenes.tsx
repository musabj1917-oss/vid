import React from 'react';
import {
  Bolt, Cage, Clamps, Coil, Engine, Floor, GlassBarrel, Glow, Gyro, Mount, Phone, PulseRings, RoadStreaks, Sensor,
} from './parts';
import type { SceneId } from './shots';

const PI = Math.PI;
type P = { f: number };

const Hero: React.FC<P> = ({ f }) => (
  <group>
    <group rotation={[0, Math.sin(f * 0.02) * 0.1, 0]}>
      <Phone />
      <Mount f={f} />
      <PulseRings f={f} />
    </group>
    <RoadStreaks f={f} />
    <Floor y={-3.2} />
  </group>
);

const CoilScene: React.FC<P> = ({ f }) => (
  <group>
    <group position={[0, 0.25, 0]}>
      <GlassBarrel />
      <Coil f={f} shake={0.6 + 0.4 * Math.sin(f * 0.05)} />
    </group>
    <Sensor y={-1.0} />
    <Clamps />
    <Cage y={0.2} />
    <Glow position={[0, -0.9, 0]} size={1.4} opacity={0.9} color='#FFE2A8' />
    <Floor y={-1.6} />
  </group>
);

const GyroScene: React.FC<P> = ({ f }) => (
  <group>
    <Gyro f={f} />
    <Floor y={-2.2} />
  </group>
);

const EngineScene: React.FC<P> = ({ f }) => (
  <group>
    <Engine f={f} />
    <RoadStreaks f={f} y={-2.4} speed={0.5} />
    <Floor y={-2.4} />
  </group>
);

const BoltScene: React.FC<P> = ({ f }) => (
  <group>
    <Bolt f={f} />
    <Floor y={-1.7} />
  </group>
);

const MountScene: React.FC<P> = ({ f }) => (
  <group>
    <Phone />
    <Mount f={f} />
    <group position={[0, -1.8, -0.2]}>
      <Coil r={0.28} n={6} h={0.7} f={f} shake={2} />
    </group>
    <PulseRings f={f} />
    <Floor y={-3.2} />
  </group>
);

const LensScene: React.FC<P> = ({ f }) => (
  <group rotation={[0, PI + Math.sin(f * 0.02) * 0.15, 0]}>
    <Phone />
  </group>
);

const ScreenScene: React.FC<P> = ({ f }) => (
  <group rotation={[0, -0.25 + Math.sin(f * 0.025) * 0.12, 0.04]}>
    <Phone />
    <PulseRings f={f} />
  </group>
);

export const SCENES: Record<SceneId, React.FC<P>> = {
  hero: Hero,
  coil: CoilScene,
  gyro: GyroScene,
  engine: EngineScene,
  bolt: BoltScene,
  mount: MountScene,
  lens: LensScene,
  screen: ScreenScene,
};
