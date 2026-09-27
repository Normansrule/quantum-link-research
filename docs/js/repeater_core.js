/* Repeater-chain model, a line-by-line port of qll/network/repeater_chain.py, swapping_scheduler.py, the swapping and
   storage recurrences, fiber_loss.transmittance, and qkd/plob_bound.py. Works in the browser (window.QLLRepeater) and
   in Node (module.exports) so tests/test_site.py can hold it to the Python to 1e-12.
   It also samples one random run of the same nested protocol (sampleRun) for the repeater lab's animation: every
   segment retries until heralded, neighbouring pairs are swapped when both exist, a failed swap loses both pairs and
   their subtrees start again. The closed-form rate averages over such runs; tests compare the two. */
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory();
  else root.QLLRepeater = factory();
})(typeof self !== "undefined" ? self : this, function () {
  const C = 299792458.0, FIBER_INDEX = 1.47;

  const transmittance = (L_km, alpha = 0.2) => Math.pow(10, -alpha * L_km / 10);
  const roundTrip = (d_m) => 2 * d_m / C;
  function expectedMaxOfTwoGeometric(p) {
    if (p >= 1) return 1;
    if (p <= 0) return Infinity;
    return 2 / p - 1 / (p * (2 - p));
  }
  function nestedExpectedTime(L_m, n, p0, pSwap, index = FIBER_INDEX) {
    const L0 = L_m / Math.pow(2, n), t0 = roundTrip(L0 / 2 * index);
    let attempts = 1 / p0;
    for (let k = 0; k < n; k++) {
      attempts = attempts > 1 ? expectedMaxOfTwoGeometric(1 / attempts) : 1;
      attempts = attempts / pSwap;
    }
    let heralds = 0;
    for (let k = 0; k < n; k++) heralds += roundTrip(L0 * Math.pow(2, k) * index / 2);
    return attempts * t0 + heralds;
  }
  const swapped = (f) => f * f + (1 - f) * (1 - f) / 3;
  const stored = (f, t, T) => 0.25 + (f - 0.25) * Math.exp(-t / T);
  const directRate = (L_km, Rsrc = 1e9, pSrc = 0.05, alpha = 0.2) => Rsrc * pSrc * transmittance(L_km, alpha);
  const plobRate = (L_km, Rsrc = 1e9, alpha = 0.2) => Rsrc * -Math.log2(1 - transmittance(L_km, alpha));

  function memoryChain(L_km, n, Tmem, o = {}) {
    const Ratt = o.R_attempt ?? 1e6, pSrc = o.p_src ?? 0.05, pSwap = o.p_swap ?? 0.5, f0 = o.f0 ?? 0.95, alpha = o.alpha ?? 0.2;
    const nSeg = Math.pow(2, n), L0 = L_km / nSeg;
    const p0 = pSrc * Math.pow(transmittance(L0 / 2, alpha), 2);
    let Tn = nestedExpectedTime(L_km * 1e3, n, p0, pSwap, FIBER_INDEX);
    Tn = Math.max(Tn, 1 / (p0 * Ratt));
    let f = f0;
    for (let k = 0; k < n; k++) f = swapped(f);
    f = stored(f, Tn, Tmem);
    const stalled = Tn > 3 * Tmem;
    return { rate_hz: stalled ? 0 : 1 / Tn, fidelity_fraction: f, hold_time_s: Tn, n_segments: nSeg, p0, stalled };
  }
  function allPhotonic(L_km, nSeg, m = 8, Rsrc = 1e6, etaDet = 0.9, alpha = 0.2) {
    const eta = transmittance(L_km / nSeg / 2, alpha), p = 1 - Math.pow(1 - eta * etaDet, m);
    return Rsrc * Math.pow(p, nSeg);
  }
  function crossover(n, Tmem, o = {}, grid) {
    const g = grid || Array.from({ length: 400 }, (_, i) => Math.pow(10, 1 + 3 * i / 399));
    for (const L of g) if (memoryChain(L, n, Tmem, o).rate_hz > directRate(L)) return L;
    return null;
  }

  // ---- one random run of the nested protocol, for the animation ----
  function rng(seed) { let a = seed >>> 0; return () => { a = (a + 0x6D2B79F5) >>> 0; let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }
  function sampleRun(L_km, n, o = {}, seed = 1) {
    const pSrc = o.p_src ?? 0.05, pSwap = o.p_swap ?? 0.5, alpha = o.alpha ?? 0.2, Ratt = o.R_attempt ?? 1e6;
    const nSeg = Math.pow(2, n), L0 = L_km / nSeg, p0 = pSrc * Math.pow(transmittance(L0 / 2, alpha), 2);
    const t0 = Math.max(roundTrip(L0 * 1e3 / 2 * FIBER_INDEX), 1 / Ratt), R = rng(seed), events = [];
    const geometric = () => Math.max(1, Math.ceil(Math.log(1 - R()) / Math.log(1 - p0)));
    // pair over segments [i, i + 2^k) becomes available after its (possibly repeated) construction starting at t
    function build(k, i, t) {
      if (k === 0) { const done = t + geometric() * t0; events.push({ t: done, kind: "pair", k: 0, i, span: 1 }); return done; }
      const half = Math.pow(2, k - 1);
      for (let tries = 0; tries < 10000; tries++) {
        const a = build(k - 1, i, t), b = build(k - 1, i + half, t), both = Math.max(a, b);
        const herald = both + roundTrip(L0 * 1e3 * Math.pow(2, k - 1) * FIBER_INDEX / 2);
        if (R() < pSwap) { events.push({ t: herald, kind: "swap", k, i, span: 2 * half }); return herald; }
        events.push({ t: herald, kind: "fail", k, i, span: 2 * half }); t = herald;
      }
      return Infinity;
    }
    const end = build(n, 0, 0);
    events.sort((x, y) => x.t - y.t);
    return { end, events, p0, t0, nSeg };
  }
  function meanRunTime(L_km, n, o = {}, runs = 400, seed = 7) {
    let s = 0; for (let r = 0; r < runs; r++) s += sampleRun(L_km, n, o, seed + 7919 * r).end; return s / runs;
  }

  return { transmittance, roundTrip, expectedMaxOfTwoGeometric, nestedExpectedTime, swapped, stored, directRate, plobRate,
           memoryChain, allPhotonic, crossover, sampleRun, meanRunTime, FIBER_INDEX };
});
