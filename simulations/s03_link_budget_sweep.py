"""S03 — Photons per second at the receiver vs distance (Flagship F2 stage S1, F3 stage S1 input).

Physics: rate = R_source · η_geo · η_atm · η_point · η_optics · η_det. Fiber uses 10^(−αL/10).
Free space uses the far-field diffraction law from qll.channels.free_space_diffraction; atmosphere
and pointing are fixed factors here (Phase 3 makes them models). Reference: Bourgoin et al. (2013).
"""
from __future__ import annotations

import numpy as np

from qll.channels.fiber_loss import transmittance
from qll.channels.free_space_diffraction import geometric_transmittance
from qll.constants.astro import EARTH_MARS_MAX_M, EARTH_MARS_MIN_M

R_SRC = 1e8          # pairs per second, bright SPDC source
ETA_ATM, ETA_POINT, ETA_OPT, ETA_DET = 0.5, 0.5, 0.3, 0.7


def free_space_rate(L_m: float, w0: float, D: float, lam: float = 810e-9, atm: float = ETA_ATM) -> float:
    return R_SRC * geometric_transmittance(L_m, lam, w0, D) * atm * ETA_POINT * ETA_OPT * ETA_DET


def fiber_rate(L_km: float, alpha: float = 0.2) -> float:
    return R_SRC * transmittance(L_km, alpha) * ETA_OPT * ETA_DET


def main() -> None:
    from _common import report, save
    import matplotlib.pyplot as plt

    L = np.logspace(0, 8.5, 400)
    leo = [free_space_rate(x * 1e3, 0.15, 1.0) for x in L]
    mars10 = [free_space_rate(x * 1e3, 0.15, 10.0, 1550e-9, 1.0) for x in L]
    fib = [fiber_rate(x) for x in L]
    report("S03 link budget sweep", [
        ("LEO 1200 km, 15 cm → 1 m, 810 nm: photons/s", f"{free_space_rate(1.2e6, 0.15, 1.0):.2e}"),
        ("Mars min, 15 cm → 10 m, 1550 nm, no atm: photons/s", f"{free_space_rate(EARTH_MARS_MIN_M, 0.15, 10.0, 1550e-9, 1.0):.2e}"),
        ("Mars max, same: photons/s", f"{free_space_rate(EARTH_MARS_MAX_M, 0.15, 10.0, 1550e-9, 1.0):.2e}"),
        ("fiber 100 km at 0.2 dB/km: photons/s", f"{fiber_rate(100):.2e}")])
    fig, ax = plt.subplots(figsize=(7.5, 4.4))
    ax.loglog(L, fib, lw=2, label="fiber 0.2 dB/km")
    ax.loglog(L, leo, lw=2, label="free space, 15 cm → 1 m, 810 nm")
    ax.loglog(L, mars10, lw=2, label="free space, 15 cm → 10 m, 1550 nm")
    for y, t in ((1, "1 photon/s"), (1 / 3600, "1 per hour"), (1 / 86400, "1 per day")):
        ax.axhline(y, ls=":", color="0.6"); ax.text(1.2, y * 1.4, t, fontsize=8, color="0.4")
    for x, t in ((1200, "LEO"), (3.844e5, "Moon"), (EARTH_MARS_MIN_M / 1e3, "Mars min"), (EARTH_MARS_MAX_M / 1e3, "Mars max")):
        ax.axvline(x, ls="--", color="0.7"); ax.text(x * 1.1, 1e7, t, rotation=90, fontsize=8, color="0.4")
    ax.set(xlabel="distance (km)", ylabel="photons per second at the receiver", ylim=(1e-8, 1e9), title="S03: what a 10⁸ pairs/s source delivers")
    ax.legend(fontsize=8, loc="lower left"); save(fig, "link_budget")


if __name__ == "__main__":
    import sys; sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent)); main()
