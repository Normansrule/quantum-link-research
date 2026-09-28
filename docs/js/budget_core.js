/* The Earth-Mars link budget, a line-by-line port of qll/systems/mars_budget.py and the channel models it calls
   (Gaussian-beam diffraction, pointing jitter, Beer-Lambert atmosphere, depolarizing storage, binary entropy).
   Needs QLLEphemeris (docs/js/ephemeris.js) for ranges and Sun angles; the memory table comes from site_data.json.
   Works in the browser (window.QLLBudget) and in Node, where tests/test_site.py holds it to the Python. */
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory;
  else root.QLLBudget = factory(root.QLLEphemeris);
})(typeof self !== "undefined" ? self : this, function (E) {
  const C = 299792458.0, SEP = 3.0, TAU = { 8.1e-7: 0.35, 8.5e-7: 0.32, 1.55e-6: 0.15 };
  const DEFAULT = { architecture: "earth_source", source_rate_hz: 1e9, modes: 1000, wavelength_m: 1550e-9, tx_waist_m: 0.5,
    rx_diameter_earth_m: 4.0, rx_diameter_mars_m: 4.0, pointing_rad: 1e-7, eta_tx: 0.8, eta_rx: 0.7, eta_det: 0.9,
    earth_elevation_deg: 40.0, duty: 0.5, memory: "171Yb+ hyperfine", f0: 0.95, storage_factor: 2.0 };
  const zR = (lam, w0) => Math.PI * w0 * w0 / lam;
  const beamRadius = (L, lam, w0) => w0 * Math.sqrt(1 + Math.pow(L / zR(lam, w0), 2));
  const geometric = (L, lam, w0, D) => { const w = beamRadius(L, lam, w0); return 1 - Math.exp(-2 * (D / 2) * (D / 2) / (w * w)); };
  const pointing = (s, L, w) => w * w / (w * w + 4 * s * s * L * L);
  function atmosphere(elev, lam) {
    const keys = Object.keys(TAU).map(Number); let best = keys[0];
    for (const k of keys) if (Math.abs(k - lam) < Math.abs(best - lam)) best = k;
    return Math.exp(-TAU[best] / Math.sin(elev * Math.PI / 180));
  }
  const h2 = (x) => (x <= 0 || x >= 1) ? 0 : -x * Math.log2(x) - (1 - x) * Math.log2(1 - x);
  const stored = (f, t, T) => 0.25 + (f - 0.25) * Math.exp(-t / T);
  function sepAt(obs, tgt) {
    const sx = -obs[0], sy = -obs[1], tx = tgt[0] - obs[0], ty = tgt[1] - obs[1];
    const c = (sx * tx + sy * ty) / (Math.hypot(sx, sy) * Math.hypot(tx, ty));
    return Math.acos(Math.max(-1, Math.min(1, c))) * 180 / Math.PI;
  }
  function leg(L, d, D, ground) {
    const out = [];
    if (ground) out.push(["Earth atmosphere", atmosphere(d.earth_elevation_deg, d.wavelength_m)]);
    out.push(["diffraction", geometric(L, d.wavelength_m, d.tx_waist_m, D)]);
    out.push(["pointing", pointing(d.pointing_rad, L, beamRadius(L, d.wavelength_m, d.tx_waist_m))]);
    out.push(["receiver and detector", d.eta_rx * d.eta_det]);
    return out;
  }
  function budget(design, tDays, memories) {
    const d = Object.assign({}, DEFAULT, design), mem = memories.find((m) => m.name === d.memory);
    if (!mem) throw new Error("unknown memory " + d.memory);
    const L = E.rangeM(tDays);
    let factors = [["transmit optics", d.eta_tx]], available, legs;
    if (d.architecture === "earth_source") {
      factors = factors.concat(leg(L, d, d.rx_diameter_mars_m, true).map(([n, f]) => ["Earth to Mars: " + n, f]));
      available = E.sepDeg(tDays) >= SEP; legs = [L];
    } else {
      const e = E.earth(tDays), m = E.mars(tDays), r = E.l4(tDays), AU = E.AU;
      const LE = Math.hypot(e[0] - r[0], e[1] - r[1]) * AU, LM = Math.hypot(r[0] - m[0], r[1] - m[1]) * AU;
      factors = factors.concat(leg(LE, d, d.rx_diameter_earth_m, true).map(([n, f]) => ["relay to Earth: " + n, f]));
      factors = factors.concat(leg(LM, d, d.rx_diameter_mars_m, false).map(([n, f]) => ["relay to Mars: " + n, f]));
      available = Math.min(sepAt(e, r), sepAt(r, m)) >= SEP; legs = [LE, LM];
    }
    factors.push(["memories (write and read, both ends)", mem.efficiency * mem.efficiency]);
    factors.push(["availability (conjunction x duty)", available ? d.duty : 0]);
    let rate = d.source_rate_hz * d.modes;
    const stages = [{ name: "source", factor: 1, rate_per_s: rate }];
    for (const [name, f] of factors) { rate *= f; stages.push({ name, factor: f, rate_per_s: rate }); }
    const tStore = d.storage_factor * L / C, f = stored(d.f0, tStore, mem.lifetime_s), F = (2 * f + 1) / 3, Q = 2 * (1 - f) / 3;
    const key = Q < 0.5 ? Math.max(0, 1 - 2 * h2(Q)) : 0;
    const perDay = rate * 86400;
    return { range_m: L, legs_m: legs, stages, storage_s: tStore, fraction: f, teleport_fidelity: F, key_bits_per_pair: key,
             pairs_per_day: perDay, useful: F > 2 / 3, teleportations_per_day: F > 2 / 3 ? perDay : 0, key_bits_per_day: perDay * key,
             total_db: stages.slice(1).reduce((s, x) => s + (x.factor > 0 ? 10 * Math.log10(x.factor) : -Infinity), 0), available };
  }
  return { DEFAULT, geometric, pointing, atmosphere, h2, budget };
});
