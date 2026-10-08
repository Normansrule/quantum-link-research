/* Exact quantum arithmetic for the circuits lab: density matrices of up to three qubits (or three fermionic modes),
   ported from the Python the suite validates:
     P11  qll/circuits/collapse_signalling.py   no-signalling: Bob's state after any instrument of Alice's
     P12  qll/circuits/teleport_cloud.py        teleportation with depolarizing CX noise, three modes
          qll/circuits/superdense_cloud.py      superdense coding and its keep-the-qubit control
     P13  qll/circuits/majorana_teleport.py     measurement-only Majorana teleportation (Jordan-Wigner)
          qll/hardware/majorana_error_budget.py its error budget [crogman2025]
   tests/test_lab_js.py compares each function with the Python to 1e-12. Matrices are {n, re, im} with Float64Arrays. */
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory();
  else root.QLLQuantum = factory();
})(typeof self !== "undefined" ? self : this, function () {
  "use strict";
  // ------------------------------------------------------------------------------------------- complex matrices
  const M = (n) => ({ n, re: new Float64Array(n * n), im: new Float64Array(n * n) });
  function from(rows) {                                       // rows of [re, im] pairs or real numbers
    const n = rows.length, A = M(n);
    rows.forEach((r, i) => r.forEach((v, j) => { const z = Array.isArray(v) ? v : [v, 0]; A.re[i * n + j] = z[0]; A.im[i * n + j] = z[1]; }));
    return A;
  }
  const eye = (n) => { const A = M(n); for (let i = 0; i < n; i++) A.re[i * n + i] = 1; return A; };
  function mul(A, B) {
    const n = A.n, Cm = M(n);
    for (let i = 0; i < n; i++) for (let k = 0; k < n; k++) {
      const ar = A.re[i * n + k], ai = A.im[i * n + k]; if (ar === 0 && ai === 0) continue;
      for (let j = 0; j < n; j++) { const br = B.re[k * n + j], bi = B.im[k * n + j]; Cm.re[i * n + j] += ar * br - ai * bi; Cm.im[i * n + j] += ar * bi + ai * br; }
    }
    return Cm;
  }
  const mulAll = (...ms) => ms.reduce((a, b) => mul(a, b));
  function add(A, B, s = 1) { const Cm = M(A.n); for (let i = 0; i < A.re.length; i++) { Cm.re[i] = A.re[i] + s * B.re[i]; Cm.im[i] = A.im[i] + s * B.im[i]; } return Cm; }
  function scale(A, sr, si = 0) { const Cm = M(A.n); for (let i = 0; i < A.re.length; i++) { Cm.re[i] = A.re[i] * sr - A.im[i] * si; Cm.im[i] = A.re[i] * si + A.im[i] * sr; } return Cm; }
  function dag(A) { const n = A.n, Cm = M(n); for (let i = 0; i < n; i++) for (let j = 0; j < n; j++) { Cm.re[j * n + i] = A.re[i * n + j]; Cm.im[j * n + i] = -A.im[i * n + j]; } return Cm; }
  function kron(...ms) {
    return ms.reduce((A, B) => {
      const n = A.n * B.n, Cm = M(n);
      for (let i = 0; i < A.n; i++) for (let j = 0; j < A.n; j++) for (let k = 0; k < B.n; k++) for (let l = 0; l < B.n; l++) {
        const ar = A.re[i * A.n + j], ai = A.im[i * A.n + j], br = B.re[k * B.n + l], bi = B.im[k * B.n + l], idx = (i * B.n + k) * n + (j * B.n + l);
        Cm.re[idx] = ar * br - ai * bi; Cm.im[idx] = ar * bi + ai * br;
      }
      return Cm;
    });
  }
  const trRe = (A) => { let s = 0; for (let i = 0; i < A.n; i++) s += A.re[i * A.n + i]; return s; };
  const sandwich = (U, rho) => mulAll(U, rho, dag(U));
  function outer(v) {                                         // v: array of [re, im]
    const n = v.length, A = M(n);
    for (let i = 0; i < n; i++) for (let j = 0; j < n; j++) { A.re[i * n + j] = v[i][0] * v[j][0] + v[i][1] * v[j][1]; A.im[i * n + j] = v[i][1] * v[j][0] - v[i][0] * v[j][1]; }
    return A;
  }
  const expect = (v, A) => {                                   // <v|A|v> (real part)
    let s = 0; const n = A.n;
    for (let i = 0; i < n; i++) for (let j = 0; j < n; j++) {
      const ar = A.re[i * n + j], ai = A.im[i * n + j], vr = v[j][0], vi = v[j][1];
      const xr = ar * vr - ai * vi, xi = ar * vi + ai * vr; s += v[i][0] * xr + v[i][1] * xi;
    }
    return s;
  };
  // keep one qubit of an n-qubit register (qubit 0 is the most significant index bit)
  function reduce(rho, nq, keep) {
    const R = M(2), shift = nq - 1 - keep;
    for (let i = 0; i < rho.n; i++) for (let j = 0; j < rho.n; j++) {
      if ((i & ~(1 << shift)) !== (j & ~(1 << shift))) continue;
      const a = (i >> shift) & 1, b = (j >> shift) & 1;
      R.re[a * 2 + b] += rho.re[i * rho.n + j]; R.im[a * 2 + b] += rho.im[i * rho.n + j];
    }
    return R;
  }
  const r2 = Math.SQRT1_2;
  const I2 = eye(2), X = from([[0, 1], [1, 0]]), Y = from([[0, [0, -1]], [[0, 1], 0]]), Z = from([[1, 0], [0, -1]]);
  const Hd = from([[r2, r2], [r2, -r2]]), Sg = from([[1, 0], [0, [0, 1]]]), Sdg = from([[1, 0], [0, [0, -1]]]);
  const PAULI = [I2, X, Y, Z];
  const blochOf = (rho) => [2 * rho.re[1], -2 * rho.im[1], rho.re[0] - rho.re[3]];
  const on = (nq, q, G) => kron(...Array.from({ length: nq }, (_, k) => (k === q ? G : I2)));
  function cx(nq, c, t) {
    const n = 1 << nq, U = M(n), sc = nq - 1 - c, st = nq - 1 - t;
    for (let i = 0; i < n; i++) U.re[(((i >> sc) & 1) ? i ^ (1 << st) : i) * n + i] = 1;
    return U;
  }
  function cz(nq, a, b) { const n = 1 << nq, U = M(n), sa = nq - 1 - a, sb = nq - 1 - b; for (let i = 0; i < n; i++) U.re[i * n + i] = ((i >> sa) & 1) && ((i >> sb) & 1) ? -1 : 1; return U; }
  function depolarize2(rho, nq, a, b, p) {                      // (1 - p) rho + p Tr_ab(rho) (x) I/4, by a Pauli twirl
    if (p === 0) return rho;
    let tw = M(rho.n);
    for (const P of PAULI) for (const Q of PAULI) { const U = mul(on(nq, a, P), on(nq, b, Q)); tw = add(tw, sandwich(U, rho)); }
    return add(scale(rho, 1 - p), scale(tw, p / 16));
  }
  const h2 = (p) => (p <= 0 || p >= 1 ? 0 : -p * Math.log2(p) - (1 - p) * Math.log2(1 - p));

  // ------------------------------------------------------------------------------- normal distribution helpers
  function erfc(x) {
    const ax = Math.abs(x); let v;
    if (ax < 3) { let term = ax, sum = ax; for (let n = 1; n < 200; n++) { term *= -ax * ax / n; const t = term / (2 * n + 1); sum += t; if (Math.abs(t) < 1e-17 * Math.abs(sum)) break; } v = 1 - 2 / Math.sqrt(Math.PI) * sum; }
    else { let f = ax, Cc = ax, D = 0; for (let n = 1; n < 300; n++) { const a = n / 2; D = ax + a * D; D = D === 0 ? 1e-300 : 1 / D; Cc = ax + a / Cc; const d = Cc * D; f *= d; if (Math.abs(d - 1) < 1e-16) break; } v = Math.exp(-ax * ax) / Math.sqrt(Math.PI) / f; }
    return x >= 0 ? v : 2 - v;
  }
  const normCdf = (x) => 0.5 * erfc(-x / Math.SQRT2);
  function normPpf(p) {                                        // Acklam's rational start, then two Halley steps
    const a = [-39.69683028665376, 220.9460984245205, -275.9285104469687, 138.357751867269, -30.66479806614716, 2.506628277459239];
    const b = [-54.47609879822406, 161.5858368580409, -155.6989798598866, 66.80131188771972, -13.28068155288572];
    const c = [-0.007784894002430293, -0.3223964580411365, -2.400758277161838, -2.549732539343734, 4.374664141464968, 2.938163982698783];
    const d = [0.007784695709041462, 0.3224671290700398, 2.445134137142996, 3.754408661907416];
    let x;
    if (p < 0.02425) { const q = Math.sqrt(-2 * Math.log(p)); x = (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1); }
    else if (p > 1 - 0.02425) { const q = Math.sqrt(-2 * Math.log(1 - p)); x = -(((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1); }
    else { const q = p - 0.5, r = q * q; x = (((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5]) * q / (((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1); }
    for (let k = 0; k < 2; k++) { const e = normCdf(x) - p, u = e * Math.sqrt(2 * Math.PI) * Math.exp(x * x / 2); x = x - u / (1 + x * u / 2); }
    return x;
  }

  // ------------------------------------------------------------------------------------- P11: the collapse code
  const SCHEMES = ["basis", "measure", "flip"];
  function projectors(theta) { const c = Math.cos(theta), s = Math.sin(theta), P0 = from([[c * c, c * s], [c * s, s * s]]); return [P0, add(I2, P0, -1)]; }
  function instrument(scheme, x) {
    if (scheme === "basis") return projectors(x === 0 ? 0 : Math.PI / 4);
    if (scheme === "measure") return x ? projectors(0) : [I2];
    return [x ? X : I2];
  }
  function werner(V) { const phi = [[r2, 0], [0, 0], [0, 0], [r2, 0]]; return add(scale(outer(phi), V), scale(eye(4), (1 - V) / 4)); }
  function bobStateAfter(rhoAB, kraus) {
    let rho = M(4); for (const K of kraus) rho = add(rho, sandwich(kron(K, I2), rhoAB));
    return reduce(rho, 2, 1);
  }
  const mutualInformation = (p0, p1) => h2(0.5 * (p0 + p1)) - 0.5 * (h2(p0) + h2(p1));
  function usesToDetect(delta, alpha = 0.01, power = 0.9, p = 0.5) {
    const z = normPpf(1 - alpha / 2) + normPpf(power), p0 = p - delta / 2, p1 = p + delta / 2;
    return Math.ceil(z * z * (p0 * (1 - p0) + p1 * (1 - p1)) / (delta * delta));
  }
  /* Bob's P(b = 1 | x) for each message bit: exact from rho_B, then the leak control (reset to |0> with probability
     `leak` when x = 1, a physical disturbance and not a property of the entangled state). */
  function collapseExpected(scheme, V, leak) {
    const rho = werner(V), out = { rhoB: [], p1: [] };
    for (const x of [0, 1]) { const rb = bobStateAfter(rho, instrument(scheme, x)); out.rhoB.push(rb); out.p1.push((x === 1 ? 1 - leak : 1) * rb.re[3]); }
    out.delta = out.p1[1] - out.p1[0]; out.mi = mutualInformation(out.p1[0], out.p1[1]);
    out.same = rho;
    return out;
  }

  // -------------------------------------------------------------------------------------- P12: teleportation
  const CARDINAL = { "0": [[1, 0], [0, 0]], "1": [[0, 0], [1, 0]], "+": [[r2, 0], [r2, 0]], "-": [[r2, 0], [-r2, 0]], "+i": [[r2, 0], [0, r2]], "-i": [[r2, 0], [0, -r2]] };
  const TELEPORT_MODES = ["feedforward", "deferred", "no_bits"];
  /* q0 = Alice's input, q1 = Alice's half of the pair, q2 = Bob's half (index 4 q0 + 2 q1 + q2). Noise: a two-qubit
     depolarizing channel after every CX, as noise_model_depolarizing(p2); Alice's classically controlled X and Z,
     and the CZ, are noiseless, as in Aer. Measurement then correction equals the controlled gates (deferred
     measurement [nielsen2010]), so all three modes are density-matrix evolutions followed by tracing out q0, q1. */
  function teleportRho(state, mode, p2) {
    const psi = CARDINAL[state] || state;
    let rho = kron(outer(psi), outer([[1, 0], [0, 0]]), outer([[1, 0], [0, 0]]));
    const stages = [];
    rho = sandwich(on(3, 1, Hd), rho); rho = depolarize2(sandwich(cx(3, 1, 2), rho), 3, 1, 2, p2); stages.push(["pair shared", rho]);
    rho = depolarize2(sandwich(cx(3, 0, 1), rho), 3, 0, 1, p2); rho = sandwich(on(3, 0, Hd), rho); stages.push(["Alice's Bell rotation", rho]);
    if (mode === "feedforward") { rho = sandwich(cx(3, 1, 2), rho); rho = sandwich(cz(3, 0, 2), rho); }
    else if (mode === "deferred") { rho = depolarize2(sandwich(cx(3, 1, 2), rho), 3, 1, 2, p2); rho = sandwich(cz(3, 0, 2), rho); }
    stages.push([mode === "no_bits" ? "no bits arrive" : "corrections applied", rho]);
    const bob = reduce(rho, 3, 2);
    return { bob, fidelity: expect(psi, bob), stages };
  }
  function teleportAverage(mode, p2) { const ks = Object.keys(CARDINAL); return ks.reduce((a, k) => a + teleportRho(k, mode, p2).fidelity, 0) / ks.length; }
  const expectedFeedforwardFidelity = (p2) => 0.5 * (1 + (1 - p2) * (1 - p2));
  const wernerAverageFidelity = (f) => (2 * f + 1) / 3;
  /* Alice's four outcomes on a noiseless run: probability 1/4 each, and Bob's state before correction is
     X^m1 Z^m0 |psi> [bennett1993]. Returned as amplitudes for the terminal. */
  function teleportOutcomes(state) {
    const [a, b] = CARDINAL[state] || state, out = [];
    for (const m0 of [0, 1]) for (const m1 of [0, 1]) {
      let v = [a.slice(), b.slice()];
      if (m0) v = [v[0], [-v[1][0], -v[1][1]]];               // Z
      if (m1) v = [v[1], v[0]];                               // X
      out.push({ m0, m1, p: 0.25, bob: v, correction: (m1 ? "X" : "") + (m0 ? (m1 ? "·" : "") + "Z" : "") || "none" });
    }
    return out;
  }

  // ------------------------------------------------------------------------------------- superdense coding
  const MESSAGES = [[0, 0], [0, 1], [1, 0], [1, 1]];
  function superdense(mode, p2) {
    const conf = [];
    for (const [i, j] of MESSAGES) {
      let rho = kron(outer([[1, 0], [0, 0]]), outer([[1, 0], [0, 0]]));
      rho = sandwich(on(2, 0, Hd), rho); rho = depolarize2(sandwich(cx(2, 0, 1), rho), 2, 0, 1, p2);
      if (j) rho = sandwich(on(2, 0, X), rho);
      if (i) rho = sandwich(on(2, 0, Z), rho);
      const row = [0, 0, 0, 0];
      if (mode === "send_qubit") {
        rho = depolarize2(sandwich(cx(2, 0, 1), rho), 2, 0, 1, p2); rho = sandwich(on(2, 0, Hd), rho);
        for (let k = 0; k < 4; k++) row[k] = rho.re[k * 4 + k];    // index 2 q0 + q1 = 2 i + j
      } else {
        const bob = reduce(rho, 2, 1); row[0] = bob.re[0]; row[1] = bob.re[3];   // guess (0, c1)
      }
      conf.push(row);
    }
    const success = conf.reduce((a, r, k) => a + r[k], 0) / 4;
    const py = [0, 1, 2, 3].map((k) => conf.reduce((a, r) => a + r[k], 0) / 4);
    const H = (q) => -q.filter((x) => x > 0).reduce((a, x) => a + x * Math.log2(x), 0);
    const bits = H(py) - conf.reduce((a, r) => a + H(r), 0) / 4;
    return { confusion: conf, success, bits_per_use: bits };
  }

  // ------------------------------------------------------------------------------------ P13: Majorana modes
  const A_ = from([[0, 1], [0, 0]]);
  function majoranas(nModes = 3) {
    const g = {};
    for (let j = 0; j < nModes; j++) {
      const c = kron(...Array.from({ length: nModes }, (_, k) => (k < j ? Z : k === j ? A_ : I2)));
      g[2 * j + 1] = add(c, dag(c)); g[2 * j + 2] = scale(add(c, dag(c), -1), 0, -1);
    }
    return g;
  }
  const G = majoranas(), ID8 = eye(8);
  const bilinear = (i, j) => scale(mul(G[i], G[j]), 0, 1);
  const logicalZ = (mode) => scale(bilinear(2 * mode + 1, 2 * mode + 2), -1);
  const projector = (op, s) => scale(add(ID8, op, s), 0.5);
  const P23 = bilinear(2, 3), P14 = bilinear(1, 4), X_C_PAPER = bilinear(4, 5);
  const CORRECTIONS = { "1,1": bilinear(5, 6), "1,-1": bilinear(3, 6), "-1,1": bilinear(3, 5), "-1,-1": ID8 };
  const MAJ_SCHEMES = ["paper_one_bit", "one_bit_best", "two_bit"];
  function initialState(psi) {                                // |psi>_A (x) |Phi+>_BC, occupation basis
    const nrm = Math.hypot(psi[0][0], psi[0][1], psi[1][0], psi[1][1]), v = Array.from({ length: 8 }, () => [0, 0]);
    for (const a of [0, 1]) for (const bc of [0, 3]) { v[4 * a + bc] = [psi[a][0] * r2 / nrm, psi[a][1] * r2 / nrm]; }
    return v;
  }
  function majoranaTeleport(psi, scheme) {
    psi = CARDINAL[psi] || psi;
    const nrm = Math.hypot(psi[0][0], psi[0][1], psi[1][0], psi[1][1]); psi = psi.map((z) => [z[0] / nrm, z[1] / nrm]);
    const rho = outer(initialState(psi)), outs = {};
    const keys = scheme === "two_bit" ? [[1, 1], [1, -1], [-1, 1], [-1, -1]] : [[1], [-1]];
    let avg = 0;
    for (const key of keys) {
      const Pi = key.length === 2 ? mul(projector(P23, key[0]), projector(P14, key[1])) : projector(P23, key[0]);
      const r = mulAll(Pi, rho, Pi), pr = trRe(r), rn = scale(r, 1 / pr);
      const U = scheme === "two_bit" ? CORRECTIONS[key.join(",")] : scheme === "paper_one_bit" ? (key[0] === 1 ? ID8 : X_C_PAPER) : (key[0] === 1 ? logicalZ(2) : ID8);
      const bob = reduce(sandwich(U, rn), 3, 2), f = expect(psi, bob);
      outs[key.join(",")] = { p: pr, fidelity: f, bloch: blochOf(bob) };
      avg += pr * f;
    }
    return { scheme, outcomes: outs, average: avg, bits_sent: scheme === "two_bit" ? 2 : 1 };
  }
  const majoranaAverage = (scheme) => Object.keys(CARDINAL).reduce((a, k) => a + majoranaTeleport(k, scheme).average, 0) / 6;
  // error budget, qll/hardware/majorana_error_budget.py
  const readoutFidelity = (snr0, gapOverKT) => 1 - 0.5 * erfc(snr0 * Math.tanh(gapOverKT / 2) / Math.SQRT2);
  const poisonedReadoutFidelity = (f, p) => (1 - p) * f + p / 2;
  const hybridizationFactor = (l, c = 1, e = 2) => Math.max(0, 1 - c * Math.exp(-e * l));
  const budgetFidelity = (snr0, gap, poison, l, readouts = 2, c = 1, e = 2) => Math.pow(poisonedReadoutFidelity(readoutFidelity(snr0, gap), poison), readouts) * hybridizationFactor(l, c, e);

  // ------------------------------------------------------------------------------------------- terminal text
  const f4 = (x) => (Math.abs(x) < 5e-13 ? "0" : Number(x.toFixed(4)).toString());
  const cstr = (z) => { const re = Math.abs(z[0]) < 5e-13 ? 0 : z[0], im = Math.abs(z[1]) < 5e-13 ? 0 : z[1]; return im === 0 ? f4(re) : re === 0 ? `${f4(im)}i` : `${f4(re)}${im < 0 ? "−" : "+"}${f4(Math.abs(im))}i`; };
  const mstr = (A) => { const rows = []; for (let i = 0; i < A.n; i++) { const r = []; for (let j = 0; j < A.n; j++) r.push(cstr([A.re[i * A.n + j], A.im[i * A.n + j]])); rows.push("[" + r.join(", ") + "]"); } return "[" + rows.join(", ") + "]"; };
  const vstr = (v) => `${cstr(v[0])}|0⟩ + ${cstr(v[1])}|1⟩`;
  const S = (label, formula, sub, value, ref) => ({ label, formula, sub, value, ref: ref || "" });

  function stepsCollapse(scheme, V, leak) {
    const e = collapseExpected(scheme, V, leak), K = instrument(scheme, 1);
    const delta = Math.max(Math.abs(e.delta), 0.01);
    return [
      S("Shared pairs", "ρ_AB = V|Φ⁺⟩⟨Φ⁺| + (1−V)·I/4", `V = ${f4(V)}`, "4 × 4 density matrix", "nielsen2010"),
      S("Alice's action, bit 1", { basis: "measure at 45°", measure: "measure at 0°", flip: "apply X" }[scheme], `${K.length} Kraus operator(s), ΣK†K = I`, mstr(K[0]), "nielsen2010"),
      S("Bob's state, bit 0", "ρ_B = Tr_A[Σ (K⊗I) ρ_AB (K⊗I)†]", "", mstr(e.rhoB[0]), "ghirardi1980"),
      S("Bob's state, bit 1", "= Tr_A[(ΣK†K ⊗ I) ρ_AB] = Tr_A ρ_AB", "cyclic trace over A", mstr(e.rhoB[1]), "ghirardi1980"),
      S("Bob's click statistics", "P(b=1 | x) = ⟨1|ρ_B|1⟩ (× (1 − leak) for x = 1)", `leak = ${f4(leak)}`, `${f4(e.p1[0])} and ${f4(e.p1[1])}`, "qll/circuits/collapse_signalling.py"),
      S("Bias", "δ = P(b=1|1) − P(b=1|0)", "", f4(e.delta), "casella2002"),
      S("Information per use", "I(X;B) = h(p̄) − [h(p₀) + h(p₁)]/2", "", `${e.mi.toExponential(3)} bits`, "cover2006"),
      S("Uses to detect δ", "n = (z₀.₉₉₅ + z₀.₉)²[p₀(1−p₀) + p₁(1−p₁)]/δ²", `δ = ${f4(delta)}`, `${usesToDetect(delta).toLocaleString("en-US")} per message value`, "casella2002"),
      S("With a classical channel", "teleport |x⟩ with two bits", "Bob reads x exactly", "1 bit per use", "bennett1993"),
      S("Verdict", "no instrument of Alice's changes ρ_B", leak > 0 ? "a nonzero δ here is the injected physical leak" : "", leak > 0 ? "leak detectable: crosstalk, not signalling" : "0 bits: no signalling", "ghirardi1980"),
    ];
  }
  function stepsTeleport(state, mode, p2) {
    const r = teleportRho(state, mode, p2), outs = teleportOutcomes(state), psi = CARDINAL[state];
    const lines = [
      S("Input", "|ψ⟩ = α|0⟩ + β|1⟩", `state "${state}"`, vstr(psi), "nielsen2010"),
      S("Shared pair", "|Φ⁺⟩ = (|00⟩ + |11⟩)/√2 via H, CX", `CX noise p₂ = ${f4(p2)}`, `F_pair = ${f4(1 - 3 * p2 / 4)}`, "bennett1993"),
      S("Alice's Bell rotation", "CX(0→1), H(0)", "|ψ⟩|Φ⁺⟩ = ½ Σ |m₀m₁⟩ X^m₁ Z^m₀ |ψ⟩", "4 outcomes", "bennett1993"),
    ];
    outs.forEach((o) => lines.push(S(`Outcome m₀m₁ = ${o.m0}${o.m1}`, "P = 1/4; Bob holds X^m₁ Z^m₀|ψ⟩", `correction: ${o.correction}`, vstr(o.bob), "bennett1993")));
    lines.push(S("Two classical bits travel", "at or below light speed", mode === "no_bits" ? "none sent" : "m₀, m₁ → Bob", mode === "no_bits" ? "Bob holds I/2" : "Bob corrects", "bennett1993"));
    lines.push(S("Bob's state", "ρ_B = Tr₀₁ ρ", "", mstr(r.bob), "nielsen2010"));
    lines.push(S("Fidelity, this input", "F = ⟨ψ|ρ_B|ψ⟩", "", f4(r.fidelity), "jozsa1994"));
    lines.push(S("Average over six states", "F̄ = mean over the 2-design", mode === "feedforward" ? `closed form (1 + (1 − p₂)²)/2 = ${f4(expectedFeedforwardFidelity(p2))}` : "", f4(teleportAverage(mode, p2)), "dankert2009"));
    lines.push(S("Classical limit", "F̄ ≤ 2/3 without entanglement", "", "0.6667", "massar1995"));
    return lines;
  }
  function stepsSuperdense(mode, p2) {
    const r = superdense(mode, p2);
    return [
      S("Shared pair", "|Φ⁺⟩ via H, CX", `CX noise p₂ = ${f4(p2)}`, "", "bennett1992"),
      S("Alice encodes (i, j)", "Z^i X^j on her qubit", "", "four messages", "bennett1992"),
      S(mode === "send_qubit" ? "Alice sends her qubit" : "Alice keeps her qubit", mode === "send_qubit" ? "Bob: CX, H, read both" : "Bob reads his half alone: ρ_B = I/2", "", "", "bennett1992"),
      S("Confusion matrix", "P(decoded | sent)", "", "[" + r.confusion.map((row) => "[" + row.map(f4).join(", ") + "]").join(", ") + "]", "qll/circuits/superdense_cloud.py"),
      S("Success", "mean of the diagonal", "", f4(r.success), "qll/circuits/superdense_cloud.py"),
      S("Information per use", "I = H(Y) − H(Y|X)", "Holevo: ≤ 2 bits with prior entanglement", `${f4(r.bits_per_use)} bits`, "holevo1973"),
    ];
  }
  function stepsMajorana(state, scheme, budget) {
    const r = majoranaTeleport(state, scheme), psi = CARDINAL[state];
    const lines = [
      S("Six Majorana modes", "γ₁ = X_A, γ₂ = Y_A, γ₃ = Z_A X_B, γ₄ = Z_A Y_B, γ₅ = Z_A Z_B X_C, γ₆ = Z_A Z_B Y_C", "Jordan–Wigner", "8 × 8 operators", "kitaev2001"),
      S("Input", "|ψ⟩_A ⊗ |Φ⁺⟩_BC", `state "${state}"`, vstr(psi), "crogman2025"),
      S("Parity measurements", scheme === "two_bit" ? "P₂₃ = iγ₂γ₃ = −X_A X_B, then P₁₄ = iγ₁γ₄ = Y_A Y_B" : "P₂₃ = iγ₂γ₃ only", "projectors (I ± P)/2", scheme === "two_bit" ? "4 outcomes" : "2 outcomes", "bonderson2008"),
    ];
    for (const [k, o] of Object.entries(r.outcomes)) lines.push(S(`Outcome (${k})`, "p = Tr(Π ρ Π)", scheme === "two_bit" ? "parity correction iγγ" : scheme === "paper_one_bit" ? "X_C if p = −1 (paper's Eq. 12)" : "Z_C if p = +1 (best one-bit)", `p = ${f4(o.p)}, F = ${f4(o.fidelity)}`, "crogman2025"));
    lines.push(S("Average fidelity, this input", "F = Σ p·F", `${r.bits_sent} classical bit(s)`, f4(r.average), "crogman2025"));
    lines.push(S("Average over six states", "two bits: 1; one bit: at most 2/3", "", f4(majoranaAverage(scheme)), "dankert2009"));
    if (budget) {
      const fr = readoutFidelity(budget.snr0, budget.gap), fe = poisonedReadoutFidelity(fr, budget.poison), hy = hybridizationFactor(budget.l);
      lines.push(S("Readout fidelity", "F_read = 1 − ½ erfc(μ₀ tanh(Δ/2kT)/(√2σ))", `μ₀/σ = ${f4(budget.snr0)}, Δ/kT = ${f4(budget.gap)}`, f4(fr), "crogman2025"));
      lines.push(S("Poisoning", "F_eff = (1 − Γτ)F_read + Γτ/2", `Γτ = ${f4(budget.poison)}`, f4(fe), "rainis2012"));
      lines.push(S("Hybridization", "1 − e^(−2L/ξ)", `L/ξ = ${f4(budget.l)}`, f4(hy), "cheng2012"));
      lines.push(S("Device bound", "F_tel ≳ F_eff^k (1 − e^(−2L/ξ)), k = 2 readouts", "", f4(budgetFidelity(budget.snr0, budget.gap, budget.poison, budget.l)), "crogman2025"));
    }
    return lines;
  }

  return {
    M, from, eye, mul, add, scale, dag, kron, trRe, outer, expect, reduce, blochOf, X, Y, Z, Hd, Sg, Sdg, cx, cz, on, depolarize2, h2,
    erfc, normCdf, normPpf, SCHEMES, projectors, instrument, werner, bobStateAfter, mutualInformation, usesToDetect, collapseExpected,
    CARDINAL, TELEPORT_MODES, teleportRho, teleportAverage, expectedFeedforwardFidelity, wernerAverageFidelity, teleportOutcomes,
    MESSAGES, superdense, majoranas, bilinear, logicalZ, P23, P14, MAJ_SCHEMES, majoranaTeleport, majoranaAverage,
    readoutFidelity, poisonedReadoutFidelity, hybridizationFactor, budgetFidelity,
    steps: { collapse: stepsCollapse, teleport: stepsTeleport, superdense: stepsSuperdense, majorana: stepsMajorana },
  };
});
