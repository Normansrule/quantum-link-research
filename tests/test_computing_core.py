"""Stabilizer codes (Stim), QFT and phase estimation (Aer), H2, magic-state distillation, oscillator states (QuTiP)."""
import math

import numpy as np
import pytest

from qll.circuits.chemistry_h2 import EXPERIMENTAL_TOTAL_ENERGY_HA, ground_energy_hartree, pauli_terms_jordan_wigner, vqe_ansatz_energy
from qll.circuits.magic_states import distilled_error_15_to_1, rounds_and_inputs, t_count_budget
from qll.circuits.stabilizer_codes import CODES, corrects_all_single_errors, memory_experiment_logical_error, syndrome_table

pytestmark = pytest.mark.phase2


def test_stabilizer_codes_syndromes():
    pytest.importorskip("stim")
    assert corrects_all_single_errors("five") and corrects_all_single_errors("steane")
    assert corrects_all_single_errors("repetition3", "X") and not corrects_all_single_errors("repetition3", "XYZ")
    assert len(syndrome_table("five")) == 16                                            # 4 stabilizers: 2^4 syndromes, all used
    assert len(syndrome_table("steane")) == 22                                          # 1 + 21 distinct single errors (6 bits)
    p = 0.05
    rep = memory_experiment_logical_error("repetition3", p)
    assert abs(rep - 3 * p**2) < 0.004                                                  # ~3p^2 (two of three flipped)
    assert memory_experiment_logical_error("repetition3", 0.4) > memory_experiment_logical_error("repetition3", 0.1)


def test_qft_and_phase_estimation():
    pytest.importorskip("qiskit_aer")
    from qiskit.quantum_info import Operator
    from qll.circuits.algorithms import phase_estimation, qft_circuit, qft_matrix
    for n in (2, 3, 4):
        assert np.allclose(Operator(qft_circuit(n)).data, qft_matrix(n))
    assert phase_estimation(0.375, 4)[0] == pytest.approx(0.375)                        # exactly representable
    assert abs(phase_estimation(0.3, 5)[0] - 0.3) <= 2**-5                              # within one bit otherwise


def test_h2_energy_and_vqe_reaches_it():
    assert ground_energy_hartree() == pytest.approx(EXPERIMENTAL_TOTAL_ENERGY_HA, abs=2e-3)
    e_min = min(vqe_ansatz_energy(t) for t in np.linspace(-math.pi, math.pi, 4001))
    assert e_min == pytest.approx(ground_energy_hartree(include_nuclear=False), abs=1e-4)
    assert pauli_terms_jordan_wigner(4) < pauli_terms_jordan_wigner(20) < pauli_terms_jordan_wigner(100)


def test_magic_state_distillation_budget():
    assert distilled_error_15_to_1(1e-3) == pytest.approx(3.5e-8)
    r, inputs, p = rounds_and_inputs(1e-3, 1e-12)
    assert r == 2 and inputs == 225 and p < 1e-12
    b = t_count_budget(1e-3, 1e9)
    assert b["rounds"] == 2 and b["raw_states_total"] == pytest.approx(2.25e11)


def test_oscillator_states_against_closed_forms():
    pytest.importorskip("qutip")
    from qll.circuits.oscillator_states import coherent_stats, fock_g2, squeezed_vacuum_stats
    c = coherent_stats(2.0)
    assert c["n_mean"] == pytest.approx(4.0, abs=1e-6) and c["var_x"] == pytest.approx(0.25, abs=1e-6) and c["g2"] == pytest.approx(1.0, abs=1e-6)
    s = squeezed_vacuum_stats(0.5)
    assert s["var_x"] == pytest.approx(math.exp(-1) / 4, rel=1e-6) and s["var_p"] == pytest.approx(math.exp(1) / 4, rel=1e-6)
    assert s["n_mean"] == pytest.approx(math.sinh(0.5) ** 2, rel=1e-6)
    assert fock_g2(1) == 0.0 and fock_g2(2) == 0.5
