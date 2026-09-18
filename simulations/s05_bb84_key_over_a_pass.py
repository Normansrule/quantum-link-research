"""S05 — Secret bits from one satellite pass vs background (Flagship F2, stage S1).

Physics: sifted rate = ½·R_det; background counts N per second inside a gate τ add errors
Q_bg ≈ N τ / (2 (R_det + N τ)); secret fraction r = 1 − 2 h₂(Q) (Shor–Preskill, asymptotic).
Pass duration 300 s. Reference: Liao et al. (2017); Ma, Fung & Lo (2007).
"""
from __future__ import annotations

import numpy as np

from qll.qkd.key_rate import bb84_rate_per_sifted_bit


def key_bits_per_pass(R_det: float, N_bg: float, tau: float = 1e-9, q_intrinsic: float = 0.01, T_pass: float = 300.0, rep_rate: float = 1e8) -> float:
    from qll.channels.link_budget import LinkBudget
    Q = min(0.5, q_intrinsic + LinkBudget.qber_from_background(R_det, N_bg, tau, rep_rate))
    r = bb84_rate_per_sifted_bit(Q)
    return 0.5 * R_det * T_pass * r


def main() -> None:
    from _common import report, save
    import matplotlib.pyplot as plt

    N = np.logspace(2, 8, 200)
    fig, ax = plt.subplots(figsize=(7, 4.2))
    rows = []
    for R, lab in ((1e2, "100 detected/s (night, Micius-class)"), (1e4, "10⁴ detected/s (Jinan-1-class)"), (1e6, "10⁶ detected/s (future)")):
        k = [key_bits_per_pass(R, n) for n in N]
        ax.semilogx(N, k, lw=2, label=lab)
        rows.append((f"{lab}: key/pass at N = 1e3 /s", f"{key_bits_per_pass(R, 1e3):.0f} bits"))
    report("S05 BB84 key per 300 s pass vs background", rows)
    ax.set(xlabel="background counts per second in the gate window", ylabel="secret bits per pass", yscale="log", ylim=(1, 1e9),
           title="S05: daylight kills the key before it kills the signal")
    ax.legend(fontsize=8); save(fig, "bb84_pass")


if __name__ == "__main__":
    import sys; sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent)); main()
