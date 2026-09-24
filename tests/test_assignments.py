"""Machine-checked answers for the problem sets. References are computed from qll; a None answer is skipped.
The reference-computation itself is tested (test_references_are_self_consistent), so the answer key can't rot."""
import importlib.util
import math
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.phase1


def _answers():
    spec = importlib.util.spec_from_file_location("answers", ROOT / "learn" / "assignments" / "answers.py")
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod


def references() -> dict:
    from qll.channels.fiber_loss import transmittance
    from qll.channels.free_space_diffraction import geometric_transmittance
    from qll.channels.light_time_delay import one_way_delay_s, round_trip_delay_s
    from qll.circuits.bell import werner_state
    from qll.circuits.chsh import chsh_werner_analytic
    from qll.circuits.noise.depolarizing import average_gate_fidelity_analytic
    from qll.circuits.noise.thermal import bose_einstein_occupation, thermal_t1
    from qll.circuits.teleportation import analytic_average_fidelity
    from qll.constants.astro import AU_METERS, EARTH_MARS_MAX_M
    from qll.network.memory_decoherence import crossover_time_s
    from qll.network.purification import bbpssw_rounds_to_target, bell_diagonal_weights, dejmps_rounds_to_target
    from qll.qkd.key_rate import bb84_rate_per_sifted_bit
    from qll.qkd.plob_bound import plob_bits_per_use
    th, ph = math.pi / 3, math.pi / 4
    w = 2 * math.pi * 6e9
    return {
        "ps1_bloch": (math.sin(th) * math.cos(ph), math.sin(th) * math.sin(ph), math.cos(th)),
        "ps1_nbar_cold": bose_einstein_occupation(w, 0.020), "ps1_nbar_hot": bose_einstein_occupation(w, 300.0),
        "ps1_t1_100mK": thermal_t1(100e-6, w, 0.100), "ps1_avg_fid_depol": average_gate_fidelity_analytic(0.1),
        "ps2_chsh_085": chsh_werner_analytic(0.85), "ps2_f_chsh_threshold": (1 + 3 / math.sqrt(2)) / 4,
        "ps2_f_teleport_threshold": 0.5, "ps2_tele_fid_085": analytic_average_fidelity(0.85),
        "ps2_delay_min": one_way_delay_s(1.2 * AU_METERS) / 60, "ps2_bits": 2,
        "ps3_eta_fiber_150": transmittance(150), "ps3_eta_leo": geometric_transmittance(1e6, 810e-9, 0.15, 1.0),
        "ps3_bb84_frac_004": bb84_rate_per_sifted_bit(0.04), "ps3_plob_150": plob_bits_per_use(transmittance(150)),
        "ps3_crossover_s": crossover_time_s(0.95, 3600.0), "ps3_beats_mars_max": crossover_time_s(0.95, 3600.0) > round_trip_delay_s(EARTH_MARS_MAX_M),
        "ps3_bbpssw_rounds": bbpssw_rounds_to_target(0.8, 0.99)[0],
        "ps3_dejmps_rounds": dejmps_rounds_to_target(bell_diagonal_weights(werner_state(0.8)), 0.99)[0],
    }


def test_references_are_self_consistent():
    r = references()
    assert r["ps2_f_chsh_threshold"] == pytest.approx((1 + 3 / math.sqrt(2)) / 4)   # S = 2 at f = (1+3/√2)/4 ≈ 0.78
    from qll.circuits.chsh import chsh_werner_analytic
    assert chsh_werner_analytic(r["ps2_f_chsh_threshold"]) == pytest.approx(2.0)
    assert r["ps3_beats_mars_max"] is True and r["ps3_dejmps_rounds"] < r["ps3_bbpssw_rounds"]


@pytest.mark.parametrize("key", sorted(references()))
def test_student_answer(key):
    a = getattr(_answers(), key, None)
    if a is None:
        pytest.skip(f"{key} not answered")
    ref = references()[key]
    if isinstance(ref, tuple):
        assert all(abs(x - y) < 1e-3 for x, y in zip(a, ref)), f"{key}: {a} vs {ref}"
    elif isinstance(ref, bool):
        assert a is ref
    elif isinstance(ref, int):
        assert a == ref
    else:
        assert a == pytest.approx(ref, rel=0.02), f"{key}: {a} vs {ref}"
