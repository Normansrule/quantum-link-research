/* The frontier, for the frontier lab, line for line the tested Python:
     qll/circuits/teleport_delay_cloud.py   teleportation with the classical channel delayed, on a cloud processor
     qll/network/teleport_across.py         banked pairs across a distance, and a swapping node halfway
     qll/network/memory_decoherence.py      the demonstrated memories
   tests/test_lab_js.py compares every function here with the Python. */
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory();
  else root.QLLFrontier = factory();
})(typeof self !== "undefined" ? self : this, function () {
  "use strict";
  const C = 299792458, FIBER = 1.47, LIMIT = 2 / 3;
  // ----------------------------------------------------------------------------------- delay on a cloud processor
  const DELAY = { t_us: 60, T1_us: 200, T2_us: 150, p2: 0.0 };
  function blochShrink(t, T1, T2) { return [Math.exp(-t / T2), Math.exp(-t / T1)]; }
  function delayFidelity(t, T1, T2, p2, mode) {
    if (mode === "no_bits") return 0.5;
    const [e2, e1] = blochShrink(t, T1, T2), k = Math.pow(1 - (p2 || 0), mode === "deferred" ? 3 : 2);
    return 0.5 + k * (2 * e2 + e1) / 6;
  }
  function crossoverDelay(T1, T2, p2) {
    if (delayFidelity(0, T1, T2, p2) <= LIMIT) return 0;
    let lo = 0, hi = 50 * Math.max(T1, T2);
    for (let i = 0; i < 200; i++) { const m = 0.5 * (lo + hi); if (delayFidelity(m, T1, T2, p2) > LIMIT) lo = m; else hi = m; }
    return 0.5 * (lo + hi);
  }
  // ----------------------------------------------------------------------------------- banked pairs over distance
  const MEMORIES = {
    "Rb/Cs atomic ensemble (DLCZ)": { lifetime_s: 1e-3, efficiency: 0.5, bibkey: "liu2024" },
    "SiV nuclear spin in cavity": { lifetime_s: 1.0, efficiency: 0.9, bibkey: "knaut2024" },
    "NV 13C register": { lifetime_s: 60.0, efficiency: 0.9, bibkey: "bradley2019" },
    "171Yb+ hyperfine": { lifetime_s: 3600.0, efficiency: 0.99, bibkey: "wang2021ion" },
    "Eu:YSO nuclear spin, 6 h (ZEFOZ+DD)": { lifetime_s: 6 * 3600.0, efficiency: 0.01, bibkey: "zhong2015" },
    "Eu:YSO nuclear spin, 13.1 h": { lifetime_s: 13.1 * 3600.0, efficiency: 0.005, bibkey: "wang2025memory" },
  };
  const AU = 149597870700.0;
  const SCENARIOS = {
    "two rooms": [10.0, FIBER], campus: [1e3, FIBER], "city to city, 100 km fiber": [1e5, FIBER], "Los Angeles to New York, 3,940 km": [3.94e6, FIBER],
    "low Earth orbit, 1,000 km": [1e6, 1.0], "the Moon": [3.844e8, 1.0], "Mars at its closest": [0.372 * AU, 1.0], "Mars at its farthest": [2.68 * AU, 1.0],
  };
  const LINK = { distance_m: 10.0, index: FIBER, f0: 0.95, T_mem_s: 1.0, bank_s: 0.0, eta_mem: 0.9, p_bsm: 0.5 };
  const werner = (f) => (4 * f - 1) / 3, fraction = (w) => (3 * w + 1) / 4;
  const lightTime = (L, n) => (n == null ? FIBER : n) * L / C;
  function link(pp) {
    const p = Object.assign({}, LINK, pp || {}), tc = lightTime(p.distance_m, p.index), tA = p.bank_s, tB = p.bank_s + tc;
    const f = fraction(werner(p.f0) * Math.exp(-(tA + tB) / p.T_mem_s)), ln = p.f0 > 0.5 ? Math.log(4 * p.f0 - 1) : 0, F = (2 * f + 1) / 3;
    return { light_time_s: tc, alice_wait_s: tA, bob_wait_s: tB, fraction: f, fidelity_with_bits: F, fidelity_without_bits: 0.5, beats_classical: F > LIMIT,
      success_per_use: p.eta_mem * p.eta_mem * p.p_bsm, max_bank_s: ln > 0 ? Math.max(0, (p.T_mem_s * ln - tc) / 2) : 0, min_memory_s: ln > 0 ? tc / ln : Infinity };
  }
  function forScenario(name, memory, extra) {
    const [L, n] = SCENARIOS[name], m = MEMORIES[memory];
    return link(Object.assign({ distance_m: L, index: n, T_mem_s: m.lifetime_s, eta_mem: m.efficiency }, extra || {}));
  }
  // ----------------------------------------------------------------------------------- a swapping node halfway
  const SWAP = { distance_m: 20.0, index: FIBER, f0: 0.95, T_mem_s: 1.0, alpha_db_per_km: 0.2, p_swap: 0.5 };
  const swappedFraction = (f1, f2) => f1 * f2 + (1 - f1) * (1 - f2) / 3;
  const transmittance = (Lkm, a) => Math.pow(10, -a * Lkm / 10);
  const maxTwoGeometric = (p) => (p >= 1 ? 1 : p <= 0 ? Infinity : 2 / p - 1 / (p * (2 - p)));
  function swap(ss) {
    const s = Object.assign({}, SWAP, ss || {}), half = lightTime(s.distance_m / 2, s.index);
    const fPair = fraction(werner(swappedFraction(s.f0, s.f0)) * Math.exp(-2 * half / s.T_mem_s));
    const tele = link({ distance_m: s.distance_m, index: s.index, f0: fPair, T_mem_s: s.T_mem_s }), Lkm = s.distance_m / 1e3;
    const ef = transmittance(Lkm, s.alpha_db_per_km), es = transmittance(Lkm / 2, s.alpha_db_per_km);
    return { half_light_time_s: half, pair_fraction: fPair, direct_fraction: s.f0, fidelity_with_bits: tele.fidelity_with_bits, beats_classical: tele.beats_classical,
      announce_s: half, teleport_s: tele.light_time_s, total_s: half + tele.light_time_s, eta_direct: ef, eta_segment: es,
      attempts_direct: 1 / ef, attempts_swapped: maxTwoGeometric(es) / s.p_swap, node_learns_key: false, trusted_relay_learns_key: true };
  }
  // ----------------------------------------------------------------------------------- the terminal
  const f = (x, d = 4) => (!isFinite(x) ? String(x) : Math.abs(x) >= 1e5 || (x !== 0 && Math.abs(x) < 1e-3) ? x.toExponential(d - 1) : (+x.toPrecision(d)).toString());
  const S = (label, formula, sub, value, ref, why) => ({ label, formula, sub, value, ref, why });
  function dur(s) {
    if (!isFinite(s)) return "forever";
    const a = Math.abs(s);
    return a < 1e-6 ? `${f(s * 1e9, 3)} ns` : a < 1e-3 ? `${f(s * 1e6, 3)} µs` : a < 1 ? `${f(s * 1e3, 3)} ms` : a < 120 ? `${f(s, 3)} s` : a < 7200 ? `${f(s / 60, 3)} min` : `${f(s / 3600, 3)} h`;
  }
  function stepsDelay(t, T1, T2, p2) {
    const [e2, e1] = blochShrink(t, T1, T2), F = delayFidelity(t, T1, T2, p2), tx = crossoverDelay(T1, T2, p2);
    return [
      S("The two bits in transit", "Bob's qubit idles for t", `t = ${f(t)} µs`, `${f(t * 1e-6 * C / 1000, 3)} km of light travel`, "qll/channels/light_time_delay.py", "While the bits travel, Bob's half just waits; on a chip the wait stands in for distance."),
      S("Dephasing", "x, y shrink by e^(−t/T₂)", `T₂ = ${f(T2)} µs`, f(e2), "krantz2019", "Superposition fades first: the phase between 0 and 1 drifts."),
      S("Relaxation", "z shrinks by e^(−t/T₁)", `T₁ = ${f(T1)} µs`, f(e1), "krantz2019", "An excited qubit falls back to 0 on its own."),
      S("Gate errors", "shrink (1 − p₂)²", `p₂ = ${f(p2)}`, f((1 - p2) ** 2), "qll/circuits/teleport_cloud.py", "The two noisy two-qubit gates blur the state a little even with no wait."),
      S("Fidelity with the bits", "F = ½ + (1 − p₂)²(2e^(−t/T₂) + e^(−t/T₁))/6", "", f(F), "nielsen2002", "How close Bob's corrected qubit is to Alice's, averaged over all inputs."),
      S("Without the bits", "F = ½", "", "0.5", "peres2004", "Without the two bits Bob has a coin flip, however long he waits: no message travels by entanglement alone."),
      S("Longest useful wait", "F(t) = 2/3", "", `${f(tx, 3)} µs`, "massar1995", "Past this wait, guessing and re-preparing would do as well as teleporting."),
      S("Mars needs", "t_Mars / t_chip", "3 to 22 minutes", `${f(lightTime(SCENARIOS["Mars at its closest"][0], 1) / (tx * 1e-6), 2)}× to ${f(lightTime(SCENARIOS["Mars at its farthest"][0], 1) / (tx * 1e-6), 2)}× longer`, "qll/channels/light_time_delay.py", "This is why planetary teleportation waits for memories that hold for hours."),
    ];
  }
  function stepsLink(pp, memoryName) {
    const p = Object.assign({}, LINK, pp || {}), r = link(p), mem = memoryName && MEMORIES[memoryName];
    return [
      S("Light time", "t_c = n L / c", `L = ${f(p.distance_m / 1000)} km, n = ${p.index}`, dur(r.light_time_s), "qll/channels/light_time_delay.py", "The two bits travel at light speed at best; nothing reaches Bob sooner."),
      S("Memories", "T_mem (as reported), η_mem (assumed)", mem ? memoryName : "custom", `${dur(p.T_mem_s)}, ${f(p.eta_mem * 100, 3)} %`, mem ? mem.bibkey : "qll/network/memory_decoherence.py", "Each end keeps its half in a memory. The coherence time is from the cited experiment; the photon storage efficiency is an assumed operating point."),
      S("Waiting", "Alice t_b, Bob t_b + t_c", `t_b = ${dur(p.bank_s)}`, `${dur(r.alice_wait_s)} and ${dur(r.bob_wait_s)}`, "qll/network/teleport_across.py", "Bob waits longest: he must hold his half until the bits arrive."),
      S("Pair after storage", "w = w₀ e^(−(t_A + t_B)/T_mem), f = (3w + 1)/4", `f₀ = ${f(p.f0)}`, f(r.fraction), "werner1989", "Stored entanglement fades; f is how close the pair still is to perfect."),
      S("Fidelity with the bits", "F = (2f + 1)/3", "", f(r.fidelity_with_bits), "horodecki1996", "Above 2/3, no classical trick could do as well; that is the quantum part."),
      S("Without the bits", "F = ½", "", "0.5", "peres2004", "Bob's half alone tells him nothing; the message moves only with the bits."),
      S("Memory needed", "T_mem > t_c / ln(4f₀ − 1)", "", dur(r.min_memory_s), "qll/network/teleport_across.py", "The shortest memory lifetime that survives this distance even with no banking."),
      S("Use the bank within", "t_b < (T_mem ln(4f₀ − 1) − t_c)/2", "", r.max_bank_s > 0 ? dur(r.max_bank_s) : "not possible", "qll/network/teleport_across.py", "Banked pairs expire: after this long a stored pair is no better than guessing."),
      S("Success per use", "η_mem² p_BSM", `p_BSM = ${p.p_bsm}`, f(r.success_per_use), "calsamiglia2001", "Both memories must give their photon back and the Bell measurement must succeed."),
    ];
  }
  function stepsSwap(ss) {
    const s = Object.assign({}, SWAP, ss || {}), r = swap(s);
    return [
      S("Two segments", "A–C and C–B, each L/2", `L = ${f(s.distance_m / 1000)} km`, `${f(s.distance_m / 2000)} km each`, "qll/network/teleport_across.py", "The node in the middle halves the distance each photon must cross."),
      S("Swap at the node", "f = f₁f₂ + (1 − f₁)(1 − f₂)/3", `f₀ = ${f(s.f0)}`, f(swappedFraction(s.f0, s.f0)), "zukowski1993", "A Bell measurement at the node joins two pairs into one between the ends; errors add up."),
      S("Wait for the node", "both ends wait L/2 at light speed", "", dur(r.half_light_time_s), "hermans2022", "The ends learn which pair they now share only when the node's message arrives."),
      S("End-to-end pair", "w → w e^(−2 t_half/T_mem)", `T_mem = ${dur(s.T_mem_s)}`, f(r.pair_fraction), "werner1989", "The waiting costs a little fidelity too."),
      S("Teleport A to B", "F = (2f + 1)/3", "", f(r.fidelity_with_bits), "horodecki1996", "With that pair, Alice teleports to Bob; the two bits still cross the whole distance."),
      S("Attempts, direct", "1/η(L)", `η = ${f(r.eta_direct)}`, f(r.attempts_direct), "pirandola2017", "Sending one photon all the way: fiber loss grows exponentially with distance."),
      S("Attempts, through the node", "E[max of two]/p_swap", `η(L/2) = ${f(r.eta_segment)}`, f(r.attempts_swapped), "sangouard2011", "With memories each half waits for the other; past a crossover distance this wins."),
      S("What the node learns", "outcomes uniform, independent of the pair", "", "nothing", "dur1999", "Unlike a trusted relay, the swapping node never holds the key."),
    ];
  }
  return { C, FIBER, LIMIT, DELAY, blochShrink, delayFidelity, crossoverDelay, MEMORIES, SCENARIOS, LINK, werner, fraction, lightTime, link, forScenario,
    SWAP, swappedFraction, transmittance, maxTwoGeometric, swap, dur, stepsDelay, stepsLink, stepsSwap };
});
