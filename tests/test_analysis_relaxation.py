"""The P02 pipeline recovers Rabi, Ramsey, echo, T1, and the T1(T) phonon model from synthetic data,
and the Phase 1 thermal law is shown to fail for an NV spin (the point of E2)."""
import math

import numpy as np
import pytest

from qll.analysis.relaxation_fit import (echo_model, fit_echo, fit_rabi, fit_ramsey, fit_t1, fit_t1_vs_temperature, inverse_t1_vs_T,
                                         rabi_model, ramsey_model, synthetic_t1_vs_temperature, t1_model, thermal_model_prediction)

pytestmark = pytest.mark.phase1
RNG = np.random.default_rng(4)


def test_rabi_ramsey_echo_t1_recovered():
    t = np.linspace(0, 2e-6, 400)
    y = rabi_model(t, 0.03, 2 * math.pi * 2e6, 5e-6, 1.0) + RNG.normal(0, 1e-3, t.size)
    f = fit_rabi(t, y); assert f.params["pi_time_s"] == pytest.approx(0.25e-6, rel=0.02)
    tau = np.linspace(0, 6e-6, 400)
    y = ramsey_model(tau, 0.015, 2e-6, 2 * math.pi * 1e6, 0.0, 1.0) + RNG.normal(0, 5e-4, tau.size)
    f = fit_ramsey(tau, y); assert f.params["T2star_s"] == pytest.approx(2e-6, rel=0.1) and f.params["detuning_rad_s"] == pytest.approx(2 * math.pi * 1e6, rel=0.02)
    te = np.linspace(0, 400e-6, 300)
    y = echo_model(te, 0.03, 100e-6, 2.0, 1.0) + RNG.normal(0, 5e-4, te.size)
    f = fit_echo(te, y); assert f.params["T2_s"] == pytest.approx(100e-6, rel=0.05) and 1.6 < f.params["n"] < 2.4
    tt = np.linspace(0, 10e-3, 200)
    y = t1_model(tt, 0.03, 2e-3, 1.0) + RNG.normal(0, 5e-4, tt.size)
    f = fit_t1(tt, y); assert f.params["T1_s"] == pytest.approx(2e-3, rel=0.05)


def test_t1_vs_temperature_phonon_model_and_thermal_law_falsified():          # REQ-THM-003 pipeline
    T = np.array([77.0, 150.0, 200.0, 250.0, 300.0, 350.0])
    T1 = synthetic_t1_vs_temperature(T, noise=0.03)
    f = fit_t1_vs_temperature(T, T1)
    assert f.params["A3_per_s_K5"] == pytest.approx(8.2e-11, rel=0.3) and f.residual_rms < 0.2 * (1 / T1).max()
    assert T1[0] > 100 * T1[-1]                                                 # phonons: two orders of magnitude from 77 K to 350 K
    thermal = thermal_model_prediction(T1[0], T)
    assert 0.15 < thermal[-1] / thermal[0] < 0.3                               # bath-occupation law: linear, ~1/4.5 from 77 K to 350 K
    assert T1[-1] / T1[0] < 1e-3                                                # phonons: orders of magnitude, so the data decide
