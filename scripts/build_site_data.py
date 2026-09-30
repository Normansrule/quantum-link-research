"""Write docs/site_data.json: every number the website shows, computed by the tested qll functions.
Run after any physics change (CI and pre-commit do). The site never hard-codes a physics number."""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def coupler_data() -> dict:
    """Curves and trajectories for the coupler lab page (docs/coupler/), all from the tested hardware models."""
    from dataclasses import replace

    from qll.hardware.cz_gate import FREQUENCY_SHAPED_FLAT_NS, CZPulse, _hamiltonian
    from qll.hardware.tunable_coupler import CoupledPair, static_zz_exact

    pair = CoupledPair()
    idle = pair.zz_free_frequency(5.0, 5.5)
    wc = np.unique(np.concatenate([np.linspace(4.60, 7.60, 151), np.linspace(5.10, 5.70, 121), [idle]]))   # dense near the zeros
    good = CZPulse()
    pulses = {"angle": good, "frequency": replace(good, shape="frequency", t_flat=FREQUENCY_SHAPED_FLAT_NS)}
    cz = {}
    for name, p in pulses.items():
        ts, p11, p20 = p.populations_from_11(dt=0.02, every=10)
        zeta = np.array([static_zz_exact(float(w), p.w2, p.alpha, p.alpha, p.g, levels=3) for w in p.w1(ts)])
        phase = -2 * np.pi * np.concatenate([[0.0], np.cumsum(0.5 * (zeta[1:] + zeta[:-1]) * np.diff(ts))])
        cz[name] = {"t_ns": ts.round(4).tolist(), "w1_ghz": p.w1(ts).round(6).tolist(), "p11": p11.round(5).tolist(),
                    "p20": p20.round(5).tolist(), "phase_rad": phase.round(5).tolist(), "zz_mhz": (1e3 * zeta).round(4).tolist(),
                    "duration_ns": p.duration, "leakage": p.leakage(0.02), "fidelity": p.average_fidelity(0.02),
                    "conditional_phase_rad": float(np.mod(p.conditional_phase(0.02), 2 * np.pi))}
    # the two levels of the {|11>, |20>} pair as qubit 1 is tuned: bare (they cross) and dressed (they avoid)
    w1 = np.linspace(5.05, 6.05, 121)
    lo, hi = [], []
    for w in w1:
        E, V = np.linalg.eigh(_hamiltonian(float(w), good.w2, good.alpha, good.g))
        weight = V[4, :] ** 2 + V[6, :] ** 2                      # rows 4, 6 = bare |11>, |20>
        pair_e = np.sort(E[np.argsort(weight)[-2:]]) - (w + good.w2)
        lo.append(pair_e[0]); hi.append(pair_e[1])
    return {
        "wc_ghz": [round(float(x), 6) for x in wc], "zz_khz": [round(1e6 * pair.zz(float(w)), 4) for w in wc],
        "geff_mhz": [round(1e3 * pair.effective_coupling(float(w)), 4) for w in wc],
        "idle_ghz": idle,
        "pair": {"w1": pair.w1, "w2": pair.w2, "alpha": pair.alpha, "g1c": pair.g1c, "g2c": pair.g2c, "g12": pair.g12},
        "cz": cz, "gate": {"w2": good.w2, "alpha": good.alpha, "g": good.g, "w1_idle": good.w1_idle, "w1_int": good.w1_int},
        "levels": {"w1_ghz": w1.round(4).tolist(), "lower_mhz": (1e3 * np.array(lo)).round(3).tolist(),
                   "upper_mhz": (1e3 * np.array(hi)).round(3).tolist(),
                   "bare20_mhz": (1e3 * (w1 - good.w2 + good.alpha)).round(3).tolist()},
        "ramsey": {"detuning_mhz": 0.5, "t2_us": 40.0},
    }


def qec_data() -> dict:
    """Lattices, sampled shots, and failure curves for the QEC lab page (docs/qec/), from the tested surface-code model."""
    from qll.circuits.surface_code_capacity import logical_failure_rate, rotated_code, sample_shots

    ps = [0.02, 0.05, 0.08, 0.11, 0.14]
    grid = [round(x, 3) for x in np.linspace(0.01, 0.16, 16)]
    out = {"ps": ps, "p_grid": grid, "codes": {}}
    for d in (3, 5, 7):
        code = rotated_code(d)
        out["codes"][str(d)] = {
            "plaquettes": [[list(c) for c in pl] for pl in code.plaquettes],
            "shots": {str(p): sample_shots(d, p, 16, seed=100 * d + int(1000 * p)) for p in ps},
            "failure": [logical_failure_rate(d, p, 20000, seed=d) for p in grid],
        }
    return out


def systems_data() -> dict:
    """The traceability matrix and stakeholder needs for the systems page (docs/systems/)."""
    import sys as _sys
    _sys.path.insert(0, str(ROOT / "scripts"))
    from build_systems_docs import NEED_TITLES
    from qll.systems.traceability import load_matrix

    return {"needs": NEED_TITLES, "requirements": load_matrix(),
            "trades": ["TS-1 link architecture", "TS-2 carrier wavelength", "TS-3 memory platform", "TS-4 apertures", "TS-5 transduction"],
            "risks": [{"id": c[1].strip(), "risk": c[2].strip(), "status": c[-2].strip()}
                      for c in (line.split("|") for line in (ROOT / "systems" / "risk_register.md").read_text(encoding="utf-8").splitlines())
                      if len(c) > 7 and c[1].strip().startswith("R-")]}


def compute_data() -> dict:
    from qll.app.messenger import required_buffer_bytes
    from qll.channels.fiber_loss import attenuation_length_km
    from qll.channels.light_time_delay import one_way_delay_s, round_trip_delay_s
    from qll.channels.link_budget import MICIUS_2017, slant_range_m
    from qll.circuits.bell import werner_state
    from qll.circuits.noise.thermal import bose_einstein_occupation
    from qll.constants.astro import AU_METERS, EARTH_MARS_MAX_M, EARTH_MARS_MIN_M
    from qll.network.memory_decoherence import BASELINES, MEMORY_TABLE, capability_matrix, crossover_time_s
    from qll.network.purification import bbpssw_rounds_to_target, bell_diagonal_weights, dejmps_rounds_to_target
    from qll.network.purified_chain import best_useful_chain, minimum_useful_memory_s
    from qll.network.repeater_chain import crossover_distance_km, memory_chain
    from qll.qkd.e91 import rounds_for_positive_di_key
    from qll.qkd.key_rate import bb84_qber_threshold
    from qll.space.ephemeris import EARTH, MARS, SYNODIC_PERIOD_DAYS, earth_mars_range_m, range_envelope_m
    from qll.space.relativity import gravitational_redshift_earth_mars

    status = json.loads((ROOT / "docs" / "status.json").read_text()) if (ROOT / "docs" / "status.json").exists() else {}
    from qll.systems.mars_budget import MarsLinkDesign
    from qll.systems.mars_budget import budget as mars_budget
    from qll.systems.key_ledger import ledger as _key_ledger
    _ledger = _key_ledger(MarsLinkDesign(), 1e6)
    _days = np.arange(0.0, 800.0, 1.0)
    _r = np.array([float(earth_mars_range_m(t)) for t in _days])
    t_close, t_far = float(_days[np.argmin(_r)]), float(_days[np.argmax(_r)])
    lo, hi = range_envelope_m()
    cm = capability_matrix(0.95)
    micius30 = 2 * MICIUS_2017.loss_db(slant_range_m(500e3, 30), 30)
    rb, _, pb = bbpssw_rounds_to_target(0.8, 0.99)
    rd, _, pd = dejmps_rounds_to_target(bell_diagonal_weights(werner_state(0.8)), 0.99)
    sample_t = list(np.linspace(0.0, 2 * SYNODIC_PERIOD_DAYS, 41))
    data = {
        "status": status,
        "headline": {
            "one_way_min_min": one_way_delay_s(EARTH_MARS_MIN_M) / 60,
            "one_way_max_min": one_way_delay_s(EARTH_MARS_MAX_M) / 60,
            "round_trip_max_min": round_trip_delay_s(EARTH_MARS_MAX_M) / 60,
            "range_min_au": lo / AU_METERS, "range_max_au": hi / AU_METERS,
            "synodic_days": SYNODIC_PERIOD_DAYS,
            "bb84_threshold_pct": 100 * bb84_qber_threshold(),
            "micius_two_link_loss_db_30deg": micius30,
            "fiber_attenuation_length_km": attenuation_length_km(),
            "nbar_5ghz_300K": bose_einstein_occupation(2 * math.pi * 5e9, 300.0),
            "nbar_5ghz_15mK": bose_einstein_occupation(2 * math.pi * 5e9, 0.015),
            "chain_crossover_km_1s_memory": crossover_distance_km(3, 1.0),
            "chain_teleport_fidelity_at_crossover": (2 * memory_chain(crossover_distance_km(3, 1.0), 3, 1.0).fidelity_fraction + 1) / 3,
            "min_useful_memory_s_1000km": minimum_useful_memory_s(1000.0),
            "mars_pairs_per_day_closest": mars_budget(MarsLinkDesign(), t_close).pairs_per_day,
            "mars_pairs_per_day_farthest": mars_budget(MarsLinkDesign(), t_far).pairs_per_day,
            "mars_fidelity_farthest": mars_budget(MarsLinkDesign(), t_far).teleport_fidelity,
            "mars_relay_pairs_per_day_closest": mars_budget(MarsLinkDesign(architecture="relay_dual"), t_close).pairs_per_day,
            "mars_purity_farthest": mars_budget(MarsLinkDesign(), t_far).purity,
            "mars_key_bits_per_day_farthest": mars_budget(MarsLinkDesign(), t_far).key_bits_per_day,
            "mars_key_bits_per_day_closest": mars_budget(MarsLinkDesign(), t_close).key_bits_per_day,
            "key_bank_mb_1e6": _ledger.capacity_bits / 8e6, "key_bank_refused_days_no_bank": _ledger.refused_days_without_bank,
            "mars_ground_purity_daylight_closest": mars_budget(MarsLinkDesign(architecture="earth_source"), t_close).extra["purity_daylight"],
            "mars_ground_days_without_dark_sky": sum(1 for t in range(780) if mars_budget(MarsLinkDesign(architecture="earth_source"), float(t)).pairs_per_day == 0),
            "min_useful_memory_segments_1000km": best_useful_chain(1000.0, 1.001 * minimum_useful_memory_s(1000.0)).n_segments,
            "min_useful_memory_rounds_1000km": sum(best_useful_chain(1000.0, 1.001 * minimum_useful_memory_s(1000.0)).rounds),
            "bbpssw_rounds_08_to_099": rb, "bbpssw_pairs": pb,
            "dejmps_rounds_08_to_099": rd, "dejmps_pairs": pd,
            "di_rounds_095": rounds_for_positive_di_key(0.95 * 2 * math.sqrt(2), 0.01),
            "mars_clock_redshift": gravitational_redshift_earth_mars(0.0),
            "mars_capable_memories": sum(1 for p in MEMORY_TABLE if cm[p.name]["Mars max"]),
            "n_memories": len(MEMORY_TABLE),
            "messenger_buffer_kB_mars_max": required_buffer_bytes(0.0, EARTH_MARS_MAX_M, 32, messages_per_s=1 / 60) / 1e3,
        },
        "memories": [{"name": p.name, "lifetime_s": p.lifetime_s, "efficiency": p.efficiency, "T_K": p.T_kelvin,
                      "crossover_s": crossover_time_s(0.95, p.lifetime_s, p.model), "survives": cm[p.name]} for p in MEMORY_TABLE],
        "baselines_round_trip_s": BASELINES,
        "elements": {name: {"a_au": el.a_au, "e": el.e, "L_deg": el.L_deg, "varpi_deg": el.varpi_deg, "period_days": el.period_days}
                     for name, el in (("earth", EARTH), ("mars", MARS))},
        "au_m": AU_METERS,
        "ephemeris_check": {"t_days": sample_t, "range_m": [float(earth_mars_range_m(t)) for t in sample_t]},
    }
    cp = coupler_data()
    data["coupler"] = cp
    data["qec"] = qec_data()
    data["systems"] = systems_data()
    data["headline"].update({"zz_idle_ghz": cp["idle_ghz"], "cz_duration_ns": cp["cz"]["angle"]["duration_ns"],
                             "cz_fidelity": cp["cz"]["angle"]["fidelity"], "cz_leakage": cp["cz"]["angle"]["leakage"],
                             "cz_leakage_frequency_shaped": cp["cz"]["frequency"]["leakage"]})
    return data


def main() -> None:
    data = json.loads(json.dumps(compute_data(), default=float))
    (ROOT / "docs" / "site_data.json").write_text(json.dumps(data, indent=1) + "\n")
    print("wrote docs/site_data.json")
    write_readme_numbers(data)


def write_readme_numbers(data: dict) -> None:
    """Regenerate the table between the numbers markers in README.md from the same data."""
    from qll.systems.mars_budget import MarsLinkDesign
    h = data["headline"]
    rows = [
        ("One-way light time, Earth → Mars", f"{h['one_way_min_min']:.1f}–{h['one_way_max_min']:.1f} min", "`qll/space/ephemeris.py`"),
        ("Round trip a memory must survive (Mars max)", f"{h['round_trip_max_min']:.1f} min", "`qll/channels/light_time_delay.py`"),
        ("Demonstrated memories that survive it (f₀ = 0.95)", f"{h["mars_capable_memories"]} of {h["n_memories"]}: hour-class ions (99 % retrieval) and rare-earth crystals (< 5 %)", "`qll/network/memory_decoherence.py`"),
        ("Micius two-downlink loss at 30° elevation", f"{h['micius_two_link_loss_db_30deg']:.1f} dB (reported 64–82 dB)", "`qll/channels/link_budget.py`"),
        ("Thermal photons a 5 GHz qubit sees", f"{h['nbar_5ghz_300K']:.0f} at 300 K, {h['nbar_5ghz_15mK']:.1e} at 15 mK", "`qll/circuits/noise/thermal.py`"),
        ("BB84 error threshold", f"{h['bb84_threshold_pct']:.2f} %", "`qll/qkd/key_rate.py`"),
        ("Where a repeater chain (1 s memories) beats direct fiber", f"{h['chain_crossover_km_1s_memory']:.0f} km", "`qll/network/repeater_chain.py`"),
        ("Teleportation fidelity of the pairs it delivers there, without purification", (lambda x: f"{x:.2f} (below 2/3: rate is not enough)" if x < 2 / 3 else f"{x:.2f} (above 2/3)")(h['chain_teleport_fidelity_at_crossover']), "`qll/network/repeater_chain.py`"),
        ("Memory needed for a useful chain (F > 2/3) that beats direct fiber over 1000 km", f"{h['min_useful_memory_s_1000km']:.0f} s (best: {h['min_useful_memory_segments_1000km']} segments, {h['min_useful_memory_rounds_1000km']} purification round{'s' if h['min_useful_memory_rounds_1000km'] != 1 else ''})", "`qll/network/purified_chain.py`"),
        (f"Useful Earth–Mars pairs per day, source in space at {MarsLinkDesign().tx_offset_m / 1e3:,.0f} km from Earth (beam waist {MarsLinkDesign().tx_waist_m:g} m, {MarsLinkDesign().rx_diameter_mars_m:g} m receiver, {MarsLinkDesign().modes:,} modes)", f"{h['mars_pairs_per_day_closest']:.1e} at closest, {h['mars_pairs_per_day_farthest']:.1e} at farthest (F = {h['mars_fidelity_farthest']:.2f}); {h['mars_relay_pairs_per_day_closest']:.0e} through an L4 relay's two downlinks", "`qll/systems/mars_budget.py`"),
        ("Secret key, measured on arrival (no memory), and the bank that spends it evenly", f"{h['mars_key_bits_per_day_closest']:.1e} bits/day at closest, {h['mars_key_bits_per_day_farthest']:.1e} at farthest, none for 3 weeks at conjunction; a {h['key_bank_mb_1e6']:.1f} MB bank carries 10⁶ bits/day through every day (refused on {h['key_bank_refused_days_no_bank']} of 780 days without one)", "`qll/app/key_bank.py`"),
        ("Sunlit Earth behind a ground transmitter, seen from Mars (100 MHz per mode)", f"{100 * (1 - h['mars_ground_purity_daylight_closest']):.1f} % of daytime heralds are noise; no dark-sky view of Mars on {h['mars_ground_days_without_dark_sky']} of 780 days; from space, {100 * h['mars_purity_farthest']:.0f} % of heralds are signal even at full-phase Earth", "`qll/channels/planetshine.py`"),
        ("Purification 0.80 → 0.99", f"BBPSSW {h['bbpssw_rounds_08_to_099']} rounds / {h['bbpssw_pairs']:.0f} pairs; DEJMPS {h['dejmps_rounds_08_to_099']} / {h['dejmps_pairs']:.0f}", "`qll/network/purification.py`"),
        ("Rounds for a device-independent key at S = 0.95·2√2", f"{h['di_rounds_095']:,}", "`qll/qkd/e91.py`"),
        ("Key buffer to message once a minute through a Mars round trip", f"{h['messenger_buffer_kB_mars_max']:.2f} kB", "`qll/app/messenger.py`"),
    ]
    table = "| Question | Answer from the code | Module |\n|---|---|---|\n" + "\n".join(f"| {a} | **{b}** | {c} |" for a, b, c in rows)
    readme = ROOT / "README.md"
    text = readme.read_text(encoding="utf-8")
    start, end = "<!-- numbers:start -->", "<!-- numbers:end -->"
    if start in text and end in text:
        pre, rest = text.split(start, 1)
        _, post = rest.split(end, 1)
        readme.write_text(pre + start + "\n" + table + "\n" + end + post, encoding="utf-8")


if __name__ == "__main__":
    main()
