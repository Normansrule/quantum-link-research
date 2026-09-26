"""Write docs/site_data.json: every number the website shows, computed by the tested qll functions.
Run after any physics change (CI and pre-commit do). The site never hard-codes a physics number."""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


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
    from qll.network.repeater_chain import crossover_distance_km
    from qll.qkd.e91 import rounds_for_positive_di_key
    from qll.qkd.key_rate import bb84_qber_threshold
    from qll.space.ephemeris import EARTH, MARS, SYNODIC_PERIOD_DAYS, earth_mars_range_m, range_envelope_m
    from qll.space.relativity import gravitational_redshift_earth_mars

    status = json.loads((ROOT / "docs" / "status.json").read_text()) if (ROOT / "docs" / "status.json").exists() else {}
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
    return data


def main() -> None:
    data = json.loads(json.dumps(compute_data(), default=float))
    (ROOT / "docs" / "site_data.json").write_text(json.dumps(data, indent=1) + "\n")
    print("wrote docs/site_data.json")
    write_readme_numbers(data)


def write_readme_numbers(data: dict) -> None:
    """Regenerate the table between the numbers markers in README.md from the same data."""
    h = data["headline"]
    rows = [
        ("One-way light time, Earth → Mars", f"{h['one_way_min_min']:.1f}–{h['one_way_max_min']:.1f} min", "`qll/space/ephemeris.py`"),
        ("Round trip a memory must survive (Mars max)", f"{h['round_trip_max_min']:.1f} min", "`qll/channels/light_time_delay.py`"),
        ("Demonstrated memories that survive it (f₀ = 0.95)", f"{h["mars_capable_memories"]} of {h["n_memories"]}: hour-class ions (99 % retrieval) and rare-earth crystals (< 5 %)", "`qll/network/memory_decoherence.py`"),
        ("Micius two-downlink loss at 30° elevation", f"{h['micius_two_link_loss_db_30deg']:.1f} dB (reported 64–82 dB)", "`qll/channels/link_budget.py`"),
        ("Thermal photons a 5 GHz qubit sees", f"{h['nbar_5ghz_300K']:.0f} at 300 K, {h['nbar_5ghz_15mK']:.1e} at 15 mK", "`qll/circuits/noise/thermal.py`"),
        ("BB84 error threshold", f"{h['bb84_threshold_pct']:.2f} %", "`qll/qkd/key_rate.py`"),
        ("Where a repeater chain (1 s memories) beats direct fiber", f"{h['chain_crossover_km_1s_memory']:.0f} km", "`qll/network/repeater_chain.py`"),
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
