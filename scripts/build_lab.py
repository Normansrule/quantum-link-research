"""Write the data the lab pages read: every tier's real-world build (qll/systems/lab_scenes.py) and the experiment
catalog (qll/systems/experiment_catalog.py) with, for each experiment, the lab tier that models it.

    python scripts/build_lab.py
"""
from __future__ import annotations

import json
import sys
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
OUT = ROOT / "docs" / "lab"

from qll.systems import lab_scenes  # noqa: E402
from qll.systems.experiment_catalog import CATALOG, PHASES  # noqa: E402

PAGE = {"link": "link/", "circuits": "circuits/"}


def catalog() -> dict:
    scenes = lab_scenes.export()
    where: dict[str, list[dict]] = {}
    for group, tiers in scenes.items():
        for t in tiers:
            for exp in t["experiments"]:
                where.setdefault(exp, []).append({"page": PAGE[group], "tier": t["id"], "title": t["title"], "rung": t["rung"]})
    items = []
    for e in CATALOG:
        d = asdict(e)
        d["phases"] = list(e.phases)
        d["lab"] = where.get(e.id, [])
        items.append(d)
    return {"phases": {str(k): v for k, v in PHASES.items()}, "experiments": items}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for name, data in (("scenes.json", lab_scenes.export()), ("catalog.json", catalog())):
        (OUT / name).write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {OUT / 'scenes.json'} and {OUT / 'catalog.json'}")


if __name__ == "__main__":
    main()
