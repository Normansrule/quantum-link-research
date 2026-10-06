"""The error budget of Majorana parity-based teleportation, after Crogman, Dang, and Erenso (2025), Equations 17 to 20
and Table 2 [crogman2025], written in dimensionless device knobs so it can be used before any device is chosen.

Physics
-------
    hybridization splitting      Gamma ~ Delta^2 exp(-2 L / xi)                              (their Eq. 17) [cheng2012]
    parity readout               signal mu(T) = mu0 tanh(Delta / 2 k T), Gaussian noise sigma,
                                 misclassification eps = (1/2) erfc(mu / (sqrt(2) sigma)),  F_read = 1 - eps   (Eq. 18)
    quasiparticle poisoning      a Poisson process of rate Gamma_qp during the integration window tau_m; a poisoned
                                 readout is a coin: F_eff = (1 - Gamma_qp tau_m) F_read + (Gamma_qp tau_m) / 2  (Eq. 19) [rainis2012]
    teleportation                F_tel >~ F_eff^k (1 - C_hyb exp(-a L / xi))                                   (Eq. 20)

Two choices are made explicit here. The paper's Equation 20 counts one readout; a complete teleportation needs two
parity measurements and two classical bits (qll/circuits/majorana_teleport.py), so the readout factor enters k = 2
times by default. The hybridization exponent is a = 2 in Equation 20 and a = 1 in the paper's bound A12; it is a
parameter. Inputs are dimensionless: the readout signal-to-noise ratio at zero temperature mu0/sigma, the gap over
the thermal energy Delta/kT, the poisoning probability per window Gamma_qp tau_m, and the separation L/xi.
"""
from __future__ import annotations

import math

from scipy.special import erfc


def readout_fidelity(snr0: float, gap_over_kT: float) -> float:
    """F_read = 1 - (1/2) erfc(mu / sqrt(2)) with mu = snr0 tanh(Delta / 2kT) in units of sigma."""
    if snr0 < 0 or gap_over_kT <= 0:
        raise ValueError("snr0 >= 0 and gap_over_kT > 0")
    mu = snr0 * math.tanh(gap_over_kT / 2)
    return 1.0 - 0.5 * erfc(mu / math.sqrt(2))


def poisoned_readout_fidelity(f_read: float, poison_prob: float) -> float:
    """F_eff with a poisoning probability Gamma_qp tau_m per readout (small-rate limit of the Poisson process)."""
    if not 0 <= poison_prob <= 1:
        raise ValueError("poison_prob in [0, 1]")
    return (1 - poison_prob) * f_read + poison_prob / 2


def hybridization_factor(l_over_xi: float, c_hyb: float = 1.0, exponent: float = 2.0) -> float:
    return max(0.0, 1.0 - c_hyb * math.exp(-exponent * l_over_xi))


def teleport_fidelity(snr0: float, gap_over_kT: float, poison_prob: float, l_over_xi: float, readouts: int = 2,
                      c_hyb: float = 1.0, exponent: float = 2.0) -> float:
    """The conservative bound F_tel >~ F_eff^readouts (1 - C_hyb e^(-exponent L/xi))."""
    f_eff = poisoned_readout_fidelity(readout_fidelity(snr0, gap_over_kT), poison_prob)
    return f_eff ** readouts * hybridization_factor(l_over_xi, c_hyb, exponent)


def splitting_ratio(l_over_xi_a: float, l_over_xi_b: float, gap_ratio: float = 1.0) -> float:
    """Gamma(b) / Gamma(a) from Gamma ~ Delta^2 exp(-2L/xi): how much a longer wire (or bigger gap) suppresses errors."""
    return gap_ratio ** 2 * math.exp(-2 * (l_over_xi_b - l_over_xi_a))


def separation_for(target_infidelity: float, c_hyb: float = 1.0, exponent: float = 2.0) -> float:
    """L/xi at which hybridization alone costs `target_infidelity`."""
    return math.log(c_hyb / target_infidelity) / exponent
