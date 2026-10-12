"""Entanglement-based QKD certified by a Bell violation.

Physics
-------
Alice and Bob share Bell pairs; matched-basis outcomes form the key, mismatched settings estimate the
CHSH value S [ekert1991] [bennett1992bbm]. Device-independent rate against collective attacks:
r >= 1 - h2((1 + sqrt(S^2/4 - 1))/2) - h2(Q) [acin2007] [pironio2009]; for the ideal S = 2 sqrt 2, Q = 0
this gives 1 bit per matched round. Settings come from a declared EntropySource (INV-7); the settings and
outcomes must be exchanged classically, so certification under planetary latency is proposal E10.
"""
from __future__ import annotations

import math

from qll.qkd.binary_entropy import h2


TSIRELSON = 2 * math.sqrt(2)


def _check(S: float, Q: float) -> None:
    """Impossible inputs are errors, not values to clip into range (audit S06): no quantum correlation exceeds
    Tsirelson's bound 2 sqrt 2 [cirelson1980], and an error rate lies in [0, 1/2]."""
    if not (math.isfinite(S) and math.isfinite(Q)):
        raise ValueError("S and Q must be finite")
    if S > TSIRELSON * (1 + 1e-9):
        raise ValueError(f"S = {S} exceeds Tsirelson's bound 2 sqrt 2: an estimate this high is an error, not a stronger key")
    if not 0.0 <= Q <= 0.5:
        raise ValueError(f"error rate Q = {Q} is outside [0, 1/2]")


def di_rate_per_round(S: float, Q: float) -> float:
    _check(S, Q)
    if S <= 2.0:
        return 0.0
    S = min(S, TSIRELSON)                                   # only rounding above the bound reaches here
    return max(0.0, 1 - h2((1 + math.sqrt(S**2 / 4 - 1)) / 2) - h2(Q))


def e91_rate_from_werner(f: float) -> float:
    """Rate when the shared pairs are Werner states of fraction f: S = 2 sqrt 2 (4f-1)/3, Q = (1-f)*2/3."""
    S = 2 * math.sqrt(2) * (4 * f - 1) / 3
    Q = 2 * (1 - f) / 3
    return di_rate_per_round(S, Q)


def di_rate_finite_key(S: float, Q: float, n_rounds: int, eps: float = 1e-10) -> float:
    """Finite-key device-independent rate per round with a simplified statistical penalty.

    Parameter estimation of S from n rounds has statistical uncertainty ~ sqrt(2 ln(2/eps) / n) on the
    estimated correlators; the rate is evaluated at the pessimistic S - delta_S with delta_S = 4 * that
    uncertainty (four correlators), and a 2 log2(1/eps)/n term pays for privacy amplification. This is the
    shape of the entropy-accumulation bound [arnon2018] with the constants simplified; it is a model for
    scheduling, not a security proof. r -> di_rate_per_round(S, Q) as n -> infinity.
    """
    if isinstance(n_rounds, bool) or not isinstance(n_rounds, int) or n_rounds <= 0:
        raise ValueError(f"n_rounds must be a positive integer, got {n_rounds!r}")
    if not 0.0 < eps < 1.0:
        raise ValueError(f"eps must lie in (0, 1), got {eps}")
    delta = 4 * math.sqrt(2 * math.log(2 / eps) / n_rounds)
    # S here is an estimate from n rounds, which may exceed 2 sqrt 2 by statistical fluctuation; only an estimate
    # whose pessimistic value S - delta still exceeds the bound is inconsistent with quantum mechanics
    _check(min(S - delta, S), Q)
    r = di_rate_per_round(min(S - delta, TSIRELSON), Q) - 2 * math.log2(1 / eps) / n_rounds
    return max(0.0, r)


def rounds_for_positive_di_key(S: float, Q: float, eps: float = 1e-10, n_max: int = 10**9) -> int | None:
    """Smallest number of rounds that gives a positive finite-key DI rate (binary search), or None."""
    if di_rate_per_round(S, Q) <= 0:
        return None
    lo, hi = 1, n_max
    if di_rate_finite_key(S, Q, hi, eps) <= 0:
        return None
    while lo < hi:
        mid = (lo + hi) // 2
        if di_rate_finite_key(S, Q, mid, eps) > 0:
            hi = mid
        else:
            lo = mid + 1
    return lo


def chsh_from_visibility(V: float) -> float:
    """CHSH value of polarization pairs with correlator E(a, b) = V cos 2(a - b) at the optimal settings 0, 45 and
    22.5, 67.5 degrees: S = 2 sqrt 2 V [clauser1969] [aspect1982]. In BBM92 the sifted error rate is Q = (1 - V)/2."""
    return 2 * math.sqrt(2) * V


def chsh_std(V: float, pairs_per_setting: float) -> float:
    """Standard error of S from n coincidences per setting pair: each correlator has variance (1 - E^2)/n with
    E^2 = V^2/2, and the four add [casella2002]: sigma_S = 2 sqrt((1 - V^2/2)/n)."""
    return 2 * math.sqrt((1 - V * V / 2) / pairs_per_setting)
