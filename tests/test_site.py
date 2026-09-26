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
