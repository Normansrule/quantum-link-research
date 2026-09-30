/* The Earth-Mars link budget, a line-by-line port of qll/systems/mars_budget.py and the channel models it calls
   (Gaussian-beam diffraction, pointing jitter, Beer-Lambert atmosphere, depolarizing storage, binary entropy, and the
   background light of qll/channels/planetshine.py and qll/space/dark_window.py).
   Needs QLLEphemeris (docs/js/ephemeris.js) for ranges and Sun angles; the memory table comes from site_data.json.
   Works in the browser (window.QLLBudget) and in Node, where tests/test_site.py holds it to the Python. */
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory;
  else root.QLLBudget = factory(root.QLLEphemeris);
})(typeof self !== "undefined" ? self : this, function (E) {
  const C = 299792458.0, H = 6.62607015e-34, SEP = 3.0, TAU = { 8.1e-7: 0.35, 8.5e-7: 0.32, 1.55e-6: 0.15 };
  const SUN = { 8.1e-7: 1.13, 1.55e-6: 0.26 }, EARTH_R = 6.371e6, EARTH_ALBEDO = 0.30, DAY_ZENITH = 60.0;
  const DEFAULT = { architecture: "space_source", source_rate_hz: 1e9, modes: 1000, wavelength_m: 1550e-9, tx_waist_m: 0.5,
    rx_diameter_earth_m: 4.0, rx_diameter_mars_m: 4.0, pointing_rad: 1e-7, eta_tx: 0.8, eta_rx: 0.7, eta_det: 0.9,
    earth_elevation_deg: 40.0, duty: 0.5, memory: "171Yb+ hyperfine", f0: 0.95, storage_factor: 2.0,
    tx_offset_m: 3.84e8, filter_hz: 1e8, stray_light: 1e-9, sun_depression_deg: 12.0, night_radiance: 1e-7 };
  const nearest = (table, lam) => { let best = null; for (const k of Object.keys(table).map(Number)) if (best === null || Math.abs(k - lam) < Math.abs(best - lam)) best = k; return table[best]; };
  const filterNm = (lam, B) => lam * lam * B / C * 1e9;
  const lambertPhase = (a) => { a = Math.min(Math.max(a, 0), Math.PI); return (Math.sin(a) + (Math.PI - a) * Math.cos(a)) / Math.PI; };
  const sunlitRadiance = (lam, z) => EARTH_ALBEDO * nearest(SUN, lam) * Math.max(0, Math.cos(z)) / Math.PI;
  const singleMode = (L, lam, B) => L * filterNm(lam, B) * lam * lam / (H * C / lam);
  const earthshineFlux = (lam, B, d, alpha) => nearest(SUN, lam) * EARTH_ALBEDO * Math.pow(EARTH_R / d, 2) * lambertPhase(alpha) * filterNm(lam, B) / (H * C / lam);
  const airy = (theta, D, lam) => { const x = Math.PI * D * Math.abs(theta) / lam; return x < 3.8317 ? 1 : Math.min(1, 8 / (Math.PI * x * x * x)); };
  const darkFraction = (eps, e, s) => Math.min(Math.max(Math.abs(eps) - e - s, 0), 180 - 2 * e, 180 - 2 * s) / 360;
  const purity = (S, N) => (S + N > 0 ? S / (S + N) : 0);
  const zR = (lam, w0) => Math.PI * w0 * w0 / lam;
  const beamRadius = (L, lam, w0) => w0 * Math.sqrt(1 + Math.pow(L / zR(lam, w0), 2));
  const geometric = (L, lam, w0, D) => { const w = beamRadius(L, lam, w0); return 1 - Math.exp(-2 * (D / 2) * (D / 2) / (w * w)); };
  const pointing = (s, L, w) => w * w / (w * w + 4 * s * s * L * L);
  const atmosphere = (elev, lam) => Math.exp(-nearest(TAU, lam) / Math.sin(elev * Math.PI / 180));
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
  const toAperture = (factors) => factors.filter(([n]) => !n.includes("receiver")).reduce((p, [, f]) => p * f, 1);
  function budget(design, tDays, memories) {
    const d = Object.assign({}, DEFAULT, design), mem = memories.find((m) => m.name === d.memory);
    if (!mem) throw new Error("unknown memory " + d.memory);
    const L = E.rangeM(tDays), lam = d.wavelength_m, A = Math.PI * Math.pow(d.rx_diameter_mars_m / 2, 2);
    const night = singleMode(d.night_radiance, lam, d.filter_hz), elong = E.sepDeg(tDays), rad = Math.PI / 180;
    let factors = [["transmit optics", d.eta_tx]], available, legs, noise, w, extra = {};
    if (d.architecture === "earth_source") {
      const lg = leg(L, d, d.rx_diameter_mars_m, true);
      factors = factors.concat(lg.map(([n, f]) => ["Earth to Mars: " + n, f]));
      factors.push(["dark-sky window (Mars up, Sun down)", darkFraction(elong, d.earth_elevation_deg, d.sun_depression_deg)]);
      available = elong >= SEP; legs = [L];
      const S = d.source_rate_hz * d.eta_tx * toAperture(lg), day = singleMode(sunlitRadiance(lam, DAY_ZENITH * rad), lam, d.filter_hz);
      noise = night; w = purity(S, night); extra = { purity_daylight: purity(S, day), noise_daylight_per_mode_s: day };
    } else if (d.architecture === "space_source") {
      if (d.tx_offset_m <= EARTH_R) throw new Error("a space source must sit off Earth's disk");
      const lg = leg(L, d, d.rx_diameter_mars_m, false);
      factors = factors.concat(lg.map(([n, f]) => ["space to Mars: " + n, f]));
      available = elong >= SEP; legs = [L];
      const theta = d.tx_offset_m / L, rej = Math.max(airy(theta, d.rx_diameter_mars_m, lam), d.stray_light);
      noise = earthshineFlux(lam, d.filter_hz, L, elong * rad) * A * rej;
      w = purity(d.source_rate_hz * d.eta_tx * toAperture(lg), noise); extra = { earth_offset_rad: theta, rejection: rej };
    } else {
      const e = E.earth(tDays), m = E.mars(tDays), r = E.l4(tDays), AU = E.AU;
      const LE = Math.hypot(e[0] - r[0], e[1] - r[1]) * AU, LM = Math.hypot(r[0] - m[0], r[1] - m[1]) * AU;
      const lgE = leg(LE, d, d.rx_diameter_earth_m, true), lgM = leg(LM, d, d.rx_diameter_mars_m, false);
      factors = factors.concat(lgE.map(([n, f]) => ["relay to Earth: " + n, f]));
      factors = factors.concat(lgM.map(([n, f]) => ["relay to Mars: " + n, f]));
      factors.push(["dark-sky window at the Earth receiver", darkFraction(sepAt(e, r), d.earth_elevation_deg, d.sun_depression_deg)]);
      available = Math.min(sepAt(e, r), sepAt(r, m)) >= SEP; legs = [LE, LM];
      const nM = earthshineFlux(lam, d.filter_hz, LM, elong * rad) * A * d.stray_light;
      noise = night + nM;
      w = purity(d.source_rate_hz * d.eta_tx * toAperture(lgE), night) * purity(d.source_rate_hz * d.eta_tx * toAperture(lgM), nM);
    }
    factors.push(["memories (write and read, both ends)", mem.efficiency * mem.efficiency]);
    factors.push(["availability (conjunction x duty)", available ? d.duty : 0]);
    let rate = d.source_rate_hz * d.modes;
    const stages = [{ name: "source", factor: 1, rate_per_s: rate }];
    for (const [name, f] of factors) { rate *= f; stages.push({ name, factor: f, rate_per_s: rate }); }
    const tStore = d.storage_factor * L / C, fStored = stored(d.f0, tStore, mem.lifetime_s), f = 0.25 + w * (fStored - 0.25);
    // key is measured on arrival (BBM92): no storage decay and no memory stage
    const F = (2 * f + 1) / 3, fKey = 0.25 + w * (d.f0 - 0.25), Q = 2 * (1 - fKey) / 3, key = Q < 0.5 ? Math.max(0, 1 - 2 * h2(Q)) : 0;
    const perDay = rate * 86400, heralds = w > 0 ? perDay / w : Infinity, useful = F > 2 / 3, memFactor = mem.efficiency * mem.efficiency;
    return { range_m: L, legs_m: legs, stages, storage_s: tStore, fraction: f, fraction_stored: fStored, teleport_fidelity: F,
             key_bits_per_pair: key, pairs_per_day: perDay, purity: w, noise_per_mode_s: noise, heralds_per_day: heralds, useful,
             teleportations_per_day: useful && perDay > 0 ? heralds : 0, key_bits_per_day: perDay > 0 ? heralds / memFactor * key : 0,
             key_error_rate: Q, memory_factor: memFactor,
             total_db: stages.slice(1).reduce((s, x) => s + (x.factor > 0 ? 10 * Math.log10(x.factor) : -Infinity), 0), available, extra };
  }
  return { DEFAULT, geometric, pointing, atmosphere, h2, lambertPhase, sunlitRadiance, singleMode, earthshineFlux, airy, darkFraction, budget };
});
