"""How close two states are.

Physics
-------
Pure target: F = <psi|rho|psi>. General (Uhlmann): F(rho, sigma) = (Tr sqrt(sqrt(rho) sigma sqrt(rho)))^2
[uhlmann1976] [jozsa1994]. Trace distance D = ||rho - sigma||_1 / 2 obeys the Fuchs-van de Graaf bounds
1 - sqrt(F) <= D <= sqrt(1 - F) [fuchs1999].
"""
from __future__ import annotations

import numpy as np


def _as_density(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=complex)
    if x.ndim == 1:
        x = x / np.linalg.norm(x)
        return np.outer(x, x.conj())
    return x


def _psd_sqrt(m: np.ndarray) -> np.ndarray:
    """Square root of a Hermitian PSD matrix by eigendecomposition (no warnings on singular input)."""
    w, v = np.linalg.eigh((m + m.conj().T) / 2)
    return (v * np.sqrt(np.clip(w, 0.0, None))) @ v.conj().T


def fidelity(a: np.ndarray, b: np.ndarray) -> float:
    """Uhlmann fidelity; reduces to <psi|rho|psi> when either argument is pure."""
    rho, sigma = _as_density(a), _as_density(b)
    sr = _psd_sqrt(rho)
    inner = _psd_sqrt(sr @ sigma @ sr)
    return float(np.real(np.trace(inner)) ** 2)


def trace_distance(a: np.ndarray, b: np.ndarray) -> float:
    rho, sigma = _as_density(a), _as_density(b)
    ev = np.linalg.eigvalsh(rho - sigma)
    return float(0.5 * np.sum(np.abs(ev)))


def fuchs_van_de_graaf_holds(a: np.ndarray, b: np.ndarray, tol: float = 1e-9) -> bool:
    f, d = fidelity(a, b), trace_distance(a, b)
    return (1 - np.sqrt(f) - tol) <= d <= (np.sqrt(max(0.0, 1 - f)) + tol)
