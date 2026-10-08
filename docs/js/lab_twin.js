/* The link twins of the lab pages, line for line the Python the test suite validates:
     qll/link/models.py, qll/link/two_room.py, qll/link/decoy.py, qll/link/expected_session.py,
     qll/link/bench_tier1.py (Tier 1 closed form), and qll/qkd/e91.py (CHSH).
   tests/test_lab_js.py runs every function here under node and compares it with the Python to 1e-9 or better.
   Each `steps.*` function returns the lines the lab terminal prints: label, formula, substitution, value, reference.
   `sample.*` draws a session pulse by pulse and writes the two per-site logs of qll/link/hardware_log.py, so a log
   made in the browser goes straight into `python run.py ingest A.csv --bob B.csv`. */
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory();
  else root.QLLTwin = factory();
})(typeof self !== "undefined" ? self : this, function () {
  "use strict";
  const H = 6.62607015e-34, C = 299792458;                 // exact SI values [bipm2019]
  const LN2 = Math.LN2;
  const log2 = (x) => Math.log(x) / LN2;
  const h2 = (p) => (p <= 0 || p >= 1 ? 0 : -p * log2(p) - (1 - p) * log2(1 - p));

  // ---------------------------------------------------------------- LinkConfig defaults (qll/link/config.py)
  const DEFAULTS = {
    scenario: "baseline", seed: 2026, n_pulses: 1000000, pulse_rate_hz: 1e6, distance_km: 0, attenuation_db_per_km: 0.2,
    extra_loss_db: 0, receiver_loss_db: 1.0, detector_efficiency: 0.2, dark_count_prob: 1e-6, crosstalk_click_prob: 0,
    misalignment_error: 0.01, source_model: "single_photon", mu_signal: 0.5, mu_decoy: 0.1, p_signal: 0.8, p_decoy: 0.15,
    eve_fraction: 0, sample_fraction: 0.1, min_sample_bits: 200, qber_threshold: 0.11, qber_alert: 0.03,
    min_key_block_bits: 1000, eps_pe: 1e-10, eps_pa: 1e-10, verify_tag_bits: 64,
  };
  const config = (over) => Object.assign({}, DEFAULTS, over || {});

  // ---------------------------------------------------------------- qll/link/models.py
  const channelTransmittance = (c) => Math.pow(10, -(c.attenuation_db_per_km * c.distance_km) / 10) * Math.pow(10, -c.extra_loss_db / 10);
  const channelLossDb = (c) => c.attenuation_db_per_km * c.distance_km + c.extra_loss_db;
  const signalClickProb = (c) => channelTransmittance(c) * Math.pow(10, -c.receiver_loss_db / 10) * c.detector_efficiency;
  const backgroundClickProb = (c) => Math.min(1, c.dark_count_prob + c.crosstalk_click_prob);
  const signalError = (c) => { const q = c.eve_fraction / 4; return q * (1 - c.misalignment_error) + (1 - q) * c.misalignment_error; };

  // ---------------------------------------------------------------- qll/link/decoy.py
  const meanUpper = (k, eps) => { const L = Math.log(1 / eps); return k + L + Math.sqrt(L * L + 2 * k * L); };
  const meanLower = (k, eps) => { const L = Math.log(1 / eps); return Math.max(0, k + 1.5 * L - Math.sqrt(2.25 * L * L + 3 * k * L)); };
  function decoyBound(mu, nu, nPulses, nDetect, decoyErrors, decoySifted, eps) {
    const [Ns, Nd, N0] = nPulses, [ks, kd, k0] = nDetect;
    if (Math.min(Ns, Nd, N0) === 0) return { single_fraction: 0, e1_upper: 0.5, y1_lower: NaN };
    const QmuHi = meanUpper(ks, eps) / Ns, Qmu = ks / Ns, QnuLo = meanLower(kd, eps) / Nd;
    const Y0hi = meanUpper(k0, eps) / N0, Y0lo = meanLower(k0, eps) / N0;
    const y1 = mu / (mu * nu - nu * nu) * (QnuLo * Math.exp(nu) - QmuHi * Math.exp(mu) * nu * nu / (mu * mu) - (mu * mu - nu * nu) / (mu * mu) * Y0hi);
    if (y1 <= 0 || Qmu === 0) return { single_fraction: 0, e1_upper: 0.5, y1_lower: y1, y0_upper: Y0hi };
    const errHi = meanUpper(decoyErrors, eps) / Math.max(decoySifted, 1) * (kd / Nd);
    const e1 = Math.min(0.5, Math.max(0, (errHi * Math.exp(nu) - 0.5 * Y0lo) / (y1 * nu)));
    return { single_fraction: Math.min(1, y1 * mu * Math.exp(-mu) / Qmu), e1_upper: e1, y1_lower: y1, y0_upper: Y0hi };
  }
  function gllpBound(mu, gain, qberUpper) {
    const pMulti = 1 - Math.exp(-mu) * (1 + mu);
    const frac = gain > 0 ? 1 - pMulti / gain : 0;
    if (frac <= 0) return { single_fraction: 0, e1_upper: 0.5 };
    return { single_fraction: frac, e1_upper: Math.min(0.5, qberUpper / frac) };
  }
  const usable = (b) => b.single_fraction > 0 && b.e1_upper < 0.5;

  // ---------------------------------------------------------------- qll/link/expected_session.py
  const EC_EFFICIENCY = 1.2;
  function classes(c) {
    const tEta = signalClickProb(c), pb = backgroundClickProb(c), ed = signalError(c);
    const mix = c.source_model === "single_photon" ? [[1, null]] : c.source_model === "weak_coherent" ? [[1, c.mu_signal]]
      : [[c.p_signal, c.mu_signal], [c.p_decoy, c.mu_decoy], [1 - c.p_signal - c.p_decoy, 0]];
    return mix.map(([share, k]) => {
      const pSig = k === null ? tEta : 1 - Math.exp(-k * tEta);
      const q = pSig + (1 - pSig) * pb;
      return { share, mu: k, q, e: q > 0 ? (pSig * ed + (1 - pSig) * pb / 2) / q : 0.5, p_sig: pSig };
    });
  }
  function expectedSession(c) {
    const cl = classes(c);
    const pDet = cl.reduce((a, k) => a + k.share * k.q, 0);
    const qber = pDet > 0 ? cl.reduce((a, k) => a + k.share * k.q * k.e, 0) / pDet : 0.5;
    const s = cl[0];
    const nSifted = 0.5 * c.n_pulses * s.share * s.q;
    const nSample = Math.max(c.min_sample_bits, Math.ceil(c.sample_fraction * nSifted));
    const nKey = Math.max(0, nSifted - nSample);
    const qUpper = Math.min(0.5, s.e + Math.sqrt(Math.log(1 / c.eps_pe) / (2 * nSample)));
    let bound, counts = null;
    if (c.source_model === "single_photon") bound = { single_fraction: 1, e1_upper: qUpper };
    else if (c.source_model === "weak_coherent") bound = gllpBound(c.mu_signal, s.q, qUpper);
    else {
      const n = cl.map((k) => Math.round(c.n_pulses * k.share)), kk = cl.map((k) => Math.round(c.n_pulses * k.share * k.q));
      const dsift = 0.5 * kk[1];
      counts = { n, k: kk, decoy_errors: Math.round(dsift * cl[1].e), decoy_sifted: Math.round(dsift) };
      bound = decoyBound(c.mu_signal, c.mu_decoy, n, kk, counts.decoy_errors, counts.decoy_sifted, c.eps_pe);
    }
    const key = nKey * bound.single_fraction * (1 - h2(bound.e1_upper)) - EC_EFFICIENCY * nKey * h2(s.e) - c.verify_tag_bits - 2 * log2(1 / c.eps_pa);
    const ok = nSifted >= nSample + c.min_key_block_bits && s.e <= c.qber_threshold && usable(bound) && key > 0;
    return { click_prob_per_pulse: pDet, qber: qber, signal_qber: s.e, sifted_bits: nSifted, sample_bits: nSample,
      key_block_bits: nKey, qber_upper: qUpper, single_fraction: bound.single_fraction, e1_upper: bound.e1_upper,
      y1_lower: bound.y1_lower, key_bits: ok ? Math.max(0, Math.floor(key)) : 0, accepted: ok, classes: cl, counts,
      reason: ok ? "accepted" : s.e > c.qber_threshold ? "error rate above threshold" : !usable(bound) ? "no single-photon bound"
        : nSifted < nSample + c.min_key_block_bits ? "too few sifted bits" : "no key after deductions" };
  }

  // ---------------------------------------------------------------- qll/link/two_room.py
  const TWO_ROOM = {
    wavelength_m: 405e-9, rep_rate_hz: 1e6, mu: 0.5, mu_decoy: 0.1, gate_s: 5e-9, sipm_pde: 0.31, sipm_dark_hz: 300e3,
    sipm_afterpulse: 0.002, channel: "free_space", path_m: 10, free_space_loss_db: 2.0, fiber_coupling_loss_db: 6.0,
    fiber_db_per_km: 30, receiver_loss_db: 1.5, polarizer_extinction: 500, waveplate_error: 0.01, n_pulses: 10000000,
  };
  const pathLossDb = (p) => (p.channel === "fiber" ? p.fiber_coupling_loss_db + p.fiber_db_per_km * p.path_m / 1000 : p.free_space_loss_db);
  const meanPhotonNumber = (E, lambda, attDb) => E / (H * C / lambda) * Math.pow(10, -attDb / 10);
  const attenuationFor = (mu, E, lambda) => 10 * Math.log10(E / (H * C / lambda) / mu);
  const darkProbPerGate = (hz, gate, detectors = 2) => 1 - Math.pow(1 - (1 - Math.exp(-hz * gate)), detectors);
  function twoRoomConfig(parts) {
    const p = Object.assign({}, TWO_ROOM, parts || {});
    const pDark = darkProbPerGate(p.sipm_dark_hz, p.gate_s);
    const base = config({ scenario: "two_room", seed: 2027, n_pulses: p.n_pulses, pulse_rate_hz: p.rep_rate_hz, distance_km: 0,
      extra_loss_db: pathLossDb(p), receiver_loss_db: p.receiver_loss_db, detector_efficiency: p.sipm_pde, dark_count_prob: pDark,
      misalignment_error: 1 / (1 + p.polarizer_extinction) + p.waveplate_error, source_model: "weak_coherent_decoy",
      mu_signal: p.mu, mu_decoy: p.mu_decoy });
    const pClick = p.mu * signalClickProb(base) + pDark;
    return Object.assign(base, { crosstalk_click_prob: p.sipm_afterpulse * pClick });
  }
  function twoRoomPredict(parts) {
    const p = Object.assign({}, TWO_ROOM, parts || {}), c = twoRoomConfig(p), e = expectedSession(c);
    return { path_loss_db: pathLossDb(p), mu: p.mu, dark_prob_per_gate: c.dark_count_prob, click_prob_per_pulse: e.click_prob_per_pulse,
      clicks_per_s: e.click_prob_per_pulse * p.rep_rate_hz, expected_qber: e.qber, sifted_bits_per_s: 0.5 * e.click_prob_per_pulse * p.rep_rate_hz,
      misalignment_error: c.misalignment_error };
  }

  // ---------------------------------------------------------------- qll/link/bench_tier1.py, closed form
  const TIER1 = { i0: 800, leakage: 0.01, ambient: 20, noise: 8, eve_fraction: 0, n_pulses: 4000, pulse_rate_hz: 2 };
  function erf(x) {                                     // Taylor series below 3, continued fraction for erfc above
    const ax = Math.abs(x);
    if (ax < 3) {
      let term = x, sum = x;
      for (let n = 1; n < 200; n++) { term *= -x * x / n; const t = term / (2 * n + 1); sum += t; if (Math.abs(t) < 1e-17 * Math.abs(sum)) break; }
      return 2 / Math.sqrt(Math.PI) * sum;
    }
    // erfc(x) = exp(-x^2)/sqrt(pi) * 1/(x + 1/2/(x + 1/(x + 3/2/(x + ...)))) by modified Lentz
    let f = ax, Cc = ax, D = 0;
    for (let n = 1; n < 300; n++) {
      const a = n / 2; D = ax + a * D; D = D === 0 ? 1e-300 : 1 / D; Cc = ax + a / Cc; const d = Cc * D; f *= d; if (Math.abs(d - 1) < 1e-16) break;
    }
    const erfc = Math.exp(-ax * ax) / Math.sqrt(Math.PI) / f;
    return x > 0 ? 1 - erfc : erfc - 1;
  }
  const meanReading = (b, pol, an) => { const c2 = Math.cos((pol - an) * Math.PI / 180) ** 2; return b.i0 * (b.leakage + (1 - 2 * b.leakage) * c2) + b.ambient; };
  function idealThresholds(b) { const bright = meanReading(b, 0, 0), dark = meanReading(b, 90, 0); return { high: dark + 0.75 * (bright - dark), low: dark + 0.25 * (bright - dark), bright, dark }; }
  function pDecideZero(mean, noise, th) {
    if (noise <= 0) return mean >= th.high ? 1 : mean <= th.low ? 0 : 0.5;
    const cdf = (v) => 0.5 * (1 + erf((v - mean) / (noise * Math.SQRT2)));
    return 1 - cdf(th.high) + 0.5 * (cdf(th.high) - cdf(th.low));
  }
  function tier1Expected(params) {
    const b = Object.assign({}, TIER1, params || {}), th = idealThresholds(b), f = b.eve_fraction;
    const e0 = 1 - pDecideZero(th.bright, b.noise, th), e1 = pDecideZero(th.dark, b.noise, th);
    const eR = e0 + e1 - (e0 * e0 + e1 * e1) / 2 - e0 * e1;
    const q = (1 - f) * (e0 + e1) / 2 + f * (eR / 2 + 0.25);
    const half = meanReading(b, 0, 45);
    return { thresholds: th, e0, e1, e_r: eR, qber: q, half, p_zero_half: pDecideZero(half, b.noise, th), sifted_per_s: 0.5 * b.pulse_rate_hz };
  }

  // ---------------------------------------------------------------- qll/qkd/e91.py
  const chshFromVisibility = (V) => 2 * Math.SQRT2 * V;
  const chshStd = (V, n) => 2 * Math.sqrt((1 - V * V / 2) / n);
  function diRatePerRound(S, Q) {
    if (S <= 2) return 0; S = Math.min(S, 2 * Math.SQRT2);
    return Math.max(0, 1 - h2((1 + Math.sqrt(S * S / 4 - 1)) / 2) - h2(Q));
  }

  // ---------------------------------------------------------------- terminal lines
  function fmt(x, d = 4) {
    if (typeof x !== "number") return String(x);
    if (!isFinite(x)) return String(x);
    if (x === 0) return "0";
    const a = Math.abs(x);
    if (a >= 1e6 || a < 1e-3) return x.toExponential(d - 1).replace("e", "e");
    if (Number.isInteger(x) && a < 1e6) return x.toLocaleString("en-US");
    return Number(x.toPrecision(d)).toString();
  }
  const pct = (x, d = 2) => (100 * x).toFixed(d) + " %";
  const S = (label, formula, sub, value, ref) => ({ label, formula, sub, value, ref: ref || "" });

  function stepsTier1(params) {
    const b = Object.assign({}, TIER1, params || {}), r = tier1Expected(b), th = r.thresholds;
    return [
      S("Malus reading, aligned", "I = I0[ε + (1−2ε)cos²Δθ] + I_amb", `${fmt(b.i0)}·[${fmt(b.leakage)} + ${fmt(1 - 2 * b.leakage)}·1] + ${fmt(b.ambient)}`, `${fmt(th.bright)} counts`, "hecht2017"),
      S("Malus reading, crossed", "Δθ = 90°", `${fmt(b.i0)}·${fmt(b.leakage)} + ${fmt(b.ambient)}`, `${fmt(th.dark)} counts`, "hecht2017"),
      S("Malus reading, wrong basis", "Δθ = 45°: cos² = 1/2", `${fmt(b.i0)}·0.5 + ${fmt(b.ambient)}`, `${fmt(r.half)} counts`, "hecht2017"),
      S("Thresholds", "high = dark + 0.75·span, low = dark + 0.25·span", `span = ${fmt(th.bright - th.dark)}`, `bit 0 ≥ ${fmt(th.high)}, bit 1 ≤ ${fmt(th.low)}`, "qll/link/bench_tier1.py"),
      S("Misread a 0", "e0 = 1 − [Φ_above(high) + ½·Φ_between]", `σ = ${fmt(b.noise)} counts`, fmt(r.e0, 5), "casella2002"),
      S("Misread a 1", "e1 = P(0 | dark)", `σ = ${fmt(b.noise)} counts`, fmt(r.e1, 5), "casella2002"),
      S("Wrong-basis decision", "P(0 | half) ≈ ½ → a coin flip, sifted away", `I = ${fmt(r.half)}`, fmt(r.p_zero_half, 4), "bennett1984"),
      S("Interception adds", "Q = (1−f)·e + f·(e_R/2 + 1/4)", `f = ${fmt(b.eve_fraction)}`, pct(r.qber), "bennett1984"),
      S("Sifted rate", "R_s = R/2", `${fmt(b.pulse_rate_hz)} Hz / 2`, `${fmt(r.sifted_per_s)} bits/s`, "bennett1984"),
      S("Security meaning", "bright light can be tapped without disturbance", "", "none: a processing-chain demo", "qll/link/bench_tier1.py"),
    ];
  }
  function linkSteps(c, e, extra) {
    const tEta = signalClickProb(c), pb = backgroundClickProb(c), ed = signalError(c), L = channelLossDb(c) + c.receiver_loss_db;
    const out = (extra || []).slice();
    out.push(S("Loss to the detector", "L = αd + L_extra + L_rx", `${fmt(c.attenuation_db_per_km)}·${fmt(c.distance_km)} + ${fmt(c.extra_loss_db)} + ${fmt(c.receiver_loss_db)}`, `${fmt(L)} dB`, "qll/link/models.py"));
    out.push(S("Single-photon click", "Tη = 10^(−L/10)·η_det", `${fmt(Math.pow(10, -L / 10))}·${fmt(c.detector_efficiency)}`, fmt(tEta, 5), "qll/link/models.py"));
    out.push(S("Background per gate", "p_bg = p_dark + p_after", `${fmt(c.dark_count_prob)} + ${fmt(c.crosstalk_click_prob)}`, fmt(pb, 4), "casella2002"));
    out.push(S("Optical error", "e_d = (1 − f/4)·e_mis + (f/4)(1 − e_mis)", `e_mis = ${fmt(c.misalignment_error)}, f = ${fmt(c.eve_fraction)}`, pct(ed), "bennett1984"));
    e.classes.forEach((k) => {
      const name = k.mu === null ? "photon" : k.mu === 0 ? "vacuum" : `μ = ${fmt(k.mu)}`;
      const how = k.mu === null ? `Tη` : `1 − e^(−${fmt(k.mu)}·Tη)`;
      out.push(S(`Gain, ${name}` + (e.classes.length > 1 ? ` (${pct(k.share, 0)} of pulses)` : ""), "Q = p_sig + (1 − p_sig)·p_bg", `p_sig = ${how} = ${fmt(k.p_sig, 4)}`, fmt(k.q, 5), "ma2005"));
      out.push(S(`Error, ${name}`, "E = [p_sig·e_d + (1 − p_sig)·p_bg/2]/Q", "", pct(k.e), "ma2005"));
    });
    out.push(S("Click probability per pulse", "p_det = Σ share·Q", "", `${fmt(e.click_prob_per_pulse, 5)} (${fmt(e.click_prob_per_pulse * c.pulse_rate_hz)} /s)`, "qll/link/models.py"));
    out.push(S("Error rate, all clicks", "QBER = Σ share·Q·E / p_det", "", pct(e.qber), "qll/link/models.py"));
    out.push(S("Sifted key bits", "n = ½·N·share_sig·Q_sig", `½·${fmt(c.n_pulses)}·${fmt(e.classes[0].share)}·${fmt(e.classes[0].q, 4)}`, fmt(Math.round(e.sifted_bits)), "bennett1984"));
    out.push(S("Error-rate bound", "Q_U = E_sig + √(ln(1/ε)/2m)", `m = ${fmt(e.sample_bits)}`, pct(e.qber_upper), "hoeffding1963"));
    if (c.source_model === "weak_coherent_decoy") {
      out.push(S("Single-photon yield", "Y₁ ≥ μ/(μν−ν²)[Q_ν e^ν − Q_μ e^μ ν²/μ² − (μ²−ν²)/μ²·Y₀]", "with Chernoff margins", fmt(e.y1_lower, 4), "ma2005"));
      out.push(S("Single-photon share", "s₁ = Y₁ μ e^(−μ) / Q_μ", "", pct(e.single_fraction, 1), "lo2005"));
      out.push(S("Single-photon error", "e₁ ≤ (E_ν Q_ν e^ν − Y₀/2)/(Y₁ ν)", "", pct(e.e1_upper), "ma2005"));
    } else if (c.source_model === "weak_coherent") {
      out.push(S("Single-photon share (no decoys)", "s₁ = 1 − P_multi/Q_μ", "", pct(e.single_fraction, 1), "gottesman2004"));
    }
    out.push(S("Secret key", "l = n_key·s₁[1 − h(e₁)] − 1.2·n_key·h(E) − t − 2log₂(1/ε)", `n_key = ${fmt(Math.round(e.key_block_bits))}`,
      e.accepted ? `${fmt(e.key_bits)} bits per ${fmt(c.n_pulses / c.pulse_rate_hz, 3)} s session` : `rejected: ${e.reason}`, "shor2000"));
    return out;
  }
  function stepsTwoRoom(parts, over) {
    const p = Object.assign({}, TWO_ROOM, parts || {}), c = Object.assign(twoRoomConfig(p), over || {}), e = expectedSession(c);
    const pd1 = 1 - Math.exp(-p.sipm_dark_hz * p.gate_s);
    const extra = [
      S("Photon energy", "E_γ = hc/λ", `${fmt(H)}·${fmt(C)}/${fmt(p.wavelength_m)}`, `${fmt(H * C / p.wavelength_m)} J`, "bipm2019"),
      S("Path loss", p.channel === "fiber" ? "L_path = L_coupling + α·d" : "L_path = clipping + windows (measured)", p.channel === "fiber" ? `${fmt(p.fiber_coupling_loss_db)} + ${fmt(p.fiber_db_per_km)}·${fmt(p.path_m / 1000)}` : `${fmt(p.free_space_loss_db)}`, `${fmt(pathLossDb(p))} dB`, "qll/link/two_room.py"),
      S("Dark click per SiPM per gate", "p = 1 − e^(−R_dark·τ)", `1 − e^(−${fmt(p.sipm_dark_hz)}·${fmt(p.gate_s)})`, fmt(pd1, 4), "casella2002"),
      S("Dark click per basis pair", "p_dark = 1 − (1 − p)²", "", fmt(c.dark_count_prob, 4), "casella2002"),
      S("Afterpulses", "p_after = P_ap·(μ·Tη + p_dark)", `${fmt(p.sipm_afterpulse)}·(…)`, fmt(c.crosstalk_click_prob, 3), "onsemi2022microfc"),
      S("Misalignment", "e_mis = 1/(1 + ER) + e_wp", `1/${fmt(1 + p.polarizer_extinction)} + ${fmt(p.waveplate_error)}`, pct(c.misalignment_error), "hecht2017"),
    ];
    return linkSteps(c, e, extra);
  }
  function tier3Config(over) {
    return config(Object.assign({ scenario: "tier3_weak_coherent", n_pulses: 10000000, pulse_rate_hz: 100000, distance_km: 0, attenuation_db_per_km: 3.5,
      extra_loss_db: 0, receiver_loss_db: 3.0, detector_efficiency: 0.5, dark_count_prob: 1e-6, misalignment_error: 0.02,
      source_model: "weak_coherent_decoy", mu_signal: 0.5, mu_decoy: 0.1, p_signal: 0.8, p_decoy: 0.15 }, over || {}));
  }
  function tier4Config(over) {
    const o = Object.assign({ visibility: 0.94, session_s: 40 }, over || {});
    const c = config({ scenario: "tier4_entanglement_bbm92", n_pulses: 2000000, pulse_rate_hz: 50000, distance_km: 1.0, attenuation_db_per_km: 3.5,
      extra_loss_db: 0, receiver_loss_db: 1.0, detector_efficiency: 0.25, dark_count_prob: 1e-5, misalignment_error: 0.03, qber_alert: 0.05 });
    for (const k of Object.keys(o)) if (k in c) c[k] = o[k];
    if (over && "visibility" in over) c.misalignment_error = (1 - o.visibility) / 2;
    if (over && "session_s" in over) c.n_pulses = Math.round(o.session_s * c.pulse_rate_hz);
    return c;
  }
  function tier4Bell(c, e) {
    const V = 1 - 2 * e.signal_qber, Sv = chshFromVisibility(V);
    const coincidences = c.n_pulses * e.click_prob_per_pulse, perSetting = coincidences / 4;
    const sd = chshStd(V, perSetting);
    return { V, S: Sv, sd, sigmas: (Sv - 2) / sd, di_rate: diRatePerRound(Sv, e.signal_qber), coincidences };
  }
  function stepsTier3(c) { return linkSteps(c, expectedSession(c)); }
  function stepsTier4(c) {
    const e = expectedSession(c), b = tier4Bell(c, e);
    const out = [S("Pair visibility", "V = 1 − 2·e_mis", `1 − 2·${fmt(c.misalignment_error)}`, fmt(1 - 2 * c.misalignment_error, 4), "bennett1992bbm92")];
    const lines = linkSteps(c, e, out);
    lines.push(S("Effective visibility", "V_eff = 1 − 2·E (accidentals included)", "", fmt(b.V, 4), "aspect1982"));
    lines.push(S("Bell value", "S = 2√2·V_eff", `2.8284·${fmt(b.V, 4)}`, fmt(b.S, 4), "clauser1969"));
    lines.push(S("Bell uncertainty", "σ_S = 2√((1 − V²/2)/n)", `n = ${fmt(Math.round(b.coincidences / 4))} per setting`, `${fmt(b.sd, 3)} → ${fmt(b.sigmas, 3)} σ above 2`, "casella2002"));
    lines.push(S("Device-independent rate", "r = 1 − h((1 + √(S²/4 − 1))/2) − h(Q)", "", `${fmt(b.di_rate, 3)} bits per round (asymptotic)`, "acin2007"));
    return lines;
  }

  // ---------------------------------------------------------------- sampling sessions (site logs)
  function rng(seed) {                                   // mulberry32: small, fast, seedable; not for cryptography
    let a = seed >>> 0;
    return () => { a |= 0; a = (a + 0x6d2b79f5) | 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
  }
  function gauss(r) { let u = 0; while (u === 0) u = r(); return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * r()); }
  /* A link session pulse by pulse: Site A's bit, basis, and intensity class; a signal click with p_sig(k), otherwise
     background with p_bg; a matched-basis signal click is wrong with e_d, everything else is a fair coin. */
  function sampleLink(c, n, seed) {
    const r = rng(seed), cl = classes(c), pb = backgroundClickProb(c), ed = signalError(c), decoy = c.source_model === "weak_coherent_decoy";
    const A = new Uint8Array(n * 3), Bidx = [], Bb = [], Bv = [];
    let clicks = 0, sifted = 0, errors = 0;
    for (let i = 0; i < n; i++) {
      const bit = r() < 0.5 ? 1 : 0, basis = r() < 0.5 ? 1 : 0;
      let k = 0; if (decoy) { const u = r(); k = u < c.p_signal ? 0 : u < c.p_signal + c.p_decoy ? 1 : 2; }
      A[3 * i] = bit; A[3 * i + 1] = basis; A[3 * i + 2] = k;
      const sig = r() < cl[k].p_sig, bg = !sig && r() < pb;
      if (!sig && !bg) continue;
      const bb = r() < 0.5 ? 1 : 0;
      const val = sig && bb === basis ? (r() < ed ? 1 - bit : bit) : (r() < 0.5 ? 1 : 0);
      Bidx.push(i); Bb.push(bb); Bv.push(val); clicks++;
      if (bb === basis && k === 0) { sifted++; if (val !== bit) errors++; }
    }
    return { n, decoy, A, B: { idx: Bidx, basis: Bb, bit: Bv }, clicks, sifted, errors, click_prob: clicks / n, qber: sifted ? errors / sifted : 0.5 };
  }
  function sampleTier1(params, n, seed) {
    const b = Object.assign({}, TIER1, params || {}), r = rng(seed), th = idealThresholds(b);
    const ANGLE = [[0, 90], [45, 135]], AN = [0, 45];
    const read = (pol, an) => meanReading(b, pol, an) + b.noise * gauss(r);
    const decide = (x) => (x >= th.high ? 0 : x <= th.low ? 1 : r() < 0.5 ? 0 : 1);
    const A = new Uint8Array(n * 3), Bidx = [], Bb = [], Bv = [], readings = [];
    let sifted = 0, errors = 0;
    for (let i = 0; i < n; i++) {
      const bit = r() < 0.5 ? 1 : 0, basis = r() < 0.5 ? 1 : 0, bb = r() < 0.5 ? 1 : 0;
      let pol = ANGLE[basis][bit];
      if (r() < b.eve_fraction) { const eb = r() < 0.5 ? 1 : 0; pol = ANGLE[eb][decide(read(pol, AN[eb]))]; }
      const x = read(pol, AN[bb]), v = decide(x);
      A[3 * i] = bit; A[3 * i + 1] = basis; Bidx.push(i); Bb.push(bb); Bv.push(v); if (i < 64) readings.push(x);
      if (bb === basis) { sifted++; if (v !== bit) errors++; }
    }
    return { n, decoy: false, A, B: { idx: Bidx, basis: Bb, bit: Bv }, clicks: n, sifted, errors, click_prob: 1, qber: sifted ? errors / sifted : 0.5, readings };
  }
  function siteCsv(s) {
    const a = [s.decoy ? "pulse,alice_bit,alice_basis,alice_intensity" : "pulse,alice_bit,alice_basis"];
    for (let i = 0; i < s.n; i++) a.push(s.decoy ? `${i},${s.A[3 * i]},${s.A[3 * i + 1]},${s.A[3 * i + 2]}` : `${i},${s.A[3 * i]},${s.A[3 * i + 1]}`);
    const b = ["pulse,bob_basis,bob_bit"];
    for (let j = 0; j < s.B.idx.length; j++) b.push(`${s.B.idx[j]},${s.B.basis[j]},${s.B.bit[j]}`);
    return { alice: a.join("\n") + "\n", bob: b.join("\n") + "\n" };
  }
  /* check_against_twin: click probability within 15 % and error rate within 1.5 points of the prediction. */
  function checkAgainstTwin(measured, predicted, clickTol = 0.15, qberTol = 0.015) {
    const dev = measured.click_prob / predicted.click_prob_per_pulse - 1;
    const rows = [
      { quantity: "click probability per pulse", predicted: predicted.click_prob_per_pulse, measured: measured.click_prob, pass: Math.abs(dev) <= clickTol, hint: "loss, detector efficiency, or mean photon number" },
      { quantity: "error rate (signal, sifted)", predicted: predicted.signal_qber, measured: measured.qber, pass: Math.abs(measured.qber - predicted.signal_qber) <= qberTol, hint: "polarizer extinction, waveplate angle, or dark counts" },
    ];
    return { rows, all_pass: rows.every((r) => r.pass) };
  }

  return {
    H, C, h2, DEFAULTS, config, channelTransmittance, channelLossDb, signalClickProb, backgroundClickProb, signalError,
    meanUpper, meanLower, decoyBound, gllpBound, classes, expectedSession, EC_EFFICIENCY,
    TWO_ROOM, pathLossDb, meanPhotonNumber, attenuationFor, darkProbPerGate, twoRoomConfig, twoRoomPredict,
    TIER1, erf, meanReading, idealThresholds, pDecideZero, tier1Expected,
    chshFromVisibility, chshStd, diRatePerRound, tier3Config, tier4Config, tier4Bell,
    steps: { tier1: stepsTier1, twoRoom: stepsTwoRoom, tier3: stepsTier3, tier4: stepsTier4 },
    sample: { link: sampleLink, tier1: sampleTier1 }, siteCsv, checkAgainstTwin, fmt, pct, rng,
  };
});
