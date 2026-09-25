"""Cryogenic wiring budget behaves physically; trapped-ion gate scalings hold."""
import math

import pytest

from qll.hardware.cryo_wiring import COOLING_POWER_W, Line, active_load_w, max_lines, passive_load_w, total_load_w
from qll.hardware.trapped_ion import lamb_dicke, ms_gate_time_s, ms_infidelity

pytestmark = pytest.mark.phase3


def test_wiring_budget_structure():
    d = Line()
    p = passive_load_w(d)
    assert p["50K"] > p["4K"] > p["still"] > p["cold_plate"] > p["mxc"]                      # conduction falls stage by stage
    a = active_load_w(d)
    assert sum(a.values()) == pytest.approx(d.input_power_w * (1 - 1e-4), rel=1e-6)          # 40 dB total: 99.99 % dissipated
    assert a["4K"] == pytest.approx(d.input_power_w * 0.99)
    n_ss, stage = max_lines(d)
    n_nbti, _ = max_lines(Line(cable="nbti"))
    assert n_nbti > n_ss and stage in ("cold_plate", "mxc", "still")                         # a cold stage limits; NbTi helps
    hot = Line(input_power_w=1e-3)                                                             # 0 dBm average drive
    assert max_lines(hot)[0] < n_ss
    tot = total_load_w([d] * 100)
    assert all(tot[s] < COOLING_POWER_W[s] for s in tot) and tot["mxc"] > 0


def test_ion_gate_scalings():
    eta = lamb_dicke(729e-9, 40, 1.5e6)
    assert 0.05 < eta < 0.12
    assert lamb_dicke(729e-9, 40, 6e6) == pytest.approx(eta / 2)                              # eta ∝ 1/sqrt(omega_z)
    assert lamb_dicke(729e-9, 9, 1.5e6) == pytest.approx(eta * math.sqrt(40 / 9))              # ∝ 1/sqrt(m)
    eta_r = lamb_dicke(397e-9, 40, 1.5e6, geometry=math.sqrt(2))
    t = ms_gate_time_s(eta_r, 200e3)
    assert 5e-6 < t < 50e-6 and ms_gate_time_s(eta_r, 400e3) == pytest.approx(t / 2)
    b = ms_infidelity(eta_r, 200e3, 100.0, 1.5e6, 20.0)
    assert b["heating"] == pytest.approx(100.0 * t) and sum(v for k, v in b.items() if k != "gate_time_s") < 0.05
    slow = ms_infidelity(eta_r, 50e3, 100.0, 1.5e6, 20.0)
    assert slow["heating"] > b["heating"] and slow["off_resonant"] < b["off_resonant"]        # the speed trade
