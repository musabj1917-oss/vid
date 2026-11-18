import React from 'react';
import { loadFont as loadHeavy } from '@remotion/google-fonts/ArchivoBlack';
import { loadFont as loadMono } from '@remotion/google-fonts/JetBrainsMono';

const HEAVY = loadHeavy().fontFamily;
const MONO = loadMono('normal', { weights: ['500'], subsets: ['latin'] }).fontFamily;
const AMBER = '#F5A83A';
const W = 1080;
const H = 1920;

export const Vignette: React.FC = () => (
  <div
    style={{
      position: 'absolute',
      inset: 0,
      background: 'radial-gradient(ellipse at center, rgba(0,0,0,0) 55%, rgba(0,0,0,0.55) 100%)',
      pointerEvents: 'none',
    }}
  />
);

export const HUD: React.FC<{ status: string; step: number }> = ({ status, step }) => (
  <div
    style={{
      position: 'absolute',
      top: 130,
      left: 40,
      right: 40,
      height: 84,
      borderRadius: 14,
      border: '1.5px solid rgba(255,255,255,0.18)',
      background: 'rgba(10,12,20,0.55)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '0 24px',
      fontFamily: MONO,
      fontSize: 30,
      color: '#E6E9F2',
      letterSpacing: 1,
    }}
  >
    <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
      <span style={{ width: 14, height: 14, borderRadius: 7, background: '#FFB020' }} />
      {status}
    </div>
    <div style={{ display: 'flex', gap: 14 }}>
      {[1, 2, 3, 4].map((n) => (
        <span
          key={n}
          style={{
            width: 50,
            height: 50,
            borderRadius: 25,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: 26,
            border: '1.5px solid rgba(255,255,255,0.35)',
            background: n <= step ? '#D9983F' : 'transparent',
            color: n <= step ? '#0A0C12' : '#ffffff',
          }}
        >
          {n}
        </span>
      ))}
    </div>
  </div>
);

export const CaptionPill: React.FC<{ text: string; hi?: string; age: number }> = ({ text, hi, age }) => {
  const o = Math.min(1, age / 5);
  const words = text.split(' ');
  return (
    <div
      style={{
        position: 'absolute',
        left: 0,
        right: 0,
        bottom: 430,
        display: 'flex',
        justifyContent: 'center',
        opacity: o,
        transform: `translateY(${(1 - o) * 14}px)`,
      }}
    >
      <div
        style={{
          background: 'rgba(8,10,16,0.66)',
          borderRadius: 16,
          padding: '12px 26px',
          fontFamily: HEAVY,
          fontSize: 50,
          color: '#ffffff',
          letterSpacing: 0.5,
          whiteSpace: 'nowrap',
        }}
      >
        {words.map((w, k) => {
          const on = !!hi && w.toLowerCase().replace(/[^a-z0-9']/g, '') === hi.toLowerCase();
          return (
            <span
              key={k}
              style={{
                marginRight: k < words.length - 1 ? 14 : 0,
                textDecoration: on ? 'underline' : 'none',
                textDecorationThickness: 5,
                textUnderlineOffset: 8,
                opacity: on ? 1 : 0.92,
              }}
            >
              {w}
            </span>
          );
        })}
      </div>
    </div>
  );
};

export const CalloutView: React.FC<{ text: string; from: [number, number]; to: [number, number]; age: number }> = ({
  text,
  from,
  to,
  age,
}) => {
  const p = Math.min(1, Math.max(0, age / 12));
  const x1 = (from[0] / 100) * W;
  const y1 = (from[1] / 100) * H;
  const x2 = (to[0] / 100) * W;
  const y2 = (to[1] / 100) * H;
  return (
    <>
      <svg width='100%' height='100%' viewBox={`0 0 ${W} ${H}`} style={{ position: 'absolute', inset: 0 }}>
        <line x1={x1} y1={y1} x2={x1 + (x2 - x1) * p} y2={y1 + (y2 - y1) * p} stroke='#ffffff' strokeWidth={3} strokeLinecap='round' opacity={0.9} />
        <circle cx={x2} cy={y2} r={9 * p} fill='#FFB020' />
      </svg>
      <div
        style={{
          position: 'absolute',
          left: x1,
          top: y1,
          transform: 'translate(-50%, -50%)',
          opacity: p,
          fontFamily: MONO,
          fontSize: 32,
          letterSpacing: 2,
          color: '#ffffff',
          background: 'rgba(10,12,20,0.78)',
          border: '1.5px solid rgba(255,176,32,0.8)',
          borderRadius: 8,
          padding: '8px 16px',
          whiteSpace: 'nowrap',
        }}
      >
        {text}
      </div>
    </>
  );
};

export const BigNumber: React.FC<{ value: string; sub?: string; age: number }> = ({ value, sub, age }) => {
  const o = Math.min(1, age / 6);
  return (
    <div style={{ position: 'absolute', top: 250, left: 0, right: 0, textAlign: 'center', opacity: o, transform: `scale(${0.9 + 0.1 * o})` }}>
      <div style={{ fontFamily: HEAVY, fontSize: 240, color: '#ffffff', lineHeight: 1 }}>{value}</div>
      {sub ? <div style={{ fontFamily: MONO, fontSize: 44, color: AMBER, letterSpacing: 8, marginTop: 10 }}>{sub}</div> : null}
    </div>
  );
};

export const Headline: React.FC<{ text: string; age: number; top?: number }> = ({ text, age, top = 250 }) => (
  <div
    style={{
      position: 'absolute',
      top,
      left: 0,
      right: 0,
      textAlign: 'center',
      opacity: Math.min(1, age / 6),
      fontFamily: HEAVY,
      fontSize: 140,
      color: AMBER,
      lineHeight: 1,
    }}
  >
    {text}
  </div>
);

export const Cross: React.FC<{ age: number }> = ({ age }) => {
  const p = Math.min(1, Math.max(0, (age - 8) / 10));
  const len = 900;
  return (
    <svg width='100%' height='100%' viewBox={`0 0 ${W} ${H}`} style={{ position: 'absolute', inset: 0 }}>
      <line x1={240} y1={680} x2={840} y2={1280} stroke={AMBER} strokeWidth={28} strokeLinecap='round' strokeDasharray={len} strokeDashoffset={len * (1 - p)} />
      <line x1={840} y1={680} x2={240} y2={1280} stroke={AMBER} strokeWidth={28} strokeLinecap='round' strokeDasharray={len} strokeDashoffset={len * (1 - Math.min(1, Math.max(0, p * 1.4 - 0.4)))} />
    </svg>
  );
};

export const Title: React.FC<{ text: string; age: number }> = ({ text, age }) => (
  <div
    style={{
      position: 'absolute',
      top: 250,
      left: 0,
      right: 0,
      textAlign: 'center',
      opacity: Math.min(1, age / 8),
      fontFamily: HEAVY,
      fontSize: 120,
      color: '#ffffff',
      letterSpacing: 4,
    }}
  >
    {text}
  </div>
);

export const Flash: React.FC<{ opacity: number }> = ({ opacity }) =>
  opacity > 0 ? <div style={{ position: 'absolute', inset: 0, background: '#ffffff', opacity }} /> : null;
