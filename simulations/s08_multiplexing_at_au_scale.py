"""S08 — How much multiplexing an Earth–Mars link needs (proposal E9; Flagship F3).

Physics: pairs per day = R_src * M * eta_total * duty, with eta_total from the Gaussian diffraction law for the
long leg, M parallel modes (time bins, frequencies, or spatial modes) each carrying an independent attempt, and
a duty cycle for pointing and conjunction. The needed M for a target (1 pair/s; or a 1 kbit/day secret key at a
DI rate of ~0.5 bit per pair) follows by division. Reference: Sinclair et al. (2014) for multimode memories;
Mohageg et al. (2022) for the DSQL geometry.
"""
from __future__ import annotations

import math

import numpy as np

from qll.channels.free_space_diffraction import geometric_transmittance
from qll.constants.astro import AU_METERS, EARTH_MARS_MAX_M, EARTH_MARS_MIN_M

ETA_OTHER = 0.05      # optics, detector, pointing at AU scale
DUTY = 0.3


def pairs_per_day(L_m: float, tx_waist_m: float, rx_diameter_m: float, R_src: float, M: int, lam: float = 1550e-9) -> float:
    eta = geometric_transmittance(L_m, lam, tx_waist_m, rx_diameter_m) * ETA_OTHER
    return R_src * M * eta * 86400 * DUTY


def multiplexing_needed(L_m: float, tx_waist_m: float, rx_diameter_m: float, R_src: float, target_pairs_per_s: float) -> float:
    per_mode = pairs_per_day(L_m, tx_waist_m, rx_diameter_m, R_src, 1) / 86400
    return target_pairs_per_s / per_mode


def main() -> None:
    from _common import report, save
    import matplotlib.pyplot as plt

    rows = []
    for L, name in ((EARTH_MARS_MIN_M, "Mars min"), (EARTH_MARS_MAX_M, "Mars max")):
        for w0, D in ((0.15, 1.0), (0.5, 10.0)):
            M1 = multiplexing_needed(L, w0, D, 1e8, 1.0)
            Mk = multiplexing_needed(L, w0, D, 1e8, 1000 / 0.5 / 86400)   # 1 kbit/day at 0.5 bit/pair
            rows.append((f"{name}, {w0*2:.1f} m tx → {D:.0f} m rx, 1e8 pairs/s", f"M for 1 pair/s: {M1:.1e}; M for 1 kbit/day: {Mk:.1e}"))
    report("S08 multiplexing needed at AU scale (η_other = 0.05, duty 0.3)", rows)

    fig, ax = plt.subplots(figsize=(7.5, 4.4))
    D = np.logspace(-0.3, 1.5, 200)
    for w0, lab in ((0.15, "30 cm transmitter"), (0.5, "1 m transmitter"), (1.5, "3 m transmitter")):
        ax.loglog(D, [multiplexing_needed(EARTH_MARS_MAX_M, w0, d, 1e8, 1.0) for d in D], lw=2, label=f"{lab}, Mars max, 1 pair/s")
    for m, t in ((1e3, "10³ (time-bin + frequency, demonstrated)"), (1e6, "10⁶ (research target)")):
        ax.axhline(m, ls="--", color="0.6"); ax.text(0.55, m * 1.3, t, fontsize=8, color="0.4")
    ax.axvline(10, ls=":", color="0.6"); ax.text(10.3, 1e1, "10 m dish", rotation=90, fontsize=8, color="0.4")
    ax.set(xlabel="receiver diameter (m)", ylabel="multiplexing factor M needed", ylim=(1, 1e9), title="S08: apertures buy M², multiplexing buys M — both are needed at Mars")
    ax.legend(fontsize=8, loc="upper right")
    ax.text(0.01, 0.03, "What to look for: with a 1 m transmitter and a 10 m receiver, 1 pair/s at Mars max needs M ~ 10²–10³;\nwith 30 cm optics it needs M ~ 10⁵. Multiplexing at 10³ is demonstrated in memories; 10⁶ is not.", transform=ax.transAxes, fontsize=8, color="0.3")
    save(fig, "multiplexing_au")


if __name__ == "__main__":
    import sys; sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent)); main()
