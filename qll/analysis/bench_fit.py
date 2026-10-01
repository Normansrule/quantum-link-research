"""Fits for the tabletop Mars-link bench (experiments/protocols/P09): each recovers one law from logged data so
that qll.analysis.bench_report can compare it with the twin (qll/systems/bench_twin.py).

Every fit is a closed-form least-squares estimate: a scale on the Lambert phase function [russell1916], power-law
slopes in log-log coordinates (distance: 0 for radiance conservation; filter width: 1) [siegman1986], the Gaussian
mode width from ln r = -2 theta^2 / theta_m^2 on the core points and the stray floor as the median of the far points,
and the polarization error from e - (1 - w)/2 = w e_opt.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from qll.channels.planetshine import lambert_phase


def _arr(x) -> np.ndarray:
    if np.iscomplexobj(np.asarray(x)):
        raise TypeError("bench data must be real")
    return np.asarray(x, dtype=float)


@dataclass(frozen=True)
class PhaseFit:
    scale: float              # power at full phase
    rms_relative: float       # residual rms / scale, over the points used


def fit_phase(phase_rad, power, max_phase_rad: float = np.radians(120)) -> PhaseFit:
    a, P = _arr(phase_rad), _arr(power)
    m = a <= max_phase_rad
    phi = np.array([lambert_phase(x) for x in a[m]])
    k = float(np.dot(phi, P[m]) / np.dot(phi, phi))
    return PhaseFit(k, float(np.sqrt(np.mean((P[m] - k * phi) ** 2)) / k))


def loglog_slope(x, y) -> float:
    """Slope of log y against log x (least squares)."""
    lx, ly = np.log(_arr(x)), np.log(_arr(y))
    return float(np.polyfit(lx, ly, 1)[0])


@dataclass(frozen=True)
class RejectionFit:
    mode_rad: float           # SMF: Gaussian theta_m; MMF: the angle where the response halves (field stop)
    floor: float              # median rejection far off axis


def fit_rejection(theta_rad, power, fiber: str, far_rad: float) -> RejectionFit:
    th, P = np.abs(_arr(theta_rad)), _arr(power)
    r = P / P[np.argmin(th)]
    far = th >= far_rad
    floor = float(np.median(r[far])) if far.any() else float(r.min())
    if fiber == "smf":
        core = (r > 0.05) & (th > 0)
        slope = float(np.dot(th[core] ** 2, np.log(r[core])) / np.dot(th[core] ** 2, th[core] ** 2))   # ln r = slope th^2
        mode = float(np.sqrt(-2.0 / slope))
    else:
        order = np.argsort(th)
        below = th[order][r[order] < 0.5]
        mode = float(below[0]) if below.size else float(th.max())
    return RejectionFit(mode, floor)


def fit_error_fraction(purity, error) -> tuple[float, float]:
    """(e_opt, residual rms) for e = w e_opt + (1 - w)/2."""
    w, e = _arr(purity), _arr(error)
    y = e - (1 - w) / 2
    e_opt = float(np.dot(w, y) / np.dot(w, w))
    return e_opt, float(np.sqrt(np.mean((y - w * e_opt) ** 2)))
