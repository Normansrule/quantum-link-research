"""Coherent, squeezed, and Fock states of a harmonic oscillator, with QuTiP as the numerical check.

Physics
-------
Coherent state |alpha> = D(alpha)|0>: Poissonian photon number with mean |alpha|^2, quadrature variances at the vacuum
level 1/4 (in the convention x = (a + a^dagger)/2) [glauber1963]. Squeezed vacuum S(r)|0>: variances e^{-2r}/4 and
e^{2r}/4, mean photon number sinh^2 r [walls2008]. These are the states of continuous-variable QKD (learn/03/17) and of
the bosonic codes (T03); a displaced squeezed state is a GKP grid state's ingredient. Fock states have g2(0) = 1 - 1/n.
"""
from __future__ import annotations

import math


def coherent_stats(alpha: complex, N: int = 60) -> dict[str, float]:
    import qutip as qt

    a = qt.destroy(N)
    psi = qt.coherent(N, alpha)
    x = (a + a.dag()) / 2
    p = (a - a.dag()) / (2j)
    var = lambda op: float(qt.expect(op * op, psi) - qt.expect(op, psi) ** 2)
    n = qt.expect(a.dag() * a, psi)
    g2 = float(qt.expect(a.dag() * a.dag() * a * a, psi)) / n**2
    return {"n_mean": float(n), "var_x": var(x), "var_p": var(p), "g2": g2}


def squeezed_vacuum_stats(r: float, N: int = 80) -> dict[str, float]:
    import qutip as qt

    a = qt.destroy(N)
    psi = qt.squeeze(N, r) * qt.basis(N, 0)
    x = (a + a.dag()) / 2
    p = (a - a.dag()) / (2j)
    var = lambda op: float(qt.expect(op * op, psi) - qt.expect(op, psi) ** 2)
    return {"n_mean": float(qt.expect(a.dag() * a, psi)), "var_x": var(x), "var_p": var(p)}


def fock_g2(n: int) -> float:
    return 1 - 1 / n if n > 0 else 0.0
