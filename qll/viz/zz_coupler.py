"""Static ZZ between two transmons versus the tunable coupler's frequency, from exact diagonalisation, with the
effective coupling g_eff on the same axis: parking the coupler at the idle point switches the interaction off."""
from __future__ import annotations

import numpy as np

from qll.hardware.tunable_coupler import CoupledPair
from qll.viz._common import cli, finish


def main() -> None:
    args = cli(__doc__)
    import matplotlib.pyplot as plt

    pair = CoupledPair()
    wc = np.linspace(4.55, 8.0, 240)
    zz = np.array([pair.zz(w) for w in wc]) * 1e6          # kHz
    geff = np.array([pair.effective_coupling(w) for w in wc]) * 1e3   # MHz
    idle = pair.zz_free_frequency(5.0, 5.5)

    fig, ax = plt.subplots(figsize=(8.5, 4.6))
    ax.semilogy(wc, np.abs(zz), lw=2.2, color="C0", label="|ZZ| (exact, kHz)")
    ax.axvline(idle, color="C2", ls="--", lw=1.4)
    ax.text(idle + 0.05, 2e3, f"idle point\n$\\omega_c$ = {idle:.3f} GHz\nZZ = 0", color="C2", fontsize=9)
    ax.set(xlabel="coupler frequency $\\omega_c/2\\pi$ (GHz)", ylabel="|static ZZ| (kHz)", ylim=(1, 1e4),
           title="A tunable coupler switches the always-on ZZ off")
    ax2 = ax.twinx()
    ax2.plot(wc, geff, color="C3", lw=1.6, ls="-.", label="$g_{\\rm eff}$ (MHz)")
    ax2.axhline(0, color="0.6", lw=0.8)
    ax2.set_ylabel("effective coupling $g_{\\rm eff}/2\\pi$ (MHz)", color="C3")
    lines = ax.get_legend_handles_labels()[0] + ax2.get_legend_handles_labels()[0]
    labels = ax.get_legend_handles_labels()[1] + ax2.get_legend_handles_labels()[1]
    ax.legend(lines, labels, fontsize=8, loc="upper right")
    ax.text(0.99, 0.03, "Qubits at 4.00 and 4.10 GHz, α = −200 MHz, g_qc = 100 MHz, direct g = 6.7 MHz.\n"
            "Near the coupler the virtual exchange dominates (ZZ ~ MHz); far away the direct term returns.",
            transform=ax.transAxes, fontsize=8, color="0.3", ha="right")
    finish(fig, args)


if __name__ == "__main__":
    main()
