"""Bloch–Redfield relaxation of a qubit in a thermal bath, checked against the Phase 1 thermal law.

Physics
-------
A qubit H = (omega/2) sigma_z coupled through sigma_x to an ohmic bath with spectral density J(w) = gamma * w / omega
relaxes by emission at rate J(omega)(n̄+1) and absorption at J(omega) n̄ (detailed balance), so the total rate is
Gamma_1 = gamma (2n̄+1) and T1(T) = T1(0)/(2n̄+1), the law qll.circuits.noise.thermal uses [breuer2002] [carmichael1999].
QuTiP's brmesolve builds the Bloch–Redfield tensor from the bath's noise power spectrum; this module fits T1 from its
output and checks the law independently of the Kraus-map implementation.
"""
from __future__ import annotations

import numpy as np

HBAR_OVER_KB = 7.638232577577646e-12   # hbar / k_B in K·s


def nbar(omega: float, T: float) -> float:
    x = HBAR_OVER_KB * omega / T if T > 0 else np.inf
    return 0.0 if x > 700 else float(1.0 / np.expm1(x))      # exp(700) is the float64 edge; n̄ is 0 there


def t1_bloch_redfield(omega: float, T: float, gamma: float, t_max_factor: float = 6.0) -> float:
    """Fit T1 (seconds) from QuTiP's Bloch–Redfield evolution of the excited state under an ohmic thermal bath.

    The solver runs in units where omega = 1 (time in 1/omega), which keeps the ODE well conditioned; the bath's Bose
    factor at a scaled frequency w is evaluated exactly as nbar(w * omega, T). QuTiP's basis(2, 0) is the +1
    eigenstate of sigma_z, i.e. the excited state of H = (omega/2) sigma_z."""
    import qutip as qt

    g = gamma / omega
    n = nbar(omega, T)

    def spectrum(w: float) -> float:
        if w == 0:
            return 0.0
        nw = nbar(abs(w) * omega, T)
        return float(g * abs(w) * (nw + 1 if w > 0 else nw))

    tau = 1.0 / (g * (2 * n + 1))                           # expected T1 in units of 1/omega
    tlist = np.linspace(0, t_max_factor * tau, 240)
    res = qt.brmesolve(0.5 * qt.sigmaz(), qt.basis(2, 0), tlist, a_ops=[[qt.sigmax(), spectrum]], e_ops=[qt.sigmaz()])
    z = np.asarray(res.expect[0])
    z_inf = -1.0 / (2 * n + 1)                              # detailed balance: <sigma_z> = -tanh(hbar omega / 2 kT)
    y = z - z_inf
    k = len(tlist) // 2
    slope = np.polyfit(tlist[:k], np.log(y[:k]), 1)[0]
    return float(-1.0 / slope / omega)


def equilibrium_sz(omega: float, T: float) -> float:
    return -1.0 / (2 * nbar(omega, T) + 1)
