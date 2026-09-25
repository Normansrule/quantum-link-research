"""Continuous-variable QKD with Gaussian-modulated coherent states and homodyne detection (GG02).

Physics
-------
Alice sends coherent states with Gaussian-distributed quadratures of variance V_A (shot-noise units); Bob homodynes.
Channel: transmittance T, excess noise xi (referred to the input). With reverse reconciliation of efficiency beta,
the asymptotic rate against collective attacks is [grosshans2002] [weedbrook2012] [laudenbach2018]:
    K = beta * I_AB - chi_BE,
    I_AB = 1/2 log2( (V + chi_tot) / (1 + chi_tot) ),   V = V_A + 1,  chi_tot = chi_line + chi_hom / T,
    chi_line = 1/T - 1 + xi,  chi_hom = (1 + v_el)/eta - 1  (homodyne efficiency eta, electronic noise v_el),
    chi_BE = g((lambda_1 - 1)/2) + g((lambda_2 - 1)/2) - g((lambda_3 - 1)/2) - g((lambda_4 - 1)/2),
with g(x) = (x+1) log2(x+1) - x log2 x and the symplectic eigenvalues lambda_i of the covariance matrices
(standard GG02 expressions). The rate is bounded by PLOB and vanishes at high loss because excess noise, referred to
the input, grows as xi/T relative to the signal.
"""
from __future__ import annotations

import math


def _g(x: float) -> float:
    return (x + 1) * math.log2(x + 1) - x * math.log2(x) if x > 1e-15 else 0.0


def cv_rate_per_symbol(T: float, xi: float = 0.01, V_A: float = 4.0, beta: float = 0.95, eta: float = 0.6, v_el: float = 0.01) -> float:
    if not 0 < T <= 1:
        return 0.0
    V = V_A + 1
    chi_line = 1 / T - 1 + xi
    chi_hom = (1 + v_el) / eta - 1
    chi_tot = chi_line + chi_hom / T
    I_AB = 0.5 * math.log2((V + chi_tot) / (1 + chi_tot))
    A = V**2 * (1 - 2 * T) + 2 * T + T**2 * (V + chi_line) ** 2
    B = T**2 * (V * chi_line + 1) ** 2
    l1 = math.sqrt(max(0.5 * (A + math.sqrt(max(A**2 - 4 * B, 0))), 0))
    l2 = math.sqrt(max(0.5 * (A - math.sqrt(max(A**2 - 4 * B, 0))), 0))
    C = (V * math.sqrt(B) + T * (V + chi_line) + A * chi_hom) / (T * (V + chi_tot))
    D = math.sqrt(B) * (V + math.sqrt(B) * chi_hom) / (T * (V + chi_tot))
    l3 = math.sqrt(max(0.5 * (C + math.sqrt(max(C**2 - 4 * D, 0))), 0))
    l4 = math.sqrt(max(0.5 * (C - math.sqrt(max(C**2 - 4 * D, 0))), 0))
    chi_BE = _g((l1 - 1) / 2) + _g((l2 - 1) / 2) - _g((l3 - 1) / 2) - _g((l4 - 1) / 2)
    return max(0.0, beta * I_AB - chi_BE)


def max_loss_db(xi: float = 0.01, **kw) -> float:
    """Largest channel loss (dB) with a positive asymptotic rate, by bisection on T. With input-referred excess noise
    the GG02 rate stays positive at any loss once xi is below a threshold of a few percent (the rate then scales as T),
    so the function returns inf in that regime; the practical loss limit comes from finite-size effects and from
    detector noise that is not trusted [laudenbach2018]."""
    lo, hi = 1e-6, 1.0
    if cv_rate_per_symbol(hi, xi, **kw) <= 0:
        return 0.0
    if cv_rate_per_symbol(lo, xi, **kw) > 0:
        return math.inf
    for _ in range(60):
        mid = math.sqrt(lo * hi)
        if cv_rate_per_symbol(mid, xi, **kw) > 0:
            hi = mid
        else:
            lo = mid
    return -10 * math.log10(hi)
