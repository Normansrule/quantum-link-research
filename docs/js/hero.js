// Hero scene: the inner Solar System from the Phase 5 Kepler ephemeris, rendered with three.js.
// Green particles are entangled photons from an L4 relay to Earth and Mars; the orange pulse is the pair of
// classical bits travelling at c. Time runs at ~6 days per second; the live panel reads range and light time
// from the same functions the Python tests check (docs/js/ephemeris.js).
import * as THREE from "three";

const E = window.QLLEphemeris;
const canvas = document.getElementById("hero-canvas");
const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(42, 1, 0.1, 2000);
const S = 10; // scene units per au

function glowTexture(inner, outer) {
  const c = document.createElement("canvas"); c.width = c.height = 128;
  const g = c.getContext("2d"), r = g.createRadialGradient(64, 64, 0, 64, 64, 64);
  r.addColorStop(0, inner); r.addColorStop(0.25, inner); r.addColorStop(1, outer);
  g.fillStyle = r; g.fillRect(0, 0, 128, 128);
  return new THREE.CanvasTexture(c);
}
function sprite(tex, size, blending = THREE.AdditiveBlending) {
  const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: tex, blending, depthWrite: false, transparent: true }));
  s.scale.set(size, size, 1); return s;
}

// stars
{
  const n = 5000, pos = new Float32Array(n * 3), col = new Float32Array(n * 3);
  for (let i = 0; i < n; i++) {
    const r = 300 + Math.random() * 500, th = Math.random() * Math.PI * 2, ph = Math.acos(2 * Math.random() - 1);
    pos.set([r * Math.sin(ph) * Math.cos(th), r * Math.cos(ph), r * Math.sin(ph) * Math.sin(th)], i * 3);
    const t = Math.random(); col.set([0.75 + 0.25 * t, 0.8 + 0.2 * t, 1.0], i * 3);
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute("position", new THREE.BufferAttribute(pos, 3)); g.setAttribute("color", new THREE.BufferAttribute(col, 3));
  scene.add(new THREE.Points(g, new THREE.PointsMaterial({ size: 1.1, vertexColors: true, transparent: true, opacity: 0.85, depthWrite: false })));
}
// sun
scene.add(sprite(glowTexture("rgba(255,236,190,1)", "rgba(255,160,60,0)"), 6));
scene.add(sprite(glowTexture("rgba(255,190,120,.12)", "rgba(255,120,40,0)"), 22));

// orbits
function orbitLine(fn, period, color) {
  const pts = [];
  for (let k = 0; k <= 256; k++) { const [x, y] = fn((period * k) / 256); pts.push(new THREE.Vector3(x * S, 0, -y * S)); }
  const line = new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts), new THREE.LineBasicMaterial({ color, transparent: true, opacity: 0.35 }));
  scene.add(line);
}
orbitLine(E.earth, 365.256, 0x5ea8ff);
orbitLine(E.mars, 686.98, 0xff6b4a);

function planet(color, radius, glowColor) {
  const m = new THREE.Mesh(new THREE.SphereGeometry(radius, 32, 32), new THREE.MeshBasicMaterial({ color }));
  m.add(sprite(glowTexture(glowColor, "rgba(0,0,0,0)"), radius * 7));
  scene.add(m); return m;
}
const earth = planet(0x4f8cff, 0.32, "rgba(94,168,255,.7)");
const mars = planet(0xff6b4a, 0.24, "rgba(255,107,74,.7)");
const relay = planet(0x45e0a0, 0.14, "rgba(69,224,160,.8)");

// link lines
const linkGeom = new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(), new THREE.Vector3()]);
const link = new THREE.Line(linkGeom, new THREE.LineDashedMaterial({ color: 0xff8a4c, dashSize: 0.4, gapSize: 0.25, transparent: true, opacity: 0.7 }));
scene.add(link);

// entangled photon streams (relay → Earth, relay → Mars) and the classical bit pulse (Earth → Mars)
const N = 70;
const photonGeom = new THREE.BufferGeometry();
const photonPos = new Float32Array(N * 2 * 3);
photonGeom.setAttribute("position", new THREE.BufferAttribute(photonPos, 3));
const photonMat = new THREE.PointsMaterial({ size: 0.18, color: 0x5ef2e0, transparent: true, opacity: 0.95, blending: THREE.AdditiveBlending, depthWrite: false });
scene.add(new THREE.Points(photonGeom, photonMat));
const phase = Array.from({ length: N }, () => Math.random());
const bit = sprite(glowTexture("rgba(255,170,90,1)", "rgba(255,120,40,0)"), 1.1);
scene.add(bit);

const readRange = document.querySelector("[data-live=range]");
const readLt = document.querySelector("[data-live=lt]");
const readSep = document.querySelector("[data-live=sep]");
const readDay = document.querySelector("[data-live=day]");

let tDays = 0, bitProgress = 0, visible = true, last = performance.now();
const toV = ([x, y]) => new THREE.Vector3(x * S, 0, -y * S);

function resize() {
  const w = canvas.clientWidth, h = canvas.clientHeight;
  renderer.setSize(w, h, false); camera.aspect = w / h; camera.updateProjectionMatrix();
}
addEventListener("resize", resize); resize();
let mx = 0, my = 0;
addEventListener("pointermove", (e) => { mx = e.clientX / innerWidth - 0.5; my = e.clientY / innerHeight - 0.5; });
new IntersectionObserver((es) => { visible = es[0].isIntersecting; }).observe(canvas);

function frame(now) {
  const dt = Math.max(0, Math.min(0.05, (now - last) / 1000)); last = now;
  if (!reduce) tDays += dt * 6;
  const pe = toV(E.earth(tDays)), pm = toV(E.mars(tDays)), pr = toV(E.l4(tDays));
  earth.position.copy(pe); mars.position.copy(pm); relay.position.copy(pr);
  const lp = link.geometry.attributes.position; lp.setXYZ(0, pe.x, pe.y, pe.z); lp.setXYZ(1, pm.x, pm.y, pm.z); lp.needsUpdate = true;
  link.computeLineDistances();
  for (let i = 0; i < N; i++) {
    phase[i] = (phase[i] + dt * 0.35) % 1;
    const a = new THREE.Vector3().lerpVectors(pr, pe, phase[i]);
    const b = new THREE.Vector3().lerpVectors(pr, pm, phase[i]);
    photonPos.set([a.x, a.y + 0.02, a.z], i * 6); photonPos.set([b.x, b.y + 0.02, b.z], i * 6 + 3);
  }
  photonGeom.attributes.position.needsUpdate = true;
  const lt = E.oneWaySeconds(tDays);
  bitProgress += dt / Math.max(1.5, lt / 180); // visual speed scales with the real light time
  if (bitProgress > 1) bitProgress = 0;
  bit.position.lerpVectors(pe, pm, bitProgress);
  const sep = E.sepDeg(tDays);
  link.material.color.set(sep < 3 ? 0x5b6780 : 0xff8a4c);
  const cx = Math.sin(now * 0.00005) * 6, r = 34;
  camera.position.set(cx + mx * 6, 13 + my * 4, r);
  camera.lookAt(0, 7, 0);   // system sits in the lower part of the frame, under the headline
  renderer.render(scene, camera);
  if (readRange && Math.floor(now / 250) !== Math.floor((now - dt * 1000) / 250)) {
    readRange.textContent = (E.rangeM(tDays) / E.AU).toFixed(3) + " au";
    readLt.textContent = (lt / 60).toFixed(1) + " min";
    readSep.textContent = sep.toFixed(1) + "°";
    readSep.className = sep < 3 ? "warm" : "ok";
    readDay.textContent = "J2000 + " + Math.floor(tDays) + " d";
  }
}
function loop(now) {
  if (visible || reduce) frame(now); else last = now;   // skip work when the hero is off screen
  if (!reduce) requestAnimationFrame(loop);
}
requestAnimationFrame(loop);
