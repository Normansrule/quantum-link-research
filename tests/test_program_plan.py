"""The mission plan (systems/program/): every experiment in the repository is catalogued and nothing done so far is
dropped, the schedule and cost arithmetic is right, the bootstrap budget stays small, and the generated documents
are current."""
import importlib.util
import re
from pathlib import Path

import numpy as np
import pytest

from qll.systems import program_plan as P
from qll.systems.experiment_catalog import CATALOG, PHASES, by_id

pytestmark = pytest.mark.phase1
ROOT = Path(__file__).resolve().parents[1]


def _gen():
    spec = importlib.util.spec_from_file_location("build_program_docs", ROOT / "scripts" / "build_program_docs.py")
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod


def test_every_experiment_file_is_in_the_catalog_and_every_path_exists():
    listed = {e.path for e in CATALOG}
    for folder, pattern in (("done", "[0-9][0-9]_*.md"), ("protocols", "P[0-9][0-9]_*.md"), ("proposed", "E[0-9][0-9]_*.md"), ("flagship", "F[0-9]_*.md")):
        for f in (ROOT / "experiments" / folder).glob(pattern):
            assert f.relative_to(ROOT).as_posix() in listed, f"{f.name} is not in the experiment catalog"
    ids = [e.id for e in CATALOG]
    assert len(ids) == len(set(ids))
    for e in CATALOG:
        for p in (e.path, e.twin, e.test, e.procedure):
            assert not p or (ROOT / p).exists(), (e.id, p)
        assert set(e.phases) <= set(PHASES)


def test_replicable_entries_have_a_procedure_a_twin_and_a_test_that_uses_it():
    for e in CATALOG:
        if e.status == "replicable":
            assert e.procedure and e.twin and e.test, e.id
            assert Path(e.twin).stem in (ROOT / e.test).read_text(encoding="utf-8"), (e.id, e.twin, e.test)


def test_pert_and_critical_path_arithmetic():
    m = P.Milestone("X", 1, "x", 2, (100, 400, 1000))
    assert m.pert_mean == pytest.approx((100 + 1600 + 1000) / 6) and m.pert_sd == pytest.approx(150)
    ms = (P.Milestone("A", 1, "a", 2, (0, 0, 0)), P.Milestone("B", 1, "b", 3, (0, 0, 0), ("A",)),
          P.Milestone("C", 1, "c", 10, (0, 0, 0), ("A",)), P.Milestone("D", 1, "d", 1, (0, 0, 0), ("B", "C")))
    s = P.schedule(ms)
    assert s["D"] == (12.0, 13.0) and P.critical_path(ms) == ["A", "C", "D"]
    with pytest.raises(ValueError):
        P.schedule((P.Milestone("A", 1, "a", 1, (0, 0, 0), ("B",)), P.Milestone("B", 1, "b", 1, (0, 0, 0), ("A",))))


def test_monte_carlo_matches_the_triangular_mean():
    ms = (P.Milestone("A", 1, "a", 1, (100, 200, 600)), P.Milestone("B", 1, "b", 1, (0, 50, 100)))
    mc = P.monte_carlo(ms, n=200_000, seed=1)[1]
    assert mc["mean"] == pytest.approx((100 + 200 + 600) / 3 + 50, rel=0.01)
    assert mc["p50"] < mc["p80"]


def test_plan_is_consistent_and_cheap_where_it_must_be():
    ids = {m.id for m in P.MILESTONES}
    for m in P.MILESTONES:
        assert set(m.after) <= ids and m.cost[0] <= m.cost[1] <= m.cost[2] and m.verify, m.id
        for x in m.builds_on:
            by_id(x)                                                          # every reference resolves
    s = P.schedule()
    for m in P.MILESTONES:
        for p in m.after:
            assert s[p][1] <= s[m.id][0]
    assert P.bootstrap_budget(1)["likely"] < 1000                             # sharing quantum states between rooms: under $1,000 likely
    assert P.bootstrap_budget(2)["likely"] < 2000                             # entanglement between rooms with a borrowed source
    assert all(m.outside for m in P.MILESTONES if m.cost[1] > 5000)          # nothing large is ever out of pocket
    assert {g.after_phase for g in P.GATES} == {0, 1, 2, 3}
    assert P.serial_weeks(2) >= P.bootstrap_budget(2)["weeks"]


def test_no_milestone_depends_on_signalling_through_collapse():
    text = " ".join(m.name + " " + m.verify for m in P.MILESTONES).lower()
    assert "faster than light" not in text and "superluminal" not in text
    assert "bounded" in by_id("P11").role or "bound" in by_id("P11").role


def test_generated_program_documents_are_current():
    g = _gen()
    for name, fn in (("01_phases_and_milestones.md", g.milestones_md), ("02_research_foundation.md", g.foundation_md)):
        assert (ROOT / "systems" / "program" / name).read_text(encoding="utf-8") == fn(), f"rerun scripts/build_program_docs.py ({name})"


def test_program_documents_link_to_files_that_exist():
    for md in (ROOT / "systems" / "program").glob("*.md"):
        for ref in re.findall(r"\]\(([^)#]+)\)", md.read_text(encoding="utf-8")):
            if ref.startswith("http"):
                continue
            assert (md.parent / ref).resolve().exists(), f"{md.name}: {ref}"


def test_trade_study_totals_are_the_weighted_sums():
    text = (ROOT / "systems" / "program" / "06_risks_and_trades.md").read_text(encoding="utf-8")
    tables = 0
    for block in re.split(r"\n### ", text)[1:]:
        lines = [l for l in block.splitlines() if l.startswith("|")]
        weights = [float(w) for w in re.findall(r"\((0\.\d+)\)", lines[0])]
        assert abs(sum(weights) - 1) < 1e-9, block.splitlines()[0]
        for row in lines[2:]:
            cells = [c.strip() for c in row.strip("|").split("|")]
            scores = [float(re.match(r"\d", c) and c[0]) for c in cells[1:1 + len(weights)]]
            total = float(cells[-1].strip("*"))
            assert total == pytest.approx(round(sum(w * x for w, x in zip(weights, scores)) + 1e-9, 1), abs=1e-9), row
        tables += 1
    assert tables == 5


def test_hand_written_program_numbers_match_the_plan():
    readme = (ROOT / "systems" / "program" / "README.md").read_text(encoding="utf-8")
    for ph in (1, 2, 3, 4, P.STARTUP):
        assert f"${P.phase_cost(ph)['likely']:,.0f}" in readme, ph
    assert f"about ${P.phase_cost(1)['likely']:,.0f} likely" in (ROOT / "README.md").read_text(encoding="utf-8")
    req = (ROOT / "systems" / "program" / "03_requirements_and_verification.md").read_text(encoding="utf-8")
    verified_by = set(re.findall(r"\| (M\d\.\d|S\d) \|\n", req))
    ids = {m.id for m in P.MILESTONES}
    assert verified_by <= ids and ids <= verified_by, sorted(ids ^ verified_by)
