"""Superconducting-circuit spectra and readout: fluxonium, dispersive shift, and the readout SNR budget.

Physics
-------
Fluxonium [manucharyan2009]: H = 4 E_C n^2 - E_J cos(phi) + (E_L/2)(phi - phi_ext)^2, diagonalised in the phi basis
(finite differences), with E_L << E_J. At half flux the qubit frequency drops to hundreds of MHz while the
charge-matrix element between |0> and |1> stays small, giving T1 of milliseconds [somoroff2023].
Dispersive readout [blais2004] [blais2021]: a qubit coupled with g to a resonator detuned by Delta = omega_q - omega_r
shifts it by chi = g^2 / Delta * alpha / (Delta + alpha) (transmon, anharmonicity alpha < 0). Measuring with n photons
for time tau through a chain of added noise n_add gives SNR ~ 2 |chi| sqrt(n) sqrt(kappa tau) / sqrt(1 + 2 n_add)
in the matched-chi = kappa/2 regime; single-shot fidelity ~ erf(SNR/2) style. The measurement must finish well
inside T1: tau << T1 sets the budget.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np


def fluxonium_spectrum(E_C: float, E_J: float, E_L: float, phi_ext: float = math.pi, n_levels: int = 4, grid: int = 801, phi_max: float = 6 * math.pi) -> np.ndarray:
    """Lowest energies (same units as inputs, e.g. GHz*h) of the fluxonium Hamiltonian by finite differences."""
    phi = np.linspace(-phi_max, phi_max, grid)
    d = phi[1] - phi[0]
    V = -E_J * np.cos(phi) + 0.5 * E_L * (phi - phi_ext) ** 2
    # 4 E_C n^2 with n = -i d/dphi -> -4 E_C d^2/dphi^2
    main = 4 * E_C * 2 / d**2 + V
    off = -4 * E_C / d**2 * np.ones(grid - 1)
    H = np.diag(main) + np.diag(off, 1) + np.diag(off, -1)
    return np.linalg.eigvalsh(H)[:n_levels]


def transmon_spectrum(E_C: float, E_J: float, n_levels: int = 4, n_max: int = 30) -> np.ndarray:
    """Charge-basis transmon for cross-checking limits: H = 4 E_C (n - n_g)^2 - E_J cos(phi)."""
    n = np.arange(-n_max, n_max + 1)
    H = np.diag(4 * E_C * n**2.0) - 0.5 * E_J * (np.eye(2 * n_max + 1, k=1) + np.eye(2 * n_max + 1, k=-1))
    return np.linalg.eigvalsh(H)[:n_levels]


def dispersive_shift(g: float, delta: float, alpha: float) -> float:
    """chi = g^2/Delta * alpha/(Delta + alpha) for a transmon (all in the same angular or ordinary frequency units)."""
    return g**2 / delta * alpha / (delta + alpha)


@dataclass(frozen=True)
class ReadoutBudget:
    chi_hz: float          # dispersive shift (Hz)
    kappa_hz: float        # resonator linewidth (Hz)
    n_photons: float
    n_added_noise: float   # amplifier chain noise referred to the resonator output (quanta); JPA ~0.5, HEMT-only ~20
    T1_s: float

    def snr(self, tau_s: float) -> float:
        # phase-sensitive homodyne SNR for two pointer states separated by 2 chi in phase, kappa-limited
        eff = 1.0 / (1.0 + 2.0 * self.n_added_noise)
        return 2 * abs(self.chi_hz) / max(self.kappa_hz, 1e-30) * math.sqrt(2 * self.n_photons * self.kappa_hz * tau_s * eff)

    def separation_fidelity(self, tau_s: float) -> float:
        """Assignment fidelity from Gaussian pointer separation, then reduced by T1 decay during tau."""
        f_sep = 0.5 * (1 + math.erf(self.snr(tau_s) / (2 * math.sqrt(2))))
        return f_sep * math.exp(-tau_s / (2 * self.T1_s))

    def optimal_tau_s(self, tau_grid=None) -> float:
        import numpy as np
        grid = tau_grid if tau_grid is not None else np.logspace(-8, -5, 200)
        return float(grid[int(np.argmax([self.separation_fidelity(t) for t in grid]))])
