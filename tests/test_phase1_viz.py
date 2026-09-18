"""Every explorer must render headlessly and write a non-empty SVG."""
import runpy
import sys

import pytest

pytestmark = pytest.mark.phase1


@pytest.mark.parametrize("name", ["thermal_explorer", "link_loss_explorer", "light_time_explorer",
                                  "qkd_rate_explorer", "stack_map", "bloch_sphere", "rabi_ramsey",
                                  "transmon_levels", "overview_storyboard", "repo_map", "flagship_overview",
                                  "repeater_rate_explorer", "mars_light_time_cycle", "modality_radar", "surface_code_lattice"])
def test_explorer_renders_headless(name, tmp_path, monkeypatch):
    out = tmp_path / f"{name}.svg"
    monkeypatch.setattr(sys, "argv", [name, "--save", str(out)])
    runpy.run_module(f"qll.viz.{name}", run_name="__main__")
    assert out.exists() and out.stat().st_size > 5_000
