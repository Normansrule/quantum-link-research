"""Mission Phase 4 on a cloud processor (M4.1 teleportation, M4.2 superdense coding) and the paper-1 analysis
pipeline: every circuit against an exact result, every control against its no-signalling value."""
import json
from pathlib import Path

import numpy as np
import pytest

from qll.analysis import collapse_report as CR
from qll.circuits import cloud_run as R
from qll.circuits import superdense_cloud as S
from qll.circuits import teleport_cloud as T

pytestmark = pytest.mark.phase2
pytest.importorskip("qiskit_aer")
ROOT = Path(__file__).resolve().parents[1]


def test_cardinal_states_are_a_two_design():
    from qiskit.quantum_info import Statevector, random_unitary
    from qiskit import QuantumCircuit
    states = []
    for s in T.CARDINAL:
        qc = QuantumCircuit(1); T._prepare(qc, 0, s); states.append(Statevector(qc).data)
    for seed in range(20):
        U = random_unitary(2, seed=seed).data
        mean = np.mean([abs(np.vdot(v, U @ v)) ** 2 for v in states])
        assert mean == pytest.approx((2 + abs(np.trace(U)) ** 2) / 6, abs=1e-12)     # the Haar average [dankert2009]


def test_inverse_preparation_undoes_preparation():
    from qiskit import QuantumCircuit
    from qiskit.quantum_info import Statevector
    for s in T.CARDINAL:
        qc = QuantumCircuit(1); T._prepare(qc, 0, s); T._prepare(qc, 0, s, inverse=True)
        assert abs(Statevector(qc).data[0]) == pytest.approx(1.0)


def test_teleportation_needs_its_two_bits():
    ff = T.analyze(R.run_aer(T.circuits("feedforward"), 2000, seed=1), "feedforward")
    de = T.analyze(R.run_aer(T.circuits("deferred"), 2000, seed=2), "deferred")
    nb = T.analyze(R.run_aer(T.circuits("no_bits"), 20000, seed=3), "no_bits")
    assert ff.average == de.average == 1.0 and ff.beats_classical and de.beats_classical
    assert nb.interval[0] < 0.5 < nb.interval[1] and not nb.beats_classical      # without the bits: exactly 1/2


def test_noisy_teleportation_matches_the_werner_closed_form():
    from qiskit import QuantumCircuit
    from qiskit.quantum_info import DensityMatrix, Kraus, Statevector, partial_trace, state_fidelity
    from qiskit_aer.noise import depolarizing_error
    p = 0.1
    assert T.werner_average_fidelity(1 - 3 * p / 4) == pytest.approx(1 - p / 2)      # pair noise alone
    dep = Kraus(depolarizing_error(p, 2).to_quantumchannel())
    for s in ("0", "+i"):                                                          # exact density-matrix calculation
        qc = QuantumCircuit(3); T._prepare(qc, 0, s)
        qc.h(1); qc.cx(1, 2); qc.append(dep, [1, 2]); qc.cx(0, 1); qc.append(dep, [0, 1]); qc.h(0); qc.cx(1, 2); qc.cz(0, 2)
        ref = QuantumCircuit(1); T._prepare(ref, 0, s)
        assert state_fidelity(partial_trace(DensityMatrix(qc), [0, 1]), Statevector(ref)) == pytest.approx(T.expected_feedforward_fidelity(p), abs=1e-12)
    v = T.analyze(R.run_aer(T.circuits("feedforward"), 20000, seed=4, noise_model=T.noise_model_depolarizing(p)), "feedforward")
    assert v.average == pytest.approx(T.expected_feedforward_fidelity(p), abs=0.005)  # Aer's noise sampling (see cloud_run)


def test_superdense_coding_and_its_control():
    from qll.circuits.superdense_coding import encode
    for m in S.MESSAGES:                                                           # Bob's half is I/2 whatever Alice encodes
        psi = encode(m); rho = np.outer(psi, psi.conj()).reshape(2, 2, 2, 2)
        assert np.allclose(np.einsum("abac->bc", rho), np.eye(2) / 2)
    sent = S.analyze(R.run_aer(S.circuits("send_qubit"), 2000, seed=5), "send_qubit")
    kept = S.analyze(R.run_aer(S.circuits("keep_qubit"), 20000, seed=6), "keep_qubit")
    assert sent.success == 1.0 and sent.bits_per_use == pytest.approx(2.0)          # the Holevo-optimal two bits
    assert kept.success == pytest.approx(0.25, abs=0.01) and kept.bits_per_use < 0.001


def test_backend_helpers_on_a_fake_device():
    pytest.importorskip("qiskit_ibm_runtime")
    b = R.get_backend("fake_torino")
    assert R.supports_feedforward(b) and R.coupling_distance(b, 0, 1) == 1 and R.coupling_distance(b, 0, 60) > 5
    assert R.coupling_distance(object(), 0, 1) is None


def _write_run(folder, scheme, leak, seed, shots=20000):
    from qll.circuits import collapse_signalling as C
    counts = C.run_aer(scheme, shots, leak=leak, seed=seed)
    rec = {"experiment": "E17 collapse code", "backend": "aer", "scheme": scheme, "layout": [0, 1], "coupling_distance": None,
           "leak_injected": leak, "seed": seed, "counts": counts}
    (folder / f"{scheme}_{leak}_{seed}.json").write_text(json.dumps(rec))


def test_paper_pipeline_flags_controls_and_passes_nulls(tmp_path):
    for i, s in enumerate(("basis", "measure", "flip")):
        _write_run(tmp_path, s, 0.0, 30 + i)
    _write_run(tmp_path, "measure", 0.1, 40)
    rows = CR.analyze_runs(CR.load(tmp_path))
    assert len(rows) == 4 and all(r["as_expected"] for r in rows)
    assert [r["detected"] for r in rows if r["control"]] == [True]
    md = CR.results_md(rows)
    assert "Every control detected: True" in md and "Every test run as expected: True" in md
    figs = CR.figures(rows, tmp_path / "fig")
    assert {f.stem for f in figs} == {"rates", "bound_vs_uses"}                    # no distances on a simulator


def test_committed_rehearsal_results_are_current():
    base = ROOT / "research" / "papers" / "P1_collapse_code"
    rows = CR.analyze_runs(CR.load(base / "data" / "rehearsal"))
    assert (base / "results.md").read_text(encoding="utf-8") == CR.results_md(rows, "Results: rehearsal on simulators (not hardware)")
    assert all(r["as_expected"] for r in rows)


@pytest.mark.slow
def test_frontier_runner_rehearses_on_a_fake_device(tmp_path):
    pytest.importorskip("qiskit_ibm_runtime")
    import importlib.util
    spec = importlib.util.spec_from_file_location("rf", ROOT / "experiments" / "bench" / "frontier" / "run_frontier.py")
    rf = importlib.util.module_from_spec(spec); spec.loader.exec_module(rf)
    path = rf.main(["superdense", "--backend", "fake_torino", "--layout", "0", "1", "--shots", "1000", "--out", str(tmp_path)])
    rec = json.loads(Path(path).read_text())
    assert rec["runs"]["send_qubit"]["verdict"]["success"] > 0.6 and abs(rec["runs"]["keep_qubit"]["verdict"]["success"] - 0.25) < 0.05


def test_numbers_quoted_in_the_paper_draft_match_the_data():
    base = ROOT / "research" / "papers" / "P1_collapse_code"
    paper = (base / "paper.md").read_text(encoding="utf-8")
    rows = CR.analyze_runs(CR.load(base / "data" / "rehearsal"))
    best = min(r["mi_upper"] for r in rows if not r["control"])
    m, e = f"{best:.1e}".split("e")
    sup = str(int(e[1:])).translate(str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹"))
    assert f"{m} × 10⁻{sup}" in paper
    leak = [r for r in rows if r["control"]][0]
    assert f"{leak['bias']:.3f}".replace("-", "−") in paper
    tele = json.loads(next((ROOT / "experiments" / "bench" / "frontier" / "rehearsal").glob("teleport_*.json")).read_text())
    for mode in ("feedforward", "deferred", "no_bits"):
        assert f"{T.analyze(tele['runs'][mode]['counts'], mode).average:.3f}" in paper, mode
