"""The real-world builds on the lab pages agree with the protocols they come from: costs add up to the protocol's bill
of materials, every part is paid for by a row that exists, every experiment named is in the catalog, every procedure
and command points at something real, and the committed JSON is what the generator writes."""
import json
import re
import sys
from pathlib import Path

import pytest

from qll.systems import lab_scenes as L
from qll.systems.experiment_catalog import CATALOG

pytestmark = pytest.mark.phase1
ROOT = Path(__file__).resolve().parents[1]
TIERS = L.link_tiers() + L.circuit_tiers()


def test_two_room_bill_of_materials_matches_P10_exactly():
    t = L.two_room()
    assert L.bom_total(t) == (530, 1180)
    text = (ROOT / t.procedure).read_text()
    for item, _, lo, hi in t.bom:
        assert f"${lo:,.0f}–{hi:,.0f}" in text, item
    assert "Four non-polarizing beamsplitters (three to combine the four diodes" in text


def test_tier1_items_fit_inside_the_stated_range():
    lo, hi = L.bom_total(L.tier1())
    assert 40 <= lo and hi <= 120


def test_every_part_is_paid_for_by_a_real_row_and_stage():
    for t in TIERS:
        ids = [p.id for p in t.parts]
        assert len(ids) == len(set(ids)), t.id
        for p in t.parts:
            assert p.bom is None or 0 <= p.bom < len(t.bom), (t.id, p.id)
            assert 0 <= p.stage <= len(t.stages), (t.id, p.id)
            assert p.param == "" or p.param in {s.key for s in t.sliders}, (t.id, p.id, p.param)
        for b in t.beams:
            assert len(b.points) >= 2 and 0 <= b.stage <= len(t.stages)
        for s in t.sliders:
            assert s.lo <= s.value <= s.hi and s.step > 0, (t.id, s.key)


def test_every_row_pays_for_at_least_one_part():
    for t in L.link_tiers():
        used = {p.bom for p in t.parts}
        for i, row in enumerate(t.bom):
            assert i in used, (t.id, row[0])


def test_two_room_geometry_is_the_twins_path():
    parts = {p.id: p for p in L.two_room().parts}
    assert parts["sipmZ0"].pos[0] - parts["diodeH"].pos[0] == pytest.approx(10.9, abs=0.1)      # the benches are 10 m apart
    assert parts["tableB"].pos[0] - parts["tableA"].pos[0] == pytest.approx(10.0)


def test_experiments_procedures_and_commands_exist():
    ids = {e.id for e in CATALOG}
    for t in TIERS:
        assert set(t.experiments) <= ids, t.id
        assert (ROOT / t.procedure).exists(), t.procedure
        for cmd in t.commands.values():
            for path in re.findall(r"(?:experiments|systems|scripts)/[\w/.-]+\.(?:py|json)", cmd):
                assert (ROOT / path).exists(), path
            for mod in re.findall(r"python -m ([\w.]+)", cmd):
                assert (ROOT / (mod.replace(".", "/") + ".py")).exists(), mod


def test_main_experiment_has_every_build_stage_populated():
    t = L.two_room()
    stages = {p.stage for p in t.parts} | {b.stage for b in t.beams}
    assert stages >= set(range(1, 9)) - {3}             # stage 3 reuses the Tier 1 rig, shown on the starter tier
    kinds = {p.kind for p in t.parts}
    assert {"laser", "polarizer", "nd", "bs", "pbs", "hwp", "sipm", "fpga", "laptop", "mediaconv", "box"} <= kinds


def test_committed_json_is_current():
    sys.path.insert(0, str(ROOT / "scripts"))
    import build_lab
    assert json.loads((ROOT / "docs" / "lab" / "scenes.json").read_text()) == json.loads(json.dumps(L.export()))
    cat = json.loads((ROOT / "docs" / "lab" / "catalog.json").read_text())
    assert [e["id"] for e in cat["experiments"]] == [e.id for e in CATALOG]
    assert cat == json.loads(json.dumps(build_lab.catalog(), ensure_ascii=False))
    assert {x["tier"] for x in next(e for e in cat["experiments"] if e["id"] == "P10")["lab"]} == {"two_room"}
