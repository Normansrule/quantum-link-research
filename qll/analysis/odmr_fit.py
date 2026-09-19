"""Fit an ODMR spectrum and extract the NV zero-field splitting and the magnetic field.

Physics
-------
Each ODMR line is a Lorentzian dip in fluorescence: S(f) = 1 - sum_k C_k * (w_k/2)^2 / ((f - f_k)^2 + (w_k/2)^2)
with contrast C_k and full width w_k [dreau2011]. For a field along one NV axis the two lines sit at
f_± = D ± gamma_e B_par (learn/00_foundations/09), so D = (f_+ + f_-)/2 and B_par = (f_+ - f_-)/(2 gamma_e); for
an arbitrary field direction up to eight lines appear (four NV orientations) and the exact spin Hamiltonian in
qll.hardware.nv_node is fitted instead. Sensitivity from the fit: eta_B = (h/(g mu_B)) * w / (C sqrt(R)) [degen2017].
Expected values: D = 2.870 GHz at 300 K (dD/dT ~ -74 kHz/K [acosta2010]); ensemble contrast 1-3 %; width 5-15 MHz.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.optimize import curve_fit

from qll.hardware.nv_node import D_ZFS_HZ, GAMMA_E_HZ_PER_G, magnetometer_sensitivity_t_per_sqrt_hz

D_TEMPERATURE_COEFF_HZ_PER_K = -74e3  # [acosta2010]


def lorentzian_dips(f: np.ndarray, *params: float) -> np.ndarray:
    """params: baseline, then triples (center, width_fwhm, contrast) for each dip."""
    base = params[0]
    y = np.full_like(f, base, dtype=float)
    for k in range((len(params) - 1) // 3):
        c, w, C = params[1 + 3 * k : 4 + 3 * k]
        y -= base * C * (w / 2) ** 2 / ((f - c) ** 2 + (w / 2) ** 2)
    return y


@dataclass(frozen=True)
class OdmrFit:
    centers_hz: np.ndarray
    widths_hz: np.ndarray
    contrasts: np.ndarray
    baseline: float
    D_hz: float | None
    B_parallel_gauss: float | None
    sensitivity_t_per_sqrt_hz: float | None
    residual_rms: float


def _initial_guess(f: np.ndarray, s: np.ndarray, n_dips: int) -> list[float]:
    base = float(np.median(s))
    depth = base - s
    guesses = [base]
    order = np.argsort(depth)[::-1]
    picked: list[float] = []
    for i in order:
        if all(abs(f[i] - p) > 8e6 for p in picked):
            picked.append(float(f[i]))
        if len(picked) == n_dips:
            break
    for c in sorted(picked):
        guesses += [c, 8e6, max(float(depth.max() / base), 1e-3)]
    return guesses


def fit_odmr(freq_hz: np.ndarray, signal: np.ndarray, n_dips: int = 2, photon_rate_hz: float | None = None) -> OdmrFit:
    f, s = np.asarray(freq_hz, dtype=float), np.asarray(signal, dtype=float)
    p0 = _initial_guess(f, s, n_dips)
    lower = [0] + [f.min(), 1e5, 0.0] * n_dips
    upper = [np.inf] + [f.max(), 2e8, 1.0] * n_dips
    popt, _ = curve_fit(lorentzian_dips, f, s, p0=p0, bounds=(lower, upper), maxfev=20000)
    base = popt[0]
    trip = popt[1:].reshape(n_dips, 3)
    order = np.argsort(trip[:, 0]); trip = trip[order]
    centers, widths, contrasts = trip[:, 0], trip[:, 1], trip[:, 2]
    D = B = eta = None
    if n_dips == 2:
        D = float((centers[0] + centers[1]) / 2)
        B = float((centers[1] - centers[0]) / (2 * GAMMA_E_HZ_PER_G))
    elif n_dips == 1:
        D = float(centers[0]); B = 0.0
    if photon_rate_hz:
        eta = magnetometer_sensitivity_t_per_sqrt_hz(float(widths.min()), float(contrasts.max()), photon_rate_hz)
    resid = float(np.sqrt(np.mean((lorentzian_dips(f, *popt) - s) ** 2)) / base)
    return OdmrFit(centers, widths, contrasts, float(base), D, B, eta, resid)


def synthetic_odmr(B_gauss: float, contrast: float = 0.02, width_hz: float = 8e6, noise: float = 2e-3,
                   f_hz: np.ndarray | None = None, T_kelvin: float = 300.0, seed: int = 0) -> tuple[np.ndarray, np.ndarray]:
    """A fake spectrum for testing the pipeline before the bench exists; D shifts with temperature [acosta2010]."""
    rng = np.random.default_rng(seed)
    f = np.linspace(2.70e9, 3.05e9, 700) if f_hz is None else f_hz
    D = D_ZFS_HZ + D_TEMPERATURE_COEFF_HZ_PER_K * (T_kelvin - 300.0)
    params = [1.0, D - GAMMA_E_HZ_PER_G * B_gauss, width_hz, contrast, D + GAMMA_E_HZ_PER_G * B_gauss, width_hz, contrast]
    return f, lorentzian_dips(f, *params) + rng.normal(0, noise, size=f.size)


def load_csv(path: str) -> tuple[np.ndarray, np.ndarray]:
    """CSV with columns frequency_hz, signal (normalized fluorescence). Header line required."""
    arr = np.genfromtxt(path, delimiter=",", names=True)
    return np.asarray(arr["frequency_hz"], dtype=float), np.asarray(arr["signal"], dtype=float)
