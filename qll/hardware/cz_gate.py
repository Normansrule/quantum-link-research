"""The adiabatic controlled-Z (CZ) gate between two transmons: tune one qubit toward the |11>-|20> avoided crossing,
wait, and come back. The computational states pick up an extra phase that |01>, |10>, and |00> do not share, and when
that conditional phase reaches pi the gate is a CZ.

Physics
-------
Qubit 1 (frequency w1(t), tunable by flux) and qubit 2 (fixed, w2) are transmons with anharmonicity alpha < 0 and an
exchange coupling g (the effective coupling a tunable coupler provides; see tunable_coupler.py). The state |11> is
coupled to |20> with matrix element sqrt(2) g, and the two are degenerate when w1 = w2 - alpha. Near that point the
|11> level is repelled, so the static ZZ zeta(w1) = E11 - E10 - E01 + E00 becomes tens of MHz. If w1 moves slowly
enough (adiabatically) the state follows the dressed |11> and returns to it, and the conditional phase is
    phi = -2 pi * integral zeta(w1(t)) dt
[dicarlo2009] [strauch2003] [krantz2019]; a pulse whose integral makes phi = pi is a CZ up to single-qubit Z phases,
which are virtual (a frame change) on every modern processor. Moving too fast leaves population in |20>: leakage,
the error that fast adiabatic pulse shapes [martinis2014] are designed to suppress.

This module integrates the Schrodinger equation for the full 3 x 3 level system (no rotating-wave approximation on the
qubits' levels beyond the Duffing model), reads the conditional phase and leakage from the propagator, and computes
the average gate fidelity of the computational block against an ideal CZ after removing the local Z phases.
Frequencies in GHz, times in ns, phases in radians.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from qll.hardware.tunable_coupler import _duffing, static_zz_exact

LEVELS = 3
COMPUTATIONAL = ((0, 0), (0, 1), (1, 0), (1, 1))
# flat top that makes the default pulse a CZ when its 15 ns ramps are shaped linearly in frequency instead of in the
# mixing angle (recomputed by tests/test_cz_gate.py with flat_time_for_cz)
FREQUENCY_SHAPED_FLAT_NS = 37.24


def _index(occupation: tuple[int, int]) -> int:
    return occupation[0] * LEVELS + occupation[1]


def _hamiltonian(w1: float, w2: float, alpha: float, g: float) -> np.ndarray:
    return _duffing((w1, w2), (alpha, alpha), {(0, 1): g}, LEVELS)


def _dressed_basis(w1: float, w2: float, alpha: float, g: float) -> np.ndarray:
    """Columns: eigenvectors of H at (w1, w2), ordered like the bare basis by maximum overlap, with a real positive
    diagonal so that phases read from the propagator are meaningful."""
    E, V = np.linalg.eigh(_hamiltonian(w1, w2, alpha, g))
    order = np.argmax(np.abs(V), axis=1)          # bare state k -> eigenvector with the largest overlap on it
    if len(set(order.tolist())) != len(order):
        raise ValueError("dressed states are not uniquely identifiable at this operating point")
    B = V[:, order]
    return B * np.sign(np.diag(B))


@dataclass(frozen=True)
class CZPulse:
    """A flat-top flux pulse on qubit 1 with sine-squared ramps (GHz, ns)."""
    w1_idle: float = 6.00
    w1_int: float = 5.25           # interaction point, 50 MHz above the |11>-|20> crossing at w2 - alpha = 5.20 GHz
    w2: float = 5.00
    alpha: float = -0.20
    g: float = 0.020
    t_ramp: float = 15.0
    t_flat: float = 29.49          # calibrated by flat_time_for_cz so the conditional phase is pi (59.5 ns in total)
    shape: str = "theta"           # "theta": sine-squared in the mixing angle [martinis2014]; "frequency": in w1 itself

    def __post_init__(self):
        for name in ("w1_idle", "w1_int", "w2", "alpha", "g", "t_ramp", "t_flat"):
            v = getattr(self, name)
            if isinstance(v, (complex, np.complexfloating)) or not np.isscalar(v):
                raise TypeError(f"{name} must be a real number")
        if self.t_ramp <= 0 or self.t_flat < 0:
            raise ValueError("t_ramp must be positive and t_flat non-negative")

    @property
    def duration(self) -> float:
        return 2 * self.t_ramp + self.t_flat

    def w1(self, t: np.ndarray | float) -> np.ndarray:
        """Qubit 1 frequency along the pulse."""
        t = np.asarray(t, dtype=float)
        up = np.sin(np.pi / 2 * np.clip(t / self.t_ramp, 0, 1)) ** 2
        down = np.sin(np.pi / 2 * np.clip((self.duration - t) / self.t_ramp, 0, 1)) ** 2
        s = np.minimum(up, down)
        if self.shape == "frequency" or (self.shape == "theta" and self.g == 0):   # no coupling: no mixing angle
            return self.w1_idle + (self.w1_int - self.w1_idle) * s
        if self.shape != "theta":
            raise ValueError("shape must be 'theta' or 'frequency'")
        # |11>-|20> mixing angle, tan(2 theta) = 2 sqrt(2) g / Delta with Delta = E_20 - E_11 = w1 - w2 + alpha:
        # moving theta smoothly makes the pulse slow exactly where the gap is small and fast where it is large
        cross = self.w2 - self.alpha
        theta = lambda w: 0.5 * np.arctan2(2 * np.sqrt(2) * self.g, w - cross)
        th = theta(self.w1_idle) + (theta(self.w1_int) - theta(self.w1_idle)) * s
        return cross + 2 * np.sqrt(2) * self.g / np.tan(2 * th)

    def propagator(self, dt: float = 0.01) -> np.ndarray:
        """Full 9 x 9 propagator in the idle point's dressed basis (midpoint rule, exact exponential per step)."""
        n = max(1, int(np.ceil(self.duration / dt)))
        h = self.duration / n
        U = np.eye(LEVELS**2, dtype=complex)
        for k in range(n):
            E, V = np.linalg.eigh(_hamiltonian(float(self.w1((k + 0.5) * h)), self.w2, self.alpha, self.g))
            U = (V * np.exp(-2j * np.pi * E * h)) @ V.T @ U
        B = _dressed_basis(self.w1_idle, self.w2, self.alpha, self.g)
        return B.T @ U @ B

    def populations_from_11(self, dt: float = 0.01, every: int = 10):
        """Times and bare-state populations of |11> and |20> along the pulse, starting in the idle dressed |11>."""
        n = max(1, int(np.ceil(self.duration / dt)))
        h = self.duration / n
        psi = _dressed_basis(self.w1_idle, self.w2, self.alpha, self.g)[:, _index((1, 1))].astype(complex)
        ts, p11, p20 = [0.0], [abs(psi[_index((1, 1))]) ** 2], [abs(psi[_index((2, 0))]) ** 2]
        for k in range(n):
            E, V = np.linalg.eigh(_hamiltonian(float(self.w1((k + 0.5) * h)), self.w2, self.alpha, self.g))
            psi = (V * np.exp(-2j * np.pi * E * h)) @ (V.T @ psi)
            if (k + 1) % every == 0 or k == n - 1:
                ts.append((k + 1) * h); p11.append(abs(psi[_index((1, 1))]) ** 2); p20.append(abs(psi[_index((2, 0))]) ** 2)
        return np.array(ts), np.array(p11), np.array(p20)

    def conditional_phase(self, dt: float = 0.01) -> float:
        """phi = arg U_11 - arg U_10 - arg U_01 + arg U_00, wrapped to (-pi, pi]."""
        U = self.propagator(dt)
        d = [U[_index(o), _index(o)] for o in COMPUTATIONAL]
        return float(np.angle(d[3] * d[0] / (d[1] * d[2])))

    def leakage(self, dt: float = 0.01) -> float:
        """Population left outside the computational subspace when starting in |11>."""
        U = self.propagator(dt)
        col = U[:, _index((1, 1))]
        return float(1 - sum(abs(col[_index(o)]) ** 2 for o in COMPUTATIONAL))

    def adiabatic_phase(self, n: int = 1201) -> float:
        """-2 pi * integral of the exact static ZZ along the pulse (the adiabatic-limit prediction, unwrapped; it
        includes the small ZZ at the idle point, which the propagator also accumulates). The simulated phase exceeds
        it by a second-order (super-adiabatic) correction that falls as 1/duration."""
        t = np.linspace(0, self.duration, n)
        zeta = np.array([static_zz_exact(float(w), self.w2, self.alpha, self.alpha, self.g, levels=LEVELS) for w in self.w1(t)])
        return float(-2 * np.pi * np.trapezoid(zeta, t))

    def average_fidelity(self, dt: float = 0.01) -> float:
        """Average gate fidelity of the computational block to CZ after removing local Z phases (leakage counts as
        error): F = (Tr(M M^dag) + |Tr M|^2) / (d (d + 1)) with M = CZ^dag P U P, d = 4 [pedersen2007]."""
        U = self.propagator(dt)
        idx = [_index(o) for o in COMPUTATIONAL]
        P = U[np.ix_(idx, idx)]
        ph = np.angle(np.diag(P))
        z = np.diag(np.exp(-1j * np.array([ph[0], ph[1], ph[2], ph[1] + ph[2] - ph[0]])))   # local Z frame change
        M = np.diag([1, 1, 1, -1]).conj().T @ z @ P
        d = 4
        return float((np.trace(M @ M.conj().T).real + abs(np.trace(M)) ** 2) / (d * (d + 1)))


def flat_time_for_cz(pulse: CZPulse, dt: float = 0.02) -> float:
    """Flat-top duration at which the simulated conditional phase is pi (a CZ): an adiabatic estimate from the
    integral of ZZ, refined by root-finding on the full simulation."""
    from dataclasses import replace

    from scipy.optimize import brentq

    guess = brentq(lambda tf: replace(pulse, t_flat=tf).adiabatic_phase() - np.pi, 0.0, 500.0, xtol=1e-4)
    err = lambda tf: float(np.angle(np.exp(1j * (replace(pulse, t_flat=max(tf, 0.0)).conditional_phase(dt) - np.pi))))
    lo, hi = max(0.0, guess - 3.0), guess + 3.0
    return float(brentq(err, lo, hi, xtol=1e-5))
