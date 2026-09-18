"""Phase 2 analytic tests: Bell states, Bell measurement, teleportation, swapping, CHSH, dense coding, GHZ, tomography."""
import math

import numpy as np
import pytest

from qll.channels.light_time_delay import NotYetArrived
from qll.circuits.bell import bell_state, concurrence, schmidt_coefficients, werner_state
from qll.circuits.bell_measurement import BellMeasurement
from qll.circuits.chsh import chsh_sampled_stim, chsh_value, chsh_werner_analytic
from qll.circuits.entanglement_swapping import swap, swapped_fraction_analytic
from qll.circuits.fidelity import fidelity, fuchs_van_de_graaf_holds, trace_distance
from qll.circuits.ghz import ghz_state, sample_ghz
from qll.circuits.superdense_coding import HOLEVO_CAPACITY_BITS_PER_QUBIT, decode, encode
from qll.circuits.teleportation import analytic_average_fidelity, average_fidelity, teleport
from qll.circuits.tomography import reconstruct
from qll.hardware.randomness import NumpyPRNG, min_entropy_from_chsh

pytestmark = pytest.mark.phase2


@pytest.mark.parametrize("kind", ["phi+", "phi-", "psi+", "psi-"])
def test_bell_states_maximally_entangled(kind):
    b = bell_state(kind)
    assert np.allclose(schmidt_coefficients(b), [1 / math.sqrt(2)] * 2)
    assert concurrence(b) == pytest.approx(1.0, abs=1e-9)
    red = np.einsum("ijkj->ik", np.outer(b, b.conj()).reshape(2, 2, 2, 2))
    assert np.allclose(red, np.eye(2) / 2)


def test_bell_circuit_matches_state():
    from qiskit.quantum_info import Statevector
    from qll.circuits.bell import bell_circuit
    sv = Statevector(bell_circuit("psi-")).data
    # Qiskit little-endian ordering: swap qubits to compare
    sv = sv.reshape(2, 2).T.reshape(4)
    assert abs(abs(np.vdot(sv, bell_state("psi-"))) - 1) < 1e-12


def test_werner_entangled_iff_f_above_half():
    assert concurrence(werner_state(0.6)) > 0
    assert concurrence(werner_state(0.5)) == pytest.approx(0.0, abs=1e-9)
    assert concurrence(werner_state(0.4)) == 0.0


def test_fidelity_basics_and_fuchs_van_de_graaf():
    z, o = np.array([1, 0]), np.array([0, 1])
    assert fidelity(z, z) == pytest.approx(1.0)
    assert fidelity(z, o) == pytest.approx(0.0, abs=1e-12)
    assert fidelity(z, np.eye(2) / 2) == pytest.approx(0.5)
    rng = np.random.default_rng(0)
    for _ in range(50):
        a = rng.normal(size=(2, 2)) + 1j * rng.normal(size=(2, 2)); a = a @ a.conj().T; a /= np.trace(a).real
        b = rng.normal(size=(2, 2)) + 1j * rng.normal(size=(2, 2)); b = b @ b.conj().T; b /= np.trace(b).real
        assert fuchs_van_de_graaf_holds(a, b)


def test_bell_measurement_success_probabilities():
    assert BellMeasurement("deterministic").success_probability == 1.0
    assert BellMeasurement("linear_optics").success_probability == 0.5
    P = BellMeasurement().projectors()
    assert np.allclose(sum(P.values()), np.eye(4))


def test_teleportation_ideal_fidelity_is_one():                         # REQ-CIR-001
    assert average_fidelity(n_haar=100) == pytest.approx(1.0, abs=1e-6)


@pytest.mark.parametrize("f", [0.95, 0.8, 0.5, 0.25])
def test_teleportation_werner_fidelity_matches_2f_plus_1_over_3(f):    # REQ-CIR-002
    assert average_fidelity(werner_state(f), n_haar=200) == pytest.approx(analytic_average_fidelity(f), abs=2e-3)
    assert analytic_average_fidelity(0.5) == pytest.approx(2 / 3)


def test_teleportation_costs_two_bits_and_one_pair_and_respects_light_time():   # REQ-PHY-002, INV-1, INV-3
    rec = teleport(np.array([0.6, 0.8j]), distance_m=1.5e8)   # 0.5 s away
    assert len(rec.classical_bits) == 2 and rec.pairs_consumed == 1
    with pytest.raises(NotYetArrived):
        rec.output.open(0.1)
    rho = rec.output.open(rec.message.earliest_arrival_s)
    assert fidelity(np.array([0.6, 0.8j]), rho) == pytest.approx(1.0, abs=1e-9)


def test_swapping_ideal_and_werner_recurrence():
    b = bell_state("phi+"); rho = np.outer(b, b.conj())
    r = swap(rho, rho, rng=np.random.default_rng(0))
    assert fidelity(b, r.pair_out) == pytest.approx(1.0, abs=1e-9)
    w = werner_state(0.9)
    r = swap(w, w, rng=np.random.default_rng(1))
    assert fidelity(b, r.pair_out) == pytest.approx(swapped_fraction_analytic(0.9), abs=1e-9)
    assert len(r.herald_bits) == 2


def test_chsh_ideal_and_werner():                                     # REQ-CIR-003
    b = bell_state("phi+")
    assert chsh_value(np.outer(b, b.conj())) == pytest.approx(2 * math.sqrt(2), abs=1e-6)
    for f in (1.0, 0.8, 0.6):
        assert chsh_value(werner_state(f)) == pytest.approx(chsh_werner_analytic(f), abs=1e-9)
    assert chsh_value(werner_state(0.5)) < 2


def test_chsh_sampled_within_error_and_requires_declared_entropy():
    with pytest.raises(ValueError):
        chsh_sampled_stim(100, NumpyPRNG(0))
    S, err = chsh_sampled_stim(20000, NumpyPRNG(1), allow_pseudo=True)
    assert abs(S - 2 * math.sqrt(2)) < 4 * err + 0.01
    assert min_entropy_from_chsh(2 * math.sqrt(2)) == pytest.approx(1.0)
    assert min_entropy_from_chsh(2.0) == pytest.approx(0.0)


def test_superdense_coding_all_messages_and_capacity():
    for bits in [(0, 0), (0, 1), (1, 0), (1, 1)]:
        probs = decode(encode(bits))
        assert probs[bits] == pytest.approx(1.0, abs=1e-12)
    assert HOLEVO_CAPACITY_BITS_PER_QUBIT == 2.0


def test_ghz_stim_all_equal_and_state():
    s = sample_ghz(1000, 300, seed=3)
    assert np.all((s.sum(axis=1) == 0) | (s.sum(axis=1) == 1000))
    v = ghz_state(3)
    assert np.allclose(np.linalg.norm(v), 1) and v[0] == v[-1]


def test_tomography_reconstructs_bell_state_physically():
    b = bell_state("phi+")
    r = reconstruct(np.outer(b, b.conj()), shots=100000, seed=5)
    assert fidelity(b, r) > 0.99
    assert np.trace(r).real == pytest.approx(1.0) and np.linalg.eigvalsh(r).min() > -1e-12
