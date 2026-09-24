"""An NV center as a spin-photon interface: levels, ODMR, and herald rates.

Physics
-------
Ground-state Hamiltonian H = D S_z^2 + gamma_e B . S with D = 2.87 GHz and gamma_e = 2.8 MHz/G;
ODMR lines at D +- gamma_e B_par for a field along the NV axis [doherty2013]. Only the zero-phonon-line
fraction (~3% at 4 K) is usable for interference, which with collection and detection efficiencies gives
herald probabilities of 1e-4-1e-6 per attempt for two-photon schemes [bernien2013] [humphreys2018]; cavities
raise the ZPL fraction by the Purcell factor. Magnetometer sensitivity for a Ramsey/CW-ODMR readout:
eta_B ~ (h / (g mu_B)) * dnu / (C sqrt(R)) with linewidth dnu, contrast C, photon rate R [degen2017].
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

D_ZFS_HZ = 2.87e9
GAMMA_E_HZ_PER_G = 2.8e6
H_OVER_G_MU_B_T_PER_HZ = 1 / (28.0e9)  # T per Hz for g = 2


def purcell_factor(Q: float, V_over_lambda_n_cubed: float) -> float:
    """Purcell enhancement F_P = (3/4 pi^2) (lambda/n)^3 Q / V for an emitter on resonance at a field maximum [purcell1946];
    V is the mode volume in units of (lambda/n)^3. Diamond nanophotonic cavities reach Q ~ 1e4, V ~ 1 -> F_P ~ 700 [bhaskar2020]."""
    return 3 / (4 * math.pi**2) * Q / V_over_lambda_n_cubed


def cooperativity(F_P: float, debye_waller: float = 0.03, quantum_efficiency: float = 0.7) -> float:
    """C = F_P * (ZPL fraction) * QE, the ratio of coherent to incoherent emission that sets the spin-photon interface quality."""
    return F_P * debye_waller * quantum_efficiency



def nv_hamiltonian_hz(B_gauss: np.ndarray) -> np.ndarray:
    """3x3 spin-1 Hamiltonian in Hz; B in gauss in the NV frame (z along the NV axis)."""
    sx = np.array([[0, 1, 0], [1, 0, 1], [0, 1, 0]]) / math.sqrt(2)
    sy = np.array([[0, -1j, 0], [1j, 0, -1j], [0, 1j, 0]]) / math.sqrt(2)
    sz = np.diag([1.0, 0.0, -1.0])
    Bx, By, Bz = B_gauss
    return D_ZFS_HZ * sz @ sz + GAMMA_E_HZ_PER_G * (Bx * sx + By * sy + Bz * sz)


def odmr_frequencies_hz(B_gauss: np.ndarray) -> tuple[float, float]:
    """The two ground-state transition frequencies (m_s = 0 -> ±1), exact diagonalization."""
    ev = np.sort(np.linalg.eigvalsh(nv_hamiltonian_hz(np.asarray(B_gauss, dtype=float))))
    return float(ev[1] - ev[0]), float(ev[2] - ev[0])


def magnetometer_sensitivity_t_per_sqrt_hz(linewidth_hz: float, contrast: float, photon_rate_hz: float) -> float:
    return H_OVER_G_MU_B_T_PER_HZ * linewidth_hz / (contrast * math.sqrt(photon_rate_hz))


@dataclass(frozen=True)
class NvNode:
    T_kelvin: float = 4.0
    zpl_fraction: float = 0.03
    collection_efficiency: float = 0.1
    detector_efficiency: float = 0.7
    attempt_rate_hz: float = 1e5
    T2_s: float = 1.0
    purcell_factor: float = 1.0

    def effective_zpl(self) -> float:
        f = self.zpl_fraction * self.purcell_factor
        return f / (f + (1 - self.zpl_fraction))   # Purcell enhances the ZPL branch only

    def herald_probability(self) -> float:
        eta = self.effective_zpl() * self.collection_efficiency * self.detector_efficiency
        return 0.5 * eta**2

    def entanglement_rate_hz(self) -> float:
        return self.herald_probability() * self.attempt_rate_hz
