"""The three measurements that define a qubit: Rabi oscillation (drive strength), Ramsey fringe
(T2*, detuning), and Hahn echo (T2). Analytic two-level formulas [nielsen2010] [sewani2020]."""
from __future__ import annotations

import numpy as np

from qll.viz._common import cli, finish


def rabi_p1(t: np.ndarray, omega_r: float, delta: float = 0.0) -> np.ndarray:
    """Excited-state population under a resonant or detuned drive: (Ω²/Ω_eff²) sin²(Ω_eff t/2)."""
    om = np.sqrt(omega_r**2 + delta**2)
    return (omega_r**2 / om**2) * np.sin(om * t / 2) ** 2


def ramsey_p1(tau: np.ndarray, delta: float, T2star: float) -> np.ndarray:
    return 0.5 * (1 + np.exp(-tau / T2star) * np.cos(delta * tau))


def echo_amplitude(tau: np.ndarray, T2: float, n: float = 1.0) -> np.ndarray:
    """Hahn-echo envelope exp(-(t/T2)^n); n≈1 Markovian bath, n≈3 slow (quasi-static) bath [delange2010]."""
    return np.exp(-((tau / T2) ** n))


def main() -> None:
    args = cli(__doc__)
    import matplotlib.pyplot as plt

    fig, (a, b, c) = plt.subplots(1, 3, figsize=(11, 3.4))
    t = np.linspace(0, 2e-6, 400)
    for d, lab in ((0.0, "resonant"), (2 * np.pi * 1e6, "detuned 1 MHz")):
        a.plot(t * 1e6, rabi_p1(t, 2 * np.pi * 2e6, d), label=lab)
    a.set(xlabel="drive time (µs)", ylabel="P(|1⟩)", title="Rabi: Ω/2π = 2 MHz")
    a.legend(fontsize=8)
    tau = np.linspace(0, 6e-6, 400)
    b.plot(tau * 1e6, ramsey_p1(tau, 2 * np.pi * 1e6, 2e-6))
    b.set(xlabel="free evolution τ (µs)", ylabel="P(|1⟩)", title="Ramsey: Δ/2π = 1 MHz, T2* = 2 µs")
    tau2 = np.linspace(0, 400e-6, 400)
    c.plot(tau2 * 1e6, echo_amplitude(tau2, 100e-6, 1.0), label="n = 1")
    c.plot(tau2 * 1e6, echo_amplitude(tau2, 100e-6, 3.0), label="n = 3 (slow bath)")
    c.set(xlabel="echo time (µs)", ylabel="echo amplitude", title="Hahn echo: T2 = 100 µs")
    c.legend(fontsize=8)
    finish(fig, args)


if __name__ == "__main__":
    main()
