"""The README's and the project tour's pictures tell the truth: the animated SVGs are valid XML, carry the tested
numbers as their final (static) frame, match the landmark files, and every local link and image in both pages resolves.
The shields.io endpoint badges follow the endpoint schema and quote docs/status.json, and the README's tests badge
reads the result the CI run deployed with the website (audit C01, U03), not a count committed to the source tree."""
import json
import re
import sys
import xml.dom.minidom
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
pytestmark = pytest.mark.phase1
sys.path.insert(0, str(ROOT / "scripts"))

NAMES = ("stats", "timescales", "latency", "stack", "marquee", "equations")


@pytest.mark.parametrize("name", NAMES)
def test_readme_art_is_valid_svg_and_referenced(name):
    path = DOCS / "figures" / f"readme_{name}.svg"
    xml.dom.minidom.parseString(path.read_bytes())
    assert f"docs/figures/readme_{name}.svg" in (ROOT / "README.md").read_text(encoding="utf-8")


def test_stats_card_shows_the_tested_numbers_as_its_static_frame():
    import make_readme_art as art

    site = json.loads((DOCS / "site_data.json").read_text(encoding="utf-8"))
    status = json.loads((DOCS / "status.json").read_text(encoding="utf-8"))
    svg = art.stats(site, status)
    h = site["headline"]
    for v, dec in ((h["round_trip_max_min"], 1), (h["one_way_max_min"], 1), (h["bb84_threshold_pct"], 2),
                   (h["chain_crossover_km_1s_memory"], 0), (status["tests"], 0)):
        final = art.fmt(v, dec)
        # the final frame is the one visible by default, so a renderer without animation shows the real value
        assert re.search(rf'visibility="visible"[^>]*>{re.escape(final)}<tspan', svg), final
    assert svg.count('visibility="visible"') == 8                      # exactly one visible frame per tile
    committed = (DOCS / "figures" / "readme_stats.svg").read_text(encoding="utf-8").replace("\r\n", "\n")   # Windows checkouts
    assert art.stats(site, status) == committed


def test_timescales_marks_exactly_the_mars_capable_memories():
    import make_readme_art as art

    site = json.loads((DOCS / "site_data.json").read_text(encoding="utf-8"))
    svg = art.timescales(site)
    assert svg.count("✓ reaches Mars") == site["headline"]["mars_capable_memories"]
    for m in site["memories"]:
        assert m["name"].replace("&", "&amp;") in svg


def test_marquee_has_one_pill_per_landmark_file():
    import make_readme_art as art

    files = sorted((ROOT / "experiments" / "done").glob("[0-9][0-9]_*.md"))
    assert len(art.LANDMARKS) == len(files)
    assert f"{len(files)} LANDMARK EXPERIMENTS" in art.marquee()


@pytest.mark.parametrize("page", ["README.md", "START_HERE.md"])
def test_every_local_link_and_image_in_the_readme_exists(page):
    text = (ROOT / page).read_text(encoding="utf-8")
    targets = re.findall(r'(?:src|href)="([^"]+)"', text) + re.findall(r"\]\(([^)\s]+)\)", text)
    local = {t.split("#")[0] for t in targets if not re.match(r"[a-z]+:", t) and not t.startswith("#")}
    missing = [t for t in sorted(local) if t and not (ROOT / t).exists()]
    assert not missing, missing


def test_endpoint_badges_follow_the_schema_and_quote_status():
    status = json.loads((DOCS / "status.json").read_text(encoding="utf-8"))
    for name in ("version", "tests", "requirements", "references", "learn"):
        b = json.loads((DOCS / "badges" / f"{name}.json").read_text(encoding="utf-8"))
        assert b["schemaVersion"] == 1 and b["label"] and b["message"] and re.fullmatch(r"[0-9A-Fa-f]{6}", b["color"])
    assert json.loads((DOCS / "badges" / "version.json").read_text(encoding="utf-8"))["message"] == f"v{status['version']}"
    assert json.loads((DOCS / "badges" / "requirements.json").read_text(encoding="utf-8"))["message"].startswith(
        f"{status['requirements_verified']}/{status['requirements']}")
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    for name in ("version", "requirements", "references", "learn"):
        assert f"docs%2Fbadges%2F{name}.json" in text
    assert "normansrule.github.io%2Fquantum-link-research%2Fbadges%2Ftests.json" in text      # written by CI at deploy
    assert "docs%2Fbadges%2Ftests.json" not in text
    committed = json.loads((DOCS / "badges" / "tests.json").read_text(encoding="utf-8"))
    assert "passed" not in committed["message"] and "CI" in committed["message"]                # an inventory, never a result


def test_readme_states_its_goal_scope_and_status():
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    head = text.split("## The goal: anywhere, at the speed of light")[0]
    assert text.count("<h1") == 1 and "\n# " not in text.split("<!-- build-guide:start -->")[0]      # one live-text H1
    assert "as close to instantaneous as physics allows" in head and "No signal outruns light" in head
    assert "Development status" in head and "not a production" in head and "model outputs" in head
    for anchor in ("## Run a simulation", "## Explore the labs", "## Build the two-room experiment", "## What is implemented?", "## The website"):
        assert anchor in text
    assert "docs/figures/readme_latency.svg" in text and "docs/figures/lab_latency.jpg" in text


def test_readme_latency_table_is_generated_and_current():
    import build_site_data as B
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    block = text.split("<!-- latency:start -->")[1].split("<!-- latency:end -->")[0]
    assert block.strip() == B.latency_table().strip(), "run python scripts/build_site_data.py"
