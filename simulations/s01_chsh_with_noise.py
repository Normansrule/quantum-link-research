"""S01 — CHSH with a noisy Bell pair (Flagship F1, stage S1).

Physics: S = |E(a,b) − E(a,b') + E(a',b) + E(a',b')|; ideal 2√2 at angles 0, π/2, π/4, 3π/4 for |Φ+⟩.
With a depolarizing channel of strength p on each qubit the pair becomes Werner-like and
S = 2√2 (1 − p)² to first order in this model. Reference: Clauser et al. (1969); Brunner et al. (2014).
"""
from __future__ import annotations

import math

import numpy as np


def chsh_aer(p_depol: float, shots: int = 20000, seed: int = 7) -> float:
    from qiskit import QuantumCircuit
    from qiskit_aer import AerSimulator
    from qiskit_aer.noise import NoiseModel, depolarizing_error

    noise = NoiseModel()
    if p_depol > 0:
        noise.add_all_qubit_quantum_error(depolarizing_error(p_depol, 1), ["ry"])
    sim = AerSimulator(noise_model=noise, seed_simulator=seed)
    settings = {"a": 0.0, "a2": math.pi / 2, "b": math.pi / 4, "b2": 3 * math.pi / 4}

    def E(ta: float, tb: float) -> float:
        qc = QuantumCircuit(2, 2)
        qc.h(0); qc.cx(0, 1)
        qc.ry(-ta, 0); qc.ry(-tb, 1)   # measure along an axis in the x–z plane
        qc.measure([0, 1], [0, 1])
        counts = sim.run(qc, shots=shots).result().get_counts()
        tot = sum(counts.values())
        return sum((1 if k.count("1") % 2 == 0 else -1) * v for k, v in counts.items()) / tot

    return abs(E(settings["a"], settings["b"]) - E(settings["a"], settings["b2"]) + E(settings["a2"], settings["b"]) + E(settings["a2"], settings["b2"]))


def main() -> None:
    from _common import report, save
    import matplotlib.pyplot as plt

    ps = np.linspace(0, 0.3, 13)
    S = [chsh_aer(p) for p in ps]
    report("S01 CHSH vs depolarizing noise", [("S at p = 0 (ideal 2√2 = 2.828)", f"{S[0]:.3f}"),
                                             ("first p with S < 2", f"{next((p for p, s in zip(ps, S) if s < 2), float('nan')):.3f}")])
    fig, ax = plt.subplots(figsize=(6.5, 4))
    ax.plot(ps, S, "o-", lw=2, label="Aer, 20k shots per setting")
    ax.plot(ps, 2 * math.sqrt(2) * (1 - ps) ** 2, "--", label="2√2 (1−p)²")
    ax.axhline(2, color="k", ls=":"); ax.text(0.005, 2.03, "local bound", fontsize=8)
    ax.set(xlabel="depolarizing probability p per qubit", ylabel="CHSH S", title="S01: how much noise a Bell test tolerates")
    ax.legend(); save(fig, "chsh_noise")


if __name__ == "__main__":
    import sys; sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent)); main()
