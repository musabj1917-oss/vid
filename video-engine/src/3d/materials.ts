import * as THREE from 'three';

export const M = {
  chrome: new THREE.MeshStandardMaterial({ color: '#cfd4dc', metalness: 1, roughness: 0.16 }),
  steel: new THREE.MeshStandardMaterial({ color: '#7b8494', metalness: 0.9, roughness: 0.32 }),
  dark: new THREE.MeshStandardMaterial({ color: '#1b2029', metalness: 0.55, roughness: 0.38 }),
  rubber: new THREE.MeshStandardMaterial({ color: '#0b0d12', metalness: 0.1, roughness: 0.7 }),
  copper: new THREE.MeshStandardMaterial({
    color: '#c8793a',
    metalness: 0.95,
    roughness: 0.26,
    emissive: '#6e2f08',
    emissiveIntensity: 0.45,
  }),
  glass: new THREE.MeshPhysicalMaterial({
    color: '#d6ebff',
    metalness: 0,
    roughness: 0.04,
    transmission: 0.92,
    thickness: 0.35,
    ior: 1.45,
    side: THREE.DoubleSide,
  }),
  floor: new THREE.MeshStandardMaterial({ color: '#0e1118', metalness: 0.7, roughness: 0.45 }),
  amber: new THREE.MeshBasicMaterial({ color: '#FFB020' }),
  white: new THREE.MeshBasicMaterial({ color: '#ffffff' }),
};

let glowTex: THREE.CanvasTexture | null = null;
export function glowTexture(): THREE.CanvasTexture {
  if (!glowTex) {
    const c = document.createElement('canvas');
    c.width = 128;
    c.height = 128;
    const g = c.getContext('2d')!;
    const gr = g.createRadialGradient(64, 64, 0, 64, 64, 64);
    gr.addColorStop(0, 'rgba(255,255,255,1)');
    gr.addColorStop(0.25, 'rgba(255,255,255,0.45)');
    gr.addColorStop(1, 'rgba(255,255,255,0)');
    g.fillStyle = gr;
    g.fillRect(0, 0, 128, 128);
    glowTex = new THREE.CanvasTexture(c);
  }
  return glowTex;
}
