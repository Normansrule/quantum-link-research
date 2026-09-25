"""Entanglement measures, Mermin inequality, channel catalogue (all CPTP), randomized benchmarking decay."""
import math

import numpy as np
import pytest

from qll.circuits.bell import bell_state, werner_state
from qll.circuits.entanglement_measures import is_entangled_ppt, negativity, partial_transpose, witness_value
from qll.circuits.ghz import ghz_state
from qll.circuits.mermin import LOCAL_BOUND_3, QUANTUM_MAX_3, mermin_sampled_stim, mermin_value
from qll.circuits.noise.catalogue import CATALOGUE, coherent_rotation_error, pauli_twirl
from qll.circuits.noise._kraus_base import average_gate_fidelity

pytestmark = pytest.mark.phase2


def test_negativity_ppt_and_witness_agree_with_werner_threshold():
    for f in (0.3, 0.5, 0.6, 0.8, 1.0):
        w = werner_state(f)
        assert negativity(w) == pytest.approx(max(0.0, f - 0.5), abs=1e-9)
        assert is_entangled_ppt(w) == (f > 0.5 + 1e-9)
        assert (witness_value(w) < 0) == (f > 0.5 + 1e-9)
    b = bell_state("phi+"); rho = np.outer(b, b.conj())
    assert negativity(rho) == pytest.approx(0.5)
    assert np.allclose(partial_transpose(partial_transpose(rho)), rho)


def test_mermin_ghz_violates_local_bound():
    m = mermin_value(ghz_state(3))
    assert abs(m) == pytest.approx(QUANTUM_MAX_3, abs=1e-9) and abs(m) > LOCAL_BOUND_3
    pytest.importorskip("stim")
    assert abs(mermin_sampled_stim(5000)) == pytest.approx(4.0, abs=0.05)
    sep = np.zeros(8, dtype=complex); sep[0] = 1.0                                  # |000>: no violation
    assert abs(mermin_value(sep)) <= LOCAL_BOUND_3 + 1e-9


def test_channel_catalogue_all_cptp_and_coherent_error_fidelity():
    for name, make in CATALOGUE.items():
        ch = make()                                                                   # KrausChannel raises if not CPTP
        assert 0.0 <= average_gate_fidelity(ch) <= 1.0 + 1e-12, name
    th = 0.2
    assert average_gate_fidelity(coherent_rotation_error(th)) == pytest.approx(1 - (2 / 3) * math.sin(th / 2) ** 2)
    tw = pauli_twirl(coherent_rotation_error(th))
    assert average_gate_fidelity(tw) == pytest.approx(average_gate_fidelity(coherent_rotation_error(th)), abs=1e-9)   # twirl preserves F_avg


@pytest.mark.slow
def test_rb_recovers_error_per_clifford():
    pytest.importorskip("qiskit_aer")
    from qll.circuits.benchmarking import error_per_clifford, fit_decay, rb_survival
    L = [1, 5, 10, 20, 40, 80]
    s = rb_survival(L, 0.01, shots=1000, n_seq=6)
    p, A, B = fit_decay(L, s)
    assert 0.95 < p < 0.995 and 0.002 < error_per_clifford(p) < 0.02                  # ~2 gates per Clifford at 1 % each
    s0 = rb_survival([1, 40], 0.0, shots=500, n_seq=3)
    assert all(x > 0.99 for x in s0)                                                    # no noise, no decay
