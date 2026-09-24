"""Rate versus distance for direct transmission, a first-generation memory chain, and the all-photonic
(third-generation-like, no memory) scheme, from qll.network.repeater_chain; PLOB capacity for reference."""
from __future__ import annotations

import numpy as np

from qll.channels.fiber_loss import transmittance
from qll.network.repeater_chain import all_photonic_chain, direct_rate_hz, memory_chain
from qll.qkd.plob_bound import plob_bits_per_use
from qll.viz._common import cli, finish


def main() -> None:
    args = cli(__doc__)
    import matplotlib.pyplot as plt

    L = np.logspace(1.5, 3.7, 250)
    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    ax.loglog(L, [direct_rate_hz(x) for x in L], "k", lw=2, label="direct, 1 GHz source × 5 % pairs")
    ax.loglog(L, [plob_bits_per_use(transmittance(x)) * 1e9 for x in L], "k:", lw=1.5, label="PLOB capacity × 1 GHz")
    ax.loglog(L, [max(memory_chain(x, 3, 1.0).rate_hz, 1e-9) for x in L], lw=2, label="gen-1 memory chain, 8 segments, T₂ = 1 s")
    ax.loglog(L, [max(memory_chain(x, 4, 3600.0).rate_hz, 1e-9) for x in L], lw=2, label="gen-1 memory chain, 16 segments, T₂ = 1 h")
    ax.loglog(L, [all_photonic_chain(x, 16) for x in L], lw=2, label="all-photonic, 16 segments, 8-fold redundancy (no memory)")
    ax.set(xlabel="distance (km)", ylabel="pairs per second", ylim=(1e-6, 1e9), title="Repeater generations: what each buys and at what cost")
    ax.legend(fontsize=8, loc="lower left")
    ax.text(0.99, 0.97, "What to look for: memory chains beat direct only past a crossover and die when the hold time\nexceeds T₂; the all-photonic scheme needs no memory but pays ~8 photons per segment per attempt.", transform=ax.transAxes, ha="right", va="top", fontsize=8, color="0.3")
    finish(fig, args)


if __name__ == "__main__":
    main()
