"""The website and README cannot drift from the code: site data regenerates to the committed values, the JavaScript
ephemeris matches the Python one, every script parses, every local link resolves, and the banner is valid SVG."""
import json
import re
import shutil
import subprocess
import sys
import xml.dom.minidom
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
pytestmark = pytest.mark.phase1
sys.path.insert(0, str(ROOT / "scripts"))


def test_site_data_matches_the_code():
    from build_site_data import compute_data
    live = json.loads(json.dumps(compute_data(), default=float))
    saved = json.loads((DOCS / "site_data.json").read_text())
    for k, v in live["headline"].items():
        assert saved["headline"][k] == pytest.approx(v, rel=1e-9), k
    assert [m["name"] for m in saved["memories"]] == [m["name"] for m in live["memories"]]


def test_readme_numbers_block_is_generated_and_current():
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    block = text.split("<!-- numbers:start -->")[1].split("<!-- numbers:end -->")[0]
    h = json.loads((DOCS / "site_data.json").read_text())["headline"]
    assert f"{h['round_trip_max_min']:.1f} min" in block and f"{h['bb84_threshold_pct']:.2f} %" in block


node = shutil.which("node")


@pytest.mark.skipif(node is None, reason="node not installed")
def test_js_ephemeris_matches_python(tmp_path):
    script = tmp_path / "check.js"
    script.write_text(
        "const fs=require('fs');const E=require(process.argv[2]);const d=JSON.parse(fs.readFileSync(process.argv[3],'utf8'));"
        "E.configure(d);let w=0;d.ephemeris_check.t_days.forEach((t,i)=>{const p=d.ephemeris_check.range_m[i];w=Math.max(w,Math.abs(E.rangeM(t)-p)/p)});console.log(w);")
    out = subprocess.run([node, str(script), str(DOCS / "js" / "ephemeris.js"), str(DOCS / "site_data.json")], capture_output=True, text=True, check=True)
    assert float(out.stdout) < 1e-9


@pytest.mark.skipif(node is None, reason="node not installed")
def test_all_site_javascript_parses(tmp_path):
    for js in (DOCS / "js").glob("*.js"):
        src = js.read_text()
        target = tmp_path / (js.stem + (".mjs" if re.search(r"^\s*import ", src, re.M) else ".js"))
        target.write_text(src)
        r = subprocess.run([node, "--check", str(target)], capture_output=True, text=True)
        assert r.returncode == 0, f"{js.name}: {r.stderr}"
    for page in (DOCS / "mars" / "index.html", DOCS / "teleport" / "index.html", DOCS / "monitor" / "index.html"):
        for i, body in enumerate(re.findall(r"<script>(.*?)</script>", page.read_text(), re.S)):
            f = tmp_path / f"inline_{i}.js"; f.write_text(body)
            r = subprocess.run([node, "--check", str(f)], capture_output=True, text=True)
            assert r.returncode == 0, r.stderr


@pytest.mark.parametrize("page", ["index.html", "mars/index.html", "teleport/index.html", "monitor/index.html"])
def test_local_links_resolve(page):
    path = DOCS / page
    html = path.read_text()
    for ref in re.findall(r'(?:href|src)="([^"]+)"', html):
        if ref.startswith(("http", "#", "data:", "mailto:")) or ref.endswith("/") and ref.startswith("http"):
            continue
        target = (path.parent / ref.split("#")[0]).resolve()
        if ref.endswith("/"):
            target = target / "index.html"
        assert target.exists(), f"{page}: {ref}"


def test_banner_is_valid_svg_with_computed_numbers():
    svg = (DOCS / "figures" / "hero_banner.svg").read_text()
    xml.dom.minidom.parseString(svg)
    h = json.loads((DOCS / "site_data.json").read_text())["headline"]
    assert f"{h['round_trip_max_min']:.1f}-min" in svg and "<animateMotion" in svg


@pytest.mark.skipif(node is None, reason="node not installed")
def test_js_teleportation_matches_qiskit(tmp_path):
    pytest.importorskip("qiskit")
    import numpy as np
    from qiskit import QuantumCircuit
    from qiskit.quantum_info import Statevector
    script = tmp_path / "tp.js"
    script.write_text("const T=require(process.argv[2]);const out=[];for(const m of [[0,0],[0,1],[1,0],[1,1]]){const r=T.steps([0.6,0],[0,0.8],m[0],m[1]);"
                      "out.push({s2:r.s2,p:r.p,F:T.fidelity(r.bob,[0.6,0],[0,0.8])})}console.log(JSON.stringify(out));")
    res = json.loads(subprocess.run([node, str(script), str(DOCS / "js" / "teleport_core.js")], capture_output=True, text=True, check=True).stdout)
    qc = QuantumCircuit(3); qc.initialize([0.6, 0.8j], 0); qc.h(1); qc.cx(1, 2); qc.cx(0, 1); qc.h(0)
    sv = Statevector(qc).data
    perm = [((i >> 2) & 1) + 2 * ((i >> 1) & 1) + 4 * (i & 1) for i in range(8)]     # ours: 4 q0 + 2 q1 + q2
    ours = np.array([complex(*a) for a in res[0]["s2"]])
    assert np.abs(ours - sv[perm]).max() < 1e-12
    for r in res:
        assert r["p"] == pytest.approx(0.25) and r["F"] == pytest.approx(1.0)


@pytest.mark.skipif(node is None, reason="node not installed")
def test_js_buffer_rule_matches_messenger(tmp_path):
    from qll.app.messenger import required_buffer_bytes
    cases = [(0.0, 1.0e11, 32, 1.0, 1 / 60), (100.0, 4.0e11, 32, 2.0, 0.5), (1e4, 2.2e11, 64, 1.0, 1.0)]
    script = tmp_path / "b.js"
    script.write_text("const L=require(process.argv[2]);const c=JSON.parse(process.argv[3]);console.log(JSON.stringify(c.map(a=>L.requiredBufferBytes(...a))));")
    out = json.loads(subprocess.run([node, str(script), str(DOCS / "js" / "linkmodel.js"), json.dumps(cases)], capture_output=True, text=True, check=True).stdout)
    for a, v in zip(cases, out):
        assert v == pytest.approx(required_buffer_bytes(*a[:3], sessions_per_message=a[3], messages_per_s=a[4]), rel=1e-12)


def test_pages_need_no_cdn_and_vendored_files_exist():
    for page in ("index.html", "mars/index.html", "teleport/index.html", "monitor/index.html"):
        html = (DOCS / page).read_text()
        assert "cdn.jsdelivr" not in html and "unpkg.com" not in html, page
    for f in ("three/three.module.js", "three/three.core.js", "three/addons/controls/OrbitControls.js", "gsap/gsap.min.js",
              "gsap/ScrollTrigger.min.js", "katex/katex.min.js", "katex/katex.min.css", "katex/contrib/auto-render.min.js", "three/LICENSE", "katex/LICENSE"):
        assert (DOCS / "vendor" / f).exists(), f
    assert len(list((DOCS / "vendor" / "katex" / "fonts").glob("*.woff2"))) >= 10


@pytest.mark.skipif(node is None, reason="node not installed")
def test_js_repeater_model_matches_python(tmp_path):
    from qll.network.repeater_chain import all_photonic_chain, crossover_distance_km, direct_rate_hz, memory_chain
    from qll.network.repeater_montecarlo import mean_chain_time_s
    from qll.qkd.plob_bound import plob_bits_per_use
    from qll.channels.fiber_loss import transmittance

    grid = [(L, n, T) for L in (50.0, 200.0, 393.0, 800.0, 1600.0) for n in (0, 1, 2, 3) for T in (0.01, 1.0, 10.0)]
    script = tmp_path / "rep.js"
    script.write_text(
        "const R=require(process.argv[2]);const g=JSON.parse(process.argv[3]);"
        "console.log(JSON.stringify({chain:g.map(([L,n,T])=>R.memoryChain(L,n,T)),direct:g.map(([L])=>R.directRate(L)),"
        "plob:g.map(([L])=>R.plobRate(L)),ap:g.map(([L,n])=>R.allPhotonic(L,Math.pow(2,n))),x:R.crossover(3,1.0),"
        "mc:R.meanRunTime(800,3,{},8000,3)}))")
    out = json.loads(subprocess.run([node, str(script), str(DOCS / "js" / "repeater_core.js"), json.dumps(grid)],
                                    capture_output=True, text=True, check=True).stdout)
    for k, (L, n, T) in enumerate(grid):
        py = memory_chain(L, n, T)
        js = out["chain"][k]
        assert js["rate_hz"] == pytest.approx(py.rate_hz, rel=1e-12, abs=0)
        assert js["fidelity_fraction"] == pytest.approx(py.fidelity_fraction, rel=1e-12)
        assert js["hold_time_s"] == pytest.approx(py.hold_time_s, rel=1e-12)
        assert out["direct"][k] == pytest.approx(direct_rate_hz(L), rel=1e-12)
        assert out["plob"][k] == pytest.approx(1e9 * plob_bits_per_use(transmittance(L)), rel=1e-12)
        assert out["ap"][k] == pytest.approx(all_photonic_chain(L, 2**n), rel=1e-12)
    assert out["x"] == pytest.approx(crossover_distance_km(3, 1.0), rel=1e-12)
    # the page's animation samples the same process as the tested Python Monte Carlo
    assert out["mc"] == pytest.approx(mean_chain_time_s(800.0, 3, 20000, seed=5)[0], rel=0.03)


@pytest.mark.skipif(node is None, reason="node not installed")
def test_js_purified_chain_matches_python(tmp_path):
    from qll.network.purified_chain import best_useful_chain, minimum_useful_memory_s, purified_chain

    cases = [(L, n, T, r) for L in (200.0, 600.0, 1500.0) for n in (1, 3) for T in (1.0, 100.0)
             for r in ([0] * (n + 1), [1] + [0] * n, [2] * (n + 1))]
    best = [(L, T) for L in (393.0, 600.0, 1000.0, 2000.0) for T in (1.0, 10.0, 100.0, 3600.0)]
    script = tmp_path / "pur.js"
    script.write_text(
        "const R=require(process.argv[2]);const c=JSON.parse(process.argv[3]);const b=JSON.parse(process.argv[4]);"
        "console.log(JSON.stringify({pc:c.map(([L,n,T,r])=>R.purifiedChain(L,n,T,r)),"
        "best:b.map(([L,T])=>{const x=R.bestUsefulChain(L,T);return x&&[x.rate_hz,x.teleport_fidelity,x.n_segments,x.rounds]}),"
        "tmin:[500,1000,2000].map((L)=>R.minimumUsefulMemory(L))}))")
    out = json.loads(subprocess.run([node, str(script), str(DOCS / "js" / "repeater_core.js"), json.dumps(cases), json.dumps(best)],
                                    capture_output=True, text=True, check=True).stdout)
    for (L, n, T, r), js in zip(cases, out["pc"]):
        py = purified_chain(L, n, T, r)
        for key in ("rate_hz", "fidelity_fraction", "hold_time_s", "pairs_per_output"):
            assert js[key] == pytest.approx(getattr(py, key), rel=1e-12, abs=0), (L, n, T, r, key)
    for (L, T), js in zip(best, out["best"]):
        py = best_useful_chain(L, T)
        assert (js is None) == (py is None)
        if py is not None:
            assert js[0] == pytest.approx(py.rate_hz, rel=1e-12) and js[2] == py.n_segments and tuple(js[3]) == py.rounds
    for L, js in zip((500.0, 1000.0, 2000.0), out["tmin"]):
        assert js == pytest.approx(minimum_useful_memory_s(L), rel=1e-12)


@pytest.mark.skipif(node is None, reason="node not installed")
def test_js_qec_checks_agree_with_every_decoded_shot(tmp_path):
    script = tmp_path / "qec.js"
    script.write_text(
        "const Q=require(process.argv[2]);const D=JSON.parse(require('fs').readFileSync(process.argv[3],'utf8')).qec;let n=0,bad=[];"
        "for(const [d,c] of Object.entries(D.codes))for(const [p,shots] of Object.entries(c.shots))shots.forEach((s,i)=>{n++;"
        "const r=Q.checkShot(+d,c.plaquettes,s);if(!r.syndromeMatches||!r.residualClean||r.logicalError!==s.logical_error)bad.push([d,p,i]);});"
        "console.log(JSON.stringify({n,bad}))")
    out = json.loads(subprocess.run([node, str(script), str(DOCS / "js" / "qec_core.js"), str(DOCS / "site_data.json")],
                                    capture_output=True, text=True, check=True).stdout)
    assert out["n"] == 3 * 5 * 16 and out["bad"] == []


@pytest.mark.skipif(node is None, reason="node not installed")
def test_js_mars_budget_matches_python(tmp_path):
    from dataclasses import replace

    from qll.systems.mars_budget import MarsLinkDesign, budget

    designs = [{}, {"architecture": "relay_dual"}, {"tx_waist_m": 2.0, "rx_diameter_mars_m": 10.0, "pointing_rad": 3e-7},
               {"memory": "Eu:YSO nuclear spin, 13.1 h", "modes": 1, "f0": 0.99}, {"wavelength_m": 810e-9, "earth_elevation_deg": 25.0}]
    days = [0.0, 150.0, 400.0, 538.0, 700.0]
    script = tmp_path / "budget.js"
    script.write_text(
        "const fs=require('fs');const E=require(process.argv[2]);const B=require(process.argv[3])(E);"
        "const data=JSON.parse(fs.readFileSync(process.argv[4],'utf8'));E.configure(data);const ds=JSON.parse(process.argv[5]);const ts=JSON.parse(process.argv[6]);"
        "console.log(JSON.stringify(ds.map(d=>ts.map(t=>{const b=B.budget(d,t,data.memories);"
        "return [b.stages.map(s=>s.rate_per_s),b.teleport_fidelity,b.key_bits_per_pair,b.storage_s];}))))")
    out = json.loads(subprocess.run([node, str(script), str(DOCS / "js" / "ephemeris.js"), str(DOCS / "js" / "budget_core.js"),
                                     str(DOCS / "site_data.json"), json.dumps(designs), json.dumps(days)],
                                    capture_output=True, text=True, check=True).stdout)
    for d, rows in zip(designs, out):
        for t, (rates, F, key, ts) in zip(days, rows):
            b = budget(replace(MarsLinkDesign(), **d), t)
            assert rates == pytest.approx([s.rate_per_s for s in b.stages], rel=1e-9, abs=1e-300), (d, t)
            assert F == pytest.approx(b.teleport_fidelity, rel=1e-9) and ts == pytest.approx(b.storage_s, rel=1e-9)
            assert key == pytest.approx(b.key_bits_per_pair, rel=1e-6, abs=1e-12)
