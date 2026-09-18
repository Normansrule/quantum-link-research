"""Regenerate every README figure headlessly: python scripts/make_figures.py"""
from __future__ import annotations

import runpy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIGS = ["thermal_explorer", "link_loss_explorer", "light_time_explorer", "qkd_rate_explorer", "stack_map",
        "bloch_sphere", "rabi_ramsey", "transmon_levels", "overview_storyboard", "repo_map"]

if __name__ == "__main__":
    (ROOT / "docs" / "figures").mkdir(parents=True, exist_ok=True)
    for name in FIGS:
        sys.argv = [name, "--save", str(ROOT / "docs" / "figures" / f"{name}.svg")]
        runpy.run_module(f"qll.viz.{name}", run_name="__main__")
