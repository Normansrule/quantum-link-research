/* Quantum channels for the channel lab, line for line the tested Python:
     qll/circuits/qubit_channel.py      Pauli transfer matrices, Choi state, fidelities, certificate, capacities
     qll/link/hallway_channel.py        the two-room parts as a quantum channel (needs lab_twin.js)
     qll/link/channel_tomography.py     simulated counts, least-squares estimate, Clopper-Pearson certificate, log
   tests/test_lab_js.py compares every function with the Python. A channel is its 4 x 4 Pauli transfer matrix R
   (rows and columns I, X, Y, Z), an array of four rows. */
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory(require("./lab_twin.js"));
  else root.QLLChannel = factory(root.QLLTwin);
})(typeof self !== "undefined" ? self : this, function (T) {
  "use strict";
  const LOG2 = Math.log(2);
  const h2 = (p) => (p <= 0 || p >= 1 ? 0 : -(p * Math.log(p) + (1 - p) * Math.log(1 - p)) / LOG2);
  const diag = (a) => a.map((v, i) => a.map((_, j) => (i === j ? v : 0)));
  const matmul = (A, B) => A.map((r, i) => B[0].map((_, j) => r.reduce((s, _, k) => s + A[i][k] * B[k][j], 0)));
  const fromAffine = (Tm, t) => [[1, 0, 0, 0], [t[0], ...Tm[0]], [t[1], ...Tm[1]], [t[2], ...Tm[2]]];

  // ------------------------------------------------------------------------------------------------ families
  const depolarizing = (p) => diag([1, 1 - p, 1 - p, 1 - p]);
  function pauliChannel(px, py, pz) { const p0 = 1 - px - py - pz; return diag([1, p0 + px - py - pz, p0 - px + py - pz, p0 - px - py + pz]); }
  function rotation(theta, axis) {
    const n0 = Math.hypot(...axis), n = axis.map((v) => v / n0), c = Math.cos(theta), s = Math.sin(theta);
    const K = [[0, -n[2], n[1]], [n[2], 0, -n[0]], [-n[1], n[0], 0]], KK = matmul(K, K);
    const Rot = [0, 1, 2].map((i) => [0, 1, 2].map((j) => (i === j ? 1 : 0) + s * K[i][j] + (1 - c) * KK[i][j]));
    return fromAffine(Rot, [0, 0, 0]);
  }
  const interceptResend = (f) => diag([1, 1 - f / 2, 1 - f, 1 - f / 2]);
  const amplitudeDamping = (g) => [[1, 0, 0, 0], [0, Math.sqrt(1 - g), 0, 0], [0, 0, Math.sqrt(1 - g), 0], [g, 0, 0, 1 - g]];
  function phaseDamping(lam) { const pz = (1 - Math.sqrt(1 - lam)) / 2; return pauliChannel(0, 0, pz); }
  function teleportChannel(p2, mode) { if (mode === "no_bits") return diag([1, 0, 0, 0]); const l = Math.pow(1 - p2, mode === "deferred" ? 3 : 2); return depolarizing(1 - l); }
  const compose = (...Rs) => Rs.reduce((acc, R) => matmul(R, acc), diag([1, 1, 1, 1]));
  const mix = (w, A, B) => A.map((r, i) => r.map((v, j) => (1 - w) * v + w * B[i][j]));

  // --------------------------------------------------------------------------------- Choi state and spectra
  // complex 4 x 4 as [re[16], im[16]]
  const PAULI = [[[1, 0], [0, 0], [0, 0], [1, 0]], [[0, 0], [1, 0], [1, 0], [0, 0]], [[0, 0], [0, -1], [0, 1], [0, 0]], [[1, 0], [0, 0], [0, 0], [-1, 0]]]; // 2x2 row-major, [re, im]
  const PT = [PAULI[0], PAULI[1], [[0, 0], [0, 1], [0, -1], [0, 0]], PAULI[3]];                                                                         // transposes (Y^T = -Y)
  function choi(R) {
    const re = new Float64Array(16), im = new Float64Array(16);
    for (let j = 0; j < 4; j++) for (let i = 0; i < 4; i++) {
      const c = R[i][j] / 4; if (c === 0) continue;
      for (let a = 0; a < 2; a++) for (let b = 0; b < 2; b++) for (let k = 0; k < 2; k++) for (let l = 0; l < 2; l++) {
        const x = PT[j][2 * a + b], y = PAULI[i][2 * k + l], idx = (2 * a + k) * 4 + (2 * b + l);
        re[idx] += c * (x[0] * y[0] - x[1] * y[1]); im[idx] += c * (x[0] * y[1] + x[1] * y[0]);
      }
    }
    return [re, im];
  }
  function jacobiEig(A) {                                   // real symmetric, returns eigenvalues
    const n = A.length, a = A.map((r) => r.slice());
    for (let sweep = 0; sweep < 100; sweep++) {
      let off = 0; for (let p = 0; p < n; p++) for (let q = p + 1; q < n; q++) off += a[p][q] * a[p][q];
      if (off < 1e-30) break;
      for (let p = 0; p < n; p++) for (let q = p + 1; q < n; q++) {
        if (Math.abs(a[p][q]) < 1e-300) continue;
        const th = (a[q][q] - a[p][p]) / (2 * a[p][q]), t = Math.sign(th || 1) / (Math.abs(th) + Math.sqrt(th * th + 1)), c = 1 / Math.sqrt(t * t + 1), s = t * c;
        for (let k = 0; k < n; k++) { const akp = a[k][p], akq = a[k][q]; a[k][p] = c * akp - s * akq; a[k][q] = s * akp + c * akq; }
        for (let k = 0; k < n; k++) { const apk = a[p][k], aqk = a[q][k]; a[p][k] = c * apk - s * aqk; a[q][k] = s * apk + c * aqk; }
      }
    }
    return a.map((r, i) => r[i]).sort((x, y) => x - y);
  }
  function hermEig([re, im], n) {                            // eigenvalues of an n x n Hermitian matrix, via the real 2n form
    const B = Array.from({ length: 2 * n }, () => new Array(2 * n).fill(0));
    for (let i = 0; i < n; i++) for (let j = 0; j < n; j++) {
      const r = (re[i * n + j] + re[j * n + i]) / 2, m = (im[i * n + j] - im[j * n + i]) / 2;
      B[i][j] = r; B[i + n][j + n] = r; B[i][j + n] = -m; B[i + n][j] = m;
    }
    return jacobiEig(B).filter((_, k) => k % 2 === 0);
  }
  const entropyOf = (w) => -w.filter((x) => x > 1e-15).reduce((s, x) => s + x * Math.log(x) / LOG2, 0);

  // ------------------------------------------------------------------------------------------ figures of merit
  const entanglementFidelity = (R) => (1 + R[1][1] + R[2][2] + R[3][3]) / 4;
  const averageFidelity = (R) => (2 * entanglementFidelity(R) + 1) / 3;
  const basisErrors = (R) => ({ x: (1 - R[1][1]) / 2, y: (1 - R[2][2]) / 2, z: (1 - R[3][3]) / 2 });
  const certifiedFe = (ez, ex) => Math.max(0, 1 - ez - ex);
  function partialTransposeMin(R) {
    const [re, im] = choi(R), pre = new Float64Array(16), pim = new Float64Array(16);
    for (let r = 0; r < 2; r++) for (let b = 0; b < 2; b++) for (let r2 = 0; r2 < 2; r2++) for (let b2 = 0; b2 < 2; b2++) {
      const src = (2 * r + b) * 4 + (2 * r2 + b2), dst = (2 * r2 + b) * 4 + (2 * r + b2); pre[dst] = re[src]; pim[dst] = im[src];
    }
    return hermEig([pre, pim], 4)[0];
  }
  const isEntanglementBreaking = (R, tol = 1e-12) => partialTransposeMin(R) >= -tol;
  const isPhysical = (R, tol = 1e-9) => hermEig(choi(R), 4)[0] >= -tol && Math.abs(R[0][0] - 1) < tol && Math.abs(R[0][1]) + Math.abs(R[0][2]) + Math.abs(R[0][3]) < tol;

  // --------------------------------------------------------------------------------------------- capacities
  function outputEntropy(R, p) {                             // input diag(p, 1 - p): Bloch (0, 0, 2p - 1)
    const z = 2 * p - 1, r = [R[1][0] + R[1][3] * z, R[2][0] + R[2][3] * z, R[3][0] + R[3][3] * z], L = Math.min(1, Math.hypot(...r));
    return entropyOf([(1 + L) / 2, (1 - L) / 2]);
  }
  function jointEntropy(R, p) {                              // S of 2 (sqrt(rho)^T (x) I) J (...)^dagger for rho = diag(p, 1 - p)
    const [re, im] = choi(R), m = [Math.sqrt(p), Math.sqrt(p), Math.sqrt(1 - p), Math.sqrt(1 - p)], ore = new Float64Array(16), oim = new Float64Array(16);
    for (let i = 0; i < 4; i++) for (let j = 0; j < 4; j++) { ore[i * 4 + j] = 2 * m[i] * m[j] * re[i * 4 + j]; oim[i * 4 + j] = 2 * m[i] * m[j] * im[i * 4 + j]; }
    return entropyOf(hermEig([ore, oim], 4));
  }
  const GRID = Array.from({ length: 201 }, (_, k) => k / 200);
  const coherentInformation = (R, p) => outputEntropy(R, p) - jointEntropy(R, p);
  const mutualInformation = (R, p) => h2(p) + outputEntropy(R, p) - jointEntropy(R, p);
  const quantumCapacityLower = (R) => Math.max(0, Math.max(...GRID.map((p) => coherentInformation(R, p))));
  const hashingBound = (R) => Math.max(0, coherentInformation(R, 0.5));
  const entanglementAssistedCapacity = (R) => Math.max(...GRID.map((p) => mutualInformation(R, p)));
  function holevoCapacityUnital(R) {
    const Tm = [1, 2, 3].map((i) => [1, 2, 3].map((j) => R[i][j])), TtT = [0, 1, 2].map((i) => [0, 1, 2].map((j) => [0, 1, 2].reduce((s, k) => s + Tm[k][i] * Tm[k][j], 0)));
    const s = Math.sqrt(Math.max(0, jacobiEig(TtT)[2]));
    return 1 - h2((1 + Math.min(s, 1)) / 2);
  }
  function amplitudeDampingQuantumCapacity(g, n = 20001) {
    if (g >= 0.5) return 0;
    let best = -Infinity; for (let k = 0; k < n; k++) { const p = k / (n - 1); best = Math.max(best, h2((1 - g) * p) - h2(g * p)); }
    return best;
  }
  const erasureCapacities = (e) => ({ quantum_one_way: Math.max(0, 1 - 2 * e), quantum_two_way: 1 - e, classical: 1 - e, entanglement_assisted: 2 * (1 - e) });
  const privateCapacityBB84 = (ez, ex) => Math.max(0, 1 - h2(ez) - h2(ex));
  const plob = (eta) => -Math.log(1 - eta) / LOG2;
  function capacities(R) {
    const unital = Math.abs(R[1][0]) + Math.abs(R[2][0]) + Math.abs(R[3][0]) < 1e-12, e = basisErrors(R);
    return { classical: unital ? holevoCapacityUnital(R) : null, entanglement_assisted: entanglementAssistedCapacity(R), quantum: quantumCapacityLower(R),
      hashing: hashingBound(R), private_bb84: privateCapacityBB84(e.z, e.x) };
  }

  // ------------------------------------------------------------------------------------------ the hallway
  function hallway(parts, eveFraction = 0) {
    const c = Object.assign(T.twoRoomConfig(parts || {}), { eve_fraction: eveFraction });
    const eta = T.signalClickProb(c), pb = T.backgroundClickProb(c), q = eta + (1 - eta) * pb, w = (1 - eta) * pb / q;
    const R = mix(w, compose(interceptResend(eveFraction), depolarizing(2 * c.misalignment_error)), diag([1, 0, 0, 0]));
    const err = basisErrors(R), s = T.expectedSession(c), hashing = hashingBound(R);
    return { eta, erasure: 1 - eta, background_share: w, ptm: R, error_zx: err.z, error_y: err.y, entanglement_fidelity: entanglementFidelity(R),
      average_fidelity: averageFidelity(R), entanglement_breaking: isEntanglementBreaking(R), decoy_e1_upper: s.e1_upper,
      certified_single_photon_fe: certifiedFe(s.e1_upper, s.e1_upper), quantum_one_way: Math.max(0, eta * hashing - (1 - eta)),
      quantum_heralded: eta * hashing, plob: plob(eta), classical_holevo_clicked: holevoCapacityUnital(R), private_bb84_clicked: privateCapacityBB84(err.z, err.x) };
  }

  // ------------------------------------------------------------------------------------------ tomography
  const INPUTS = { H: [0, 0, 1], V: [0, 0, -1], D: [1, 0, 0], A: [-1, 0, 0], R: [0, 1, 0], L: [0, -1, 0] };
  const BASES = { X: 0, Y: 1, Z: 2 };
  const ERROR_OUTCOME = { "H,Z": 1, "V,Z": 0, "D,X": 1, "A,X": 0 };
  function probabilityZero(R, s, b) { const v = [1, ...INPUTS[s]], k = 1 + BASES[b]; return 0.5 * (1 + R[k].reduce((a, x, j) => a + x * v[j], 0)); }
  function simulateCounts(R, shots, inputs = ["H", "V", "D", "A", "R"], bases = ["X", "Y", "Z"], seed = 1) {
    const r = T.rng(seed), out = {};
    for (const s of inputs) for (const b of bases) {
      const p = Math.min(1, Math.max(0, probabilityZero(R, s, b))); let n0 = 0;
      for (let i = 0; i < shots; i++) if (r() < p) n0++;
      out[`${s},${b}`] = [n0, shots - n0];
    }
    return out;
  }
  function solve4(M, y) {                                    // Gaussian elimination with partial pivoting
    const A = M.map((r, i) => [...r, y[i]]);
    for (let c = 0; c < 4; c++) {
      let p = c; for (let r = c + 1; r < 4; r++) if (Math.abs(A[r][c]) > Math.abs(A[p][c])) p = r;
      [A[c], A[p]] = [A[p], A[c]]; if (Math.abs(A[c][c]) < 1e-12) throw new Error("the inputs do not span the sphere");
      for (let r = 0; r < 4; r++) if (r !== c) { const f = A[r][c] / A[c][c]; for (let k = c; k < 5; k++) A[r][k] -= f * A[c][k]; }
    }
    return A.map((r, i) => r[4] / r[i]);
  }
  function estimate(counts) {
    const R = [[1, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]];
    for (const [b, k] of Object.entries(BASES)) {
      const rows = Object.entries(counts).filter(([key, [n0, n1]]) => key.split(",")[1] === b && n0 + n1 > 0);
      if (rows.length < 4) throw new Error(`basis ${b}: need at least four inputs that span the sphere`);
      const A = rows.map(([key]) => [1, ...INPUTS[key.split(",")[0]]]), y = rows.map(([, [n0, n1]]) => (n0 - n1) / (n0 + n1));
      const AtA = [0, 1, 2, 3].map((i) => [0, 1, 2, 3].map((j) => A.reduce((s, r) => s + r[i] * r[j], 0))), Aty = [0, 1, 2, 3].map((i) => A.reduce((s, r, n) => s + r[i] * y[n], 0));
      const coef = solve4(AtA, Aty); R[1 + k] = coef;
    }
    return R;
  }
  // regularized incomplete beta and its inverse (Numerical Recipes continued fraction; Lanczos log-gamma)
  function lgamma(x) {
    const g = 7, c = [0.99999999999980993, 676.5203681218851, -1259.1392167224028, 771.32342877765313, -176.61502916214059, 12.507343278686905, -0.13857109526572012, 9.9843695780195716e-6, 1.5056327351493116e-7];
    if (x < 0.5) return Math.log(Math.PI / Math.abs(Math.sin(Math.PI * x))) - lgamma(1 - x);
    x -= 1; let a = c[0]; const t = x + g + 0.5; for (let i = 1; i < 9; i++) a += c[i] / (x + i);
    return 0.5 * Math.log(2 * Math.PI) + (x + 0.5) * Math.log(t) - t + Math.log(a);
  }
  function betacf(a, b, x) {
    const FP = 1e-300; let qab = a + b, qap = a + 1, qam = a - 1, c = 1, d = 1 - qab * x / qap; if (Math.abs(d) < FP) d = FP; d = 1 / d; let h = d;
    for (let m = 1; m <= 10000; m++) {
      const m2 = 2 * m; let aa = m * (b - m) * x / ((qam + m2) * (a + m2));
      d = 1 + aa * d; if (Math.abs(d) < FP) d = FP; c = 1 + aa / c; if (Math.abs(c) < FP) c = FP; d = 1 / d; h *= d * c;
      aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2));
      d = 1 + aa * d; if (Math.abs(d) < FP) d = FP; c = 1 + aa / c; if (Math.abs(c) < FP) c = FP; d = 1 / d; const del = d * c; h *= del;
      if (Math.abs(del - 1) < 1e-15) break;
    }
    return h;
  }
  function betainc(a, b, x) {
    if (x <= 0) return 0; if (x >= 1) return 1;
    const bt = Math.exp(lgamma(a + b) - lgamma(a) - lgamma(b) + a * Math.log(x) + b * Math.log(1 - x));
    return x < (a + 1) / (a + b + 2) ? bt * betacf(a, b, x) / a : 1 - bt * betacf(b, a, 1 - x) / b;
  }
  function betaPpf(q, a, b) { let lo = 0, hi = 1; for (let i = 0; i < 200; i++) { const m = (lo + hi) / 2; if (betainc(a, b, m) < q) lo = m; else hi = m; if (hi - lo < 1e-15) break; } return (lo + hi) / 2; }
  const upper = (k, n, alpha) => (k === n ? 1 : betaPpf(1 - alpha, k + 1, n - k));
  function certify(counts, alpha = 0.01) {
    const up = {}, rate = {};
    for (const [key, err] of Object.entries(ERROR_OUTCOME)) {
      const [n0, n1] = counts[key], s = key.split(",")[0], k = err === 1 ? n1 : n0, n = n0 + n1;
      up[s] = upper(k, n, alpha / 4); rate[s] = k / n;
    }
    const ez = (rate.H + rate.V) / 2, ex = (rate.D + rate.A) / 2, ezu = (up.H + up.V) / 2, exu = (up.D + up.A) / 2, bound = certifiedFe(ezu, exu);
    return { e_z: ez, e_x: ex, e_z_upper: ezu, e_x_upper: exu, fe_estimate: 1 - ez - ex, fe_lower: bound, certified_quantum: bound > 0.5, confidence: 1 - alpha };
  }
  function tomographyCsv(counts, seed = 1) {
    const rows = []; for (const [key, [n0, n1]] of Object.entries(counts)) { const [s, b] = key.split(","); for (let i = 0; i < n0; i++) rows.push(`${s},${b},0`); for (let i = 0; i < n1; i++) rows.push(`${s},${b},1`); }
    const r = T.rng(seed); for (let i = rows.length - 1; i > 0; i--) { const j = Math.floor(r() * (i + 1)); [rows[i], rows[j]] = [rows[j], rows[i]]; }
    return "input,basis,outcome\n" + rows.join("\n") + "\n";
  }

  // --------------------------------------------- superdense coding through the hallway (qll/circuits/superdense_photonic.py)
  const BELL = ["Psi-", "Psi+", "Phi+", "Phi-"];
  function sdDecoder(vhom) { const d = 1 - vhom; return [[1 - d / 2, d / 2, 0], [d / 2, 1 - d / 2, 0], [0, 0, 1], [0, 0, 1]]; }
  function sdPopulations(m, V) { const p = [1, 1, 1, 1].map(() => (1 - V) / 4); p[BELL.indexOf(m)] = (1 + 3 * V) / 4; return p; }
  function sdConfusion(V, vhom, messages = ["Psi-", "Psi+", "Phi+"]) { const D = sdDecoder(vhom); return messages.map((m) => { const p = sdPopulations(m, V); return [0, 1, 2].map((j) => p.reduce((s, x, i) => s + x * D[i][j], 0)); }); }
  function sdBits(V, vhom, messages) {
    const C = sdConfusion(V, vhom, messages), H = (q) => -q.filter((x) => x > 0).reduce((s, x) => s + x * Math.log(x) / LOG2, 0);
    const mean = [0, 1, 2].map((j) => C.reduce((s, r) => s + r[j], 0) / C.length);
    return H(mean) - C.reduce((s, r) => s + H(r), 0) / C.length;
  }
  function stepsSuperdense(V, vhom) {
    const C = sdConfusion(V, vhom), bits = sdBits(V, vhom), Fpair = (1 + 3 * V) / 4;
    return [
      S("Shared pair", "ρ = V|Φ⁺⟩⟨Φ⁺| + (1 − V) I/4", `V = ${f(V, 3)}`, `intended Bell state weight ${f(Fpair, 3)}`, "mattle1996", "The two photons are prepared together; one stays with Bob, one goes to Alice before any message exists."),
      S("Alice encodes", "I, X, Z, or XZ with waveplates", "three messages: Ψ⁻, Ψ⁺, Φ⁺", "log₂ 3 = 1.585 bits ideal", "bennett1992", "Turning waveplates on her photon alone moves the pair into one of the Bell states; that is the message."),
      S("The photon crosses the hallway", "the quantum channel carries the message", "", "one photon per message", "mattle1996", "Unlike collapse, this is a real signal: the photon travels, at light speed or slower."),
      S("Bob's Bell measurement", "50/50 beamsplitter + two polarizing beamsplitters", `two-photon interference visibility ${f(vhom, 3)}`, "three classes: Ψ⁻, Ψ⁺, Φ", "hong1987", "The two photons interfere; which detectors fire together reveals the Bell state, three of four with linear optics."),
      S("Confusion matrix", "P(class | message)", "", "[" + C.map((r) => "[" + r.map((v) => f(v, 3)).join(", ") + "]").join(", ") + "]", "mattle1996", "Rows are what Alice sent; columns what Bob decoded. A perfect channel is the identity."),
      S("Bits per detected photon", "I = H(Y) − H(Y|X)", "", `${f(bits, 3)} ${bits > 1 ? "> 1: beats any single-qubit encoding" : "≤ 1: no advantage yet"}`, "holevo1973", "Without a shared pair, one photon's polarization can carry at most 1 bit (Holevo)."),
    ];
  }

  // ------------------------------------------------------------------------------------------ terminal lines
  const f = (x, d = 4) => (x === null || x === undefined ? "n/a" : Math.abs(x) < 5e-13 ? "0" : (+x.toFixed(d)).toString());
  const pct = (x) => (100 * x).toFixed(2) + " %";
  const S = (label, formula, sub, value, ref, why) => ({ label, formula, sub, value, ref: ref || "", why: why || "" });
  function steps(R, info) {
    const e = basisErrors(R), Fe = entanglementFidelity(R), cap = capacities(R), eb = isEntanglementBreaking(R), cert = certifiedFe(e.z, e.x);
    const lines = [];
    if (info && info.eta !== undefined) {
      lines.push(S("Photons that click", "η = T·η_det", "", f(info.eta, 4), "qll/link/hallway_channel.py", "Most photons never arrive. Each loss is announced by silence: no detector fires, so Bob knows which ones to ignore."));
      lines.push(S("Dark clicks among clicks", "w = (1 − η)p_bg / [η + (1 − η)p_bg]", "", pct(info.background_share), "casella2002", "A few clicks are detector noise, not photons; they carry a random bit."));
    }
    lines.push(S("Pauli transfer matrix", "R_ij = ½ Tr[σ_i E(σ_j)]", "", "[" + R.map((r) => "[" + r.map((v) => f(v, 3)).join(", ") + "]").join(", ") + "]", "nielsen2010",
      "Sixteen numbers say everything the channel does to one qubit: how it shrinks, turns, and shifts the sphere of polarizations."));
    lines.push(S("Bloch sphere shrink", "λ_x, λ_y, λ_z = R_11, R_22, R_33", "", `${f(R[1][1], 3)}, ${f(R[2][2], 3)}, ${f(R[3][3], 3)}`, "nielsen2010", "1 means a direction survives untouched; 0 means it is completely scrambled."));
    lines.push(S("Error rate per basis", "e_a = (1 − R_aa)/2", "", `Z ${pct(e.z)}, X ${pct(e.x)}, Y ${pct(e.y)}`, "nielsen2010", "The chance that a state sent along one axis comes out flipped; Z and X are what BB84 already measures."));
    lines.push(S("Entanglement fidelity", "F_e = (1 + Tr T)/4", "", f(Fe), "nielsen2002", "How well half of an entangled pair survives the trip. A classical relay can never exceed 0.5."));
    lines.push(S("Average fidelity", "F = (2F_e + 1)/3", "", f(averageFidelity(R)), "nielsen2002", "How close an average input state arrives to itself; the classical limit is 2/3."));
    lines.push(S("Certificate from BB84 counts", "F_e ≥ 1 − e_Z − e_X", `1 − ${f(e.z)} − ${f(e.x)}`, `${f(cert)} ${cert > 0.5 ? "> 0.5: certified quantum" : "≤ 0.5: not certified"}`, "horodecki2003eb",
      "This bound holds for every qubit channel, so the two error rates the link already measures prove it is not a measure-and-resend relay."));
    lines.push(S("Entanglement breaking?", "Choi state has a positive partial transpose", "", eb ? "yes: a classical relay could do this" : "no: the channel preserves entanglement", "horodecki1996sep",
      "An entanglement-breaking channel destroys quantum information; anything it does, measuring and resending could do."));
    lines.push(S("Classical capacity", "C = 1 − h((1 + s_max)/2)", cap.classical === null ? "non-unital: closed form not used" : "", cap.classical === null ? "see entanglement-assisted" : `${f(cap.classical)} bits per use`, "king2002", "Ordinary bits per qubit sent. Never more than 1."));
    lines.push(S("Entanglement-assisted capacity", "C_E = max_ρ I(R;B)", "", `${f(cap.entanglement_assisted)} bits per use`, "bennett2002", "Bits per qubit when sender and receiver already share entangled pairs: up to 2 (superdense coding)."));
    lines.push(S("Quantum capacity (lower bound)", "Q ≥ max_ρ [S(B) − S(RB)]", `hashing at ρ = I/2: ${f(cap.hashing)}`, `${f(cap.quantum)} qubits per use`, "devetak2005q", "Qubits per use that error correction can protect over this channel."));
    lines.push(S("Private capacity (lower bound)", "P ≥ 1 − h(e_Z) − h(e_X)", "", `${f(cap.private_bb84)} secret bits per use`, "shor2000", "Secret-key bits per clicked photon, as BB84 with ideal post-processing would distill."));
    if (info && info.eta !== undefined) {
      lines.push(S("One-way quantum rate per photon sent", "Q₁ ≥ η·Q_click − (1 − η)", "erasure above 50 %: zero", `${f(info.quantum_one_way)} qubits`, "bennett1997erasure", "Without telling Alice which photons arrived, a link this lossy cannot carry qubits at all."));
      lines.push(S("With heralding over the classical channel", "Q₂ ≥ η·[1 − H(p)]", "", `${f(info.quantum_heralded)} qubits per photon`, "bennett1997erasure", "Announcing the arrivals over the classical fiber recovers a quantum rate proportional to η: the two channels work together."));
      lines.push(S("Repeaterless bound", "−log₂(1 − η)", "", `${f(info.plob, 3)} per photon`, "pirandola2017", "No protocol over this loss can beat this without quantum repeaters."));
      lines.push(S("Single-photon certificate (decoys)", "F_e ≥ 1 − 2e₁", `e₁ ≤ ${pct(info.decoy_e1_upper)}`, f(info.certified_single_photon_fe, 3), "ma2005", "With a laser source, decoy pulses bound the single-photon error, which certifies the channel a quantum network would use."));
    }
    return lines;
  }
  return {
    h2, depolarizing, pauliChannel, rotation, interceptResend, amplitudeDamping, phaseDamping, teleportChannel, compose, mix, fromAffine, matmul,
    choi, hermEig, jacobiEig, entanglementFidelity, averageFidelity, basisErrors, certifiedFe, isEntanglementBreaking, isPhysical, partialTransposeMin,
    coherentInformation, mutualInformation, quantumCapacityLower, hashingBound, entanglementAssistedCapacity, holevoCapacityUnital,
    amplitudeDampingQuantumCapacity, erasureCapacities, privateCapacityBB84, plob, capacities, hallway,
    BELL, sdConfusion, sdBits, stepsSuperdense, INPUTS, BASES, probabilityZero, simulateCounts, estimate, betainc, betaPpf, certify, tomographyCsv, steps,
  };
});
