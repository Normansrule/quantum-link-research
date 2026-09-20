"""Each simulation must run and reproduce one analytic limit."""
import math
import sys
from pathlib import Path

import pytest

SIM = Path(__file__).resolve().parents[1] / "simulations"
sys.path.insert(0, str(SIM))
pytestmark = pytest.mark.phase1


def test_s01_ideal_chsh_is_two_root_two():
    pytest.importorskip("qiskit_aer")
    from s01_chsh_with_noise import chsh_aer
    assert abs(chsh_aer(0.0, shots=40000) - 2 * math.sqrt(2)) < 0.03


def test_s02_zero_delay_gives_unit_fidelity_and_guard_holds():
    pytest.importorskip("qiskit_aer")
    from s02_teleportation_with_light_time import teleport_fidelity_aer
    assert teleport_fidelity_aer(0.0, 1.0) > 0.99
    assert teleport_fidelity_aer(10.0, 1.0) < 0.75   # ten T2's of storage → near 2/3 · (classical) floor


def test_s03_fiber_and_free_space_limits():
    from s03_link_budget_sweep import fiber_rate, free_space_rate, R_SRC, ETA_OPT, ETA_DET
    assert math.isclose(fiber_rate(100), R_SRC * 0.01 * ETA_OPT * ETA_DET, rel_tol=1e-9)
    assert free_space_rate(2e6, 0.15, 1.0) / free_space_rate(4e6, 0.15, 1.0) == pytest.approx(4.0, rel=0.03)


def test_s04_repetition_code_below_threshold():
    pytest.importorskip("stim")
    from s04_repetition_code_stim import logical_error_rate
    assert logical_error_rate(3, 0.05) < logical_error_rate(1, 0.05)
    assert abs(logical_error_rate(3, 0.1, shots=100000) - (3 * 0.1**2 * 0.9 + 0.1**3)) < 0.004


def test_s05_no_background_matches_bb84_formula():
    from s05_bb84_key_over_a_pass import key_bits_per_pass
    from qll.qkd.key_rate import bb84_rate_per_sifted_bit
    assert math.isclose(key_bits_per_pass(1e4, 0.0), 0.5 * 1e4 * 300 * bb84_rate_per_sifted_bit(0.01), rel_tol=1e-9)


def test_s06_finite_key_di_limits_and_sealing():
    pytest.importorskip("stim")
    from s06_di_certification_under_latency import certify_after_light_time
    from qll.qkd.e91 import di_rate_finite_key, di_rate_per_round, rounds_for_positive_di_key
    S = 2 * math.sqrt(2)
    assert abs(di_rate_finite_key(S, 0.0, 10**9) - di_rate_per_round(S, 0.0)) < 1e-2     # asymptotic limit (slow: infinite slope of the bound at 2√2)
    assert di_rate_finite_key(S, 0.0, 10) == 0.0                                        # too few rounds
    n = rounds_for_positive_di_key(0.95 * S, 0.01)
    assert 1000 < n < 5000 and di_rate_finite_key(0.95 * S, 0.01, n) > 0 >= di_rate_finite_key(0.95 * S, 0.01, n - 1)
    assert rounds_for_positive_di_key(2.0, 0.0) is None                                 # no violation, no key
    Sm, err, r = certify_after_light_time(5000, 1e8, seed=3)
    assert abs(Sm - S) < 4 * err + 0.05 and r > 0


def test_s07_transduction_bounds_and_architectures():
    from s07_transduction_free_vs_through import architecture_a, architecture_b
    from qll.hardware.nv_node import NvNode
    from qll.hardware.transduction import STATE_OF_THE_ART_2020, TARGET, Transducer, matched_cooperativity_efficiency
    t = Transducer(0.2, 0.05)
    assert t.signal_fraction() == pytest.approx(0.8) and t.preserves_entanglement()
    assert not Transducer(0.1, 0.1).preserves_entanglement()                            # n_add = eta_t is the edge
    assert matched_cooperativity_efficiency(1e4, 1e4) == pytest.approx(1.0, abs=1e-3)
    assert matched_cooperativity_efficiency(1, 1) == pytest.approx(4 / 9)
    r20, F20 = architecture_a(STATE_OF_THE_ART_2020)
    assert F20 <= 2 / 3 + 1e-9                                                            # 2020-class device: no useful entanglement
    rT, FT = architecture_a(TARGET)
    assert FT > 0.9 and rT > architecture_b(NvNode())[0]                                  # a target-class transducer wins on rate
    rb, Fb = architecture_b(NvNode())
    assert Fb == pytest.approx(architecture_b(NvNode(purcell_factor=30))[1])             # B's fidelity does not depend on ZPL
    assert architecture_b(NvNode(purcell_factor=30))[0] > 10 * rb                         # but its rate does
