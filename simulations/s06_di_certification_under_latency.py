"""S06 — Device-independent certification under planetary latency (proposal E10; Flagship F3, stage S5).

Physics: a DI key needs the CHSH value S, which needs the settings and outcomes of both parties exchanged
classically; they arrive after one light time, so rounds accumulate in a buffer for a round trip before
S can be evaluated. Finite-key effects then depend on how many rounds fit in that window: n = R_pairs * 2d/c.
The simulation samples CHSH rounds with settings from a declared EntropySource (Stim-backed), holds each
party's record in a ClassicalMessage until the light time has passed, then computes S, the finite-key rate,
and the minimum pair rate at which Mars can certify a key at all. Reference: Acín et al. (2007);
Arnon-Friedman et al. (2018); Nadlinger et al. (2022).
"""
from __future__ import annotations

import math

import numpy as np

from qll.channels.light_time_delay import ClassicalMessage, NotYetArrived, round_trip_delay_s
from qll.circuits.chsh import chsh_sampled_stim
from qll.constants.astro import EARTH_MARS_MAX_M, EARTH_MARS_MIN_M
from qll.hardware.randomness import NumpyPRNG
from qll.qkd.e91 import di_rate_finite_key, di_rate_per_round, rounds_for_positive_di_key


def certify_after_light_time(n_rounds: int, distance_m: float, seed: int = 0) -> tuple[float, float, float]:
    """Run n CHSH rounds, seal both records for the light time, and return (S, stderr, finite-key rate)."""
    S, err = chsh_sampled_stim(n_rounds, NumpyPRNG(seed), allow_pseudo=True, seed=seed)
    record = ClassicalMessage(payload=(n_rounds,), sent_at_s=0.0, distance_m=distance_m)
    try:
        record.receive(now_s=0.0)
        raise RuntimeError("records readable before arrival")
    except NotYetArrived:
        pass
    record.receive(now_s=record.earliest_arrival_s)         # S can be computed only now
    return S, err, di_rate_finite_key(S, 0.0, n_rounds)


def main() -> None:
    from _common import report, save
    import matplotlib.pyplot as plt

    S_ideal = 2 * math.sqrt(2)
    n_min = rounds_for_positive_di_key(S_ideal * 0.98, 0.01)       # a slightly imperfect device
    rt_max = round_trip_delay_s(EARTH_MARS_MAX_M)
    rows = [("asymptotic DI rate at S = 0.98·2√2, Q = 1 %", f"{di_rate_per_round(S_ideal*0.98, 0.01):.3f} bits/round"),
            ("rounds needed for a positive finite key (ε = 1e-10)", f"{n_min:,}"),
            ("pair rate needed to gather them in one Mars-max round trip", f"{n_min/rt_max:.1f} pairs/s"),
            ("Mars-max round trip", f"{rt_max/60:.1f} min")]
    S, err, r = certify_after_light_time(20000, EARTH_MARS_MIN_M, seed=1)
    rows.append(("sampled S from 20 000 rounds (records sealed for the light time)", f"{S:.3f} ± {err:.3f} → finite-key rate {r:.3f}"))
    report("S06 DI certification under latency", rows)

    fig, ax = plt.subplots(figsize=(7.5, 4.2))
    ns = np.logspace(3, 8, 200)
    for Sfrac, lab in ((1.0, "ideal S = 2√2"), (0.95, "S = 0.95·2√2"), (0.92, "S = 0.92·2√2")):
        ax.semilogx(ns, [di_rate_finite_key(S_ideal * Sfrac, 0.01, int(n)) for n in ns], lw=2, label=lab)
    for d, name in ((EARTH_MARS_MIN_M, "Mars min"), (EARTH_MARS_MAX_M, "Mars max")):
        for R, ls in ((1.0, ":"), (100.0, "--")):
            n = R * round_trip_delay_s(d)
            ax.axvline(n, ls=ls, color="0.5"); ax.text(n * 1.05, 0.02, f"{name}, {R:g} pair/s", rotation=90, fontsize=7, color="0.4")
    ax.set(xlabel="rounds accumulated before S can be evaluated (one round trip)", ylabel="finite-key DI rate (bits/round)", ylim=(0, 1),
           title="S06: device-independent key needs enough rounds per round trip")
    ax.legend(fontsize=8, loc="upper left")
    ax.text(0.99, 0.03, "What to look for: one Mars-max round trip at 1 pair/s holds ~2 700 rounds, enough for S ≥ 0.95·2√2 (2 535 needed)\nbut not for 0.92·2√2 (3 425); the rate, not the delay, decides whether Mars can certify.", transform=ax.transAxes, ha="right", fontsize=8, color="0.3")
    save(fig, "di_latency")


if __name__ == "__main__":
    import sys; sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent)); main()
