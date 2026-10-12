"""The frontier: teleportation with a delayed classical channel on a cloud processor matches its closed form in Aer,
banked pairs across a distance follow the memory model and the light time, and a swapping node multiplies Werner
parameters, learns nothing, and pays off only past a crossover distance."""
import math

import pytest

from qll.channels.light_time_delay import one_way_delay_s
from qll.circuits import teleport_cloud as T
from qll.circuits import teleport_delay_cloud as D
from qll.circuits.entanglement_swapping import swapped_fraction_analytic
from qll.circuits.qubit_channel import average_fidelity, ptm_from_affine
from qll.network import teleport_across as X
from qll.network.memory_decoherence import fraction_after_storage_analytic

pytestmark = pytest.mark.phase4


def test_delay_fidelity_is_the_idle_channels_average_fidelity():
    import numpy as np
    for t, T1, T2 in [(0, 200, 150), (50, 200, 150), (120, 100, 180), (400, 300, 60)]:
        e2, e1 = D.bloch_shrink(t, T1, T2)
        R = ptm_from_affine(np.diag([e2, e2, e1]), np.array([0, 0, 1 - e1]))
        assert D.average_fidelity(t, T1, T2) == pytest.approx(average_fidelity(R), abs=1e-12)
    assert D.average_fidelity(500, mode="no_bits") == 0.5
    assert D.average_fidelity(0, p2=0.03) == pytest.approx(T.expected_feedforward_fidelity(0.03), abs=1e-12)


def test_crossover_delay_solves_two_thirds():
    t = D.crossover_delay_us(200, 150, 0.01)
    assert D.average_fidelity(t, 200, 150, 0.01) == pytest.approx(2 / 3, abs=1e-9)
    assert 100 < D.crossover_delay_us() < 300                                  # a transmon holds the bits for about 180 µs
    assert D.crossover_delay_us(200, 150, p2=0.5) == 0.0


def test_delayed_teleportation_in_aer_matches_the_closed_form():
    from qll.circuits import cloud_run as R
    for mode in ("feedforward", "deferred", "no_bits"):
        for t in (0.0, 150.0):
            counts = R.run_aer(D.circuits(t, mode), 40000, 7, None, "density_matrix")
            assert T.analyze(counts, mode).average == pytest.approx(D.average_fidelity(t, mode=mode), abs=0.008), (mode, t)


def test_hardware_mode_uses_a_real_delay_instruction():
    qc = D.circuit("+", 80.0, delay="hardware")
    ops = [i.operation for i in qc.data if i.operation.name == "delay"]
    assert len(ops) == 1 and ops[0].duration == 80.0 and ops[0].unit == "us"
    assert D.sweep_delays_us(150, 6) == [0.0, 60.0, 120.0, 180.0, 240.0, 300.0]


def test_banked_link_is_the_memory_model_on_both_halves():
    p = X.Link(distance_m=3.0e8, index=1.0, f0=0.93, T_mem_s=20.0, bank_s=2.0)
    r = X.link(p)
    tc = one_way_delay_s(3.0e8)
    assert r["light_time_s"] == pytest.approx(tc)
    f = fraction_after_storage_analytic(fraction_after_storage_analytic(0.93, 2.0, 20.0), 2.0 + tc, 20.0)
    assert r["fraction"] == pytest.approx(f, rel=1e-12)
    assert r["fidelity_with_bits"] == pytest.approx((2 * f + 1) / 3) and r["fidelity_without_bits"] == 0.5
    edge = X.link(X.Link(distance_m=3.0e8, index=1.0, f0=0.93, T_mem_s=20.0, bank_s=r["max_bank_s"]))
    assert edge["fidelity_with_bits"] == pytest.approx(2 / 3, abs=1e-12)
    assert X.link(X.Link(distance_m=3.0e8, index=1.0, f0=0.93, T_mem_s=r["min_memory_s"]))["fidelity_with_bits"] == pytest.approx(2 / 3, abs=1e-12)


def test_which_memories_survive_which_distances():
    tab = X.memory_table()
    assert tab["Rb/Cs atomic ensemble (DLCZ)"]["two rooms"] and not tab["Rb/Cs atomic ensemble (DLCZ)"]["the Moon"]
    assert tab["SiV nuclear spin in cavity"]["low Earth orbit, 1,000 km"] and not tab["SiV nuclear spin in cavity"]["the Moon"]   # 1 s < 1.3 s / ln 2.8
    assert tab["NV 13C register"]["the Moon"] and not tab["NV 13C register"]["Mars at its closest"]
    assert tab["171Yb+ hyperfine"]["Mars at its farthest"]                              # an hour outlasts 22 minutes
    mars = X.for_scenario("Mars at its farthest", "171Yb+ hyperfine")
    assert 1200 < mars["light_time_s"] < 1400 and mars["fidelity_with_bits"] > 2 / 3
    assert mars["success_per_use"] == pytest.approx(0.99 ** 2 * 0.5)


def test_swapping_multiplies_werner_parameters_and_learns_nothing():
    assert X.swapped_fraction(0.9, 0.9) == pytest.approx(swapped_fraction_analytic(0.9), rel=1e-12)
    assert X.werner(X.swapped_fraction(0.9, 0.8)) == pytest.approx(X.werner(0.9) * X.werner(0.8), rel=1e-12)
    s = X.swap(X.Swap(distance_m=20.0, T_mem_s=1e9))
    assert s["pair_fraction"] == pytest.approx(swapped_fraction_analytic(0.95), rel=1e-6)
    assert s["node_learns_key"] is False and s["trusted_relay_learns_key"] is True
    assert s["total_s"] == pytest.approx(one_way_delay_s(1.47 * 10.0) + one_way_delay_s(1.47 * 20.0))


def test_the_node_pays_off_only_past_a_crossover():
    near, far = X.swap(X.Swap(distance_m=20e3)), X.swap(X.Swap(distance_m=200e3))
    assert near["attempts_swapped"] > near["attempts_direct"]                      # a lossy Bell measurement costs more than 20 km of fiber
    assert far["attempts_swapped"] < far["attempts_direct"] / 30                   # at 200 km, waiting for each other wins thirtyfold
    assert math.isclose(far["eta_segment"] ** 2, far["eta_direct"], rel_tol=1e-12)


def test_zero_delay_offset_is_the_gate_error_shrink():
    for t in (0, 75, 210):
        assert D.with_offset(t, 180, 120, (1 - 0.02) ** 2) == pytest.approx(D.average_fidelity(t, 180, 120, 0.02), abs=1e-14)


def test_fake_device_rehearsal_follows_the_calibrated_decay():
    import json
    from pathlib import Path
    files = sorted((Path(__file__).resolve().parents[1] / "experiments/bench/frontier/rehearsal").glob("delay_fake_*.json"))
    assert files, "run: python experiments/bench/frontier/run_frontier.py delay --backend fake_torino --layout 0 1 2 --delays 0 60 120 180"
    rec = json.loads(files[-1].read_text(encoding="utf-8"))
    for r in rec["runs"].values():
        v = r["verdict"]
        assert v["ci_low"] - 0.01 <= D.with_offset(r["delay_us"], rec["T1_us"], rec["T2_us"], rec["zero_delay_shrink_k"]) <= v["ci_high"] + 0.01, r["delay_us"]
    assert abs(rec["no_bits"]["verdict"]["average_fidelity"] - 0.5) < 0.02
