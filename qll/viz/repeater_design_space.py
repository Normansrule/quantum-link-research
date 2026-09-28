"""Where a fiber repeater chain is worth building: for each distance and memory coherence time, how much faster the
best chain (up to 16 segments, with or without BBPSSW purification) delivers pairs good enough to teleport with
(F > 2/3) than direct transmission does; the minimum memory time that makes such a chain possible; and which
demonstrated memories, once their retrieval efficiency is counted, reach that region."""
from __future__ import annotations

import numpy as np

from qll.network.memory_decoherence import MEMORY_TABLE
from qll.network.purified_chain import minimum_useful_memory_s, useful_advantage_map, useful_distance_range_km
from qll.viz._common import cli, finish


def main() -> None:
    args = cli(__doc__)
    import matplotlib.pyplot as plt
    from matplotlib.colors import TwoSlopeNorm

    L = np.logspace(2, np.log10(3000), 70)
    T = np.logspace(-1, 5, 70)
    M = useful_advantage_map(L, T)
    fig, (a, b) = plt.subplots(1, 2, figsize=(13, 4.8), gridspec_kw={"width_ratios": [1.35, 1]})
    a.set_facecolor("#e9e9ef")
    a.contourf(L, T, np.isnan(M).astype(float), levels=[0.5, 1.5], colors="none", hatches=["////"])
    pcm = a.pcolormesh(L, T, np.ma.masked_invalid(M), cmap="RdYlGn", norm=TwoSlopeNorm(0, -5, 30), shading="auto",
                        linewidth=0, antialiased=False, rasterized=True)
    fig.colorbar(pcm, ax=a, label="log₁₀(useful chain rate / direct rate)")
    Lm = np.logspace(np.log10(400), np.log10(3000), 30)
    Tm = [minimum_useful_memory_s(float(x)) for x in Lm]
    a.plot(Lm, Tm, color="k", lw=2, label="minimum memory for a useful chain that beats direct")
    for p in MEMORY_TABLE:
        if not 0.1 <= p.lifetime_s <= 1e5:
            continue
        a.axhline(p.lifetime_s, color="0.25", lw=0.7, ls=":")
        a.text(102, p.lifetime_s * 1.15, p.name, fontsize=7, color="0.2")
    a.set(xscale="log", yscale="log", xlabel="fiber distance (km)", ylabel="memory coherence time T (s)",
          title="Hatched: no chain delivers F > 2/3", xlim=(100, 3000), ylim=(0.1, 1e5))
    a.legend(fontsize=8, loc="lower right")

    names, ranges = [], []
    for p in MEMORY_TABLE:
        names.append(f"{p.name}\nT = {p.lifetime_s:g} s, retrieval {100 * p.efficiency:g} %")
        ranges.append(useful_distance_range_km(p.lifetime_s, p.efficiency))
    for k, r in enumerate(ranges):
        if r:
            b.barh(k, r[1] - r[0], left=r[0], color="C2", height=0.55)
            b.text(r[1] * 1.05, k, f"{r[0]:.0f}–{r[1]:.0f} km", va="center", fontsize=8.5)
        else:
            b.text(120, k, "never useful and faster", va="center", fontsize=8.5, color="C3")
    b.set_yticks(range(len(names)), names, fontsize=7.5)
    b.set(xscale="log", xlim=(100, 20000), xlabel="fiber distance (km)", title="Demonstrated memories as repeater nodes")
    b.set_ylim(len(names) - 0.5, -0.5)
    fig.text(0.5, -0.03, "Closed-form model (qll/network/purified_chain.py): 1 MHz attempts, p_src = 0.05, P_s = 0.5 × retrieval², "
             "f₀ = 0.95, 0.2 dB/km; best of 1–16 segments and 0–2 BBPSSW rounds per level.", ha="center", fontsize=8.5, color="0.3")
    finish(fig, args)


if __name__ == "__main__":
    main()
