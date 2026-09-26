/* Three-qubit teleportation, exact state-vector arithmetic. Qubit order: index = 4*q0 + 2*q1 + q2
   (q0 = Alice's input, q1 = Alice's half of the Bell pair, q2 = Bob's half). Complex numbers are [re, im].
   Used by docs/teleport/ and checked against Qiskit in tests/test_site.py. */
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory();
  else root.QLLTeleport = factory();
})(typeof self !== "undefined" ? self : this, function () {
  const R = Math.SQRT1_2;
  const cmul = (a, b) => [a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]];
  const cadd = (a, b) => [a[0] + b[0], a[1] + b[1]];
  const cscale = (a, s) => [a[0] * s, a[1] * s];
  const bit = (i, q) => (i >> (2 - q)) & 1;
  const flip = (i, q) => i ^ (1 << (2 - q));
  function init(alpha, beta) { const s = Array.from({ length: 8 }, () => [0, 0]); s[0] = alpha.slice(); s[4] = beta.slice(); return s; }
  function H(s, q) {
    const out = s.map(() => [0, 0]);
    s.forEach((a, i) => { const j = flip(i, q); const sign = bit(i, q) ? -1 : 1;
      out[i] = cadd(out[i], cscale(a, sign * R)); out[j] = cadd(out[j], cscale(a, R)); });
    return out;
  }
  function X(s, q) { const out = s.map(() => [0, 0]); s.forEach((a, i) => (out[flip(i, q)] = a.slice())); return out; }
  function Z(s, q) { return s.map((a, i) => (bit(i, q) ? cscale(a, -1) : a.slice())); }
  function CX(s, c, t) { const out = s.map(() => [0, 0]); s.forEach((a, i) => (out[bit(i, c) ? flip(i, t) : i] = a.slice())); return out; }
  function prob(a) { return a[0] * a[0] + a[1] * a[1]; }
  function measure(s, m0, m1) {
    // project q0 = m0, q1 = m1 and renormalise; returns [state, probability]
    const out = s.map((a, i) => (bit(i, 0) === m0 && bit(i, 1) === m1 ? a.slice() : [0, 0]));
    const p = out.reduce((acc, a) => acc + prob(a), 0);
    return [out.map((a) => cscale(a, 1 / Math.sqrt(p))), p];
  }
  function bobState(s, m0, m1) { const base = 4 * m0 + 2 * m1; return [s[base].slice(), s[base + 1].slice()]; }
  function steps(alpha, beta, m0, m1) {
    const s0 = init(alpha, beta);
    const s1 = CX(H(s0, 1), 1, 2);          // Bell pair between Alice (q1) and Bob (q2)
    const s2 = H(CX(s1, 0, 1), 0);          // Alice's Bell-basis rotation
    const [s3, p] = measure(s2, m0, m1);    // Alice measures: two classical bits
    let s4 = s3; if (m1) s4 = X(s4, 2); if (m0) s4 = Z(s4, 2);   // Bob's corrections, after the bits arrive
    return { s0, s1, s2, s3, s4, p, bob: bobState(s4, m0, m1) };
  }
  function blochOf(v) {
    const [a, b] = v; const ab = cmul([a[0], -a[1]], b);
    return [2 * ab[0], 2 * ab[1], prob(a) - prob(b)];
  }
  function fidelity(v, alpha, beta) {
    // |<psi|v>|^2 up to global phase
    const ip = cadd(cmul([alpha[0], -alpha[1]], v[0]), cmul([beta[0], -beta[1]], v[1]));
    return prob(ip);
  }
  return { init, H, X, Z, CX, measure, steps, blochOf, fidelity, prob };
});
