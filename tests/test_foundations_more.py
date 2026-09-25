"""Decompositions, one-bit teleportation, filter functions, quantum walks, Landauer."""
import math

import numpy as np
import pytest
from scipy.stats import unitary_group

from qll.circuits.decompositions import cnot_count, one_bit_teleportation, one_bit_teleportation_expected, zyz_angles, zyz_reconstruct
from qll.circuits.noise.filter_functions import coherence_decay_exponent, cpmg_times, filter_function, peak_frequency
from qll.circuits.quantum_walk import classical_walk_distribution, hadamard_walk_distribution, std
from qll.circuits.thermodynamics import landauer_energy_j, reset_power_bound_w

pytestmark = pytest.mark.phase2


def test_zyz_and_cnot_counts():
    pytest.importorskip("qiskit")
    for seed in range(3):
        U = unitary_group.rvs(2, random_state=seed)
        assert np.allclose(zyz_reconstruct(*zyz_angles(U)), U)
    cx = np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]])
    swap = np.array([[1, 0, 0, 0], [0, 0, 1, 0], [0, 1, 0, 0], [0, 0, 0, 1]])
    assert cnot_count(np.eye(4)) == 0 and cnot_count(cx) == 1 and cnot_count(swap) == 3
    assert cnot_count(unitary_group.rvs(4, random_state=7)) == 3                      # generic unitary needs three


def test_one_bit_teleportation_matches_x_h_rz():
    psi = np.array([0.6, 0.8j])
    for phi in (0.0, 0.7, math.pi / 2):
        for m in (0, 1):
            assert abs(np.vdot(one_bit_teleportation(psi, phi, m), one_bit_teleportation_expected(psi, phi, m))) == pytest.approx(1.0, abs=1e-12)


def test_filter_functions_and_cpmg_extends_coherence():
    w = np.linspace(0.01, 50, 3000); T = 1.0
    assert np.allclose(filter_function(w, T, []), 4 * np.sin(w * T / 2) ** 2)
    assert np.allclose(filter_function(w, T, [T / 2]), 16 * np.sin(w * T / 4) ** 4)
    assert filter_function(np.array([1e-6]), T, [T / 2])[0] < 1e-12                        # echo blocks DC
    S = lambda om: 1.0 / om                                                               # 1/f noise
    chi = [coherence_decay_exponent(S, T, cpmg_times(n, T) if n else []) for n in (0, 1, 4, 16)]
    assert chi[0] > chi[1] > chi[2] > chi[3]                                               # more pulses, more coherence
    assert peak_frequency(T, 8) == pytest.approx(8 * math.pi)


def test_quantum_walk_is_ballistic():
    for t in (10, 40, 160):
        assert hadamard_walk_distribution(t).sum() == pytest.approx(1.0)
    q40, q160 = std(hadamard_walk_distribution(40)), std(hadamard_walk_distribution(160))
    c40, c160 = std(classical_walk_distribution(40)), std(classical_walk_distribution(160))
    assert q160 / q40 == pytest.approx(4.0, rel=0.05) and c160 / c40 == pytest.approx(2.0, rel=0.05)   # t vs sqrt(t)
    assert std(hadamard_walk_distribution(100)) / 100 == pytest.approx(0.54, abs=0.02)             # ~0.54 t for the Hadamard walk


def test_landauer():
    assert landauer_energy_j(300) == pytest.approx(2.87e-21, rel=1e-3)
    assert reset_power_bound_w(1000, 1e6, 0.01) < 1e-12                                     # far below the mK stage's microwatts
