"""AFC memory, frequency conversion, and Purcell factor against their closed-form limits."""
import math

import pytest

from qll.channels.frequency_conversion import Converter, internal_efficiency, pump_power_for_full_conversion_W, target_wavelength_m
from qll.hardware.nv_node import cooperativity, purcell_factor
from qll.network.afc_memory import AfcMemory, afc_efficiency_backward, afc_efficiency_forward, optimal_optical_depth_forward, temporal_modes

pytestmark = pytest.mark.phase3


def test_afc_limits():
    for F in (5.0, 10.0, 50.0):
        d = optimal_optical_depth_forward(F)
        assert afc_efficiency_forward(d, F) >= afc_efficiency_forward(1.5 * d, F) and afc_efficiency_forward(d, F) >= afc_efficiency_forward(0.5 * d, F)
    assert afc_efficiency_forward(2 * 1e4, 1e4) == pytest.approx(4 * math.exp(-2), rel=1e-3)      # 54 % forward limit
    assert afc_efficiency_backward(1e5, 1e4) == pytest.approx(1.0, abs=2e-3) and afc_efficiency_backward(1e5, 1e4) > afc_efficiency_forward(2e4, 1e4)
    m = AfcMemory(20.0, 10.0, 1e6, 6 * 3600)
    assert m.echo_time_s == pytest.approx(1e-6) and temporal_modes(10.0) == 5 and 0.4 < m.efficiency() < 0.55
    with pytest.raises(ValueError):
        afc_efficiency_forward(1.0, 0.0)


def test_frequency_conversion_law_and_wavelengths():
    assert target_wavelength_m(637e-9, 1064e-9) == pytest.approx(1588e-9, rel=2e-3)              # NV -> telecom [dreau2018]
    assert target_wavelength_m(737e-9, 1405e-9) == pytest.approx(1550e-9, rel=2e-3)
    with pytest.raises(ValueError):
        target_wavelength_m(1550e-9, 1064e-9)
    P = pump_power_for_full_conversion_W(1.0, 4.0)
    assert 0.05 < P < 0.5 and internal_efficiency(P, 1.0, 4.0) == pytest.approx(1.0)
    assert internal_efficiency(P / 4, 1.0, 4.0) == pytest.approx(0.5)                              # sin^2(pi/4)
    c = Converter()
    assert c.external_efficiency(P) == pytest.approx(0.7 * 0.8)
    assert c.qber_floor(0.9 * P, 1e5, 1e-9, 1e8) < c.qber_floor(0.1 * P, 1e5, 1e-9, 1e8) * 5   # rate/noise trade exists
    # SNR = eff / noise falls monotonically with pump
    assert c.external_efficiency(0.2 * P) / c.noise_rate_hz(0.2 * P) > c.external_efficiency(0.9 * P) / c.noise_rate_hz(0.9 * P)


def test_purcell_and_cooperativity():
    assert purcell_factor(1e4, 1.0) == pytest.approx(3 / (4 * math.pi**2) * 1e4)
    assert 500 < purcell_factor(1e4, 1.0) < 1000                                                   # diamond nanocavity scale
    assert cooperativity(purcell_factor(1e4, 1.0)) > 10                                            # strong spin-photon interface
