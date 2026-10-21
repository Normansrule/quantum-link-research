// The lab's 3D view: every part of a tier's real-world build (docs/lab/scenes.json, from qll/systems/lab_scenes.py)
// placed where it stands in the rooms, the beams between them, photons that travel and are lost at the rate the twin
// predicts, dark counts that flash at the detectors, and the build stages of the protocol revealed one at a time.
// Optics are drawn at twice their size so they stay visible from across the rooms; positions are to scale.
import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";

const BEAM_Y = 0.94, TOP = 0.80, OPTIC = 2.4;
const OPTICAL = new Set(["qwp", "pump", "laser", "polarizer", "nd", "bs", "pbs", "hwp", "lens", "iris", "sipm", "photodiode", "crystal", "spad", "tube", "paddles", "servo"]);
const BEAM_COLOR = { violet: 0x8b5cf6, red: 0xff3b3b, nir: 0xff6fb5, pair: 0xff9f43, pump: 0x7c3aed, classical: 0xf5c518, sync: 0x9aa4b2, usb: 0x5ea8ff, cloud: 0x5ef2e0 };
const DETECTORS = new Set(["sipm", "spad", "photodiode"]);

function mat(color, o = {}) { return new THREE.MeshStandardMaterial(Object.assign({ color, roughness: 0.55, metalness: 0.15 }, o)); }
function glass(color, opacity = 0.35) { return new THREE.MeshPhysicalMaterial({ color, transparent: true, opacity, roughness: 0.05, metalness: 0, transmission: 0.2, depthWrite: false }); }
function box(w, h, d, m) { return new THREE.Mesh(new THREE.BoxGeometry(w, h, d), m); }
function cyl(r, h, m, seg = 24) { return new THREE.Mesh(new THREE.CylinderGeometry(r, r, h, seg), m); }
function post(g, fromY, toY) { const p = cyl(0.006, toY - fromY, mat(0x9aa4b2, { metalness: 0.7 })); p.position.y = (fromY + toY) / 2 - BEAM_Y; g.add(p); }   // group origin at BEAM_Y
function labelSprite(text, size = 0.22, color = "#e8eef8") {
  const c = document.createElement("canvas"), g = c.getContext("2d"), f = 48;
  g.font = `600 ${f}px Geist, system-ui, sans-serif`; const w = Math.ceil(g.measureText(text).width) + 40;
  c.width = w; c.height = f + 28; g.font = `600 ${f}px Geist, system-ui, sans-serif`;
  g.fillStyle = "rgba(10,15,28,.72)"; g.beginPath(); g.roundRect(0, 0, w, f + 28, 18); g.fill();
  g.fillStyle = color; g.textBaseline = "middle"; g.fillText(text, 20, (f + 28) / 2 + 2);
  const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: new THREE.CanvasTexture(c), depthWrite: false, transparent: true }));
  s.scale.set(size * w / (f + 28), size, 1); s.renderOrder = 10; return s;
}

/* One builder per kind; each returns a Group whose origin is the part's position. */
const BUILD = {
  room(p) {
    const [w, d] = p.size, g = new THREE.Group(), wallM = mat(0x1b2436, { transparent: true, opacity: 0.28, side: THREE.DoubleSide, depthWrite: false }), H = 2.6;
    const floor = box(w, 0.02, d, mat(0x121a2b)); floor.position.y = -0.01; g.add(floor);
    const grid = new THREE.GridHelper(Math.max(w, d), Math.max(w, d) * 2, 0x24314a, 0x1a2336); grid.position.y = 0.002; g.add(grid);
    const back = box(w, H, 0.06, wallM); back.position.set(0, H / 2, -d / 2); g.add(back);
    const side = p.pos[0] < 0 ? -1 : 1;
    const outer = box(0.06, H, d, wallM); outer.position.set(side * w / 2, H / 2, 0); g.add(outer);
    const door = 1.0;                                                                 // hallway wall with an open door
    for (const s of [-1, 1]) { const seg = box(0.06, H, (d - door) / 2, wallM); seg.position.set(-side * w / 2, H / 2, s * (door / 2 + (d - door) / 4)); g.add(seg); }
    const lab = labelSprite(p.label, 0.28); lab.position.set(0, H + 0.25, -d / 2 + 0.2); g.add(lab);
    g.userData.static = true; return g;
  },
  hallway(p) {
    const [w, d] = p.size, g = new THREE.Group(); const f = box(w, 0.02, d, mat(0x0f1626)); f.position.y = -0.01; g.add(f);
    const lab = labelSprite(p.label, 0.2, "#93a1b8"); lab.position.set(0, 2.2, -d / 2); g.add(lab); g.userData.static = true; return g;
  },
  table(p) {
    const [w, d] = p.size.length ? p.size : [1.8, 0.9], g = new THREE.Group(), m = mat(0x3a4256, { roughness: 0.8 });
    const top = box(w, 0.04, d, m); top.position.y = TOP - 0.02; g.add(top);
    for (const sx of [-1, 1]) for (const sz of [-1, 1]) { const l = box(0.04, TOP - 0.04, 0.04, m); l.position.set(sx * (w / 2 - 0.05), (TOP - 0.04) / 2, sz * (d / 2 - 0.05)); g.add(l); }
    return g;
  },
  laser(p, ctx) {
    const g = new THREE.Group(), b = new THREE.Group();
    const body = cyl(0.011, 0.06, mat(0x2b3240, { metalness: 0.6 })); body.rotation.z = Math.PI / 2; b.add(body);
    const tip = cyl(0.008, 0.006, mat(ctx.beamColor, { emissive: ctx.beamColor, emissiveIntensity: 1.5 })); tip.rotation.z = Math.PI / 2; tip.position.x = 0.033; b.add(tip);
    const base = box(0.05, 0.012, 0.04, mat(0x1f2633)); base.position.y = -0.02; b.add(base);
    b.scale.setScalar(OPTIC); g.add(b); post(g, TOP, BEAM_Y - 0.04); return g;
  },
  polarizer() { const g = new THREE.Group(); const d = cyl(0.03 * OPTIC / 1.4, 0.004, glass(0x9fb7ff, 0.45)); d.rotation.z = Math.PI / 2; g.add(d);
    const ring = new THREE.Mesh(new THREE.TorusGeometry(0.03 * OPTIC / 1.4, 0.003, 8, 32), mat(0x222a38)); ring.rotation.y = Math.PI / 2; g.add(ring); post(g, TOP, BEAM_Y - 0.04); return g; },
  nd() { const g = new THREE.Group(); g.add(box(0.004, 0.06 * OPTIC / 1.4, 0.06 * OPTIC / 1.4, glass(0x111111, 0.85))); post(g, TOP, BEAM_Y - 0.04); return g; },
  bs(p, ctx, tint = 0xdbeafe) {
    const g = new THREE.Group(), s = 0.025 * OPTIC; g.add(box(s, s, s, glass(tint, 0.28)));
    const diag = new THREE.Mesh(new THREE.PlaneGeometry(s * 1.4, s), glass(tint === 0xdbeafe ? 0xffffff : 0x22d3ee, 0.5));
    diag.rotation.y = Math.PI / 4; g.add(diag); post(g, TOP, BEAM_Y - s / 2); return g;
  },
  pbs(p, ctx) { return BUILD.bs(p, ctx, 0x67e8f9); },
  hwp() { const g = new THREE.Group(); const d = cyl(0.022 * OPTIC / 1.4, 0.004, glass(0xffb347, 0.6)); d.rotation.z = Math.PI / 2; g.add(d); post(g, TOP, BEAM_Y - 0.03); return g; },
  qwp() { const g = new THREE.Group(); const d = cyl(0.022 * OPTIC / 1.4, 0.004, glass(0x86efac, 0.6)); d.rotation.z = Math.PI / 2; g.add(d);
    const ring = new THREE.Mesh(new THREE.TorusGeometry(0.022 * OPTIC / 1.4, 0.003, 8, 32), mat(0x14532d)); ring.rotation.y = Math.PI / 2; g.add(ring); post(g, TOP, BEAM_Y - 0.03); return g; },
  lens() { const g = new THREE.Group(); const l = new THREE.Mesh(new THREE.SphereGeometry(0.03, 24, 12), glass(0xe0f2fe, 0.45)); l.scale.set(0.25, 1, 1); l.scale.multiplyScalar(OPTIC / 1.4); g.add(l); post(g, TOP, BEAM_Y - 0.04); return g; },
  iris() { const g = new THREE.Group(); const r = new THREE.Mesh(new THREE.TorusGeometry(0.02, 0.008, 8, 24), mat(0x222a38)); r.rotation.y = Math.PI / 2; g.add(r); post(g, TOP, BEAM_Y - 0.03); return g; },
  sipm(p) {
    const g = new THREE.Group(); const pcb = box(0.003, 0.05 * OPTIC / 1.4, 0.05 * OPTIC / 1.4, mat(0x14532d)); g.add(pcb);
    const s = box(0.004, 0.02, 0.02, mat(0x111827, { emissive: 0x000000 })); s.name = "sensor"; g.add(s); post(g, TOP, BEAM_Y - 0.035);
    return g;
  },
  spad() { const g = new THREE.Group(); const b = box(0.09, 0.06, 0.06, mat(0x111827, { metalness: 0.4 })); g.add(b); const w = box(0.002, 0.012, 0.012, mat(0x1f2937)); w.name = "sensor"; w.position.x = -0.046; g.add(w); g.position.y = 0; post(g, TOP, BEAM_Y - 0.03); return g; },
  photodiode() { const g = new THREE.Group(); g.add(box(0.004, 0.03, 0.03, mat(0x0f172a))); const s = box(0.005, 0.012, 0.012, mat(0x1e293b)); s.name = "sensor"; g.add(s); post(g, TOP, BEAM_Y - 0.02); return g; },
  servo() { const g = new THREE.Group(); const b = box(0.05, 0.04, 0.025, mat(0x1d4ed8)); b.position.y = TOP + 0.02 - BEAM_Y; g.add(b); return g; },
  box(p) { const [w, h, d] = p.size, g = new THREE.Group(); const b = box(w, h, d, mat(0x05070d, { transparent: true, opacity: 0.18, depthWrite: false })); b.position.y = h / 2; g.add(b);
    const e = new THREE.LineSegments(new THREE.EdgesGeometry(new THREE.BoxGeometry(w, h, d)), new THREE.LineBasicMaterial({ color: 0x334155 })); e.position.copy(b.position); g.add(e); return g; },
  tube() { const g = new THREE.Group(); const t = cyl(0.018, 0.4, mat(0x0b0f17)); t.rotation.z = Math.PI / 2; g.add(t); post(g, TOP, BEAM_Y - 0.02); return g; },
  crystal() { const g = new THREE.Group(); g.add(box(0.03, 0.03, 0.03, glass(0xc084fc, 0.6))); post(g, TOP, BEAM_Y - 0.02); return g; },
  paddles() { const g = new THREE.Group(); for (let i = 0; i < 3; i++) { const d = cyl(0.04, 0.006, mat(0x475569)); d.rotation.z = Math.PI / 2; d.position.x = (i - 1) * 0.035; g.add(d); } return g; },
  fpga() { const g = new THREE.Group(); g.add(box(0.1, 0.004, 0.07, mat(0x166534))); const c = box(0.025, 0.004, 0.025, mat(0x111827)); c.position.y = 0.004; g.add(c);
    const led = box(0.004, 0.003, 0.004, mat(0x22c55e, { emissive: 0x22c55e, emissiveIntensity: 2 })); led.position.set(0.035, 0.004, 0.025); led.name = "led"; g.add(led); return g; },
  arduino() { const g = new THREE.Group(); g.add(box(0.07, 0.004, 0.054, mat(0x0e7490))); const c = box(0.03, 0.006, 0.01, mat(0x111827)); c.position.y = 0.004; g.add(c); return g; },
  laptop() { const g = new THREE.Group(), m = mat(0x2a3142, { metalness: 0.5 }); const base = box(0.32, 0.016, 0.22, m); g.add(base);
    const scr = new THREE.Group(); const lid = box(0.32, 0.2, 0.01, m); lid.position.y = 0.1; scr.add(lid);
    const disp = new THREE.Mesh(new THREE.PlaneGeometry(0.29, 0.17), new THREE.MeshBasicMaterial({ color: 0x0b1224 })); disp.position.set(0, 0.1, 0.0055); disp.name = "screen"; scr.add(disp);
    scr.position.z = -0.105; scr.rotation.x = -0.25; g.add(scr); return g; },
  mediaconv() { const g = new THREE.Group(); g.add(box(0.1, 0.03, 0.07, mat(0x334155))); const l = box(0.004, 0.004, 0.004, mat(0xf5c518, { emissive: 0xf5c518, emissiveIntensity: 2 })); l.position.set(0.04, 0.016, 0.03); l.name = "led"; g.add(l); return g; },
  supply() { return (() => { const g = new THREE.Group(); g.add(box(0.06, 0.025, 0.04, mat(0x52525b))); return g; })(); },
  coaxend() { const g = new THREE.Group(); const c = cyl(0.006, 0.04, mat(0x9ca3af, { metalness: 0.8 })); g.add(c); return g; },
  timetagger() { const g = new THREE.Group(); g.add(box(0.22, 0.05, 0.16, mat(0xa1a1aa, { metalness: 0.7, roughness: 0.3 }))); return g; },
  pump() { const g = new THREE.Group(); const b = box(0.28, 0.08, 0.1, mat(0x1e1b4b)); g.add(b); const w = box(0.06, 0.03, 0.002, mat(0xfacc15)); w.position.set(0, 0.0, 0.051); g.add(w); post(g, TOP, BEAM_Y - 0.04); return g; },
  spool() { const g = new THREE.Group(); const t = new THREE.Mesh(new THREE.TorusGeometry(0.16, 0.06, 16, 40), mat(0xeab308)); t.rotation.x = Math.PI / 2; g.add(t); return g; },
  fridge() { const g = new THREE.Group(), gold = mat(0xd4a017, { metalness: 0.9, roughness: 0.25 });
    [0.34, 0.3, 0.26, 0.22, 0.18].forEach((r, i) => { const pl = cyl(r, 0.025, gold, 48); pl.position.y = 2.1 - i * 0.32; g.add(pl);
      if (i) for (let k = 0; k < 3; k++) { const rod = cyl(0.012, 0.32, gold, 8); const a = k * 2.094; rod.position.set(Math.cos(a) * r * 0.7, 2.1 - i * 0.32 + 0.16, Math.sin(a) * r * 0.7); g.add(rod); } });
    const can = cyl(0.42, 2.0, mat(0x94a3b8, { transparent: true, opacity: 0.12, depthWrite: false, side: THREE.DoubleSide }), 48); can.position.y = 1.2; g.add(can);
    const frame = box(1.1, 0.06, 1.1, mat(0x334155)); frame.position.y = 2.35; g.add(frame); return g; },
  chip() { const g = new THREE.Group(); g.add(box(0.12, 0.01, 0.12, mat(0x0f172a)));
    for (let i = 0; i < 4; i++) for (let j = 0; j < 4; j++) { const q = new THREE.Mesh(new THREE.SphereGeometry(0.006, 8, 6), mat(0x5ef2e0, { emissive: 0x5ef2e0, emissiveIntensity: 1 })); q.position.set(-0.042 + i * 0.028, 0.008, -0.042 + j * 0.028); q.name = "qubit"; g.add(q); }
    g.position.y = 0; return g; },
  nanowire() { const g = new THREE.Group(); g.add(box(0.3, 0.01, 0.16, mat(0x1f2937)));
    for (const z of [-0.04, 0.04]) { const w = cyl(0.004, 0.24, mat(0x94a3b8, { metalness: 0.8 }), 8); w.rotation.z = Math.PI / 2; w.position.set(0, 0.01, z); g.add(w);
      for (const x of [-0.12, 0, 0.12]) { const m0 = new THREE.Mesh(new THREE.SphereGeometry(0.01, 12, 8), mat(0xa78bfa, { emissive: 0xa78bfa, emissiveIntensity: 1.6 })); m0.position.set(x, 0.016, z); m0.name = "qubit"; g.add(m0); } }
    return g; },
  building(p) {
    const [w, h, d] = p.size, g = new THREE.Group(), m = mat(0x3b4763, { roughness: 0.9 });
    const b = box(w, h, d, m); b.position.y = h / 2; g.add(b);
    const roof = box(w - 0.1, 0.06, d - 0.1, mat(0x5b6683, { roughness: 1 })); roof.position.y = h + 0.03; g.add(roof);
    const win = mat(0x5ea8ff, { emissive: 0x1d4ed8, emissiveIntensity: 0.35 });
    for (let fl = 1; fl < h / 3; fl++) for (let k = -2; k <= 2; k++) for (const side of [-1, 1]) { const wdw = box(0.6, 0.9, 0.02, win); wdw.position.set(k * w / 5.5, fl * 3, side * (d / 2 + 0.01)); g.add(wdw); }
    for (const z of [-1, 1]) { const parapet = box(w, 0.4, 0.15, m); parapet.position.set(0, h + 0.2, z * d / 2); g.add(parapet); }
    const lab = labelSprite(p.label, 0.6); lab.position.set(0, h + 2.2, -d / 2 + 0.5); g.add(lab);
    g.userData.static = true; return g;
  },
  telescope(p) {
    const g = new THREE.Group(), r = (p.size[0] || 0.1) / 2, len = p.size[1] || 0.5;
    const pier = cyl(0.04, 0.8, mat(0x475569)); pier.position.y = 0.4; g.add(pier);
    const head = new THREE.Group(); head.name = "aim"; head.position.y = 0.9;
    const tube = cyl(r * 1.3, len, mat(0xe2e8f0, { metalness: 0.4, roughness: 0.35 }), 24); tube.rotation.z = Math.PI / 2; tube.position.x = len * 0.3; head.add(tube);
    const lensM = new THREE.Mesh(new THREE.CircleGeometry(r * 1.2, 24), glass(0x93c5fd, 0.6)); lensM.rotation.y = Math.PI / 2; lensM.position.x = len * 0.8 + 0.001; head.add(lensM);
    g.add(head); head.rotation.y = -(p.rot || 0) * Math.PI / 180;
    return g;
  },
  dome(p) {
    const g = new THREE.Group(), r = p.size[0] || 2.5, m = mat(0xd4d4d8, { metalness: 0.5, roughness: 0.35 });
    const wall = cyl(r, 2.2, mat(0x94a3b8), 48); wall.position.y = 1.1; g.add(wall);
    const cap = new THREE.Mesh(new THREE.SphereGeometry(r, 48, 24, 0, Math.PI * 2, 0, Math.PI / 2), mat(0xd4d4d8, { metalness: 0.5, roughness: 0.35, side: THREE.DoubleSide, transparent: true, opacity: 0.45 }));
    cap.position.y = 2.2; g.add(cap);
    const lab = labelSprite(p.label, 0.5); lab.position.set(0, 2.2 + r + 0.9, 0); g.add(lab);
    g.userData.static = true; return g;
  },
  satellite(p) {
    const g = new THREE.Group(), m = mat(0xd4a017, { metalness: 0.8, roughness: 0.3 });
    g.add(box(0.5, 0.5, 0.7, m));
    for (const s of [-1, 1]) { const pan = box(1.4, 0.03, 0.6, mat(0x1e3a8a, { metalness: 0.6, emissive: 0x1e3a8a, emissiveIntensity: 0.3 })); pan.position.x = s * 1.0; g.add(pan); }
    const ap = cyl(0.12, 0.2, mat(0x0f172a)); ap.position.y = -0.33; g.add(ap);
    const lab = labelSprite(p.label, 0.5); lab.position.set(0, 1.0, 0); g.add(lab); g.scale.setScalar(1.4);
    return g;
  },
  planet(p) {
    const r = p.size[0] || 1, col = p.size[1] || 0x2f6fd6, g = new THREE.Group();
    const ball = new THREE.Mesh(new THREE.SphereGeometry(r, 48, 32), mat(col, { roughness: 0.85, emissive: col, emissiveIntensity: 0.12 })); g.add(ball);
    const halo = new THREE.Mesh(new THREE.SphereGeometry(r * 1.06, 48, 32), new THREE.MeshBasicMaterial({ color: col, transparent: true, opacity: 0.12, depthWrite: false })); g.add(halo);
    const lab = labelSprite(p.label, 0.6); lab.position.set(0, r + 0.8, 0); g.add(lab);
    return g;
  },
  note(p) { const g = new THREE.Group(), l = labelSprite(p.label, p.size[0] || 0.5, "#fde68a"); g.add(l); g.userData.static = true; return g; },
  ground(p) {
    const [w, d] = p.size, g = new THREE.Group(); const f = box(w, 0.04, d, mat(0x13241c, { roughness: 1 })); f.position.y = -0.02; g.add(f);
    const grid = new THREE.GridHelper(Math.max(w, d), Math.max(w, d) / 2, 0x24314a, 0x1a2336); grid.position.y = 0.003; g.add(grid);
    g.userData.static = true; return g;
  },
  cloud() { const g = new THREE.Group(); const s = new THREE.Mesh(new THREE.IcosahedronGeometry(0.35, 1), new THREE.MeshBasicMaterial({ color: 0x5ef2e0, wireframe: true, transparent: true, opacity: 0.5 })); s.name = "spin"; g.add(s); return g; },
};

function placePart(p, ctx) {
  const build = BUILD[p.kind]; if (!build) return null;
  const g = build(p, ctx);
  // a part "on a bench" sits 0.6-1.3 m above a table's floor (rooms at ground level, or tables on a roof)
  const table = ctx.tables.find((t) => p.pos[1] - t.y > 0.6 && p.pos[1] - t.y < 1.3 && Math.abs(p.pos[0] - t.x) <= t.w / 2 + 0.05 && Math.abs(p.pos[2] - t.z) <= t.d / 2 + 0.05);
  const floorY = table ? table.y : 0, benchHeight = p.pos[1] - floorY > 0.6 && p.pos[1] - floorY < 1.3;
  if (OPTICAL.has(p.kind) && benchHeight) g.position.set(p.pos[0], floorY + BEAM_Y, p.pos[2]);
  else if (table) {                                       // sits on the bench: lift so its lowest point touches the top
    const bb = new THREE.Box3().setFromObject(g); g.children.forEach((c) => (c.position.y -= bb.min.y)); g.position.set(p.pos[0], floorY + TOP, p.pos[2]);
  } else g.position.set(p.pos[0], p.pos[1], p.pos[2]);
  if (["laser", "sipm", "spad", "photodiode", "polarizer", "hwp", "qwp", "nd", "lens", "iris"].includes(p.kind)) g.rotation.y = -(p.rot || 0) * Math.PI / 180;
  g.userData.part = p;
  g.traverse((o) => { if (o.isMesh) o.userData.part = p; });
  return g;
}

export function createLab(container, opts = {}) {
  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false, preserveDrawingBuffer: !!opts.preserve });
  renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
  renderer.setClearColor(0x05070d);
  container.appendChild(renderer.domElement);
  const scene = new THREE.Scene(); scene.fog = new THREE.Fog(0x05070d, 18, 40);
  const camera = new THREE.PerspectiveCamera(45, 1, 0.02, 200);
  const controls = new OrbitControls(camera, renderer.domElement); controls.enableDamping = true; controls.target.set(0, 0.9, 0);
  scene.add(new THREE.HemisphereLight(0xbfd4ff, 0x0b0f17, 0.9));
  const sun = new THREE.DirectionalLight(0xffffff, 1.4); sun.position.set(4, 8, 6); scene.add(sun);
  const root = new THREE.Group(); scene.add(root);
  const tip = document.createElement("div"); tip.className = "lab3d-tip"; tip.hidden = true; container.appendChild(tip);

  let tier = null, stage = 99, values = {}, rates = { photons: 6, transmit: 0.5, dark: 0.5, packets: 1 }, focusParam = "";
  let partObjs = [], beamObjs = [], detectors = [], photons = [], packets = [], mainPath = null, flashes = [], paused = false;
  const raycaster = new THREE.Raycaster(), mouse = new THREE.Vector2();
  const listeners = { pick: [] };

  function clear() { while (root.children.length) { const o = root.children.pop(); o.traverse((x) => { x.geometry && x.geometry.dispose(); }); } partObjs = []; beamObjs = []; detectors = []; photons = []; packets = []; flashes = []; }
  function beamMesh(b) {
    const g = new THREE.Group(), color = BEAM_COLOR[b.kind] || 0xffffff;
    const thick = b.kind === "classical" || b.kind === "sync" || b.kind === "usb" ? 0.008 : b.kind === "red" ? 0.006 : 0.005;
    const m = new THREE.MeshBasicMaterial({ color, transparent: true, opacity: b.kind === "nir" ? 0.45 : 0.85, depthWrite: false });
    const pts = b.points.map((q) => new THREE.Vector3(q[0], q[1], q[2]));
    for (let i = 0; i + 1 < pts.length; i++) {
      const a = pts[i], c = pts[i + 1], len = a.distanceTo(c); if (len < 1e-6) continue;
      const seg = new THREE.Mesh(new THREE.CylinderGeometry(thick, thick, len, 6), m);
      seg.position.copy(a).add(c).multiplyScalar(0.5); seg.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), c.clone().sub(a).normalize()); g.add(seg);
    }
    g.userData.beam = b; g.userData.pts = pts; g.userData.mat = m;
    const lens = [0]; for (let i = 1; i < pts.length; i++) lens.push(lens[i - 1] + pts[i].distanceTo(pts[i - 1]));
    g.userData.lens = lens; return g;
  }
  function along(beam, s) {
    const { pts, lens } = beam.userData, L = lens[lens.length - 1], d = Math.min(L, Math.max(0, s * L));
    let i = 1; while (i < lens.length - 1 && lens[i] < d) i++;
    const t = (d - lens[i - 1]) / Math.max(1e-9, lens[i] - lens[i - 1]);
    return pts[i - 1].clone().lerp(pts[i], t);
  }

  let labelsOn = false, labelGroup = null;
  const NO_LABEL = new Set(["room", "hallway", "table", "box", "tube", "coaxend", "building", "dome", "note", "ground", "satellite", "planet"]);
  function buildLabels() {
    labelGroup = new THREE.Group(); labelGroup.visible = labelsOn;
    for (const o of partObjs) {
      const p = o.userData.part; if (NO_LABEL.has(p.kind)) continue;
      const s = labelSprite(p.label.length > 30 ? p.label.slice(0, 28) + "…" : p.label, 0.045);
      s.position.copy(o.position).add(new THREE.Vector3(0, OPTICAL.has(p.kind) ? 0.13 : 0.16, 0)); s.userData.part = p; labelGroup.add(s);
    }
    root.add(labelGroup);
  }
  function setLabels(on) { labelsOn = !!on; if (labelGroup) { labelGroup.visible = labelsOn; labelGroup.children.forEach((s) => { const o = partObjs.find((x) => x.userData.part === s.userData.part); s.visible = !!(o && o.visible); }); } }
  function setTier(t, opt = {}) {
    clear(); bloch = null; ellipsoid = null; cone = null; tier = t; renderer.setClearColor(0x05070d); scene.fog.color.set(0x05070d); scene.fog.near = 18; scene.fog.far = 40; if (hemi) hemi.intensity = 0.9;
    const quantumKinds = new Set(["violet", "red", "nir", "pair"]);
    const firstQ = t.beams.find((b) => quantumKinds.has(b.kind));
    const ctx = { beamColor: firstQ ? BEAM_COLOR[firstQ.kind] : 0x8b5cf6,
      tables: t.parts.filter((p) => p.kind === "table").map((p) => ({ x: p.pos[0], y: p.pos[1], z: p.pos[2], w: (p.size[0] || 1.8), d: (p.size[1] || 0.9) })) };
    for (const p of t.parts) { const o = placePart(p, ctx); if (!o) continue; root.add(o); partObjs.push(o); if (DETECTORS.has(p.kind)) detectors.push(o); }
    for (const b of t.beams) { const o = beamMesh(b); root.add(o); beamObjs.push(o); }
    if (!t.rooms && !t.parts.some((p) => p.kind === "planet")) { const fl = new THREE.GridHelper(12, 24, 0x24314a, 0x141c2c); fl.userData.static = true; root.add(fl); }
    mainPath = beamObjs.find((o) => o.userData.beam.main) || beamObjs.filter((o) => quantumKinds.has(o.userData.beam.kind)).sort((a, b) => b.userData.lens.at(-1) - a.userData.lens.at(-1))[0] || null;
    buildLabels();
    stage = opt.stage ?? 99; applyStage(); view(opt.view || "overview", true);
  }
  function applyStage() {
    for (const o of partObjs) { const p = o.userData.part, eve = p.id.startsWith("eve"); o.visible = p.stage <= stage && (!eve || (values.eve_fraction || 0) > 0); }
    for (const o of beamObjs) o.visible = o.userData.beam.stage <= stage;
    setLabels(labelsOn);
  }
  function setStage(n) { stage = n; applyStage(); }
  function setValues(v, r) { values = Object.assign({}, v); if (r) rates = Object.assign(rates, r); applyStage();
    for (const o of beamObjs) { const b = o.userData.beam; if (b.kind === "violet" || b.kind === "nir" || b.kind === "pair") o.userData.mat.opacity = 0.25 + 0.6 * Math.min(1, rates.beam ?? 0.6); if (b.kind === "red") o.userData.mat.opacity = 0.3 + 0.7 * Math.min(1, rates.beam ?? 1); } }
  function setFocus(param) { focusParam = param || ""; }
  const VIEWS = { overview: [[0.6, 5.6, 9.6], [0, 0.6, -0.3]], roomA: [[-3.6, 1.9, 1.9], [-5.1, 0.92, 0]], roomB: [[6.2, 1.8, 1.6], [4.7, 0.92, -0.3]],
    hallway: [[0, 2.2, 3.5], [0, 1.0, 0]], sphere: [[2.5, 2.1, 2.9], [0.6, 1.4, 0.4]], bench: [[-3.6, 1.9, 1.6], [-5, 0.95, 0]], desk: [[3.8, 2.6, 4.6], [0, 1.2, 0]],
    roofs: [[0, 15, 23], [0, 4.5, 0]], sendRoof: [[-4.5, 9.5, 5], [-9, 6.9, 0]], recvRoof: [[4.5, 9.5, 5], [9, 6.9, 0]], station: [[15, 8, 27], [0, 6, 0]], sky: [[0, 3, 26], [0, 10, 0]],
    nodes: [[0, 8.5, 9], [0, 0.5, 0]], nodeC: [[1.6, 2.4, 2.9], [0, 0.9, 0]], nodeB: [[8.2, 2.5, 3.0], [6, 0.9, 0]], planets: [[0, 9, 25], [0, 4, 0]], earth: [[-3.5, 6, 9], [-8, 3, 0]] };
  let fly = null;
  function view(name, instant) {
    let v = VIEWS[name] || VIEWS.overview;
    if (tier && !tier.rooms && name === "overview") v = tier.parts.some((p) => p.kind === "fridge") ? VIEWS.desk : VIEWS.bench;
    const to = { pos: new THREE.Vector3(...v[0]), tgt: new THREE.Vector3(...v[1]) };
    if (instant) { camera.position.copy(to.pos); controls.target.copy(to.tgt); fly = null; } else fly = { from: { pos: camera.position.clone(), tgt: controls.target.clone() }, to, t: 0 };
  }
  function partAt(ev) {
    const r = renderer.domElement.getBoundingClientRect();
    mouse.set(((ev.clientX - r.left) / r.width) * 2 - 1, -((ev.clientY - r.top) / r.height) * 2 + 1);
    raycaster.setFromCamera(mouse, camera);
    const hits = raycaster.intersectObjects(partObjs.filter((o) => o.visible && !o.userData.static && o.userData.part.kind !== "table"), true);
    return hits.length ? hits[0].object.userData.part : null;
  }
  renderer.domElement.addEventListener("pointermove", (ev) => {
    const p = partAt(ev); tip.hidden = !p; if (!p) return;
    const r = container.getBoundingClientRect(); tip.textContent = p.label; tip.style.left = ev.clientX - r.left + 14 + "px"; tip.style.top = ev.clientY - r.top + 10 + "px";
  });
  let down = null;
  renderer.domElement.addEventListener("pointerdown", (ev) => { down = [ev.clientX, ev.clientY]; });
  renderer.domElement.addEventListener("pointerup", (ev) => { if (!down || Math.hypot(ev.clientX - down[0], ev.clientY - down[1]) > 5) return; const p = partAt(ev); listeners.pick.forEach((f) => f(p)); });

  // ---------------------------------------------------------------------------------------------- animation
  const photonGeo = new THREE.SphereGeometry(0.018, 10, 8);
  const POL = [0, Math.PI / 2, Math.PI / 4, 3 * Math.PI / 4];            // H, V, D, A: the four BB84 polarizations
  const barGeo = new THREE.CylinderGeometry(0.004, 0.004, 0.09, 6);
  function spawnPhoton(kind) {
    if (!mainPath || !mainPath.visible) return;
    const color = BEAM_COLOR[mainPath.userData.beam.kind] || 0xffffff;
    const g = new THREE.Group(), mat = new THREE.MeshBasicMaterial({ color, transparent: true, opacity: 1 });
    g.add(new THREE.Mesh(photonGeo, mat));
    const bar = new THREE.Mesh(barGeo, new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.9 })); g.add(bar);
    const lost = Math.random() > rates.transmit, lossAt = 0.15 + 0.8 * Math.random();
    root.add(g); photons.push({ m: g, mat, bar, phi: POL[Math.floor(Math.random() * 4)], s: 0, lost, lossAt, speed: 0.22 + 0.04 * Math.random() });
  }
  const _up = new THREE.Vector3(0, 1, 0), _y = new THREE.Vector3(0, 1, 0);
  function orientBar(ph) {                                   // the polarization bar lies across the direction of travel
    const a = along(mainPath, ph.s), b = along(mainPath, Math.min(1, ph.s + 0.002)), d = b.sub(a);
    if (d.lengthSq() < 1e-12) return; d.normalize();
    const e2 = new THREE.Vector3().crossVectors(d, _up); if (e2.lengthSq() < 1e-9) e2.set(1, 0, 0); e2.normalize();
    const e1 = new THREE.Vector3().crossVectors(e2, d).normalize();
    const v = e2.multiplyScalar(Math.cos(ph.phi)).add(e1.multiplyScalar(Math.sin(ph.phi)));
    ph.bar.quaternion.setFromUnitVectors(_y, v);
  }
  function flash(det, color) {
    const s = det.getObjectByName("sensor"); if (!s) return;
    s.material = s.material.clone(); s.material.emissive = new THREE.Color(color); s.material.emissiveIntensity = 3; flashes.push({ s, t: 0.25 });
  }
  function spawnPacket(beam) {
    const m = new THREE.Mesh(new THREE.BoxGeometry(0.06, 0.03, 0.03), new THREE.MeshBasicMaterial({ color: BEAM_COLOR[beam.userData.beam.kind] }));
    root.add(m); packets.push({ m, beam, s: 0, speed: 0.35 });
  }
  const clock = new THREE.Clock(); let acc = 0, accDark = 0, accPk = 0;
  function frame() {
    const dt = Math.min(0.05, clock.getDelta());
    if (fly) { fly.t = Math.min(1, fly.t + dt * 1.6); const e = 1 - Math.pow(1 - fly.t, 3); camera.position.lerpVectors(fly.from.pos, fly.to.pos, e); controls.target.lerpVectors(fly.from.tgt, fly.to.tgt, e); if (fly.t >= 1) fly = null; }
    controls.update();
    if (!paused) {
      acc += dt * rates.photons; while (acc > 1) { acc -= 1; spawnPhoton(); }
      for (let i = photons.length - 1; i >= 0; i--) {
        const ph = photons[i]; ph.s += dt * ph.speed * 10 / Math.max(1, mainPath ? mainPath.userData.lens.at(-1) : 10);
        if (ph.lost && ph.s > ph.lossAt) { ph.mat.opacity -= dt * 4; ph.bar.material.opacity = ph.mat.opacity; ph.m.scale.multiplyScalar(1 + dt * 3); if (ph.mat.opacity <= 0) { root.remove(ph.m); photons.splice(i, 1); } continue; }
        if (ph.s >= 1 || !mainPath) { root.remove(ph.m); photons.splice(i, 1); const vis = detectors.filter((d) => d.visible && d.position.x > 0 === (mainPath && along(mainPath, 1).x > 0)); if (vis.length) flash(vis[Math.floor(Math.random() * vis.length)], 0x5ef2e0); continue; }
        ph.m.position.copy(along(mainPath, ph.s)); orientBar(ph);
      }
      accDark += dt * rates.dark; while (accDark > 1) { accDark -= 1; const vis = detectors.filter((d) => d.visible); if (vis.length) flash(vis[Math.floor(Math.random() * vis.length)], 0xff8a4c); }
      accPk += dt * rates.packets; while (accPk > 1) { accPk -= 1; for (const b of beamObjs) if (b.visible && ["classical", "sync", "cloud", "usb"].includes(b.userData.beam.kind)) spawnPacket(b); }
      for (let i = packets.length - 1; i >= 0; i--) { const k = packets[i]; k.s += dt * k.speed * 6 / Math.max(1, k.beam.userData.lens.at(-1)); if (k.s >= 1) { root.remove(k.m); packets.splice(i, 1); continue; } k.m.position.copy(along(k.beam, k.s)); }
      for (let i = flashes.length - 1; i >= 0; i--) { const f = flashes[i]; f.t -= dt; f.s.material.emissiveIntensity = Math.max(0, f.t * 12); if (f.t <= 0) flashes.splice(i, 1); }
      root.traverse((o) => { if (o.name === "spin") o.rotation.y += dt * 0.3; });
    }
    const pulse = 0.5 + 0.5 * Math.sin(performance.now() / 180);
    for (const o of partObjs) {
      const on = focusParam && o.userData.part.param === focusParam;
      o.traverse((x) => { if (x.isMesh && x.material && x.material.emissive && x.name !== "sensor" && x.name !== "led" && x.name !== "qubit") {
        if (on) { if (!x.userData.hl) { x.material = x.material.clone(); x.userData.hl = true; } x.material.emissive.setHex(0x5ef2e0); x.material.emissiveIntensity = 0.4 + 0.8 * pulse; }
        else if (x.userData.hl) { x.material.emissiveIntensity = 0; } } });
    }
    renderer.render(scene, camera);
  }
  function resize() { const w = container.clientWidth, h = container.clientHeight; renderer.setSize(w, h, false); camera.aspect = w / Math.max(1, h); camera.updateProjectionMatrix(); }
  new ResizeObserver(resize).observe(container); resize();
  renderer.setAnimationLoop(frame);
  /* A Bloch sphere hovering over the desk: each entry {v: [x, y, z], color, label}; a zero vector is the maximally
     mixed state I/2 and shows as a dot at the centre. */
  let bloch = null;
  function setBloch(list, at = [1.45, 1.45, 1.15], r = 0.42) {
    if (bloch) { root.remove(bloch); bloch = null; }
    if (!list || !list.length) return;
    bloch = new THREE.Group(); bloch.position.set(...at);
    bloch.add(new THREE.Mesh(new THREE.SphereGeometry(r, 32, 16), new THREE.MeshBasicMaterial({ color: 0x5ea8ff, wireframe: true, transparent: true, opacity: 0.12 })));
    const ax = (d, c) => { const g = new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(...d.map((x) => -x * r)), new THREE.Vector3(...d.map((x) => x * r))]); bloch.add(new THREE.Line(g, new THREE.LineBasicMaterial({ color: c, transparent: true, opacity: 0.5 }))); };
    ax([1, 0, 0], 0xff8a4c); ax([0, 0, 1], 0x45e0a0); ax([0, 1, 0], 0x5ea8ff);
    const z0 = labelSprite("|0⟩", 0.07); z0.position.set(0, r + 0.07, 0); bloch.add(z0);
    const z1 = labelSprite("|1⟩", 0.07); z1.position.set(0, -r - 0.07, 0); bloch.add(z1);
    for (const e of list) {
      const [x, y, z] = e.v, len = Math.hypot(x, y, z), dir = new THREE.Vector3(x, z, -y);   // Bloch z up, y into the screen
      if (len < 1e-6) { const d = new THREE.Mesh(new THREE.SphereGeometry(0.025, 16, 12), new THREE.MeshBasicMaterial({ color: e.color })); bloch.add(d); }
      else bloch.add(new THREE.ArrowHelper(dir.clone().normalize(), new THREE.Vector3(), len * r, e.color, 0.06, 0.035));
      if (e.label) { const l = labelSprite(e.label, 0.06); l.position.copy(len < 1e-6 ? new THREE.Vector3(0.09, 0.05, 0) : dir.clone().multiplyScalar(r * 1.15)); bloch.add(l); }
    }
    root.add(bloch);
  }
  /* A channel's action on the Bloch sphere: the faint sphere of all inputs, the ellipsoid of outputs r -> T r + t,
     and where the six cardinal inputs land. R is the 4 x 4 Pauli transfer matrix (qll/circuits/qubit_channel.py). */
  let ellipsoid = null;
  const toThree = (b) => new THREE.Vector3(b[0], b[2], -b[1]);
  function setEllipsoid(R, at = [0, 1.75, 0.6], r = 0.5) {
    if (ellipsoid) { root.remove(ellipsoid); ellipsoid = null; }
    if (!R) return;
    ellipsoid = new THREE.Group(); ellipsoid.position.set(...at);
    ellipsoid.add(new THREE.Mesh(new THREE.SphereGeometry(r, 32, 16), new THREE.MeshBasicMaterial({ color: 0x5ea8ff, wireframe: true, transparent: true, opacity: 0.1 })));
    const map = (b) => [0, 1, 2].map((i) => R[i + 1][0] + R[i + 1][1] * b[0] + R[i + 1][2] * b[1] + R[i + 1][3] * b[2]);
    const geo = new THREE.SphereGeometry(r, 48, 24), pos = geo.attributes.position;
    for (let k = 0; k < pos.count; k++) {
      const v = new THREE.Vector3(pos.getX(k), pos.getY(k), pos.getZ(k)).divideScalar(r), out = toThree(map([v.x, -v.z, v.y])).multiplyScalar(r);
      pos.setXYZ(k, out.x, out.y, out.z);
    }
    geo.computeVertexNormals();
    ellipsoid.add(new THREE.Mesh(geo, new THREE.MeshStandardMaterial({ color: 0x5ef2e0, transparent: true, opacity: 0.32, roughness: 0.4, depthWrite: false, side: THREE.DoubleSide })));
    ellipsoid.add(new THREE.LineSegments(new THREE.WireframeGeometry(geo), new THREE.LineBasicMaterial({ color: 0x5ef2e0, transparent: true, opacity: 0.25 })));
    const ax = (d, c) => { const g = new THREE.BufferGeometry().setFromPoints([toThree(d.map((x) => -x * r * 1.15)), toThree(d.map((x) => x * r * 1.15))]); ellipsoid.add(new THREE.Line(g, new THREE.LineBasicMaterial({ color: c, transparent: true, opacity: 0.6 }))); };
    ax([1, 0, 0], 0xff8a4c); ax([0, 1, 0], 0x5ea8ff); ax([0, 0, 1], 0x45e0a0);
    const INPUTS = { H: [0, 0, 1], V: [0, 0, -1], D: [1, 0, 0], A: [-1, 0, 0], R: [0, 1, 0], L: [0, -1, 0] };
    for (const [name, b] of Object.entries(INPUTS)) {
      const from = toThree(b).multiplyScalar(r), to = toThree(map(b)).multiplyScalar(r);
      const dot = new THREE.Mesh(new THREE.SphereGeometry(0.018, 12, 8), new THREE.MeshBasicMaterial({ color: 0xfde68a })); dot.position.copy(to); ellipsoid.add(dot);
      const g = new THREE.BufferGeometry().setFromPoints([from, to]); ellipsoid.add(new THREE.Line(g, new THREE.LineBasicMaterial({ color: 0xfde68a, transparent: true, opacity: 0.55 })));
      const l = labelSprite(name, 0.06); l.position.copy(from.clone().multiplyScalar(1.22)); ellipsoid.add(l);
    }
    const t = labelSprite("Bloch sphere: inputs (blue) → outputs (cyan)", 0.055); t.position.set(0, r * 1.45, 0); ellipsoid.add(t);
    root.add(ellipsoid);
  }
  /* Outdoor helpers: the sky's brightness, moving and aiming parts, and a beam drawn as a widening cone. */
  const hemi = scene.children.find((o) => o.isHemisphereLight);
  function setSky(radiance) {
    const lv = Math.log10(Math.max(radiance, 1e-10));                    // -10 .. 0
    const day = Math.min(1, Math.max(0, (lv + 4) / 3)), dusk = Math.max(0, 1 - Math.abs(lv + 3) / 1.5) * 0.6;
    const col = new THREE.Color(0x05070d).lerp(new THREE.Color(0x2b5f9e), day).lerp(new THREE.Color(0x6b3f5e), dusk * (1 - day));
    renderer.setClearColor(col); scene.fog.color.copy(col); scene.fog.near = 30; scene.fog.far = 120;
    if (hemi) hemi.intensity = 0.9 + 1.4 * day;
  }
  const objById = (id) => partObjs.find((o) => o.userData.part.id === id);
  function movePart(id, pos) { const o = objById(id); if (o) o.position.set(...pos); }
  function aimPart(id, target) {
    const o = objById(id); if (!o) return; const head = o.getObjectByName("aim"); if (!head) return;
    const wp = new THREE.Vector3(); head.getWorldPosition(wp); const d = new THREE.Vector3(...target).sub(wp);
    head.rotation.set(0, Math.atan2(-d.z, d.x), Math.atan2(d.y, Math.hypot(d.x, d.z)), "YZX");
  }
  let cone = null;
  function setCone(from, to, r0, r1, color = 0x8b5cf6) {
    if (cone) { root.remove(cone); cone = null; } if (!from) return;
    const a = new THREE.Vector3(...from), b = new THREE.Vector3(...to), len = a.distanceTo(b);
    cone = new THREE.Mesh(new THREE.CylinderGeometry(r1, r0, len, 32, 1, true), new THREE.MeshBasicMaterial({ color, transparent: true, opacity: 0.16, side: THREE.DoubleSide, depthWrite: false }));
    cone.position.copy(a).add(b).multiplyScalar(0.5); cone.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), b.clone().sub(a).normalize());
    root.add(cone);
  }
  return { setTier, setStage, setValues, setFocus, view, setBloch, setEllipsoid, setLabels, setSky, movePart, aimPart, setCone, onPick: (f) => listeners.pick.push(f), pause: (v) => (paused = v),
    get stage() { return stage; }, renderer, scene, camera, partCount: () => partObjs.filter((o) => o.visible).length, visibleIds: () => partObjs.filter((o) => o.visible).map((o) => o.userData.part.id) };
}
