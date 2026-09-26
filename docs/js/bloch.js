// Interactive Bloch sphere (three.js). The state is a pair of complex amplitudes; gates multiply it exactly and
// the arrow animates along the shortest rotation between the old and new Bloch vectors. Probabilities are Born-rule.
import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";

const canvas = document.getElementById("bloch-canvas");
if (canvas) {
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
  renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(40, 1, 0.1, 100);
  camera.position.set(3.1, 2.2, 3.4);
  const controls = new OrbitControls(camera, canvas); controls.enableDamping = true; controls.enablePan = false; controls.minDistance = 3; controls.maxDistance = 8;

  scene.add(new THREE.Mesh(new THREE.SphereGeometry(1, 48, 32), new THREE.MeshBasicMaterial({ color: 0x5ea8ff, transparent: true, opacity: 0.06 })));
  scene.add(new THREE.LineSegments(new THREE.WireframeGeometry(new THREE.SphereGeometry(1, 24, 12)), new THREE.LineBasicMaterial({ color: 0x5ea8ff, transparent: true, opacity: 0.12 })));
  const ring = (rot) => { const g = new THREE.RingGeometry(0.995, 1.005, 128); const m = new THREE.Mesh(g, new THREE.MeshBasicMaterial({ color: 0x93a1b8, side: THREE.DoubleSide, transparent: true, opacity: 0.4 })); m.rotation.set(...rot); scene.add(m); };
  ring([Math.PI / 2, 0, 0]); ring([0, 0, 0]); ring([0, Math.PI / 2, 0]);
  // physics axes: x -> three x, y -> three -z, z -> three y
  const phys = (x, y, z) => new THREE.Vector3(x, z, -y);
  const axis = (v, color) => scene.add(new THREE.ArrowHelper(v.clone().normalize(), new THREE.Vector3(), 1.25, color, 0.06, 0.04));
  axis(phys(1, 0, 0), 0x93a1b8); axis(phys(0, 1, 0), 0x93a1b8); axis(phys(0, 0, 1), 0x93a1b8);
  function label(text, v) {
    const c = document.createElement("canvas"); c.width = 128; c.height = 64; const g = c.getContext("2d");
    g.fillStyle = "#e8eef8"; g.font = "600 34px JetBrains Mono, monospace"; g.textAlign = "center"; g.fillText(text, 64, 44);
    const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: new THREE.CanvasTexture(c), transparent: true })); s.scale.set(0.42, 0.21, 1); s.position.copy(v); scene.add(s);
  }
  label("|0⟩", phys(0, 0, 1.42)); label("|1⟩", phys(0, 0, -1.42)); label("|+⟩", phys(1.45, 0, 0)); label("|+i⟩", phys(0, 1.5, 0));
  const arrow = new THREE.ArrowHelper(phys(0, 0, 1), new THREE.Vector3(), 1, 0x5ef2e0, 0.14, 0.08);
  scene.add(arrow);
  const tip = new THREE.Mesh(new THREE.SphereGeometry(0.05, 16, 16), new THREE.MeshBasicMaterial({ color: 0x5ef2e0 }));
  scene.add(tip);

  // complex arithmetic on [re, im]
  const mul = (a, b) => [a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]];
  const add = (a, b) => [a[0] + b[0], a[1] + b[1]];
  const r2 = Math.SQRT1_2;
  const G = {
    X: [[[0, 0], [1, 0]], [[1, 0], [0, 0]]], Y: [[[0, 0], [0, -1]], [[0, 1], [0, 0]]], Z: [[[1, 0], [0, 0]], [[0, 0], [-1, 0]]],
    H: [[[r2, 0], [r2, 0]], [[r2, 0], [-r2, 0]]], S: [[[1, 0], [0, 0]], [[0, 0], [0, 1]]], T: [[[1, 0], [0, 0]], [[0, 0], [r2, r2]]],
  };
  let st = [[1, 0], [0, 0]];
  const bloch = ([a, b]) => {
    const ab = mul([a[0], -a[1]], b); // conj(a) * b
    return phys(2 * ab[0], 2 * ab[1], a[0] ** 2 + a[1] ** 2 - b[0] ** 2 - b[1] ** 2);
  };
  let cur = bloch(st).normalize(), target = cur.clone(), t0 = 0;
  const out = document.getElementById("bloch-readout"), bar = document.getElementById("bloch-p0");
  function readout() {
    const p0 = st[0][0] ** 2 + st[0][1] ** 2;
    const v = bloch(st);
    out.innerHTML = `P(|0⟩) = <b>${p0.toFixed(3)}</b> &nbsp; P(|1⟩) = <b>${(1 - p0).toFixed(3)}</b><br>⟨X⟩ = <b>${v.x.toFixed(2)}</b> &nbsp; ⟨Y⟩ = <b>${(-v.z).toFixed(2)}</b> &nbsp; ⟨Z⟩ = <b>${v.y.toFixed(2)}</b>`;
    bar.style.width = (100 * p0).toFixed(1) + "%";
  }
  function apply(g) {
    if (g === "reset") st = [[1, 0], [0, 0]];
    else { const M = G[g]; st = [add(mul(M[0][0], st[0]), mul(M[0][1], st[1])), add(mul(M[1][0], st[0]), mul(M[1][1], st[1]))]; }
    cur = arrow.userData.dir || cur; target = bloch(st).normalize(); t0 = performance.now(); readout();
  }
  document.querySelectorAll("[data-gate]").forEach((b) => b.addEventListener("click", () => apply(b.dataset.gate)));
  readout();

  function resize() { const w = canvas.clientWidth, h = canvas.clientHeight; renderer.setSize(w, h, false); camera.aspect = w / h; camera.updateProjectionMatrix(); }
  addEventListener("resize", resize); resize();
  (function loop(now) {
    const k = Math.min(1, (now - t0) / 600), e = 1 - Math.pow(1 - k, 3);
    const q = new THREE.Quaternion().setFromUnitVectors(cur, target);
    const dir = cur.clone().applyQuaternion(new THREE.Quaternion().slerp(q, e)).normalize();
    arrow.setDirection(dir); arrow.userData.dir = dir; tip.position.copy(dir);
    controls.update(); renderer.render(scene, camera); requestAnimationFrame(loop);
  })(performance.now());
}
