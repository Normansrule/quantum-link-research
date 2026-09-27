"""The simulated CZ gate against its analytic limits: no coupling gives no conditional phase; a slow pulse follows the
adiabatic integral of the static ZZ, with a residue that falls as 1/duration; the calibrated default is a CZ with
negligible leakage; and shaping the same ramps in frequency instead of mixing angle leaks."""
from dataclasses import replace

import numpy as np
import pytest

from qll.hardware.cz_gate import CZPulse, flat_time_for_cz

pytestmark = pytest.mark.phase1


def _wrap(x: float) -> float:
    return float(np.angle(np.exp(1j * x)))


def test_no_coupling_means_no_conditional_phase_and_no_leakage():
    p = CZPulse(g=0.0, t_ramp=5.0, t_flat=5.0)
    assert abs(p.conditional_phase(0.02)) < 1e-9
    assert abs(p.leakage(0.02)) < 1e-12
    assert abs(p.adiabatic_phase()) < 1e-12


def test_slow_pulse_follows_the_adiabatic_integral_with_a_1_over_T_residue():
    residues = []
    for tr in (60.0, 120.0):
        p = CZPulse(g=0.010, w1_int=5.23, t_ramp=tr, t_flat=0.0)
        assert p.leakage(0.02) < 1e-5
        residues.append(_wrap(p.conditional_phase(0.02) - p.adiabatic_phase()))
    assert abs(residues[0]) < 0.02 * p.adiabatic_phase() / 2          # within 1 % of the phase at T = 120 ns
    assert residues[1] == pytest.approx(residues[0] / 2, rel=0.1)     # super-adiabatic correction ~ 1/T


def test_calibrated_default_is_a_cz_with_negligible_leakage():
    p = CZPulse()
    assert _wrap(p.conditional_phase() - np.pi) == pytest.approx(0.0, abs=2e-3)
    assert p.leakage() < 1e-3
    assert p.average_fidelity() > 0.9995
    assert p.duration == pytest.approx(59.49, abs=0.01)
    assert flat_time_for_cz(p) == pytest.approx(p.t_flat, abs=0.02)


def test_frequency_shaped_ramps_leak_where_angle_shaped_ramps_do_not():
    from qll.hardware.cz_gate import FREQUENCY_SHAPED_FLAT_NS as FREQ_FLAT

    good = CZPulse()
    bad = replace(good, shape="frequency")
    tf = flat_time_for_cz(bad)
    assert tf == pytest.approx(FREQ_FLAT, abs=0.05)
    bad = replace(bad, t_flat=tf)
    assert _wrap(bad.conditional_phase() - np.pi) == pytest.approx(0.0, abs=2e-3)
    assert bad.leakage() > 100 * good.leakage()
    assert bad.average_fidelity() < good.average_fidelity()


def test_fidelity_of_an_idle_pulse_to_cz_is_the_textbook_value():
    # no interaction: the block is the identity up to local phases, and F(I, CZ) = (4 + |Tr(CZ)|^2) / 20 = 0.4
    assert CZPulse(g=0.0, t_ramp=5.0, t_flat=0.0).average_fidelity(0.02) == pytest.approx(0.4, abs=1e-9)


def test_rejects_complex_and_nonsense_parameters():
    with pytest.raises(TypeError):
        CZPulse(g=0.02 + 0.0j)
    with pytest.raises(ValueError):
        CZPulse(t_ramp=0.0)
    with pytest.raises(ValueError):
        CZPulse(shape="square").w1(1.0)
