"""Linear optics as unitary mode transformations; Hong-Ou-Mandel bunching.

Physics
-------
A lossless beam splitter maps (a1, a2) -> (t a1 + r a2, -r* a1 + t* a2) with |t|^2 + |r|^2 = 1. Two
identical photons on a 50:50 splitter never leave in separate ports [hong1987]: |1,1> -> (|2,0> - |0,2>)/sqrt2.
With partial distinguishability (overlap |<phi1|phi2>|^2 = V) the coincidence probability is
P_c = (1 - V)/2 for a 50:50 splitter; for reflectivity R, P_c = (1 - 2R(1-R)(1 + V)) ... derived in the
docstring test. The visibility V is what limits every linear-optics Bell measurement [kok2007].
"""
from __future__ import annotations

import numpy as np


def beam_splitter_unitary(R: float = 0.5, phase: float = 0.0) -> np.ndarray:
    t, r = np.sqrt(1 - R), np.sqrt(R) * np.exp(1j * phase)
    return np.array([[t, r], [-np.conj(r), np.conj(t)]])


def hom_coincidence_probability(R: float = 0.5, visibility: float = 1.0) -> float:
    """Probability that two single photons (one per input) exit in different ports.

    Distinguishable photons: P = R^2 + (1-R)^2 ... = 1 - 2R(1-R); identical photons add the
    interference term: P = 1 - 2R(1-R)(1 + V) with V the mode overlap.
    """
    return 1 - 2 * R * (1 - R) * (1 + visibility)


def hom_dip(delay_s: np.ndarray, coherence_time_s: float, visibility: float = 1.0, R: float = 0.5) -> np.ndarray:
    """Coincidence rate vs relative delay for Gaussian-spectrum photons: V(tau) = V exp(-(tau/tau_c)^2)."""
    v = visibility * np.exp(-((delay_s / coherence_time_s) ** 2))
    return 1 - 2 * R * (1 - R) * (1 + v)
