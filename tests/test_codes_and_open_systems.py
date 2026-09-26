"""Decoders, quantum volume, Bloch–Redfield relaxation, hypergraph-product codes, Clifford group sizes."""
import math

import numpy as np
import pytest

from qll.circuits.bloch_redfield import equilibrium_sz, nbar, t1_bloch_redfield
from qll.circuits.groups import pauli_group_size_mod_phase, single_qubit_clifford_group, two_qubit_clifford_count
from qll.circuits.qldpc import (css_parameters, gf2_rank, hamming_checks, hypergraph_product, max_check_weight,
                                repetition_checks)

pytestmark = pytest.mark.phase2


def test_matching_decoder_shows_threshold_and_beats_no_decoding():
    pytest.importorskip("pymatching"); pytest.importorskip("stim")
    from qll.circuits.decoders import logical_error_rate
    low = [logical_error_rate(d, 0.02, shots=20000) for d in (3, 5, 7)]
    high = [logical_error_rate(d, 0.15, shots=20000) for d in (3, 5, 7)]
    assert low[0] > low[1] > low[2]                                    # below threshold: bigger is better
    assert high[0] < high[2]                                           # above threshold: bigger is worse
    assert logical_error_rate(5, 0.03, 20000) < logical_error_rate(5, 0.03, 20000, decoder="none") / 5


def test_bloch_redfield_reproduces_the_thermal_law():
    pytest.importorskip("qutip")
    w, g = 2 * math.pi * 5e9, 1e5
    for T in (0.02, 0.1, 0.3):
        assert t1_bloch_redfield(w, T, g) * g == pytest.approx(1 / (2 * nbar(w, T) + 1), rel=1e-3)
    assert equilibrium_sz(w, 1e-4) == pytest.approx(-1.0) and equilibrium_sz(w, 300) > -0.01


def test_hypergraph_products():
    for d in (3, 5, 7):
        HX, HZ = hypergraph_product(repetition_checks(d), repetition_checks(d))
        assert not ((HX @ HZ.T) % 2).any()
        assert css_parameters(HX, HZ) == (d * d + (d - 1) ** 2, 1)          # the (unrotated) surface code
        assert max_check_weight(HX, HZ) == 4
    HX, HZ = hypergraph_product(hamming_checks(), hamming_checks())
    assert not ((HX @ HZ.T) % 2).any() and css_parameters(HX, HZ) == (58, 16)
    assert gf2_rank(hamming_checks()) == 3


def test_clifford_group_sizes():
    assert len(single_qubit_clifford_group()) == 24
    assert pauli_group_size_mod_phase(2) == 16
    pytest.importorskip("stim")
    assert two_qubit_clifford_count() == 11520


@pytest.mark.slow
def test_quantum_volume_heavy_output():
    pytest.importorskip("qiskit_aer")
    from qll.circuits.quantum_volume import heavy_output_probability, ideal_limit
    assert heavy_output_probability(4, 0.0, 10, 500) > 2 / 3 + 0.05
    assert heavy_output_probability(4, 0.15, 10, 500) < 2 / 3
    assert ideal_limit() == pytest.approx((1 + math.log(2)) / 2)
