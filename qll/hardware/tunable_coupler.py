"""Static ZZ crosstalk between transmons, and the tunable coupler that cancels it.

Physics
-------
Two transmons (frequencies w1, w2, anharmonicities a1, a2 < 0) coupled by J (exchange, J(a1^dag a2 + h.c.)) never
fully decouple: the |11> level is pushed by its neighbours |02> and |20>, so the energy of |11> is not the sum of |01>
and |10>. The residue is the static ZZ rate
    zeta = E_11 - E_10 - E_01 + E_00,
which to second order in J is [krantz2019] [ku2020]
    zeta = 2 J^2 (a1 + a2) / ((Delta + a1)(Delta - a2)),   Delta = w1 - w2.
(The sign of the second factor is easy to get wrong from memory; this module computes zeta exactly by diagonalising the
Duffing Hamiltonian and the tests hold the formula to the exact value.) ZZ is always on, so an idle qubit's phase
depends on its neighbour's state: a coherent error of order zeta * t per gate.

A tunable coupler [yan2018] puts a third transmon (frequency wc) between the qubits. Its virtual exchange adds an
indirect coupling of opposite sign to the direct one,
    g_eff = g12 + (g1c g2c / 2) (1/(w1 - wc) + 1/(w2 - wc)),
so moving wc switches the interaction off (an "idle point", where exact ZZ crosses zero) or on (for a CZ gate). This is
the architecture of Google's Sycamore/Willow and IBM's Heron processors [sung2021]. Frequencies are ordinary
frequencies in GHz (omega / 2 pi); every returned rate is in GHz.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


def _lowering(levels: int) -> np.ndarray:
    return np.diag(np.sqrt(np.arange(1, levels)), 1)


def _embed(op: np.ndarray, site: int, levels: int, n_sites: int) -> np.ndarray:
    out = np.array([[1.0]])
    for k in range(n_sites):
        out = np.kron(out, op if k == site else np.eye(levels))
    return out


def _duffing(freqs, anharms, couplings, levels: int) -> np.ndarray:
    """Coupled Duffing oscillators: sum_i w_i n_i + a_i/2 n_i(n_i-1) + sum_{i<j} g_ij (a_i^dag a_j + h.c.)."""
    n = len(freqs)
    a = [_embed(_lowering(levels), k, levels, n) for k in range(n)]
    H = np.zeros((levels**n, levels**n))
    for w, al, ak in zip(freqs, anharms, a):
        num = ak.T @ ak
        H += w * num + al / 2 * (num @ num - num)
    for (i, j), g in couplings.items():
        H += g * (a[i].T @ a[j] + a[i] @ a[j].T)
    return H


def _dressed_energy(E: np.ndarray, V: np.ndarray, occupation: tuple[int, ...], levels: int) -> float:
    """Energy of the eigenstate with the largest overlap on the bare product state |occupation>."""
    idx = 0
    for k in occupation:
        idx = idx * levels + k
    return float(E[int(np.argmax(np.abs(V[idx, :])))])


def static_zz_exact(w1: float, w2: float, a1: float, a2: float, J: float, levels: int = 4) -> float:
    """Exact ZZ = E11 - E10 - E01 + E00 of two directly coupled transmons (GHz)."""
    for v in (w1, w2, a1, a2, J):
        if isinstance(v, (complex, np.complexfloating)):
            raise TypeError("frequencies and couplings must be real")
    E, V = np.linalg.eigh(_duffing((w1, w2), (a1, a2), {(0, 1): J}, levels))
    e = lambda o: _dressed_energy(E, V, o, levels)
    return e((1, 1)) - e((1, 0)) - e((0, 1)) + e((0, 0))


def static_zz_perturbative(w1: float, w2: float, a1: float, a2: float, J: float) -> float:
    """Second-order ZZ, 2 J^2 (a1 + a2) / ((Delta + a1)(Delta - a2)) with Delta = w1 - w2 [krantz2019]."""
    d = w1 - w2
    return 2 * J**2 * (a1 + a2) / ((d + a1) * (d - a2))


@dataclass(frozen=True)
class CoupledPair:
    """Qubit - coupler - qubit, all transmons with the same anharmonicity (GHz)."""
    w1: float = 4.00
    w2: float = 4.10
    alpha: float = -0.20
    g1c: float = 0.10
    g2c: float = 0.10
    g12: float = 0.0067
    levels: int = 3

    def zz(self, wc: float) -> float:
        """Exact static ZZ of the two qubits with the coupler parked (in its ground state) at wc."""
        H = _duffing((self.w1, wc, self.w2), (self.alpha,) * 3,
                     {(0, 1): self.g1c, (1, 2): self.g2c, (0, 2): self.g12}, self.levels)
        E, V = np.linalg.eigh(H)
        e = lambda o: _dressed_energy(E, V, o, self.levels)
        return e((1, 0, 1)) - e((1, 0, 0)) - e((0, 0, 1)) + e((0, 0, 0))

    def effective_coupling(self, wc: float) -> float:
        """g12 + (g1c g2c / 2)(1/(w1 - wc) + 1/(w2 - wc)) [yan2018]."""
        return self.g12 + self.g1c * self.g2c / 2 * (1 / (self.w1 - wc) + 1 / (self.w2 - wc))

    def zz_free_frequency(self, lo: float, hi: float) -> float:
        """Coupler frequency in [lo, hi] where exact ZZ vanishes (the idle point); raises if ZZ keeps one sign."""
        from scipy.optimize import brentq

        return float(brentq(self.zz, lo, hi, xtol=1e-9))
