/* Outdoors and toward orbit, for the outdoor lab, line for line the tested Python:
     qll/link/outdoor_link.py           the Phase 1 link between two roofs, with sky background
     qll/link/satellite_pass.py         a satellite pass over a ground station and its decoy-state key
     qll/channels/free_space_diffraction.py, pointing_jitter.py, atmosphere.py, link_budget.py, thermal_background.py
     qll/qkd/decoy_state.py             the asymptotic decoy-state key per pulse
   tests/test_lab_js.py compares every function here with the Python. Needs lab_twin.js. */
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory(require("./lab_twin.js"));
  else root.QLLOutdoor = factory(root.QLLTwin);
})(typeof self !== "undefined" ? self : this, function (T) {
  "use strict";
  const H = 6.62607015e-34, C = 299792458, R_E = 6371000, GM = 3.986004418e14;
  const log2 = (x) => Math.log(x) / Math.LN2, h2 = (p) => (p <= 0 || p >= 1 ? 0 : -p * log2(p) - (1 - p) * log2(1 - p));
  // ----------------------------------------------------------------------------------------- channel modules
  const rayleighRange = (lam, w0) => Math.PI * w0 * w0 / lam;
  const beamRadius = (L, lam, w0) => w0 * Math.sqrt(1 + (L / rayleighRange(lam, w0)) ** 2);
  const geometric = (L, lam, w0, D) => { const w = beamRadius(L, lam, w0); return -Math.expm1(-2 * (D / 2) ** 2 / (w * w)); };   // expm1: no cancellation at long range
  const pointing = (sigma, L, w) => (w * w) / (w * w + 4 * sigma * sigma * L * L);
  const airmass = (e) => 1 / Math.sin(e * Math.PI / 180);
  const TAU = [[810e-9, 0.35], [850e-9, 0.32], [1550e-9, 0.15]];
  function atmospheric(e, lam, tau) { if (tau == null) tau = TAU.reduce((b, k) => (Math.abs(k[0] - lam) < Math.abs(b[0] - lam) ? k : b))[1]; return Math.exp(-tau * airmass(e)); }
  const skyRadianceCounts = (Llam, lam, dlam, A, omega, eta) => Llam * A * omega * dlam / (H * C / lam) * eta;
  // ----------------------------------------------------------------------------------------- outdoor link
  const SKY = { "sunlit day": 1e-1, twilight: 1e-3, "city night": 1e-6, "dark site, moonless": 1e-8 };
  const RECEIVERS = { sipm: {}, spad: { sipm_pde: 0.30, sipm_dark_hz: 300.0, sipm_afterpulse: 0.005 } };
  const OUTDOOR = { distance_m: 300, tx_waist_m: 0.01, rx_aperture_m: 0.05, pointing_urad: 10, air_db_per_km: 1.0, coupling_loss_db: 3.0, sky_radiance: 1e-6, filter_nm: 3.0, fov_mrad: 1.0, receiver: {} };
  const parts = (p) => { const o = Object.assign({}, OUTDOOR, p || {}); o.receiver = Object.assign({}, T.TWO_ROOM, o.receiver || {}); return o; };
  function factors(pp) {
    const p = parts(pp), lam = p.receiver.wavelength_m, w = beamRadius(p.distance_m, lam, p.tx_waist_m);
    return { beam_radius_m: w, geometric: geometric(p.distance_m, lam, p.tx_waist_m, p.rx_aperture_m), pointing: pointing(p.pointing_urad * 1e-6, p.distance_m, w),
      air: Math.pow(10, -p.air_db_per_km * p.distance_m / 1000 / 10), coupling: Math.pow(10, -p.coupling_loss_db / 10) };
  }
  const pathLossDb = (pp) => { const f = factors(pp); return -10 * Math.log10(f.geometric * f.pointing * f.air * f.coupling); };
  function skyCounts(pp) {
    const p = parts(pp), r = p.receiver, A = Math.PI * (p.rx_aperture_m / 2) ** 2, om = Math.PI * (p.fov_mrad * 1e-3 / 2) ** 2;
    return skyRadianceCounts(p.sky_radiance * 1e9, r.wavelength_m, p.filter_nm * 1e-9, A, om, Math.pow(10, -r.receiver_loss_db / 10) * r.sipm_pde);
  }
  function config(pp) {
    const p = parts(pp), r = Object.assign({}, p.receiver, { channel: "free_space", path_m: p.distance_m, free_space_loss_db: pathLossDb(p) });
    const base = T.twoRoomConfig(r);
    const skyPair = 1 - Math.exp(-skyCounts(p) / 2 * r.gate_s), pd = 1 - (1 - base.dark_count_prob) * (1 - skyPair);
    return Object.assign(base, { scenario: "outdoor", seed: 2028, dark_count_prob: pd, crosstalk_click_prob: r.sipm_afterpulse * (r.mu * T.signalClickProb(base) + pd) });
  }
  function predict(pp) {
    const c = config(pp), s = T.expectedSession(c);
    return Object.assign({ path_loss_db: pathLossDb(pp) }, factors(pp), { sky_counts_per_s: skyCounts(pp), dark_prob_per_gate: c.dark_count_prob,
      click_prob_per_pulse: s.click_prob_per_pulse, qber: s.qber, key_bits: s.key_bits, accepted: s.accepted, session: s, config: c });
  }
  // ----------------------------------------------------------------------------------------- satellite pass
  const BUDGETS = { micius: { lambda_m: 810e-9, w0_m: 0.026, D_rx_m: 1.2, sigma_point_rad: 1.2e-6, eta_optics: 0.25, eta_det: 0.5 },
    jinan1: { lambda_m: 850e-9, w0_m: 0.06, D_rx_m: 0.28, sigma_point_rad: 1.0e-6, eta_optics: 0.3, eta_det: 0.55 } };
  const DOWNLINK = { budget: "micius", altitude_m: 500e3, min_elevation_deg: 15, rep_rate_hz: 100e6, mu: 0.5, y0: 1e-6, e_det: 0.01 };
  const PRESETS = { micius: Object.assign({}, DOWNLINK), jinan1: Object.assign({}, DOWNLINK, { budget: "jinan1", rep_rate_hz: 625e6 / 10 }) };
  const slantRange = (h, e) => { const s = Math.sin(e * Math.PI / 180); return -R_E * s + Math.sqrt((R_E * s) ** 2 + 2 * R_E * h + h * h); };
  function budgetFactors(b, L, e) {
    const w = beamRadius(L, b.lambda_m, b.w0_m);
    return { geo: geometric(L, b.lambda_m, b.w0_m, b.D_rx_m), atm: atmospheric(e, b.lambda_m, b.tau_zenith), point: pointing(b.sigma_point_rad, L, w), optics: b.eta_optics, det: b.eta_det };
  }
  const etaTotal = (b, L, e) => Object.values(budgetFactors(b, L, e)).reduce((a, x) => a * x, 1);
  function decoyRate(eta, mu = 0.5, Y0 = 1e-6, e_det = 0.015, f_ec = 1.16, q = 0.5) {
    const e0 = 0.5, Qmu = 1 - Math.exp(-eta * mu) + Y0, Emu = (e0 * Y0 + e_det * (1 - Math.exp(-eta * mu))) / Qmu, Y1 = eta + Y0, e1 = (e0 * Y0 + e_det * eta) / Y1, Q1 = Y1 * mu * Math.exp(-mu);
    return Math.max(0, q * (-Qmu * f_ec * h2(Math.min(Emu, 0.5)) + Q1 * (1 - h2(Math.min(e1, 0.5)))));
  }
  const angularRate = (h) => Math.sqrt(GM / (R_E + h) ** 3);
  const elevationDeg = (th, h) => Math.atan2(Math.cos(th) - R_E / (R_E + h), Math.sin(Math.abs(th))) * 180 / Math.PI;
  function passHalfAngle(h, emin) { const e = emin * Math.PI / 180; return Math.acos(R_E * Math.cos(e) / (R_E + h)) - e; }
  const dl = (d) => { const o = Object.assign({}, DOWNLINK, d || {}); o.b = typeof o.budget === "string" ? BUDGETS[o.budget] : o.budget; return o; };
  function atTime(dd, t) {
    const d = dl(dd), th = angularRate(d.altitude_m) * t, e = elevationDeg(th, d.altitude_m);
    if (e <= 0) return { t_s: t, elevation_deg: e, range_m: NaN, loss_db: Infinity, eta: 0, key_per_pulse: 0, theta: th };
    const L = slantRange(d.altitude_m, e), eta = etaTotal(d.b, L, e);
    return { t_s: t, elevation_deg: e, range_m: L, loss_db: -10 * Math.log10(eta), eta, key_per_pulse: decoyRate(eta, d.mu, d.y0, d.e_det), factors: budgetFactors(d.b, L, e), theta: th };
  }
  function passSummary(dd, step = 1) {
    const d = dl(dd), half = passHalfAngle(d.altitude_m, d.min_elevation_deg) / angularRate(d.altitude_m), n = Math.floor(half / step);
    const rows = []; for (let k = -n; k <= n; k++) rows.push(atTime(d, k * step));
    return { duration_s: 2 * half, rows, key_bits: rows.reduce((a, r) => a + r.key_per_pulse, 0) * d.rep_rate_hz * step,
      min_loss_db: Math.min(...rows.map((r) => r.loss_db)), max_loss_db: Math.max(...rows.map((r) => r.loss_db)) };
  }
  // ----------------------------------------------------------------------------------------- terminal lines
  const f = (x, d = 4) => (!isFinite(x) ? String(x) : Math.abs(x) >= 1e5 || (x !== 0 && Math.abs(x) < 1e-3) ? x.toExponential(d - 1) : (+x.toPrecision(d)).toString());
  const db = (x) => (-10 * Math.log10(x)).toFixed(2) + " dB";
  const S = (label, formula, sub, value, ref, why) => ({ label, formula, sub, value, ref, why });
  function stepsOutdoor(pp) {
    const p = parts(pp), fa = factors(p), r = predict(p), c = r.config, s = r.session, lam = p.receiver.wavelength_m;
    return [
      S("Beam after the sending telescope", "w(L) = w₀ √(1 + (L/z_R)²), z_R = πw₀²/λ", `w₀ = ${f(p.tx_waist_m * 1000)} mm, L = ${f(p.distance_m)} m, z_R = ${f(rayleighRange(lam, p.tx_waist_m))} m`, `${f(fa.beam_radius_m * 1000)} mm`, "siegman1986", "A laser beam spreads as it travels; a wider starting beam spreads less."),
      S("Light caught by the receiving telescope", "η_geo = 1 − exp(−2(D/2)²/w²)", `D = ${f(p.rx_aperture_m * 1000)} mm`, `${f(fa.geometric)} (${db(fa.geometric)})`, "bourgoin2013", "The receiving lens catches the part of the spreading beam that falls on it."),
      S("Pointing jitter", "η_pt = w²/(w² + 4σ²L²)", `σ = ${f(p.pointing_urad)} µrad`, `${f(fa.pointing)} (${db(fa.pointing)})`, "bourgoin2013", "A tripod that wobbles by microradians moves the spot by millimetres at the far roof."),
      S("Air", "η_air = 10^(−αL/10)", `α = ${f(p.air_db_per_km)} dB/km`, `${f(fa.air)} (${db(fa.air)})`, "andrews2005", "Air scatters violet light (that is why the sky is blue), more on hazy days."),
      S("Coupling at the receiver", "field stop and detector coupling", "", `${db(fa.coupling)}`, "qll/link/outdoor_link.py", "Getting the collected light onto small detectors through a field stop costs a few decibels."),
      S("Path loss in total", "L = −10 log₁₀(η_geo η_pt η_air η_c)", "", `${f(r.path_loss_db)} dB`, "qll/link/outdoor_link.py", "This replaces the hallway's 2 dB in the two-room twin."),
      S("Sky photons into the receiver", "N = L_λ A Ω Δλ/(hc/λ)·η_rx", `L_λ = ${f(p.sky_radiance)} W m⁻² sr⁻¹ nm⁻¹, Δλ = ${f(p.filter_nm)} nm, field ${f(p.fov_mrad)} mrad`, `${f(r.sky_counts_per_s)} per second`, "er-long2005", "The sky glows; whatever of it falls within the telescope's field and the filter's color is counted like a photon."),
      S("False clicks per gate, one basis", "p_bg = 1 − (1 − p_dark)(1 − e^(−Nτ/2))", `τ = ${f(p.receiver.gate_s * 1e9)} ns`, f(c.dark_count_prob, 3), "casella2002", "Detector noise and skylight together: each false click is a random bit."),
      S("Click probability per pulse", "p_det = Σ share·Q", "", f(s.click_prob_per_pulse, 4), "qll/link/models.py", "What the receiver's counter shows, per pulse sent."),
      S("Error rate", "QBER = Σ share·Q·E / p_det", "", (100 * s.qber).toFixed(2) + " %", "qll/link/models.py", "Above 11 % no key can be made; skylight pushes it toward 50 %."),
      S("Secret key per session", "decoy bound, Cascade, amplification", "", s.accepted ? `${s.key_bits.toLocaleString("en-US")} bits per ${f(c.n_pulses / c.pulse_rate_hz, 3)} s` : `rejected: ${s.reason}`, "shor2000", "What survives every deduction; zero means this setup cannot make a key here."),
    ];
  }
  function stepsPass(dd, t) {
    const d = dl(dd), r = atTime(d, t), sm = passSummary(d);
    if (!(r.elevation_deg > 0)) return [S("Below the horizon", "e ≤ 0", "", "no line of sight", "qll/link/satellite_pass.py", "The satellite cannot be seen from the station.")];
    const fa = r.factors;
    return [
      S("Orbit", "ω = √(GM/(R + h)³)", `h = ${f(d.altitude_m / 1000)} km`, `period ${(2 * Math.PI / angularRate(d.altitude_m) / 60).toFixed(1)} min`, "petit2010", "Lower orbits are faster: a 500 km satellite circles Earth in about an hour and a half."),
      S("Where it is", "e = atan2(cos θ − R/(R + h), sin θ)", `t = ${t.toFixed(0)} s after overhead`, `elevation ${r.elevation_deg.toFixed(1)}°`, "qll/link/satellite_pass.py", "The satellite rises, passes overhead, and sets within minutes."),
      S("How far", "range = −R sin e + √((R sin e)² + 2Rh + h²)", "", `${f(r.range_m / 1000)} km`, "qll/channels/link_budget.py", "Low on the horizon it is three times farther than overhead."),
      S("Beam spreading", "η_geo = 1 − exp(−2(D/2)²/w²)", `receiver ${f(d.b.D_rx_m * 100)} cm`, `${db(fa.geo)}`, "bourgoin2013", "From hundreds of kilometres even a tight beam is metres wide; the telescope catches a sliver."),
      S("Air mass", "η_atm = exp(−τ/sin e)", "", `${db(fa.atm)}`, "andrews2005", "Low passes look through more air."),
      S("Pointing", "η_pt = w²/(w² + 4σ²L²)", `σ = ${f(d.b.sigma_point_rad * 1e6)} µrad`, `${db(fa.point)}`, "bourgoin2013", "Holding a beam on a telescope from orbit takes microradian pointing."),
      S("Optics and detector", "η_opt·η_det", "", `${db(fa.optics * fa.det)}`, "yin2017", "Telescopes, filters, and detectors lose light too."),
      S("Total loss now", "−10 log₁₀ η", "", `${r.loss_db.toFixed(1)} dB`, "yin2017", "Micius-class links lose 20 to 40 dB on one downlink; the twin reproduces the published range."),
      S("Key per pulse now", "R = ½{Q₁[1 − h(e₁)] − f Q_μ h(E_μ)}", `μ = ${d.mu}, Y₀ = ${f(d.y0)}`, f(r.key_per_pulse, 3), "lo2005", "The decoy-state key rate per pulse sent, if the statistics were perfect."),
      S("Key over the pass", "Σ R · rate · Δt", `${(sm.duration_s / 60).toFixed(1)} min above ${d.min_elevation_deg}°`, `${f(sm.key_bits, 3)} bits (upper estimate)`, "ma2005", "Finite counts and real system losses reduce this; it bounds what one pass could give."),
    ];
  }
  return { rayleighRange, beamRadius, geometric, pointing, airmass, atmospheric, skyRadianceCounts, SKY, RECEIVERS, OUTDOOR, parts, factors, pathLossDb, skyCounts, config, predict,
    BUDGETS, PRESETS, slantRange, budgetFactors, etaTotal, decoyRate, angularRate, elevationDeg, passHalfAngle, atTime, passSummary, stepsOutdoor, stepsPass };
});
