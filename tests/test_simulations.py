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
