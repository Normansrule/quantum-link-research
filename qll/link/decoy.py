"""Single-photon bounds for a weak-coherent source: with decoy intensities, and the worst case without them.

Method
------
An attenuated laser sends Poisson photon numbers. Only single-photon pulses carry secret bits: from a multi-photon
pulse an adversary can split off a photon and read it after the bases are announced, without causing errors
(photon-number splitting [brassard2000]). The key length must therefore rest on a lower bound on the single-photon
detections and an upper bound on their error rate.

With decoys (signal intensity mu, weak decoy nu, vacuum) the gains Q (detections per pulse sent) of the three classes
bound the single-photon yield and error rate [hwang2003] [lo2005] [ma2005]:
    Y_1 >= mu / (mu nu - nu^2) [Q_nu e^nu - Q_mu e^mu nu^2/mu^2 - (mu^2 - nu^2)/mu^2 Y_0],
    e_1 <= (E_nu Q_nu e^nu - Y_0 / 2) / (Y_1 nu),
with Y_0 the vacuum yield (the vacuum class's gain) and E_nu the decoy class's error rate. The single-photon share of
signal detections is then Q_1 / Q_mu, Q_1 = Y_1 mu e^(-mu). Each count enters with a statistical margin in the
direction that makes the bound conservative: for a count k, the mean lies between
k + 1.5 L - sqrt(2.25 L^2 + 3 k L) and k + L + sqrt(L^2 + 2 k L), L = ln(1/eps), the inverted multiplicative
Chernoff bounds [chernoff1952] evaluated at the observed count, a common finite-size approximation (not a composable
finite-key proof).

Without decoys (GLLP [gottesman2004]) the adversary is granted every multi-photon pulse: the single-photon share is at
least 1 - P_multi / Q_mu with P_multi = 1 - e^-mu (1 + mu), and all errors are charged to single photons,
e_1 <= E_mu / (1 - P_multi/Q_mu). Beyond a few dB of loss this share reaches zero and no key is possible.
"""
from __future__ import annotations

import math
from dataclasses import dataclass


def mean_upper(k: float, eps: float) -> float:
    L = math.log(1 / eps)
    return k + L + math.sqrt(L * L + 2 * k * L)


def mean_lower(k: float, eps: float) -> float:
    L = math.log(1 / eps)
    return max(0.0, k + 1.5 * L - math.sqrt(2.25 * L * L + 3 * k * L))


@dataclass(frozen=True)
class SinglePhotonBound:
    single_fraction: float      # lower bound on the share of signal detections from single-photon pulses
    e1_upper: float             # upper bound on their error rate
    y1_lower: float = float("nan")
    y0_upper: float = float("nan")
    gains: tuple = ()           # (Q_mu, Q_nu, Q_0) measured

    @property
    def usable(self) -> bool:
        return self.single_fraction > 0 and self.e1_upper < 0.5


def decoy_bound(mu: float, nu: float, n_pulses: tuple[int, int, int], n_detect: tuple[int, int, int],
                decoy_errors: int, decoy_sifted: int, eps: float) -> SinglePhotonBound:
    """Vacuum + weak decoy bounds from counts: pulses sent and detections per class (signal, decoy, vacuum), and the
    errors among the decoy class's sifted bits (all of which are disclosed)."""
    (Ns, Nd, N0), (ks, kd, k0) = n_pulses, n_detect
    if min(Ns, Nd, N0) == 0:
        return SinglePhotonBound(0.0, 0.5)
    Qmu_hi, Qmu = mean_upper(ks, eps) / Ns, ks / Ns
    Qnu_lo = mean_lower(kd, eps) / Nd
    Y0_hi, Y0_lo = mean_upper(k0, eps) / N0, mean_lower(k0, eps) / N0
    y1 = mu / (mu * nu - nu * nu) * (Qnu_lo * math.exp(nu) - Qmu_hi * math.exp(mu) * nu * nu / (mu * mu)
                                     - (mu * mu - nu * nu) / (mu * mu) * Y0_hi)
    if y1 <= 0 or Qmu == 0:
        return SinglePhotonBound(0.0, 0.5, y1, Y0_hi, (Qmu, kd / Nd, k0 / N0))
    # errors in the decoy class: E_nu Q_nu = (decoy errors / decoy sifted) x (decoy detections / decoy pulses)
    err_hi = mean_upper(decoy_errors, eps) / max(decoy_sifted, 1) * (kd / Nd)
    e1 = min(0.5, max(0.0, (err_hi * math.exp(nu) - 0.5 * Y0_lo) / (y1 * nu)))
    frac = min(1.0, y1 * mu * math.exp(-mu) / Qmu)
    return SinglePhotonBound(frac, e1, y1, Y0_hi, (Qmu, kd / Nd, k0 / N0))


def gllp_bound(mu: float, signal_gain: float, qber_upper: float) -> SinglePhotonBound:
    """No decoys: every multi-photon pulse is the adversary's, every error a single-photon error."""
    p_multi = 1 - math.exp(-mu) * (1 + mu)
    frac = 1 - p_multi / signal_gain if signal_gain > 0 else 0.0
    if frac <= 0:
        return SinglePhotonBound(0.0, 0.5, gains=(signal_gain,))
    return SinglePhotonBound(frac, min(0.5, qber_upper / frac), gains=(signal_gain,))
