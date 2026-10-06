"""Majorana measurement-only teleportation (Crogman, Dang, and Erenso 2025): the fermionic algebra, the protocol,
the appendix theorems, the error budget, and the qubit emulation, each against an exact result."""
import itertools

import numpy as np
import pytest

from qll.circuits import majorana_teleport as M
from qll.hardware import majorana_error_budget as EB

pytestmark = pytest.mark.phase2
RNG = np.random.default_rng(7)
PA = {"I": np.eye(2), "X": M.PAULI[0], "Y": M.PAULI[1], "Z": M.PAULI[2]}


def _haar(rng=RNG):
    v = rng.normal(size=2) + 1j * rng.normal(size=2)
    return v / np.linalg.norm(v)


def _pauli_string(label):
    return M._kron(*[PA[ch] for ch in label])


def test_majorana_algebra_and_logical_z():
    for i, j in itertools.product(range(1, 7), repeat=2):
        assert np.allclose(M.G[i] @ M.G[j] + M.G[j] @ M.G[i], 2 * np.eye(8) * (i == j))
        assert np.allclose(M.G[i], M.G[i].conj().T)
    for m in range(3):
        n = np.diag([int(format(k, "03b")[m]) for k in range(8)])
        assert np.allclose(M.bilinear(2 * m + 1, 2 * m + 2), 2 * n - np.eye(8))      # i g g = 2n - 1 for c = (g + i g)/2
        assert np.allclose(M.logical_z(m), np.eye(8) - 2 * n)


def test_jordan_wigner_map_and_the_protocol_as_pauli_measurements():
    from qll.circuits.majorana_cloud import JW
    for k, label in JW.items():
        assert np.allclose(M.G[k], _pauli_string(label))
    assert np.allclose(M.P23, -_pauli_string("XXI")) and np.allclose(M.P14, _pauli_string("YYI"))   # a Bell measurement of A, B
    assert np.allclose(M.X_C_PAPER, -_pauli_string("IXX"))                                           # acts on B as well as C


def test_two_parity_measurements_teleport_exactly():
    for _ in range(30):
        psi = _haar()
        t = M.teleport(psi, "two_bit")
        assert t.bits_sent == 2 and len(t.outcomes) == 4
        for pr, f in t.outcomes.values():
            assert pr == pytest.approx(0.25) and f == pytest.approx(1.0)
    assert M.average_fidelity("two_bit") == pytest.approx(1.0)


def test_corrections_are_parity_even_cliffords():
    paulis = [_pauli_string(a + b + c) for a, b, c in itertools.product("IXYZ", repeat=3)]
    for U in M.CORRECTIONS.values():
        assert np.allclose(U @ U.conj().T, np.eye(8)) and np.allclose(U, U.conj().T)
        assert np.allclose(U @ M.ID, M.ID @ U)
        parity = M.logical_z(0) @ M.logical_z(1) @ M.logical_z(2)
        assert np.allclose(U @ parity, parity @ U)                                   # total fermion parity conserved
        for P in paulis:                                                             # Clifford: Paulis map to Paulis (Theorem A4)
            Q = U @ P @ U.conj().T
            assert any(np.allclose(Q, s * R) for R in paulis for s in (1, -1, 1j, -1j))


def test_one_parity_bit_cannot_beat_the_classical_limit():
    for key in ((1,), (-1,)):
        T, t = M.bloch_map("one_bit_best", key)
        assert np.allclose(np.abs(T), np.diag([1, 0, 0])) and np.allclose(t, 0)      # only the X component survives
        assert M.best_average_fidelity(T) == pytest.approx(2 / 3)
    assert M.average_fidelity("one_bit_best") == pytest.approx(2 / 3)               # the explicit correction reaches the optimum
    assert M.average_fidelity("paper_one_bit") == pytest.approx(0.5)


def test_no_feedforward_no_signalling():
    for _ in range(20):
        assert np.allclose(M.no_feedforward_state(_haar()), np.eye(2) / 2)
    for scheme in ("two_bit", "paper_one_bit"):                                      # averaged over outcomes, before correction
        psi = _haar()
        avg = sum(pr * M.reduced(r, "C") for pr, r in M.bob_conditional(psi, scheme).values())
        assert np.allclose(avg, np.eye(2) / 2)


def test_sender_is_left_maximally_mixed():                                         # Theorem A2
    psi = _haar()
    for pr, r in M.bob_conditional(psi, "two_bit").values():
        assert np.allclose(M.reduced(r, "A"), np.eye(2) / 2)


def test_entropy_under_ideal_parity_measurement():                                  # Theorems A5, A6 and Remark A1
    P = M.P23
    w = RNG.random(8); w /= w.sum()
    evecs = np.linalg.eigh(P)[1]
    rho = evecs @ np.diag(w) @ evecs.conj().T                                        # commutes with P
    assert np.allclose(M.luders(rho, P), rho) and M.von_neumann(M.luders(rho, P)) == pytest.approx(M.von_neumann(rho))
    increased = 0
    for _ in range(20):
        A = RNG.normal(size=(8, 8)) + 1j * RNG.normal(size=(8, 8))
        rho = A @ A.conj().T; rho /= np.trace(rho)
        s0, s1 = M.von_neumann(rho), M.von_neumann(M.luders(rho, P))
        assert s1 >= s0 - 1e-10                                                      # never decreases (a unital channel)
        increased += s1 > s0 + 1e-6
    assert increased > 15


def test_local_protection_in_its_correct_form():                                    # Lemma A1, stated precisely
    Z = M.logical_z(0)
    g1 = M.G[1]
    assert np.allclose(g1 @ Z, -Z @ g1)                                               # a single Majorana anticommutes with the parity
    zero, one = M.ket([0, 0, 0]), M.ket([1, 0, 0])
    assert abs(zero.conj() @ g1 @ zero) < 1e-12 and abs(one.conj() @ g1 @ one) < 1e-12   # it cannot read the qubit
    assert abs(one.conj() @ g1 @ zero) == pytest.approx(1.0)                         # but it flips it (poisoning)
    assert len(M.parity_even_operators_on((1,))) == 1                                # the only allowed local operator is I
    ops = M.parity_even_operators_on((1, 2))
    assert any(np.allclose(o, 1j * Z) or np.allclose(o, -1j * Z) for o in ops)        # reading needs both ends


def test_error_budget_limits_and_trends():
    assert EB.readout_fidelity(0.0, 5.0) == pytest.approx(0.5)
    assert EB.readout_fidelity(10.0, 50.0) == pytest.approx(1.0, abs=1e-12)
    assert EB.readout_fidelity(3.0, 2.0) < EB.readout_fidelity(3.0, 10.0)             # warmer: less signal
    assert EB.poisoned_readout_fidelity(0.99, 1.0) == pytest.approx(0.5)
    f = [EB.teleport_fidelity(5.0, 10.0, 1e-2, x) for x in (1, 2, 4, 8)]
    assert f == sorted(f)
    assert EB.teleport_fidelity(5, 10, 1e-2, 8, readouts=2) == pytest.approx(EB.teleport_fidelity(5, 10, 1e-2, 8, readouts=1) ** 2 /
                                                                             EB.hybridization_factor(8), rel=1e-12)
    assert EB.splitting_ratio(3, 4) == pytest.approx(np.exp(-2))
    assert EB.separation_for(1e-3) == pytest.approx(np.log(1000) / 2)
    assert EB.separation_for(1e-3, exponent=1) == pytest.approx(np.log(1000))


def test_qubit_emulation_matches_the_fermionic_model():
    pytest.importorskip("qiskit_aer")
    from qll.circuits import cloud_run as R
    from qll.circuits import majorana_cloud as MC
    from qll.circuits import teleport_cloud as T
    r = 1 / np.sqrt(2)
    vec = {"0": [1, 0], "1": [0, 1], "+": [r, r], "-": [r, -r], "+i": [r, 1j * r], "-i": [r, -1j * r]}
    scheme = {"two_bit": "two_bit", "one_bit": "one_bit_best", "paper_one_bit": "paper_one_bit"}
    for mode in MC.MODES:
        v = T.analyze(R.run_aer(MC.circuits(mode), 20000, seed=3), mode)
        assert v.average == pytest.approx(MC.EXPECTED[mode], abs=0.012)
        if mode in scheme:
            for s, f in v.per_state.items():
                assert f == pytest.approx(M.teleport(vec[s], scheme[mode]).average, abs=0.02), (mode, s)


def test_numbers_in_the_theory_note_match_the_error_budget():
    from pathlib import Path
    text = (Path(__file__).resolve().parents[1] / "research" / "theories" / "T16_majorana_measurement_only_teleportation.md").read_text(encoding="utf-8")
    for snr, gkt, pq, L in ((3, 10, 0.01, 3), (5, 10, 0.01, 6), (10, 10, 0.001, 6), (5, 10, 0.1, 6)):
        assert f"| {snr} | {gkt} | {pq:g} | {L} | {EB.teleport_fidelity(snr, gkt, pq, L):.3f} |" in text
    assert f"{EB.separation_for(1e-3):.1f}" in text and f"{EB.separation_for(1e-6):.1f}" in text


def test_rehearsal_numbers_in_protocol_p13_match_the_data():
    import json
    from pathlib import Path
    from qll.circuits import teleport_cloud as T
    root = Path(__file__).resolve().parents[1]
    text = (root / "experiments" / "protocols" / "P13_majorana_teleportation_on_a_cloud_processor.md").read_text(encoding="utf-8")
    rec = json.loads(next((root / "experiments" / "bench" / "frontier" / "rehearsal").glob("majorana_*.json")).read_text())
    for mode in ("two_bit", "one_bit", "paper_one_bit", "no_bits"):
        assert f"{T.analyze(rec['runs'][mode]['counts'], mode).average:.3f}" in text, mode
