"""The nested repeater protocol sampled 20 000 times against the closed-form waiting time it is usually summarized by:
the distribution of times to the first end-to-end pair for an 8-segment, 800 km chain, and the ratio of the sampled
mean to the closed form for 1 to 8 segments. The closed form is exact without nesting and a few percent conservative
with it."""
from __future__ import annotations

import numpy as np

from qll.network.repeater_chain import memory_chain
from qll.network.repeater_montecarlo import sample_chain_time_s
from qll.viz._common import cli, finish

CASES = [(300.0, 0), (100.0, 1), (400.0, 2), (800.0, 3)]
RUNS = 20000


def main() -> None:
    args = cli(__doc__)
    import matplotlib.pyplot as plt

    fig, (a, b) = plt.subplots(1, 2, figsize=(12.5, 4.3), gridspec_kw={"width_ratios": [1.35, 1]})
    ratios, errs = [], []
    for L, n in CASES:
        rng = np.random.default_rng(5)
        x = np.array([sample_chain_time_s(L, n, rng) for _ in range(RUNS)])
        closed = memory_chain(L, n, 1e9).hold_time_s
        ratios.append(x.mean() / closed); errs.append(x.std(ddof=1) / np.sqrt(RUNS) / closed)
        if n == 3:
            a.hist(x, bins=np.logspace(np.log10(x.min()), np.log10(x.max()), 60), color="C0", alpha=0.75)
            a.axvline(x.mean(), color="C0", lw=2, label=f"sampled mean {x.mean():.1f} s")
            a.axvline(closed, color="C3", lw=2, ls="--", label=f"closed form {closed:.1f} s")
            a.axvline(np.median(x), color="0.4", lw=1.2, ls=":", label=f"median {np.median(x):.1f} s")
    a.set(xscale="log", xlabel="time to the first end-to-end pair (s)", ylabel=f"runs (of {RUNS:,})",
          title="800 km, 8 segments, P_s = 0.5: one pair takes seconds to minutes")
    a.legend(fontsize=8.5)
    segs = [2**n for _, n in CASES]
    b.errorbar(range(len(CASES)), ratios, yerr=[2 * e for e in errs], fmt="o", color="C0", ms=8, capsize=4)
    b.axhline(1, color="C3", ls="--", lw=1.2)
    b.set_xticks(range(len(CASES)), [f"{s} seg\n{int(L)} km" for s, (L, _) in zip(segs, CASES)])
    for k, r in enumerate(ratios):
        b.text(k + 0.12, r, f"{r:.3f}", va="center", fontsize=9)
    b.set(ylabel="sampled mean / closed form", ylim=(0.85, 1.05), title="Exact without nesting, conservative with it")
    fig.text(0.5, -0.02, "qll/network/repeater_montecarlo.py samples the protocol exactly (geometric attempts, the later of two "
             "children, restart after a failed swap); error bars are 2 standard errors.", ha="center", fontsize=8.5, color="0.3")
    finish(fig, args)


if __name__ == "__main__":
    main()
