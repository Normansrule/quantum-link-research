"""Fluxonium and transmon spectra against analytic limits, readout budget behaviour, Rydberg blockade scale, CV-QKD below PLOB."""
import math

import pytest

from qll.hardware.rydberg import blockade_radius_um, gate_infidelity, interaction_hz, rydberg_lifetime_blackbody_s
from qll.hardware.superconducting import ReadoutBudget, dispersive_shift, fluxonium_spectrum, transmon_spectrum
from qll.qkd.cv_qkd import cv_rate_per_symbol, max_loss_db
from qll.qkd.plob_bound import plob_bits_per_use

pytestmark = pytest.mark.phase3


def test_transmon_charge_basis_matches_analytic_and_fluxonium_half_flux_is_low():
    E = transmon_spectrum(0.3, 15.0)
    assert E[1] - E[0] == pytest.approx(math.sqrt(8 * 15 * 0.3) - 0.3, rel=0.01)
    assert (E[2] - E[1]) - (E[1] - E[0]) == pytest.approx(-0.3, rel=0.2)             # anharmonicity ~ -E_C
    f_half = fluxonium_spectrum(1.0, 4.0, 1.0, math.pi)
    f_zero = fluxonium_spectrum(1.0, 4.0, 1.0, 0.0)
    assert (f_half[1] - f_half[0]) < 0.2 * (f_zero[1] - f_zero[0])                     # half flux: sweet-spot, low frequency
    assert fluxonium_spectrum(1.0, 4.0, 1.0, math.pi, grid=1201)[1] - fluxonium_spectrum(1.0, 4.0, 1.0, math.pi, grid=1201)[0] == pytest.approx(f_half[1] - f_half[0], rel=1e-3)   # grid-converged


def test_dispersive_readout_budget():
    chi = dispersive_shift(100e6, 1.5e9, -300e6)
    assert chi == pytest.approx(100e6**2 / 1.5e9 * (-300e6) / (1.2e9))          # negative for a transmon (alpha < 0)
    rb = ReadoutBudget(abs(chi), 2 * abs(chi), 5, 0.5, 50e-6)
    tau = rb.optimal_tau_s()
    assert 1e-7 < tau < 1e-5 and rb.separation_fidelity(tau) > 0.95
    worse = ReadoutBudget(abs(chi), 2 * abs(chi), 5, 20.0, 50e-6)                       # HEMT-only chain
    assert worse.separation_fidelity(worse.optimal_tau_s()) < rb.separation_fidelity(tau)
    assert rb.snr(2 * tau) == pytest.approx(math.sqrt(2) * rb.snr(tau))


def test_rydberg_scales():
    R = blockade_radius_um(5e6)
    assert 4 < R < 12 and interaction_hz(R) == pytest.approx(5e6)
    assert blockade_radius_um(5e5) / R == pytest.approx(10 ** (1 / 6))
    b = gate_infidelity(0.25e-6, 150e-6, 5e6, 3.0)
    assert sum(b.values()) < 0.02 and b["finite_blockade"] < b["decay"]
    assert rydberg_lifetime_blackbody_s(150e-6, 4.0) > 1.5 * 150e-6                     # cryogenic enclosure lengthens tau_R


def test_cv_qkd_below_plob_and_noise_threshold():
    for T in (0.9, 0.5, 0.1, 0.01):
        r = cv_rate_per_symbol(T, 0.01)
        assert 0 < r < plob_bits_per_use(T)
    assert cv_rate_per_symbol(0.01, 0.1) == 0.0                                          # 10 % excess noise kills the key
    assert math.isinf(max_loss_db(0.01)) and 5 < max_loss_db(0.1) < 20
    assert cv_rate_per_symbol(0.5, 0.01, V_A=4.0) > cv_rate_per_symbol(0.5, 0.01, V_A=0.5)
