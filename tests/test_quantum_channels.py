"""Quantum channels: representations agree with each other, the BB84 certificate holds for every qubit channel,
the capacities match their closed forms, the hallway twin is consistent with the link twin, and tomography of a
known channel recovers it and certifies it."""
import math

import numpy as np
import pytest

from qll.circuits import qubit_channel as Q
from qll.circuits.noise._kraus_base import KrausChannel
from qll.circuits.noise.amplitude_damping import amplitude_damping
from qll.circuits.noise.depolarizing import depolarizing
from qll.circuits.noise.phase_damping import phase_damping
from qll.link import channel_tomography as CT
from qll.link import two_room
from qll.link.expected_session import expected_session
from qll.link.hallway_channel import hallway_channel
from qll.qkd.binary_entropy import h2

pytestmark = pytest.mark.phase3


def random_channel(rng, k=3) -> KrausChannel:
    G = rng.normal(size=(2 * k, 2)) + 1j * rng.normal(size=(2 * k, 2))
    Qm, _ = np.linalg.qr(G)                            # an isometry C^2 -> C^(2k): its blocks are Kraus operators
    return KrausChannel(tuple(Qm[2 * i:2 * i + 2, :] for i in range(k)), "random")


def H(p):
    p = np.asarray(p); p = p[p > 0]
    return float(-np.sum(p * np.log2(p)))


def test_ptm_choi_and_fidelities_agree_with_kraus():
    rng = np.random.default_rng(1)
    for _ in range(20):
        ch = random_channel(rng)
        R = Q.ptm(ch)
        J = sum(np.kron(np.eye(2)[:, [a]] @ np.eye(2)[[b], :], ch.apply(np.eye(2)[:, [a]] @ np.eye(2)[[b], :])) for a in (0, 1) for b in (0, 1)) / 2
        assert np.allclose(Q.choi(R), J, atol=1e-12)
        assert Q.entanglement_fidelity(R) == pytest.approx(float(np.real(Q.PHI_PLUS.conj() @ J @ Q.PHI_PLUS)), abs=1e-12)
        from qll.circuits.noise._kraus_base import average_gate_fidelity
        assert Q.average_fidelity(R) == pytest.approx(average_gate_fidelity(ch), abs=1e-12)
        assert Q.is_physical(R)


def test_basis_errors_are_the_averaged_measured_errors_and_the_certificate_holds_for_every_channel():
    rng = np.random.default_rng(2)
    ket = {"H": [1, 0], "V": [0, 1], "D": [1, 1], "A": [1, -1]}
    for _ in range(200):
        ch = random_channel(rng, k=int(rng.integers(1, 5)))
        R = Q.ptm(ch)
        err = {}
        for s, v in ket.items():
            v = np.array(v, complex) / np.linalg.norm(v)
            out = ch.apply(np.outer(v, v.conj()))
            w = {"H": [0, 1], "V": [1, 0], "D": [1, -1], "A": [1, 1]}[s]
            w = np.array(w, complex) / np.linalg.norm(w)
            err[s] = float(np.real(w.conj() @ out @ w))
        e = Q.basis_errors(R)
        assert e["z"] == pytest.approx((err["H"] + err["V"]) / 2, abs=1e-12) and e["x"] == pytest.approx((err["D"] + err["A"]) / 2, abs=1e-12)
        assert Q.entanglement_fidelity(R) >= Q.certified_entanglement_fidelity(e["z"], e["x"]) - 1e-12
        if Q.certified_entanglement_fidelity(e["z"], e["x"]) > 0.5:
            assert not Q.is_entanglement_breaking(R)
        if Q.is_entanglement_breaking(R):
            assert Q.entanglement_fidelity(R) <= 0.5 + 1e-12 and Q.average_fidelity(R) <= 2 / 3 + 1e-12


def test_entanglement_breaking_thresholds():
    assert Q.is_entanglement_breaking(Q.intercept_resend_ptm(1.0)) and not Q.is_entanglement_breaking(Q.intercept_resend_ptm(0.9))
    assert Q.entanglement_fidelity(Q.intercept_resend_ptm(1.0)) == pytest.approx(0.5)
    assert not Q.is_entanglement_breaking(Q.depolarizing_ptm(2 / 3 - 1e-6)) and Q.is_entanglement_breaking(Q.depolarizing_ptm(2 / 3))
    assert np.allclose(Q.ptm(depolarizing(0.3)), Q.depolarizing_ptm(0.3), atol=1e-12)
    assert np.allclose(Q.compose(Q.rotation_ptm(0.4, (1, 1, 0)), Q.rotation_ptm(-0.4, (1, 1, 0))), np.eye(4), atol=1e-12)


@pytest.mark.parametrize("p", [0.0, 0.05, 0.15, 0.3, 0.6])
def test_depolarizing_capacities_match_closed_forms(p):
    R = Q.depolarizing_ptm(p)
    probs = [1 - 3 * p / 4, p / 4, p / 4, p / 4]
    assert Q.holevo_capacity_unital(R) == pytest.approx(1 - h2(1 - p / 2), abs=1e-12)
    assert Q.hashing_bound(R) == pytest.approx(max(0.0, 1 - H(probs)), abs=1e-10)
    assert Q.entanglement_assisted_capacity(R) == pytest.approx(2 - H(probs), abs=1e-10)


def test_hashing_threshold_of_the_depolarizing_channel():
    # 1 - H(1 - 3q, q, q, q) = 0 at a total Pauli error 3q of about 0.1893 (Bennett, DiVincenzo, Smolin, and Wootters 1996)
    from scipy.optimize import brentq
    f = lambda q: 1 - H([1 - 3 * q, q, q, q])
    q0 = brentq(f, 0.01, 0.1)
    assert 3 * q0 == pytest.approx(0.1893, abs=5e-4)
    assert Q.hashing_bound(Q.depolarizing_ptm(4 * q0 - 0.005)) > 0 and Q.hashing_bound(Q.depolarizing_ptm(4 * q0 + 0.005)) == 0


@pytest.mark.parametrize("gamma", [0.1, 0.25, 0.4, 0.6])
def test_amplitude_damping_quantum_capacity(gamma):
    R = Q.ptm(amplitude_damping(gamma))
    assert Q.quantum_capacity_lower(R) == pytest.approx(Q.amplitude_damping_quantum_capacity(gamma), abs=2e-4)


def test_dephasing_and_erasure():
    lam = 0.3
    R = Q.ptm(phase_damping(lam))
    pz = (1 - math.sqrt(1 - lam)) / 2                   # phase damping = Z flip with this probability
    assert np.allclose(R, Q.pauli_channel(0, 0, pz), atol=1e-12)
    assert Q.hashing_bound(R) == pytest.approx(1 - h2(pz), abs=1e-10)
    e = Q.erasure_capacities(0.3)
    assert e["quantum_one_way"] == pytest.approx(0.4) and e["quantum_two_way"] == pytest.approx(0.7) and Q.erasure_capacities(0.6)["quantum_one_way"] == 0


def test_hallway_channel_is_the_link_twin_per_photon():
    parts = two_room.TwoRoomParts()
    h = hallway_channel(parts)
    c = two_room.config(parts)
    cl = __import__("qll.link.expected_session", fromlist=["classes"]).classes(c.with_(source_model="single_photon"))
    assert h["error_zx"] == pytest.approx(cl[0][2], rel=1e-12)                 # the twin's single-photon error rate
    assert h["eta"] == pytest.approx(cl[0][3], rel=1e-12)
    assert h["certified_single_photon_fe"] == pytest.approx(1 - 2 * expected_session(c)["e1_upper"])
    assert h["certified_single_photon_fe"] > 0.5 and not h["entanglement_breaking"]
    assert h["quantum_one_way"] == 0.0 < h["quantum_heralded"] < h["plob"]
    eve = hallway_channel(parts, eve_fraction=1.0)
    c_eve = c.with_(eve_fraction=1.0, source_model="single_photon")
    assert eve["error_zx"] == pytest.approx(__import__("qll.link.expected_session", fromlist=["classes"]).classes(c_eve)[0][2], rel=1e-12)
    assert eve["entanglement_breaking"] and eve["entanglement_fidelity"] <= 0.5


def test_tomography_recovers_a_known_channel_and_certifies_it():
    R = Q.compose(Q.rotation_ptm(0.2, (0, 1, 0)), Q.depolarizing_ptm(0.06))
    counts = CT.simulate_counts(R, 200_000, seed=3)
    est = CT.estimate(counts)
    assert np.allclose(est, R, atol=0.01)
    cert = CT.certify(counts)
    assert cert["certified_quantum"] and cert["fe_lower"] <= Q.entanglement_fidelity(R) + 0.005
    assert cert["fe_lower"] < cert["fe_estimate"]
    # an intercept-resend relay is never certified
    eb = CT.certify(CT.simulate_counts(Q.intercept_resend_ptm(1.0), 200_000, seed=4))
    assert not eb["certified_quantum"]


def test_tomography_with_four_inputs_and_the_log_round_trip(tmp_path):
    R = Q.compose(Q.rotation_ptm(0.3, (1, 0, 0)), Q.depolarizing_ptm(0.04))
    counts = CT.simulate_counts(R, 100_000, inputs=("H", "V", "D", "R"), seed=5)
    assert np.allclose(CT.estimate(counts), R, atol=0.015)
    small = CT.simulate_counts(R, 50, seed=6)
    path = CT.write_log(tmp_path / "tomo.csv", small)
    assert CT.read_log(path) == small
    with pytest.raises(ValueError):
        CT.estimate({k: v for k, v in counts.items() if k[0] in ("H", "V")})


def test_teleportation_is_a_quantum_channel_only_with_its_bits():
    pytest.importorskip("qiskit_aer")
    from qll.circuits import teleport_channel_cloud as TC
    from qll.circuits.cloud_run import run_aer
    from qll.circuits.teleport_cloud import noise_model_depolarizing

    p2 = 0.05
    for mode, power in (("feedforward", 2), ("deferred", 3), ("no_bits", None)):
        keys, circs = TC.circuits(mode)
        counts = TC.counts_to_tomography(keys, run_aer(circs, 20000, seed=11, noise_model=noise_model_depolarizing(p2)))
        R = CT.estimate(counts)
        if power is None:
            assert np.allclose(R[1:, :], 0, atol=0.02) and not CT.certify(counts)["certified_quantum"]
        else:
            lam = (1 - p2) ** power
            assert np.allclose(R, np.diag([1, lam, lam, lam]), atol=0.02), mode
            assert CT.certify(counts)["certified_quantum"]


def test_photonic_superdense_coding_beats_one_bit_only_with_good_pairs_and_interference():
    from qll.circuits import superdense_photonic as SP

    assert SP.bits_per_photon(1, 1) == pytest.approx(math.log2(3), abs=1e-12)
    assert SP.bits_per_photon(1, 1, SP.BELL) == pytest.approx(1.5, abs=1e-12)        # four messages, three classes
    assert SP.bits_per_photon(0, 1) == pytest.approx(0, abs=1e-12)                   # no entanglement, no extra bits
    assert np.allclose(SP.confusion(0.8, 0.7).sum(axis=1), 1)
    assert SP.bits_per_photon(0.94, 0.9) > 1 > SP.bits_per_photon(0.8, 0.7)
    v = [SP.bits_per_photon(x, 0.9) for x in (0.7, 0.8, 0.9, 1.0)]
    assert v == sorted(v)


def test_hand_written_channel_numbers_match_the_twin():
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    h = hallway_channel()
    p14 = (root / "experiments" / "protocols" / "P14_the_hallway_as_a_quantum_channel.md").read_text(encoding="utf-8")
    doc = (root / "systems" / "program" / "09_quantum_channels.md").read_text(encoding="utf-8")
    for text in (p14, doc):
        assert f"{100 * h['error_zx']:.1f} %" in text and f"{h['entanglement_fidelity']:.3f}" in text
        assert f"{h['certified_single_photon_fe']:.2f}" in text and f"{h['quantum_heralded']:.2f}" in text and f"{h['plob']:.3f}" in text
    assert f"{h['eta']:.3f}" in p14 and f"{100 * h['eta']:.1f} %" in doc


def test_certificate_states_its_model_and_refuses_empty_data():
    """Audit P04: the witness returns its assumptions and trial counts; empty or missing classes are insufficient data."""
    from qll.link import channel_tomography as CT
    counts = {(s, b): (900, 100) if s in "HD" else (100, 900) for s in CT.INPUTS for b in CT.BASES}
    r = CT.certify(counts)
    assert r["scope"].startswith("witness") and any("fair sampling" in a for a in r["assumptions"]) and r["trials"]["HZ"] == 1000
    bad = dict(counts); bad[("H", "Z")] = (0, 0)
    with pytest.raises(ValueError, match="insufficient"):
        CT.certify(bad)
    del bad[("H", "Z")]
    with pytest.raises(ValueError, match="insufficient"):
        CT.certify(bad)


def test_unknown_memory_models_are_rejected():
    from qll.network.memory_decoherence import MemoryPlatform, crossover_time_s, fraction_after_storage_analytic
    with pytest.raises(ValueError):
        fraction_after_storage_analytic(0.9, 1.0, 10.0, "dephsing")              # a typo no longer selects another model
    with pytest.raises(ValueError):
        crossover_time_s(0.9, 10.0, "amplitude")
    with pytest.raises(ValueError):
        MemoryPlatform("x", 1.0, 0.5, 4.0, 600, "ref", efficiency_status="measured")   # measured needs a source
