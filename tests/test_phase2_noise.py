"""Kraus channels: CPTP on construction, analytic fidelities, and QuTiP Lindblad cross-checks."""
import math

import numpy as np
import pytest

from qll.circuits.noise._kraus_base import KrausChannel, average_gate_fidelity
from qll.circuits.noise.amplitude_damping import amplitude_damping, gamma_from_time
from qll.circuits.noise.amplitude_damping import lindblad_solution as ad_lindblad
from qll.circuits.noise.depolarizing import average_gate_fidelity_analytic, depolarizing
from qll.circuits.noise.phase_damping import lambda_from_time, phase_damping, t2_from_t1_tphi
from qll.circuits.noise.phase_damping import lindblad_solution as pd_lindblad
from qll.circuits.noise.thermal import bath_ground_weight, generalized_amplitude_damping_kraus

pytestmark = pytest.mark.phase2
RHO_PLUS = np.array([[0.5, 0.5], [0.5, 0.5]], dtype=complex)


def test_non_cptp_rejected():                                            # INV-4
    with pytest.raises(ValueError):
        KrausChannel((np.eye(2) * 0.9,), "bad")


@pytest.mark.parametrize("p", [0.0, 0.1, 0.5, 1.0])
def test_depolarizing_fidelity_and_full_mixing(p):
    ch = depolarizing(p)
    assert average_gate_fidelity(ch) == pytest.approx(average_gate_fidelity_analytic(p), abs=1e-12)
    if p == 1.0:
        assert np.allclose(ch.apply(RHO_PLUS), np.eye(2) / 2)


def test_amplitude_damping_matches_lindblad_and_relaxes_to_ground():
    t, T1 = 2.0, 3.0
    kraus = amplitude_damping(gamma_from_time(t, T1)).apply(RHO_PLUS)
    assert np.allclose(kraus, ad_lindblad(RHO_PLUS, t, T1), atol=1e-5)
    assert np.allclose(amplitude_damping(1.0).apply(RHO_PLUS), np.diag([1, 0]))


def test_phase_damping_matches_lindblad_and_t2_bound():
    t, Tphi = 1.5, 2.0
    kraus = phase_damping(lambda_from_time(t, Tphi)).apply(RHO_PLUS)
    assert np.allclose(kraus, pd_lindblad(RHO_PLUS, t, Tphi), atol=1e-5)
    assert kraus[0, 1].real == pytest.approx(0.5 * math.exp(-t / Tphi), abs=1e-5)
    assert t2_from_t1_tphi(50e-6, 1e9) <= 2 * 50e-6 + 1e-12


def test_thermal_gad_is_a_valid_kraus_channel_and_reduces_to_ad_at_zero_T():
    ops = generalized_amplitude_damping_kraus(0.3, bath_ground_weight(2 * math.pi * 5e9, 0.0))
    ch = KrausChannel(tuple(ops), "gad")
    assert np.allclose(ch.apply(RHO_PLUS), amplitude_damping(0.3).apply(RHO_PLUS))


def test_aer_adapter_builds():
    pytest.importorskip("qiskit_aer")
    err = depolarizing(0.1).to_aer()
    assert err.size == 1


def test_qutip_superop_adapter_is_trace_preserving():
    qt = pytest.importorskip("qutip")
    S = phase_damping(0.3).to_qutip_superop()
    assert S.istp
