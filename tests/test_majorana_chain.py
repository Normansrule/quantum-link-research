"""Scaling Majorana parity teleportation to a chain: every hop's parities are local Pauli products wherever the hop
sits, the emulated chain matches (1 + s^N)/2 in Aer, the bits are needed at every length, and the error budget turns
a chain length into a readout requirement."""
import math

import numpy as np
import pytest

from qll.circuits import majorana_chain as MC
from qll.circuits import teleport_cloud as T
from qll.hardware.majorana_error_budget import teleport_fidelity

pytestmark = pytest.mark.phase4


@pytest.mark.parametrize("n_modes", [3, 5, 7])
def test_every_hop_measures_local_parities(n_modes):
    for k in range(n_modes - 1):
        P, Q = MC.hop_parities(k, n_modes)
        assert np.allclose(P, -MC.pauli_string({k: "X", k + 1: "X"}, n_modes))      # the Jordan-Wigner strings cancel
        assert np.allclose(Q, MC.pauli_string({k: "Y", k + 1: "Y"}, n_modes))
        assert np.allclose(P @ Q, Q @ P)                                             # one Bell measurement per hop


def test_chain_in_aer_matches_the_scaling_law():
    from qll.circuits import cloud_run as R
    for hops in (1, 2, 3):
        assert T.analyze(R.run_aer(MC.circuits(hops), 1000, 3), "two_bit").average == pytest.approx(1.0, abs=1e-12), hops
    for hops in (1, 2):
        noisy = T.analyze(R.run_aer(MC.circuits(hops), 6000, 5, T.noise_model_depolarizing(0.03), "density_matrix"), "two_bit").average
        assert noisy == pytest.approx(MC.expected_fidelity(hops, 0.03), abs=0.02), hops
    blind = T.analyze(R.run_aer(MC.circuits(3, "no_bits"), 6000, 7), "no_bits").average
    assert blind == pytest.approx(0.5, abs=0.02)                                     # no signalling at any length


def test_max_hops_and_the_crossover():
    s = 0.9
    n = MC.max_hops(s)
    assert MC.chain_fidelity(n, s) > 2 / 3 >= MC.chain_fidelity(n + 1, s)
    assert MC.max_hops(1 / 3) == 0 and MC.max_hops(1.0) == math.inf
    assert MC.max_hops((1 - 0.01) ** 2) == 54                                        # a 1 % two-qubit error: about fifty hops


def test_budget_turns_a_chain_length_into_a_readout_requirement():
    assert MC.hop_shrink(4, 5, 0.01, 3) == pytest.approx(2 * teleport_fidelity(4, 5, 0.01, 3) - 1)
    snrs = [MC.required_snr(n) for n in (1, 2, 4, 8, 16)]
    assert all(a < b for a, b in zip(snrs, snrs[1:]))                                 # longer chains need cleaner readout
    s1 = snrs[0]
    assert MC.chain_fidelity(1, MC.hop_shrink(s1 * 1.0001, 5, 0.001, 6)) > 2 / 3 > MC.chain_fidelity(1, MC.hop_shrink(s1 * 0.999, 5, 0.001, 6))
    assert math.isinf(MC.required_snr(4, poison_prob=0.2))                            # poisoning alone can forbid a chain


def test_offset_absorbs_preparation_and_readout():
    s, k = 0.95, 0.7
    n = MC.max_hops(s, k)
    assert k * s ** n > 1 / 3 >= k * s ** (n + 1)
    assert MC.max_hops(0.99, 0.3) == 0                                               # a readout this poor fails before the first hop
