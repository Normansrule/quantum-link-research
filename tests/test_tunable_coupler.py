"""Static ZZ: the second-order formula converges to exact diagonalisation; a tunable coupler has a ZZ-free idle point."""
import numpy as np
import pytest

from qll.hardware.tunable_coupler import CoupledPair, static_zz_exact, static_zz_perturbative

pytestmark = pytest.mark.phase3


def test_perturbative_zz_matches_exact_and_converges():
    w1, w2, a = 5.0, 5.2, -0.3
    for J, tol in ((0.001, 0.005), (0.003, 0.01)):
        exact, pert = static_zz_exact(w1, w2, a, a, J), static_zz_perturbative(w1, w2, a, a, J)
        assert exact > 0 and pert == pytest.approx(exact, rel=tol)          # same sign: the formula's sign is right
    assert static_zz_exact(w1, w2, a, a, 0.002) == pytest.approx(4 * static_zz_exact(w1, w2, a, a, 0.001), rel=0.01)  # ~J^2
    assert static_zz_exact(w1, w2, a, a, 0.0) == pytest.approx(0.0, abs=1e-12)
    with pytest.raises(TypeError):
        static_zz_exact(w1, w2, a, a, 0.001 + 0j)


def test_tunable_coupler_idle_point():
    pair = CoupledPair()
    idle = pair.zz_free_frequency(5.0, 5.5)
    assert 5.0 < idle < 5.5 and abs(pair.zz(idle)) < 1e-9                   # < 1 Hz at the idle point
    assert abs(pair.zz(4.6)) > 1e-3                                         # > 1 MHz with the coupler close to the qubits
    zz = np.array([pair.zz(w) for w in (5.0, idle, 6.0)])
    assert zz[0] > 0 and zz[2] > 0                                          # ZZ returns on both sides of the idle point
    g = [pair.effective_coupling(w) for w in (4.6, 6.0, 20.0, 100.0)]
    assert g[0] < 0 < g[1] < g[2] < g[3]                                    # virtual exchange dominates near the qubits
    assert g[3] == pytest.approx(pair.g12, rel=0.02)                        # a far-detuned coupler leaves the direct term
