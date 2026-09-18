"""Bloch sphere: a pure qubit state |ψ⟩ = cos(θ/2)|0⟩ + e^{iφ} sin(θ/2)|1⟩ as a point; a mixed
state as a point inside. Also shows how T1 pulls the vector toward |0⟩ (with a thermal offset
p_exc from noise/thermal.py) and T2 shrinks it toward the axis [nielsen2010] [krantz2019]."""
from __future__ import annotations

import math

import numpy as np

from qll.circuits.noise.thermal import excited_state_population
from qll.viz._common import cli, finish


def bloch_vector(theta: float, phi: float) -> np.ndarray:
    return np.array([math.sin(theta) * math.cos(phi), math.sin(theta) * math.sin(phi), math.cos(theta)])


def decay_trajectory(r0: np.ndarray, T1: float, T2: float, z_eq: float, t: np.ndarray) -> np.ndarray:
    """Bloch-equation solution: transverse components decay with T2, longitudinal relaxes to z_eq with T1."""
    x = r0[0] * np.exp(-t / T2)
    y = r0[1] * np.exp(-t / T2)
    z = z_eq + (r0[2] - z_eq) * np.exp(-t / T1)
    return np.stack([x, y, z], axis=1)


def main() -> None:
    args = cli(__doc__)
    import matplotlib.pyplot as plt

    fig = plt.figure(figsize=(9, 4.4))
    ax = fig.add_subplot(1, 2, 1, projection="3d")
    u, v = np.mgrid[0:2 * np.pi:40j, 0:np.pi:20j]
    ax.plot_wireframe(np.cos(u) * np.sin(v), np.sin(u) * np.sin(v), np.cos(v), color="0.85", lw=0.4)
    for vec, lab in ((bloch_vector(0, 0), "|0⟩"), (bloch_vector(math.pi, 0), "|1⟩"),
                     (bloch_vector(math.pi / 2, 0), "|+⟩"), (bloch_vector(math.pi / 2, math.pi / 2), "|+i⟩")):
        ax.quiver(0, 0, 0, *vec, color="0.4", arrow_length_ratio=0.1)
        ax.text(*(vec * 1.15), lab)
    psi = bloch_vector(math.radians(60), math.radians(40))
    ax.quiver(0, 0, 0, *psi, color="C0", lw=2, arrow_length_ratio=0.1)
    ax.text(*(psi * 1.2), "|ψ⟩ (θ=60°, φ=40°)", color="C0")
    ax.set(xlim=(-1, 1), ylim=(-1, 1), zlim=(-1, 1), title="pure state = surface point")
    ax.set_axis_off()

    ax2 = fig.add_subplot(1, 2, 2)
    T1, T2 = 50e-6, 30e-6
    p_exc = excited_state_population(2 * math.pi * 5e9, 0.05)  # 5 GHz qubit at 50 mK
    z_eq = 1 - 2 * p_exc
    t = np.linspace(0, 150e-6, 300)
    traj = decay_trajectory(bloch_vector(math.pi / 2, 0), T1, T2, z_eq, t)
    ax2.plot(t * 1e6, traj[:, 0], label="⟨X⟩  ∝ e^{−t/T2}")
    ax2.plot(t * 1e6, traj[:, 2], label="⟨Z⟩  → 1 − 2 p_exc(T)")
    ax2.plot(t * 1e6, np.linalg.norm(traj, axis=1), "k--", lw=1, label="|r|  (purity)")
    ax2.set(xlabel="time (µs)", ylabel="Bloch components", title="from |+⟩: T1 = 50 µs, T2 = 30 µs, 50 mK bath")
    ax2.legend(fontsize=8)
    finish(fig, args)


if __name__ == "__main__":
    main()
