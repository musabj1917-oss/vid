import React, { useLayoutEffect, useMemo } from 'react';
import * as THREE from 'three';
import { RoomEnvironment } from 'three/examples/jsm/environments/RoomEnvironment.js';
import { useThree } from '@react-three/fiber';
import { ThreeCanvas } from '@remotion/three';
import { AbsoluteFill, Audio, staticFile, useCurrentFrame, useVideoConfig } from 'remotion';
import { sampleCamera } from './camera';
import type { CamKey } from './camera';
import { SHOTS, locate } from './shots';
import { SCENES } from './scenes';
import { BigNumber, CalloutView, CaptionPill, Cross, Flash, HUD, Headline, Title, Vignette } from './overlays';

const Env: React.FC = () => {
  const gl = useThree((s) => s.gl);
  const scene = useThree((s) => s.scene);
  const env = useMemo(() => {
    const pm = new THREE.PMREMGenerator(gl);
    const tex = pm.fromScene(new RoomEnvironment(), 0.04).texture;
    pm.dispose();
    return tex;
  }, [gl]);
  useLayoutEffect(() => {
    scene.environment = env;
    scene.environmentIntensity = 0.5;
    return () => {
      scene.environment = null;
    };
  }, [scene, env]);
  return null;
};

const Lights: React.FC = () => (
  <>
    <ambientLight intensity={0.25} color='#8fa3d6' />
    <directionalLight
      position={[5, 6, 4]}
      intensity={2.4}
      color='#ffd9a8'
      castShadow
      shadow-mapSize={[2048, 2048]}
      shadow-camera-left={-6}
      shadow-camera-right={6}
      shadow-camera-top={6}
      shadow-camera-bottom={-6}
      shadow-bias={-0.0004}
    />
    <directionalLight position={[-5, 3, -4]} intensity={3.2} color='#5d86ff' />
    <pointLight position={[0, 1.5, 3]} intensity={12} color='#ffb060' distance={12} />
  </>
);

const CameraRig: React.FC<{ keys: CamKey[]; t: number; frame: number }> = ({ keys, t, frame }) => {
  const camera = useThree((s) => s.camera) as THREE.PerspectiveCamera;
  const c = sampleCamera(keys, t);
  const sh = 0.012; // tiny handheld drift so the frame is never perfectly still
  camera.position.set(c.pos[0] + Math.sin(frame * 0.07) * sh, c.pos[1] + Math.cos(frame * 0.053) * sh, c.pos[2]);
  camera.lookAt(c.look[0], c.look[1], c.look[2]);
  camera.fov = c.fov;
  camera.updateProjectionMatrix();
  return null;
};

export const Inspired3D: React.FC<{ audio?: string | null; mids?: number[] }> = ({ audio }) => {
  const frame = useCurrentFrame();
  const { width, height, fps } = useVideoConfig();
  const { i, shot, local, total } = locate(frame);
  const t = local / total;
  const Scene = SCENES[shot.scene];
  const sec = local / fps;
  const cap = [...shot.caps].reverse().find((c) => sec >= c.at) ?? shot.caps[0];
  const capAge = local - Math.round(cap.at * fps);

  let flash = 0;
  if (shot.flashIn && local < 6) flash = 1 - local / 6;
  const next = SHOTS[i + 1];
  if (next && next.flashIn && local >= total - 6) flash = (local - (total - 6)) / 6;

  return (
    <AbsoluteFill style={{ background: '#0A0C12' }}>
      {audio ? <Audio src={staticFile(audio)} /> : null}
      <ThreeCanvas
        width={width}
        height={height}
        shadows
        camera={{ fov: 34, near: 0.1, far: 100, position: [0, 0, 6] }}
        gl={{ antialias: true, toneMapping: THREE.ACESFilmicToneMapping, toneMappingExposure: 1.15, preserveDrawingBuffer: true }}
        style={{ position: 'absolute', inset: 0 }}
      >
        <color attach='background' args={['#0A0C12']} />
        <fog attach='fog' args={['#0A0C12', 9, 24]} />
        <Env />
        <Lights />
        <CameraRig keys={shot.cam} t={t} frame={frame} />
        <Scene key={i} f={local} />
      </ThreeCanvas>

      <Vignette />
      {shot.callout && sec >= (shot.callout.at ?? 0) ? (
        <CalloutView text={shot.callout.text} from={shot.callout.from} to={shot.callout.to} age={local - Math.round((shot.callout.at ?? 0) * fps)} />
      ) : null}
      {shot.headline ? <Headline text={shot.headline} age={local} /> : null}
      {shot.cross ? <Cross age={local} /> : null}
      {shot.big ? <BigNumber value={shot.big.value} sub={shot.big.sub} age={local} /> : null}
      {shot.title ? <Title text={shot.title} age={local} /> : null}
      <HUD status={shot.status} step={shot.step} />
      <CaptionPill text={cap.text} hi={cap.hi} age={capAge} />
      <Flash opacity={flash} />
    </AbsoluteFill>
  );
};
