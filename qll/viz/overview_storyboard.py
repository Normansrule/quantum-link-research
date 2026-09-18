"""One-picture storyboard of the project for newcomers: qubit → photon → channel → light-time →
memory → teleportation, each panel drawn from the same qll functions the tests validate."""
from __future__ import annotations

import math

import numpy as np

from qll.channels.fiber_loss import transmittance
from qll.channels.free_space_diffraction import geometric_transmittance
from qll.channels.light_time_delay import one_way_delay_s
from qll.circuits.noise.thermal import bose_einstein_occupation
from qll.constants.astro import AU_METERS, EARTH_MARS_MAX_M, EARTH_MARS_MIN_M
from qll.viz._common import cli, finish


def main() -> None:
    args = cli(__doc__)
    import matplotlib.pyplot as plt
    from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch

    fig, axes = plt.subplots(2, 3, figsize=(13, 7.2))
    fig.suptitle("quantum-link-research in one picture: a qubit on a bench → a message to Mars", fontsize=14, y=0.99)

    # 1 qubit
    ax = axes[0, 0]
    ax.set_title("1  A qubit is a point on a sphere")
    ax.add_patch(Circle((0, 0), 1, fill=False, lw=1.5, color="0.6"))
    ax.plot([0, 0], [-1, 1], color="0.7", lw=1); ax.plot([-1, 1], [0, 0], color="0.7", lw=1)
    th = math.radians(55)
    ax.add_patch(FancyArrowPatch((0, 0), (math.sin(th), math.cos(th)), arrowstyle="->", mutation_scale=18, lw=2.5, color="C0"))
    ax.text(0.05, 1.08, "|0⟩", ha="center"); ax.text(0.05, -1.18, "|1⟩", ha="center")
    ax.text(0, -1.38, "|ψ⟩ = cos(θ/2)|0⟩ + e^{iφ} sin(θ/2)|1⟩", ha="center", fontsize=8, color="C0")
    ax.text(0, -1.62, "noise shrinks the arrow: T₁ pulls it to |0⟩, T₂ blurs the angle", ha="center", fontsize=8)
    ax.set(xlim=(-1.6, 1.6), ylim=(-1.8, 1.3)); ax.set_aspect("equal"); ax.axis("off")

    # 2 temperature
    ax = axes[0, 1]
    ax.set_title("2  Heat fills modes with noise photons")
    T = np.logspace(-3, 3, 200)
    ax.loglog(T, [max(bose_einstein_occupation(2 * math.pi * 5e9, t), 1e-40) for t in T], lw=2, label="5 GHz qubit")
    ax.loglog(T, [max(bose_einstein_occupation(2 * math.pi * 193e12, t), 1e-40) for t in T], lw=2, label="optical photon")
    ax.axvline(0.015, ls="--", color="0.6"); ax.axvline(300, ls="--", color="0.6")
    ax.text(0.017, 1e2, "fridge", fontsize=8, color="0.4"); ax.text(320, 1e2, "room", fontsize=8, color="0.4")
    ax.set(xlabel="temperature (K)", ylabel="thermal photons per mode n̄", ylim=(1e-40, 1e5)); ax.legend(fontsize=8, loc="lower right")

    # 3 channel loss
    ax = axes[0, 2]
    ax.set_title("3  Fiber loses exponentially, space only as 1/L²")
    L = np.logspace(0, 8.5, 300)
    ax.loglog(L, [transmittance(x, 0.2) for x in L], lw=2, label="fiber")
    ax.loglog(L, [geometric_transmittance(x * 1e3, 810e-9, 0.15, 1.0) for x in L], lw=2, label="free space")
    for x, n in ((1200, "satellite"), (3.844e5, "Moon"), (EARTH_MARS_MIN_M / 1e3, "Mars")):
        ax.axvline(x, ls="--", color="0.6"); ax.text(x * 1.2, 1e-3, n, rotation=90, fontsize=8, color="0.4")
    ax.set(xlabel="distance (km)", ylabel="fraction of photons that arrive", ylim=(1e-18, 2)); ax.legend(fontsize=8, loc="lower left")

    # 4 light time
    ax = axes[1, 0]
    ax.set_title("4  Classical bits take d/c: minutes to Mars")
    d = np.logspace(5, 12, 200)
    ax.loglog(d / 1e3, [one_way_delay_s(x) / 60 for x in d], lw=2)
    for x, n in ((3.844e8, "Moon 1.3 s"), (EARTH_MARS_MIN_M, "Mars min 3 min"), (AU_METERS, "1 au 8.3 min"), (EARTH_MARS_MAX_M, "Mars max 22 min")):
        ax.plot(x / 1e3, one_way_delay_s(x) / 60, "o", color="C3"); ax.text(x / 1e3 * 1.15, one_way_delay_s(x) / 60 * 0.6, n, fontsize=8)
    ax.set(xlabel="distance (km)", ylabel="one-way delay (minutes)")

    # 5 memory vs delay
    ax = axes[1, 1]
    ax.set_title("5  The memory must outlive the round trip")
    t = np.logspace(-3, 5, 300)
    for T2, lab in ((60, "NV ¹³C ~1 min"), (3600, "ion ~1 h"), (13.1 * 3600, "Eu:YSO 13 h")):
        F = 0.25 + (0.95 - 0.25) * np.exp(-t / T2)
        ax.semilogx(t, F, lw=2, label=lab)
    ax.axhline(2 / 3, ls=":", color="k"); ax.text(2e-3, 0.68, "classical limit 2/3", fontsize=8)
    ax.axvspan(2 * EARTH_MARS_MIN_M / 299792458, 2 * EARTH_MARS_MAX_M / 299792458, color="C3", alpha=0.12)
    ax.text(600, 0.3, "Mars round trip\n6–45 min", fontsize=8, color="C3", ha="center")
    ax.set(xlabel="storage time (s)", ylabel="teleportation fidelity F = (2f+1)/3", ylim=(0.2, 1.0)); ax.legend(fontsize=8, loc="upper right")

    # 6 protocol
    ax = axes[1, 2]
    ax.set_title("6  Teleportation: one Bell pair + two bits")
    ax.axis("off"); ax.set(xlim=(0, 10), ylim=(0, 10))
    for x, y, txt, c in ((0.5, 7.5, "Earth\n|ψ⟩ + half of\nBell pair", "C0"), (6.0, 7.5, "Mars\nother half\nin memory", "C1"),
                         (0.5, 3.0, "Bell\nmeasurement\n→ bits (i, j)", "C0"), (6.0, 3.0, "apply Zⁱ Xʲ\n→ |ψ⟩ arrives", "C1")):
        ax.add_patch(FancyBboxPatch((x, y), 3.4, 2.2, boxstyle="round,pad=0.1", fc=c, alpha=0.15, ec=c))
        ax.text(x + 1.7, y + 1.1, txt, ha="center", va="center", fontsize=8)
    ax.add_patch(FancyArrowPatch((3.9, 8.6), (6.0, 8.6), arrowstyle="<->", mutation_scale=14, lw=2, color="C2", ls="--"))
    ax.text(4.95, 9.0, "entanglement\n(no message)", ha="center", fontsize=7, color="C2")
    ax.add_patch(FancyArrowPatch((2.2, 7.4), (2.2, 5.3), arrowstyle="->", mutation_scale=14, lw=1.5, color="C0"))
    ax.add_patch(FancyArrowPatch((3.9, 4.1), (6.0, 4.1), arrowstyle="->", mutation_scale=14, lw=2.5, color="C3"))
    ax.text(4.95, 4.45, "2 classical bits\nat light speed\n3–22 min", ha="center", fontsize=7, color="C3")
    ax.text(5, 0.6, "nothing travels faster than light; the state is unusable until the bits arrive", ha="center", fontsize=8)
    finish(fig, args)


if __name__ == "__main__":
    main()
