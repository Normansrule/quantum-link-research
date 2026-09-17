import math
import numpy as np
import pytest

from qll.constants.physical import HBAR, K_BOLTZMANN
from qll.channels.thermal_background import blackbody_occupation
from qll.circuits.noise.thermal import (
    bose_einstein_occupation, excited_state_population, generalized_amplitude_damping_kraus, thermal_t1,
)

pytestmark = pytest.mark.phase1
W5GHZ = 2 * math.pi * 5e9
W193THZ = 2 * math.pi * 193.4e12


def test_zero_temperature_gives_zero_occupation():
    assert bose_einstein_occupation(W5GHZ, 0.0) == 0.0


def test_rayleigh_jeans_limit():
    T = 1e6
    assert math.isclose(bose_einstein_occupation(W5GHZ, T), K_BOLTZMANN * T / (HBAR * W5GHZ), rel_tol=1e-3)


def test_microwave_qubit_cold_and_warm():
    assert bose_einstein_occupation(W5GHZ, 0.015) < 1e-6
    assert bose_einstein_occupation(W5GHZ, 300.0) > 1000


def test_telecom_photon_at_room_temperature_is_essentially_vacuum():
    n = bose_einstein_occupation(W193THZ, 300.0)
    assert n < 1e-12 and math.isclose(n, 4e-14, rel_tol=0.5)


def test_excited_population_below_half():
    for T in (0.015, 1.0, 300.0, 1e6):
        assert excited_state_population(W5GHZ, T) < 0.5


def test_t1_reduces_to_zero_temperature_value():
    assert thermal_t1(50e-6, W5GHZ, 0.0) == 50e-6
    assert thermal_t1(50e-6, W5GHZ, 300.0) < 50e-6 / 1000


@pytest.mark.parametrize("gamma,p", [(0.0, 1.0), (0.3, 0.7), (1.0, 0.5)])
def test_gad_kraus_trace_preserving(gamma, p):
    ops = generalized_amplitude_damping_kraus(gamma, p)
    total = sum(e.conj().T @ e for e in ops)
    assert np.allclose(total, np.eye(2), atol=1e-12)


def test_gad_full_damping_at_p_ground_one_has_no_upward_terms():
    e0, e1, e2, e3 = generalized_amplitude_damping_kraus(1.0, 1.0)
    assert np.allclose(e2, 0) and np.allclose(e3, 0)


def test_blackbody_matches_bose_einstein():
    nu = 193.4e12
    assert math.isclose(blackbody_occupation(nu, 300.0), bose_einstein_occupation(2 * math.pi * nu, 300.0), rel_tol=1e-9)
