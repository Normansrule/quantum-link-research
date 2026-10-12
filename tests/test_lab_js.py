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
                      "const out = (() => {" + body + "})();\nprocess.stdout.write(JSON.stringify(out));\n", encoding="utf-8")
    (tmp_path / "data.json").write_text(json.dumps(data), encoding="utf-8")
    r = subprocess.run([_node(), str(script), str(JS / "lab_twin.js"), str(JS / "lab_quantum.js"), str(tmp_path / "data.json")],
                       capture_output=True, text=True, encoding="utf-8", check=True)
    return json.loads(r.stdout)


def preset(name: str, **over) -> LinkConfig:
    d = {k: v for k, v in json.loads((HW / f"{name}.json").read_text(encoding="utf-8")).items() if not k.startswith("_")}
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
                           " const C = require(process.argv[2].replace('lab_twin.js', 'lab_channel.js'));"
                           " all.push(...C.steps(C.hallway({}).ptm, C.hallway({})), ...C.steps(C.amplitudeDamping(0.3)), ...C.stepsSuperdense(0.94, 0.9));"
                           " const O = require(process.argv[2].replace('lab_twin.js', 'lab_outdoor.js'));"
                           " all.push(...O.stepsOutdoor({distance_m: 900, receiver: O.RECEIVERS.spad}), ...O.stepsPass(O.PRESETS.micius, 60), ...O.stepsPass(O.PRESETS.jinan1, 3000));"
                           " const F = require(process.argv[2].replace('lab_twin.js', 'lab_frontier.js'));"
                           " all.push(...F.stepsDelay(60, 200, 150, 0.01), ...F.stepsLink({}, 'SiV nuclear spin in cavity'), ...F.stepsLink({distance_m: 4e11, index: 1, T_mem_s: 1}), ...F.stepsSwap({distance_m: 1e5}));"
                           " const M = require(process.argv[2].replace('lab_twin.js', 'lab_messenger.js'));"
                           " for (const s of Object.keys(M.sources())) for (const p of M.POLICIES) all.push(...M.steps(s, p, {preloaded_bits: 8e12, distance_m: 4e11}));"
                           " return all.map(l => [l.label, l.ref, String(l.value), l.why]);", None)
    keys = set()
    for bib in (ROOT / "docs").glob("references*.bib"):
        import re
        keys |= set(re.findall(r"@\w+\{([^,]+),", bib.read_text(encoding="utf-8")))
    assert len(out) > 80
    for label, ref, value, why in out:
        assert ref in keys or (ROOT / ref).exists(), (label, ref)
        assert len(why) > 20, f"{label}: every terminal line needs a plain-language note"
        assert "NaN" not in value and "undefined" not in value, (label, value)


def run_channel(tmp_path, body: str, data):
    script = tmp_path / "ch.js"
    script.write_text("const C = require(process.argv[2]);\n"
                      "const data = JSON.parse(require('fs').readFileSync(process.argv[3], 'utf8'));\n"
                      "const out = (() => {" + body + "})();\nprocess.stdout.write(JSON.stringify(out));\n", encoding="utf-8")
    (tmp_path / "chdata.json").write_text(json.dumps(data), encoding="utf-8")
    r = subprocess.run([_node(), str(script), str(JS / "lab_channel.js"), str(tmp_path / "chdata.json")], capture_output=True, text=True, encoding="utf-8", check=True)
    return json.loads(r.stdout)


def test_channel_lab_matches_python_channels_and_capacities(tmp_path):
    from qll.circuits import qubit_channel as Qc
    from qll.circuits.noise.amplitude_damping import amplitude_damping
    from qll.circuits.noise.phase_damping import phase_damping

    specs = [["dep", 0.1], ["dep", 0.4], ["rot", 0.7], ["ir", 0.6], ["ir", 1.0], ["ad", 0.3], ["ad", 0.7], ["pd", 0.4], ["tel", 0.05], ["mix", 0.2]]
    out = run_channel(tmp_path, """return data.map(([k, v]) => {
        const R = k === 'dep' ? C.depolarizing(v) : k === 'rot' ? C.compose(C.rotation(v, [1, 2, 2]), C.depolarizing(0.05)) : k === 'ir' ? C.interceptResend(v)
          : k === 'ad' ? C.amplitudeDamping(v) : k === 'pd' ? C.phaseDamping(v) : k === 'tel' ? C.teleportChannel(v, 'deferred') : C.mix(v, C.amplitudeDamping(0.2), C.depolarizing(1));
        return {R, fe: C.entanglementFidelity(R), eb: C.isEntanglementBreaking(R), phys: C.isPhysical(R), cap: C.capacities(R),
                ad: k === 'ad' ? C.amplitudeDampingQuantumCapacity(v) : null}; });""", specs)
    for (k, v), js in zip(specs, out):
        R = {"dep": lambda: Qc.depolarizing_ptm(v), "rot": lambda: Qc.compose(Qc.rotation_ptm(v, (1, 2, 2)), Qc.depolarizing_ptm(0.05)),
             "ir": lambda: Qc.intercept_resend_ptm(v), "ad": lambda: Qc.ptm(amplitude_damping(v)), "pd": lambda: Qc.ptm(phase_damping(v)),
             "tel": lambda: Qc.depolarizing_ptm(1 - (1 - v) ** 3),
             "mix": lambda: (1 - v) * Qc.ptm(amplitude_damping(0.2)) + v * Qc.depolarizing_ptm(1)}[k]()
        assert np.allclose(js["R"], R, atol=1e-12), k
        assert js["fe"] == pytest.approx(Qc.entanglement_fidelity(R), abs=1e-12)
        assert js["eb"] == Qc.is_entanglement_breaking(R) and js["phys"] == Qc.is_physical(R)
        assert js["cap"]["quantum"] == pytest.approx(Qc.quantum_capacity_lower(R), abs=1e-9)
        assert js["cap"]["hashing"] == pytest.approx(Qc.hashing_bound(R), abs=1e-9)
        assert js["cap"]["entanglement_assisted"] == pytest.approx(Qc.entanglement_assisted_capacity(R), abs=1e-9)
        if js["cap"]["classical"] is not None:
            assert js["cap"]["classical"] == pytest.approx(Qc.holevo_capacity_unital(R), abs=1e-9)
        if k == "ad":
            assert js["ad"] == pytest.approx(Qc.amplitude_damping_quantum_capacity(v), abs=1e-12)


def test_channel_lab_hallway_tomography_and_certificate_match_python(tmp_path):
    from qll.link import channel_tomography as CT
    from qll.link.hallway_channel import hallway_channel
    from scipy import stats

    parts = [{}, {"sipm_dark_hz": 1.5e6}, {"polarizer_extinction": 50, "waveplate_error": 0.04}]
    out = run_channel(tmp_path, """
        const T = require(process.argv[2].replace('lab_channel.js', 'lab_twin.js'));
        const R = C.compose(C.rotation(0.25, [0, 1, 0]), C.depolarizing(0.06));
        const counts = C.simulateCounts(R, 20000, ['H', 'V', 'D', 'A', 'R'], ['X', 'Y', 'Z'], 3);
        return {hall: data.parts.map((p) => C.hallway(p)), eve: C.hallway({}, 1.0), counts, est: C.estimate(counts), cert: C.certify(counts),
                ppf: data.ppf.map(([q, a, b]) => C.betaPpf(q, a, b)), csv: C.tomographyCsv({'H,Z': [3, 1], 'D,X': [2, 2]}, 4)};""",
                      {"parts": parts, "ppf": [[0.9975, 101, 19900], [0.99, 1, 50], [0.5, 30, 70]]})
    for p, js in zip(parts, out["hall"]):
        py = hallway_channel(two_room.TwoRoomParts(**p))
        for key, v in py.items():
            if key == "ptm":
                assert np.allclose(js[key], v, atol=1e-12)
            elif isinstance(v, (bool, np.bool_)):
                assert js[key] == bool(v), key
            else:
                assert js[key] == pytest.approx(v, rel=1e-9, abs=1e-12), (p, key)
    assert out["eve"]["entanglement_breaking"] is True
    counts = {tuple(k.split(",")): tuple(v) for k, v in out["counts"].items()}
    assert np.allclose(out["est"], CT.estimate(counts), atol=1e-12)
    py = CT.certify(counts)
    for key in ("e_z", "e_x", "e_z_upper", "e_x_upper", "fe_lower"):
        assert out["cert"][key] == pytest.approx(py[key], abs=1e-10), key
    assert out["cert"]["certified_quantum"] == py["certified_quantum"]
    assert out["ppf"] == pytest.approx([stats.beta.ppf(q, a, b) for q, a, b in [[0.9975, 101, 19900], [0.99, 1, 50], [0.5, 30, 70]]], abs=1e-10)
    (tmp_path / "t.csv").write_text(out["csv"], encoding="utf-8")
    assert CT.read_log(tmp_path / "t.csv") == {("H", "Z"): (3, 1), ("D", "X"): (2, 2)}


def test_channel_lab_superdense_matches_python(tmp_path):
    from qll.circuits import superdense_photonic as SP

    cases = [[1, 1], [0.94, 0.9], [0.8, 0.6], [0.0, 1.0]]
    out = run_channel(tmp_path, "return data.map(([V, h]) => [C.sdBits(V, h), C.sdBits(V, h, C.BELL), C.sdConfusion(V, h)]);", cases)
    for (V, h), js in zip(cases, out):
        assert js[0] == pytest.approx(SP.bits_per_photon(V, h), abs=1e-12) and js[1] == pytest.approx(SP.bits_per_photon(V, h, SP.BELL), abs=1e-12)
        assert np.allclose(js[2], SP.confusion(V, h), atol=1e-14)


def run_outdoor(tmp_path, body: str, data):
    script = tmp_path / "od.js"
    script.write_text("const O = require(process.argv[2]);\n"
                      "const data = JSON.parse(require('fs').readFileSync(process.argv[3], 'utf8'));\n"
                      "const out = (() => {" + body + "})();\nprocess.stdout.write(JSON.stringify(out));\n", encoding="utf-8")
    (tmp_path / "oddata.json").write_text(json.dumps(data), encoding="utf-8")
    r = subprocess.run([_node(), str(script), str(JS / "lab_outdoor.js"), str(tmp_path / "oddata.json")], capture_output=True, text=True, encoding="utf-8", check=True)
    return json.loads(r.stdout)


def test_outdoor_lab_matches_python(tmp_path):
    from qll.link import outdoor_link as O
    from qll.link import satellite_pass as S
    from qll.qkd.decoy_state import decoy_rate_per_pulse

    cases = [{}, {"distance_m": 1500, "sky_radiance": 1e-3, "receiver": "spad"}, {"distance_m": 50, "pointing_urad": 40, "air_db_per_km": 3, "receiver": "spad"},
             {"distance_m": 800, "tx_waist_m": 0.02, "rx_aperture_m": 0.1, "fov_mrad": 0.5, "filter_nm": 1, "sky_radiance": 0.1}]
    spad = {"sipm_pde": 0.30, "sipm_dark_hz": 300.0, "sipm_afterpulse": 0.005}
    js_cases = [dict(c, receiver=spad if c.get("receiver") == "spad" else {}) for c in cases]
    out = run_outdoor(tmp_path, """return {p: data.c.map((c) => { const r = O.predict(c); delete r.session; delete r.config; return r; }),
        t: data.t.map(([k, t]) => O.atTime(O.PRESETS[k], t)), s: ['micius', 'jinan1'].map((k) => { const s = O.passSummary(O.PRESETS[k]); return [s.duration_s, s.key_bits, s.min_loss_db, s.max_loss_db]; }),
        d: data.d.map((a) => O.decoyRate(...a))};""",
                      {"c": js_cases, "t": [["micius", 0], ["micius", 140], ["jinan1", -90], ["micius", 2000]], "d": [[1e-3, 0.5, 1e-6, 0.01], [1e-5, 0.6, 1e-5, 0.02]]})
    for c, js in zip(cases, out["p"]):
        p = O.OutdoorParts(**{k: v for k, v in c.items() if k != "receiver"}, receiver=O.RECEIVERS[c.get("receiver", "sipm")])
        py = O.predict(p)
        for k, v in py.items():
            if isinstance(v, bool) or k == "key_bits":
                assert js[k] == v, (c, k)
            else:
                assert js[k] == pytest.approx(v, rel=1e-9, abs=1e-15), (c, k)
    for (k, t), js in zip([["micius", 0], ["micius", 140], ["jinan1", -90], ["micius", 2000]], out["t"]):
        py = S.at_time(S.PRESETS[k], t)
        assert js["elevation_deg"] == pytest.approx(py["elevation_deg"], abs=1e-9)
        if py["elevation_deg"] > 0:
            assert js["range_m"] == pytest.approx(py["range_m"], rel=1e-12) and js["loss_db"] == pytest.approx(py["loss_db"], rel=1e-12)
            assert js["key_per_pulse"] == pytest.approx(py["key_per_pulse"], rel=1e-10, abs=1e-18)
        else:
            assert js["key_per_pulse"] == 0
    for k, js in zip(["micius", "jinan1"], out["s"]):
        py = S.pass_summary(S.PRESETS[k])
        assert js == pytest.approx([py["duration_s"], py["key_bits"], py["min_loss_db"], py["max_loss_db"]], rel=1e-9)
    assert out["d"] == pytest.approx([decoy_rate_per_pulse(1e-3, 0.5, 1e-6, 0.01), decoy_rate_per_pulse(1e-5, 0.6, 1e-5, 0.02)], rel=1e-12, abs=1e-20)


def run_frontier(tmp_path, body: str, data):
    script = tmp_path / "fr.js"
    script.write_text("const F = require(process.argv[2]);\n"
                      "const data = JSON.parse(require('fs').readFileSync(process.argv[3], 'utf8'));\n"
                      "const out = (() => {" + body + "})();\nprocess.stdout.write(JSON.stringify(out));\n", encoding="utf-8")
    (tmp_path / "frdata.json").write_text(json.dumps(data), encoding="utf-8")
    r = subprocess.run([_node(), str(script), str(JS / "lab_frontier.js"), str(tmp_path / "frdata.json")], capture_output=True, text=True, encoding="utf-8", check=True)
    return json.loads(r.stdout)


def test_frontier_lab_matches_python(tmp_path):
    from qll.circuits import teleport_delay_cloud as D
    from qll.network import teleport_across as X
    from qll.network.memory_decoherence import MEMORY_TABLE

    delays = [[0, 200, 150, 0, "feedforward"], [90, 200, 150, 0.02, "feedforward"], [300, 120, 200, 0.05, "deferred"], [50, 200, 150, 0, "no_bits"]]
    links = [{}, {"distance_m": 3.844e8, "index": 1.0, "T_mem_s": 60, "bank_s": 5, "f0": 0.9}, {"distance_m": 1e5, "T_mem_s": 1e-3, "eta_mem": 0.5, "p_bsm": 1.0}]
    swaps = [{}, {"distance_m": 2e5, "T_mem_s": 0.01}, {"distance_m": 5e4, "f0": 0.85, "alpha_db_per_km": 0.3, "p_swap": 1.0}]
    out = run_frontier(tmp_path, """return {d: data.d.map(([t, T1, T2, p2, m]) => F.delayFidelity(t, T1, T2, p2, m)), x: data.d.map(([t, T1, T2, p2]) => F.crossoverDelay(T1, T2, p2)),
        l: data.l.map((p) => F.link(p)), s: data.s.map((p) => F.swap(p)), m: Object.fromEntries(Object.entries(F.MEMORIES).map(([k, v]) => [k, [v.lifetime_s, v.efficiency, v.bibkey]])),
        sc: Object.keys(F.SCENARIOS).map((k) => [k, F.SCENARIOS[k]]), table: Object.keys(F.MEMORIES).map((m) => Object.keys(F.SCENARIOS).map((s) => F.forScenario(s, m).beats_classical))};""",
                       {"d": delays, "l": links, "s": swaps})
    for (t, T1, T2, p2, m), js, jx in zip(delays, out["d"], out["x"]):
        assert js == pytest.approx(D.average_fidelity(t, T1, T2, p2, m), abs=1e-14)
        assert jx == pytest.approx(D.crossover_delay_us(T1, T2, p2), abs=1e-9)
    for c, js in zip(links, out["l"]):
        py = X.link(X.Link(**c))
        for k, v in py.items():
            if k != "events":
                assert js[k] == (v if isinstance(v, bool) else pytest.approx(v, rel=1e-12)), (c, k)
    for c, js in zip(swaps, out["s"]):
        for k, v in X.swap(X.Swap(**c)).items():
            assert js[k] == (v if isinstance(v, bool) else pytest.approx(v, rel=1e-12)), (c, k)
    assert out["m"] == {m.name: [m.lifetime_s, m.efficiency, m.bibkey] for m in MEMORY_TABLE}
    assert [[k, list(v)] for k, v in X.SCENARIOS.items()] == [[k, pytest.approx(v, rel=1e-12)] for k, v in out["sc"]]
    tab = X.memory_table()
    assert out["table"] == [[tab[m][s] for s in X.SCENARIOS] for m in tab]


def test_messenger_lab_matches_python(tmp_path):
    from qll.link import authentication as A
    from qll.link import keyed_messaging as K

    script = tmp_path / "ms.js"
    script.write_text("const M = require(process.argv[2]);\n"
                      "const data = JSON.parse(require('fs').readFileSync(process.argv[3], 'utf8'));\n"
                      "const out = {src: Object.fromEntries(Object.entries(M.sources()).map(([k, v]) => [k, v.hourly_bits])),\n"
                      "  plans: data.plans.map(([s, p, o]) => { const r = M.plan(s, p, o); return Object.fromEntries(Object.entries(r).map(([k, v]) => [k, typeof v === 'number' && !isFinite(v) ? 'inf' : v])); }),\n"
                      "  tags: data.tags.map(([k, r, hex]) => M.tag(BigInt(k), BigInt(r), Buffer.from(hex, 'hex')).toString())};\n"
                      "process.stdout.write(JSON.stringify(out));\n", encoding="utf-8")
    plans = [["two rooms (P10)", "one-time pad", {}], ["two buildings at night, 1 km", "one-time pad", {"messages_per_day": 800, "msg_bytes": 1000}],
             ["one satellite pass a night", "hybrid ML-KEM + QKD", {"rekey_every": 10, "messages_per_day": 1e5}], ["one satellite pass a night", "one-time pad", {"messages_per_day": 1e4}],
             ["a Mars lander (key loaded before launch)", "QKD-keyed AES-256-GCM", {"preloaded_bits": 8e12, "distance_m": 4e11}], ["two rooms (P10)", "conventional ECDHE + AES (today)", {}]]
    tags = [[12345678901234567890, 987654321, "68656c6c6f"], [A.P127 - 2, A.P127 - 5, "00" * 31], [7, 0, ""]]
    (tmp_path / "ms.json").write_text(json.dumps({"plans": plans, "tags": [[str(k), str(r), h] for k, r, h in tags]}), encoding="utf-8")
    r = subprocess.run([_node(), str(script), str(JS / "lab_messenger.js"), str(tmp_path / "ms.json")], capture_output=True, text=True, encoding="utf-8", check=True)
    out = json.loads(r.stdout)
    for k, v in K.sources().items():
        assert out["src"][k] == pytest.approx(v["hourly_bits"], rel=1e-10), k
    for (s, p, o), js in zip(plans, out["plans"]):
        for k, v in K.plan(s, p, **o).items():
            if isinstance(v, float) and math.isinf(v):
                assert js[k] == "inf", (s, p, k)
            elif isinstance(v, (bool, str)):
                assert js[k] == v, (s, p, k)
            else:
                assert js[k] == pytest.approx(v, rel=1e-10, abs=1e-12), (s, p, k)
    for (k, pad, h), js in zip(tags, out["tags"]):
        assert int(js) == A.tag(k, pad, bytes.fromhex(h))
