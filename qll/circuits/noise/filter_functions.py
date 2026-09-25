"""Dynamical decoupling as a filter: which noise frequencies a pulse sequence lets through.

Physics
-------
For pure dephasing by classical noise with spectrum S(omega), the coherence after time T under a sequence of pi pulses
decays as exp(-chi(T)) with chi = (1/2pi) int S(omega) F(omega T) / omega^2 domega, where the filter function F depends
only on the pulse timings [cywinski2008] [biercuk2011]. In the convention used here (F = |sum_k (-1)^k (e^{i omega t_{k+1}} -
e^{i omega t_k})|^2), free induction gives F = 4 sin^2(omega T/2) (passes low frequencies, hence T2* < T2) and Hahn echo
F = 16 sin^4(omega T/4) (blocks DC); other papers absorb a factor 2 into chi. CPMG with n pulses shifts the passband to
omega ~ pi n / T, so scanning n turns the qubit into a spectrum analyser of its own environment (noise spectroscopy).
For 1/f noise S ~ A/omega the echo decay is Gaussian-like and CPMG extends T2 as ~ n^{2/3} [medford2012].
"""
from __future__ import annotations

import numpy as np


def filter_function(omega: np.ndarray, T: float, pulse_times: list[float]) -> np.ndarray:
    """|sum_k (-1)^k (e^{i omega t_{k+1}} - e^{i omega t_k})|^2 with t_0 = 0, t_{n+1} = T [cywinski2008]."""
    ts = [0.0] + sorted(pulse_times) + [T]
    acc = np.zeros_like(omega, dtype=complex)
    for k in range(len(ts) - 1):
        acc += (-1) ** k * (np.exp(1j * omega * ts[k + 1]) - np.exp(1j * omega * ts[k]))
    return np.abs(acc) ** 2


def cpmg_times(n: int, T: float) -> list[float]:
    return [T * (k - 0.5) / n for k in range(1, n + 1)]


def coherence_decay_exponent(S, T: float, pulse_times: list[float], omega_max: float = None, n_omega: int = 20000) -> float:
    """chi(T) = (1/2pi) int_0^inf S(omega) F(omega T)/omega^2 domega, integrated numerically on a log grid."""
    omega_max = omega_max or 1e4 / T
    omega = np.logspace(np.log10(1e-3 / T), np.log10(omega_max), n_omega)
    F = filter_function(omega, T, pulse_times)
    integrand = S(omega) * F / omega**2
    return float(np.trapezoid(integrand, omega) / (2 * np.pi))


def peak_frequency(T: float, n: int) -> float:
    """Passband centre of an n-pulse CPMG sequence: omega = pi n / T."""
    return np.pi * n / T
