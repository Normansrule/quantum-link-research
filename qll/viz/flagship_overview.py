"""The three flagship experiments in one figure: Earth↔Earth (two computers, metropolitan fiber),
Earth↔satellite (LEO downlink), Earth↔Mars (interplanetary relay). Every number comes from the
tested qll functions; callouts say what to look for."""
from __future__ import annotations

import math

from qll.channels.fiber_loss import transmittance
from qll.channels.free_space_diffraction import geometric_transmittance
from qll.channels.light_time_delay import one_way_delay_s, round_trip_delay_s
from qll.constants.astro import EARTH_MARS_MAX_M, EARTH_MARS_MIN_M
from qll.viz._common import cli, finish


def fmt_s(s: float) -> str:
    return f"{s*1e6:.0f} µs" if s < 1e-3 else f"{s*1e3:.1f} ms" if s < 1 else f"{s:.1f} s" if s < 120 else f"{s/60:.0f} min"


def main() -> None:
    args = cli(__doc__)
    import matplotlib.pyplot as plt
    from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch

    fig, axes = plt.subplots(1, 3, figsize=(15, 5.6))
    fig.suptitle("Three flagship experiments: the same physics, three distances", fontsize=15, y=0.995)

    def node(ax, x, y, label, color):
        ax.add_patch(FancyBboxPatch((x - 0.11, y - 0.07), 0.22, 0.14, boxstyle="round,pad=0.02", fc=color, alpha=0.18, ec=color, lw=2))
        ax.text(x, y, label, ha="center", va="center", fontsize=9, fontweight="bold")

    def arrow(ax, x0, y0, x1, y1, color, ls="-", lw=2):
        ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="<->", mutation_scale=14, lw=lw, color=color, ls=ls))

    # F1 Earth ↔ Earth
    ax = axes[0]; ax.axis("off"); ax.set(xlim=(0, 1), ylim=(0, 1))
    ax.set_title("F1 · two computers, one city  (25 km fiber)", fontsize=11)
    node(ax, 0.2, 0.62, "Lab A\nNV / SPDC node", "C0"); node(ax, 0.8, 0.62, "Lab B\nNV / SPDC node", "C0")
    node(ax, 0.5, 0.85, "midpoint\nBell measurement", "C2")
    arrow(ax, 0.31, 0.66, 0.42, 0.82, "C2", ls="--"); arrow(ax, 0.58, 0.82, 0.69, 0.66, "C2", ls="--")
    arrow(ax, 0.31, 0.58, 0.69, 0.58, "C3")
    eta = transmittance(12.5, 0.2)
    ax.text(0.5, 0.50, f"photon survival per 12.5 km arm: {eta:.2f}\nherald round trip: {fmt_s(round_trip_delay_s(12.5e3))}", ha="center", fontsize=9)
    ax.text(0.5, 0.30, "What to look for:\n• heralded entanglement rate (Hz)\n• CHSH S > 2 after the herald\n• teleportation F > 2/3", ha="center", va="top", fontsize=9, color="0.3")
    ax.text(0.5, 0.05, "Done in the field: Delft–The Hague 2024, Boston 2024.\nOur version: P03 bench, then campus fiber.", ha="center", fontsize=8, color="C0")

    # F2 Earth ↔ satellite
    ax = axes[1]; ax.axis("off"); ax.set(xlim=(0, 1), ylim=(0, 1))
    ax.set_title("F2 · ground station ↔ LEO satellite  (500–1200 km)", fontsize=11)
    ax.add_patch(Circle((0.5, -0.55), 0.85, color="C0", alpha=0.12)); ax.text(0.5, 0.12, "Earth", ha="center", fontsize=9, color="C0")
    node(ax, 0.25, 0.30, "ground station\n1 m telescope", "C0"); node(ax, 0.75, 0.30, "ground station\n1 m telescope", "C0")
    node(ax, 0.5, 0.85, "satellite\nSPDC source", "C1")
    arrow(ax, 0.42, 0.80, 0.30, 0.38, "C2", ls="--"); arrow(ax, 0.58, 0.80, 0.70, 0.38, "C2", ls="--")
    arrow(ax, 0.36, 0.30, 0.64, 0.30, "C3")
    eta = geometric_transmittance(1.2e6, 810e-9, 0.15, 1.0)
    ax.text(0.01, 0.66, f"geometric loss per\ndownlink: ~{eta:.0e}\n+ atmosphere, pointing,\ndaylight → ~1e-6 total\nlight time: {fmt_s(one_way_delay_s(1.2e6))}", ha="left", va="top", fontsize=8)
    ax.text(0.99, 0.66, "What to look for:\n• pairs per pass\n• QBER vs sun angle\n• key bits per pass", ha="right", va="top", fontsize=8, color="0.3")
    ax.text(0.5, 0.04, "Done: Micius 2017–2020, Jinan-1 2025.\nOur version: P04 rooftop link + link-budget reproduction.", ha="center", fontsize=8, color="C0")

    # F3 Earth ↔ Mars
    ax = axes[2]; ax.axis("off"); ax.set(xlim=(0, 1), ylim=(0, 1))
    ax.set_title("F3 · Earth ↔ Mars  (0.37–2.68 au)", fontsize=11)
    node(ax, 0.15, 0.55, "Earth\nmemory node", "C0"); node(ax, 0.85, 0.55, "Mars\nmemory node", "C3")
    node(ax, 0.5, 0.82, "relay(s)\nsource + memory", "C1")
    arrow(ax, 0.26, 0.60, 0.40, 0.78, "C2", ls="--"); arrow(ax, 0.60, 0.78, 0.74, 0.60, "C2", ls="--")
    arrow(ax, 0.26, 0.50, 0.74, 0.50, "C3", lw=3)
    lo, hi = one_way_delay_s(EARTH_MARS_MIN_M), one_way_delay_s(EARTH_MARS_MAX_M)
    eta = geometric_transmittance(EARTH_MARS_MIN_M, 810e-9, 0.15, 10.0)
    ax.text(0.5, 0.40, f"two classical bits: {fmt_s(lo)} to {fmt_s(hi)} one way\nmemory must hold ≥ {fmt_s(2*lo)}–{fmt_s(2*hi)}\ndiffraction to a 10 m dish at closest: ~{eta:.0e}", ha="center", fontsize=9)
    ax.text(0.5, 0.25, "What to look for:\n• fidelity vs storage time crossing 2/3\n• pairs per day with multiplexing\n• messenger that fails closed", ha="center", va="top", fontsize=9, color="0.3")
    ax.text(0.5, 0.03, "Not done anywhere (TRL 1–2).\nOur version: E1 delayed-bits bench, E3 scheduling sim, E5 messenger.", ha="center", fontsize=8, color="C3")
    finish(fig, args)


if __name__ == "__main__":
    main()
