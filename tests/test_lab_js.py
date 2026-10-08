"""The lab pages compute in the browser what the Python computes here. Every function of docs/js/lab_twin.js and
docs/js/lab_quantum.js runs under node and is compared with the tested Python: the link twins to 1e-9, the quantum
arithmetic to 1e-12, and a session sampled in JavaScript is read back by qll/link/hardware_log.py."""
import json
import math
import shutil
import subprocess
from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest

from qll.link import bench_tier1, two_room
from qll.link.config import LinkConfig
from qll.link.decoy import decoy_bound, gllp_bound
from qll.link.expected_session import expected_session
from qll.qkd import e91

pytestmark = pytest.mark.phase3
ROOT = Path(__file__).resolve().parents[1]
JS = ROOT / "docs" / "js"
HW = ROOT / "systems" / "see510" / "hardware"


def _node():
    for cand in (shutil.which("node"), "/opt/node22/bin/node"):
        if cand and Path(cand).exists():
            return cand
    pytest.skip("node is not installed")


def run_js(tmp_path, body: str, data) -> dict:
    script = tmp_path / "lab.js"
    script.write_text("const T = require(process.argv[2]); const Q = require(process.argv[3]);\n"
                      "const data = JSON.parse(require('fs').readFileSync(process.argv[4], 'utf8'));\n"
                      "const out = (() => {" + body + "})();\nprocess.stdout.write(JSON.stringify(out));\n")
    (tmp_path / "data.json").write_text(json.dumps(data))
    r = subprocess.run([_node(), str(script), str(JS / "lab_twin.js"), str(JS / "lab_quantum.js"), str(tmp_path / "data.json")],
                       capture_output=True, text=True, check=True)
    return json.loads(r.stdout)


def preset(name: str, **over) -> LinkConfig:
    d = {k: v for k, v in json.loads((HW / f"{name}.json").read_text()).items() if not k.startswith("_")}
    return replace(LinkConfig.from_dict(d), **over)


PARTS = [{}, {"mu": 0.3, "mu_decoy": 0.05}, {"sipm_dark_hz": 900e3, "gate_s": 3e-9}, {"channel": "fiber"},
         {"polarizer_extinction": 100, "waveplate_error": 0.03}, {"free_space_loss_db": 8.0, "sipm_pde": 0.2}]


def test_two_room_twin_matches_python(tmp_path):
    out = run_js(tmp_path, "return data.map(p => ({pred: T.twoRoomPredict(p), sess: T.expectedSession(T.twoRoomConfig(p))}));", PARTS)
    for p, js in zip(PARTS, out):
        parts = two_room.TwoRoomParts(**p)
        py = two_room.predict(parts)
        for k, v in py.items():
            assert js["pred"][k] == pytest.approx(v, rel=1e-12), (p, k)
        es = expected_session(two_room.config(parts))
        for k, v in es.items():
            if isinstance(v, bool) or k == "key_bits":
                assert js["sess"][k] == v, (p, k)
            else:
                assert js["sess"][k] == pytest.approx(v, rel=1e-9), (p, k)


CONFIGS = [("tier3", {}), ("tier3", {"distance_km": 4.0, "detector_efficiency": 0.3}), ("tier4", {}),
           ("tier4", {"misalignment_error": 0.08, "distance_km": 3.0}), ("tier4", {"dark_count_prob": 3e-4}),
           ("tier3", {"source_model": "weak_coherent"}), ("tier3", {"source_model": "single_photon", "eve_fraction": 0.3})]


def test_expected_session_matches_python_for_every_tier(tmp_path):
    cfgs = [{k: v for k, v in preset(n, **o).to_dict().items()} for n, o in CONFIGS]
    out = run_js(tmp_path, "return data.map(c => T.expectedSession(T.config(c)));", cfgs)
    for (n, o), c, js in zip(CONFIGS, cfgs, out):
        py = expected_session(LinkConfig.from_dict(c))
        for k, v in py.items():
            if isinstance(v, bool) or k == "key_bits":
                assert js[k] == v, (n, o, k)
            else:
                assert js[k] == pytest.approx(v, rel=1e-9, abs=1e-15), (n, o, k)


def test_tier_config_builders_match_the_presets(tmp_path):
    out = run_js(tmp_path, "return [T.tier3Config(), T.tier4Config(), T.tier4Config({visibility: 0.9, session_s: 10})];", None)
    for name, js in (("tier3", out[0]), ("tier4", out[1])):
        for k, v in preset(name).to_dict().items():
            if k in js and k not in ("seed", "scenario"):
                assert js[k] == pytest.approx(v) if isinstance(v, float) else js[k] == v, (name, k)
    assert out[2]["misalignment_error"] == pytest.approx(0.05) and out[2]["n_pulses"] == 500000


def test_decoy_and_gllp_bounds_match_python(tmp_path):
    cases = [[0.5, 0.1, [8000000, 1500000, 500000], [558588, 25273, 1570], 1285, 12637, 1e-10],
             [0.6, 0.2, [800000, 150000, 50000], [9000, 900, 30], 60, 450, 1e-6], [0.5, 0.1, [10, 0, 5], [1, 0, 0], 0, 0, 1e-6]]
    gl = [[0.5, 0.05, 0.03], [0.5, 0.2, 0.04], [0.8, 0.01, 0.02]]
    out = run_js(tmp_path, "return {d: data.d.map(a => T.decoyBound(...a)), g: data.g.map(a => T.gllpBound(...a))};", {"d": cases, "g": gl})
    for a, js in zip(cases, out["d"]):
        py = decoy_bound(a[0], a[1], tuple(a[2]), tuple(a[3]), a[4], a[5], a[6])
        assert js["single_fraction"] == pytest.approx(py.single_fraction, rel=1e-12, abs=1e-15)
        assert js["e1_upper"] == pytest.approx(py.e1_upper, rel=1e-12)
    for a, js in zip(gl, out["g"]):
        py = gllp_bound(*a)
        assert js["single_fraction"] == pytest.approx(py.single_fraction, rel=1e-12, abs=1e-15) and js["e1_upper"] == pytest.approx(py.e1_upper)


TIER1 = [{}, {"noise": 150}, {"noise": 150, "eve_fraction": 1.0}, {"noise": 250, "eve_fraction": 0.5},
         {"i0": 400, "ambient": 120, "leakage": 0.05, "noise": 60}, {"noise": 0}]


def test_tier1_closed_form_matches_python_and_its_monte_carlo(tmp_path):
    out = run_js(tmp_path, "return {e: data.map(p => T.tier1Expected(p)), mc: T.sample.tier1({noise: 150, eve_fraction: 0.5}, 40000, 9).qber,"
                           " erf: [0.1, 1.2, 2.9, 3.1, 5.0, -2.2].map(T.erf)};", TIER1)
    for p, js in zip(TIER1, out["e"]):
        b = bench_tier1.MalusBench(**{k: v for k, v in p.items() if k != "eve_fraction"})
        th = bench_tier1.ideal_thresholds(b)
        assert js["thresholds"]["high"] == pytest.approx(th.high, rel=1e-12) and js["thresholds"]["low"] == pytest.approx(th.low, rel=1e-12)
        assert js["qber"] == pytest.approx(bench_tier1.expected_error(b, th, p.get("eve_fraction", 0.0)), rel=1e-10, abs=1e-15), p
    assert out["mc"] == pytest.approx(bench_tier1.expected_error(bench_tier1.MalusBench(noise=150), None, 0.5), abs=0.01)
    assert out["erf"] == pytest.approx([math.erf(x) for x in (0.1, 1.2, 2.9, 3.1, 5.0, -2.2)], abs=1e-12)


def test_python_tier1_closed_form_matches_its_bench():
    for noise, f in ((150, 0.0), (150, 1.0)):
        bench = bench_tier1.MalusBench(noise=noise, seed=3)
        th = bench_tier1.ideal_thresholds(bench)
        rec = bench_tier1.run(bench, 30000, 5, f, th)
        m = rec.states.bases == rec.det.bases
        assert np.mean(rec.states.bits[m] != rec.det.bits[m]) == pytest.approx(bench_tier1.expected_error(bench, th, f), abs=0.012)


def test_chsh_helpers_match_python(tmp_path):
    cases = [(0.94, 1000), (0.7, 50), (1.0, 10)]
    out = run_js(tmp_path, "return data.map(([V, n]) => [T.chshFromVisibility(V), T.chshStd(V, n), T.diRatePerRound(T.chshFromVisibility(V), (1 - V)/2)]);", cases)
    for (V, n), js in zip(cases, out):
        assert js == pytest.approx([e91.chsh_from_visibility(V), e91.chsh_std(V, n), e91.di_rate_per_round(e91.chsh_from_visibility(V), (1 - V) / 2)], rel=1e-12, abs=1e-15)


def test_a_session_sampled_in_the_browser_is_read_by_the_python_pipeline(tmp_path):
    from qll.link.hardware_log import read_site_logs, run_from_site_logs

    out = run_js(tmp_path, "const c = T.twoRoomConfig(); const s = T.sample.link(c, 2000000, 7); const csv = T.siteCsv(s);"
                           "require('fs').writeFileSync(data + '/A.csv', csv.alice); require('fs').writeFileSync(data + '/B.csv', csv.bob);"
                           "return {click: s.click_prob, qber: s.qber, check: T.checkAgainstTwin(s, T.expectedSession(c))};", str(tmp_path))
    rec = read_site_logs(tmp_path / "A.csv", tmp_path / "B.csv")
    assert len(rec.states.bits) == 2_000_000 and rec.det.detected.mean() == pytest.approx(out["click"], rel=1e-12)
    pred = two_room.predict()
    assert out["click"] == pytest.approx(pred["click_prob_per_pulse"], rel=0.01) and out["check"]["all_pass"]
    res = run_from_site_logs(tmp_path / "A.csv", tmp_path / "B.csv", two_room.config())
    check = two_room.check_against_twin(res.metrics)
    assert check["all_pass"], check


def test_collapse_code_matches_python(tmp_path):
    from qll.circuits import collapse_signalling as cs

    cases = [(s, V, leak) for s in cs.SCHEMES for V, leak in ((1.0, 0.0), (0.9, 0.0), (0.97, 0.1))]
    out = run_js(tmp_path, "const f = (A) => [Array.from(A.re), Array.from(A.im)];"
                           "return {e: data.c.map(([s, V, l]) => { const r = Q.collapseExpected(s, V, l); return {p1: r.p1, mi: r.mi, rho: r.rhoB.map(f)}; }),"
                           " n: data.d.map(d => Q.usesToDetect(d)), ppf: [0.995, 0.9, 0.5, 1e-6].map(Q.normPpf),"
                           " mi: data.m.map(([a, b]) => Q.mutualInformation(a, b))};",
                 {"c": cases, "d": [0.01, 0.05, 0.003], "m": [[0.5, 0.45], [0.1, 0.9], [0.5, 0.5]]})
    for (s, V, leak), js in zip(cases, out["e"]):
        rho = 0.25 * (1 - V) * np.eye(4) + V * np.outer([1, 0, 0, 1], [1, 0, 0, 1]) / 2
        for x in (0, 1):
            rb = cs.bob_state_after(rho, cs.instrument(s, x))
            got = np.array(js["rho"][x][0]).reshape(2, 2) + 1j * np.array(js["rho"][x][1]).reshape(2, 2)
            assert np.allclose(got, rb, atol=1e-14) and np.allclose(rb, np.eye(2) / 2, atol=1e-14)
        assert js["p1"] == pytest.approx([0.5, 0.5 * (1 - leak)], abs=1e-14)
    assert out["n"] == [cs.uses_to_detect(d) for d in (0.01, 0.05, 0.003)]
    from scipy import stats
    assert out["ppf"] == pytest.approx([stats.norm.ppf(p) for p in (0.995, 0.9, 0.5, 1e-6)], abs=1e-12)
    assert out["mi"] == pytest.approx([cs.mutual_information(a, b) for a, b in ((0.5, 0.45), (0.1, 0.9), (0.5, 0.5))], abs=1e-14)


def test_teleportation_matches_the_closed_form_and_aer(tmp_path):
    from qll.circuits.teleport_cloud import expected_feedforward_fidelity

    p2s = [0.0, 0.02, 0.1]
    out = run_js(tmp_path, "return data.map(p => ({ff: Q.teleportAverage('feedforward', p), de: Q.teleportAverage('deferred', p),"
                           " nb: Q.teleportAverage('no_bits', p), per: Object.keys(Q.CARDINAL).map(k => Q.teleportRho(k, 'deferred', p).fidelity)}));", p2s)
    for p, js in zip(p2s, out):
        assert js["ff"] == pytest.approx(expected_feedforward_fidelity(p), abs=1e-12)
        assert js["nb"] == pytest.approx(0.5, abs=1e-12)
    aer = pytest.importorskip("qiskit_aer")
    from qiskit import QuantumCircuit
    from qiskit_aer.noise import NoiseModel, depolarizing_error
    from qll.circuits.teleport_cloud import CARDINAL, _prepare

    p = 0.1
    nm = NoiseModel(); nm.add_all_qubit_quantum_error(depolarizing_error(p, 2), ["cx"])
    sim = aer.AerSimulator(method="density_matrix", noise_model=nm)
    for state, js_f in zip(CARDINAL, out[2]["per"]):
        qc = QuantumCircuit(3)
        _prepare(qc, 0, state); qc.h(1); qc.cx(1, 2); qc.cx(0, 1); qc.h(0); qc.cx(1, 2); qc.cz(0, 2)
        _prepare(qc, 2, state, inverse=True)
        qc.save_density_matrix(qubits=[2])          # run untranspiled: the noise model's basis would turn the CZ into a noisy CX
        rho = sim.run(qc).result().data()["density_matrix"]
        assert js_f == pytest.approx(float(np.real(rho.data[0, 0])), abs=1e-12), state


def test_superdense_matches_aer(tmp_path):
    out = run_js(tmp_path, "return [Q.superdense('send_qubit', 0), Q.superdense('keep_qubit', 0), Q.superdense('send_qubit', 0.08)];", None)
    assert out[0]["success"] == pytest.approx(1) and out[0]["bits_per_use"] == pytest.approx(2)
    assert out[1]["success"] == pytest.approx(0.25) and out[1]["bits_per_use"] == pytest.approx(0, abs=1e-12)
    aer = pytest.importorskip("qiskit_aer")
    from qiskit import QuantumCircuit
    from qiskit_aer.noise import NoiseModel, depolarizing_error

    nm = NoiseModel(); nm.add_all_qubit_quantum_error(depolarizing_error(0.08, 2), ["cx"])
    sim = aer.AerSimulator(method="density_matrix", noise_model=nm)
    for row, (i, j) in enumerate(((0, 0), (0, 1), (1, 0), (1, 1))):
        qc = QuantumCircuit(2)
        qc.h(0); qc.cx(0, 1)
        if j: qc.x(0)
        if i: qc.z(0)
        qc.cx(0, 1); qc.h(0); qc.save_probabilities_dict(qubits=[0, 1])
        probs = sim.run(qc).result().data()["probabilities"]
        for k in range(4):                     # Qiskit's key is q1 q0 as an integer q0 + 2 q1; ours is 2 q0 + q1
            q0, q1 = k >> 1, k & 1
            assert out[2]["confusion"][row][k] == pytest.approx(probs.get(q0 + 2 * q1, 0.0), abs=1e-12)


def test_majorana_matches_python(tmp_path):
    from qll.circuits import majorana_teleport as mt
    from qll.hardware import majorana_error_budget as eb

    keys = ["0", "1", "+", "-", "+i", "-i"]
    out = run_js(tmp_path, "return {t: data.flatMap(k => Q.MAJ_SCHEMES.map(s => Q.majoranaTeleport(k, s))),"
                           " avg: Q.MAJ_SCHEMES.map(Q.majoranaAverage), b: [Q.budgetFidelity(4, 5, 0.01, 3), Q.readoutFidelity(2, 1.5), Q.budgetFidelity(10, 20, 0.001, 6)]};", keys)
    r = 1 / math.sqrt(2)
    vec = {"0": [1, 0], "1": [0, 1], "+": [r, r], "-": [r, -r], "+i": [r, 1j * r], "-i": [r, -1j * r]}
    it = iter(out["t"])
    for k in keys:
        for s in mt.SCHEMES:
            js, py = next(it), mt.teleport(vec[k], s)
            assert js["average"] == pytest.approx(py.average, abs=1e-12)
            for key, (p, f) in py.outcomes.items():
                o = js["outcomes"][",".join(map(str, key))]
                assert o["p"] == pytest.approx(p, abs=1e-12) and o["fidelity"] == pytest.approx(f, abs=1e-12), (k, s, key)
    assert out["avg"] == pytest.approx([mt.average_fidelity(s) for s in mt.SCHEMES], abs=1e-12)
    assert out["b"] == pytest.approx([eb.teleport_fidelity(4, 5, 0.01, 3), eb.readout_fidelity(2, 1.5), eb.teleport_fidelity(10, 20, 0.001, 6)], rel=1e-12)


def test_every_terminal_line_cites_a_known_source(tmp_path):
    out = run_js(tmp_path, "const all = [...T.steps.tier1({noise: 50, eve_fraction: 0.3}), ...T.steps.twoRoom({}), ...T.steps.twoRoom({channel: 'fiber'}),"
                           " ...T.steps.tier3(T.tier3Config()), ...T.steps.tier3(T.tier3Config({source_model: 'weak_coherent'})), ...T.steps.tier4(T.tier4Config()),"
                           " ...Q.steps.collapse('basis', 0.97, 0.1), ...Q.steps.teleport('+i', 'deferred', 0.02), ...Q.steps.superdense('keep_qubit', 0),"
                           " ...Q.steps.majorana('-', 'paper_one_bit', {snr0: 4, gap: 5, poison: 0.01, l: 3})];"
                           " return all.map(l => [l.label, l.ref, String(l.value)]);", None)
    keys = set()
    for bib in (ROOT / "docs").glob("references*.bib"):
        import re
        keys |= set(re.findall(r"@\w+\{([^,]+),", bib.read_text()))
    assert len(out) > 80
    for label, ref, value in out:
        assert ref in keys or (ROOT / ref).exists(), (label, ref)
        assert "NaN" not in value and "undefined" not in value, (label, value)
