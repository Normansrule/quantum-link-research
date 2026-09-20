"""Fit the pulsed-control datasets of P02 (Rabi, Ramsey, Hahn echo, T1) and the temperature dependence of T1.

Physics
-------
Rabi: P1(t) = A sin^2(Omega t / 2) e^{-t/tau_R} + c. Ramsey: A e^{-tau/T2*} cos(Delta tau + phi) + c.
Echo: A e^{-(tau/T2)^n} + c with n ~ 1-3 [delange2010]. T1: A e^{-t/T1} + c.
NV ensemble T1 versus temperature follows a two-phonon Raman plus Orbach model [jarmola2012]:
    1/T1(T) = A_1 + A_2 / (exp(Delta/k_B T) - 1) + A_3 T^5,
with Delta ~ 73 meV, A_1 the sample-dependent (cross-relaxation) floor, A_3 the Raman prefactor. Below ~100 K
T1 saturates at 1/A_1 (hours are reported for single centers); at 300 K it is milliseconds. The thermal model of
Phase 1 (qll.circuits.noise.thermal.thermal_t1, a bath-occupation law at the qubit frequency) predicts only the
linear factor 1/(2 n_bar + 1), about 4.5x from 77 K to 350 K for a 2.87 GHz spin, whereas the phonon law gives
orders of magnitude (~T^5). P02 step 8 is designed to distinguish the two, which closes REQ-THM-003 (memory
coherence as a function of temperature) with data rather than with the wrong model.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
from scipy.optimize import curve_fit

K_B_EV_PER_K = 8.617333262e-5
DELTA_ORBACH_EV = 0.073   # [jarmola2012]


def rabi_model(t, A, omega, tau, c):
    return A * np.sin(omega * t / 2) ** 2 * np.exp(-t / tau) + c


def ramsey_model(t, A, T2s, delta, phi, c):
    return A * np.exp(-t / T2s) * np.cos(delta * t + phi) + c


def echo_model(t, A, T2, n, c):
    return A * np.exp(-((t / T2) ** n)) + c


def t1_model(t, A, T1, c):
    return A * np.exp(-t / T1) + c


def inverse_t1_vs_T(T, A1, A2, A3):
    return A1 + A2 / np.expm1(DELTA_ORBACH_EV / (K_B_EV_PER_K * T)) + A3 * T**5


@dataclass(frozen=True)
class Fit:
    params: dict
    residual_rms: float


def _fit(model, t, y, p0, bounds=(-np.inf, np.inf)) -> tuple[np.ndarray, float]:
    popt, _ = curve_fit(model, t, y, p0=p0, bounds=bounds, maxfev=20000)
    return popt, float(np.sqrt(np.mean((model(t, *popt) - y) ** 2)))


def fit_rabi(t, y) -> Fit:
    t, y = np.asarray(t, float), np.asarray(y, float)
    f0 = np.fft.rfftfreq(len(t), t[1] - t[0]); spec = np.abs(np.fft.rfft(y - y.mean()))
    omega0 = 2 * math.pi * f0[np.argmax(spec[1:]) + 1]
    p, r = _fit(rabi_model, t, y, [y.max() - y.min(), omega0, t.max() * 3, y.min()], ([0, 0, 0, -np.inf], [np.inf, np.inf, np.inf, np.inf]))
    return Fit({"A": p[0], "omega_rad_s": p[1], "pi_time_s": math.pi / p[1], "tau_s": p[2], "c": p[3]}, r)


def fit_ramsey(t, y) -> Fit:
    t, y = np.asarray(t, float), np.asarray(y, float)
    f0 = np.fft.rfftfreq(len(t), t[1] - t[0]); spec = np.abs(np.fft.rfft(y - y.mean()))
    d0 = 2 * math.pi * f0[np.argmax(spec[1:]) + 1]
    p, r = _fit(ramsey_model, t, y, [(y.max() - y.min()) / 2, t.max() / 2, d0, 0.0, y.mean()], ([0, 0, 0, -np.pi, -np.inf], [np.inf, np.inf, np.inf, np.pi, np.inf]))
    return Fit({"A": p[0], "T2star_s": p[1], "detuning_rad_s": p[2], "phi": p[3], "c": p[4]}, r)


def fit_echo(t, y) -> Fit:
    t, y = np.asarray(t, float), np.asarray(y, float)
    p, r = _fit(echo_model, t, y, [y.max() - y.min(), t.max() / 2, 1.5, y.min()], ([0, 0, 0.5, -np.inf], [np.inf, np.inf, 4.0, np.inf]))
    return Fit({"A": p[0], "T2_s": p[1], "n": p[2], "c": p[3]}, r)


def fit_t1(t, y) -> Fit:
    t, y = np.asarray(t, float), np.asarray(y, float)
    p, r = _fit(t1_model, t, y, [y.max() - y.min(), t.max() / 3, y.min()], ([0, 0, -np.inf], [np.inf, np.inf, np.inf]))
    return Fit({"A": p[0], "T1_s": p[1], "c": p[2]}, r)


def fit_t1_vs_temperature(T_K, T1_s) -> Fit:
    """Fit 1/T1(T) to the Orbach + Raman model; returns A1 (1/s), A2 (1/s), A3 (1/(s K^5))."""
    T, y = np.asarray(T_K, float), 1.0 / np.asarray(T1_s, float)
    p, r = _fit(inverse_t1_vs_T, T, y, [y.min(), y.max(), 1e-12], ([0, 0, 0], [np.inf, np.inf, np.inf]))
    return Fit({"A1_per_s": p[0], "A2_per_s": p[1], "A3_per_s_K5": p[2]}, r)


def thermal_model_prediction(T1_low_T_s: float, T_K: np.ndarray, f_hz: float = 2.87e9) -> np.ndarray:
    """What Phase 1's bath-occupation law predicts for the same spin (for the falsification plot)."""
    from qll.circuits.noise.thermal import thermal_t1
    return np.array([thermal_t1(T1_low_T_s, 2 * math.pi * f_hz, T) for T in T_K])


def synthetic_t1_vs_temperature(T_K: np.ndarray, A1: float = 1 / 3600.0, A2: float = 300.0, A3: float = 8.2e-11, noise: float = 0.05, seed: int = 0):
    """Jarmola-like ensemble: T1 ~ minutes below 100 K, ~ms at 300 K, Raman T^5 dominant above 150 K (illustrative constants; TODO: fit to [jarmola2012])."""
    rng = np.random.default_rng(seed)
    T1 = 1.0 / inverse_t1_vs_T(np.asarray(T_K, float), A1, A2, A3)
    return T1 * np.exp(rng.normal(0, noise, size=len(T1)))
