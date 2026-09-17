"""The level map as a figure: where each Phase 1 equation lives and where temperature enters."""
from __future__ import annotations

from qll.viz._common import cli, finish

LEVELS = [
    ("Level 0  qubit & photon", "n̄ = 1/(e^{ħω/k_BT} − 1);  T1(T) = T1(0)/(2n̄+1)", "circuits/noise/thermal.py"),
    ("Level 1  two-qubit primitives", "|ψ⟩⊗|Φ⁺⟩ → 2 classical bits → X^j Z^i|ψ⟩", "circuits/teleportation.py (Phase 2)"),
    ("Level 2  one link", "η = 10^(−αL/10);  θ = λ/(πw₀);  r = 1 − 2h₂(Q)", "channels/*, qkd/*"),
    ("Level 3  network", "F' from F via BBPSSW;  t_mem ≳ 2d/c", "network/* (Phase 4)"),
    ("Level 4  Earth–Mars", "τ = d/c ∈ [3, 22] min;  N = n̄ M B η", "channels/light_time_delay.py, thermal_background.py"),
]


def main() -> None:
    args = cli(__doc__)
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(9, 4.2))
    ax.axis("off")
    for i, (name, eq, where) in enumerate(LEVELS):
        y = 1 - i * 0.2
        ax.add_patch(plt.Rectangle((0.0, y - 0.16), 1.0, 0.15, color="C0", alpha=0.08 + 0.05 * i))
        ax.text(0.01, y - 0.05, name, fontsize=10, fontweight="bold", va="center")
        ax.text(0.30, y - 0.05, eq, fontsize=9, va="center", family="monospace")
        ax.text(0.99, y - 0.13, where, fontsize=7, va="center", ha="right", color="0.4")
    ax.annotate("temperature T enters every level", xy=(1.02, 0.1), xytext=(1.02, 0.95), rotation=90,
                ha="center", va="center", color="C3", fontsize=9,
                arrowprops=dict(arrowstyle="->", color="C3"))
    ax.set(xlim=(0, 1.05), ylim=(0, 1.02))
    finish(fig, args)


if __name__ == "__main__":
    main()
