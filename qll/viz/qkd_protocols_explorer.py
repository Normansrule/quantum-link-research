"""Rate versus channel transmittance for BB84 (decoy), MDI, and twin-field, against the PLOB bound:
which protocol wins at which loss, and where the repeaterless bound is beaten."""
from __future__ import annotations

import numpy as np

from qll.qkd.decoy_state import decoy_rate_per_pulse
from qll.qkd.mdi import mdi_rate_per_pulse
from qll.qkd.plob_bound import plob_bits_per_use
from qll.qkd.twin_field import twin_field_rate_per_pulse
from qll.qkd.cv_qkd import cv_rate_per_symbol
from qll.viz._common import cli, finish


def main() -> None:
    args = cli(__doc__)
    import matplotlib.pyplot as plt

    eta = np.logspace(-8, -0.05, 400)
    L_km = -10 * np.log10(eta) / 0.2
    fig, ax = plt.subplots(figsize=(8, 4.8))
    ax.loglog(L_km, [plob_bits_per_use(e) for e in eta], "k", lw=2, label="PLOB bound (repeaterless)")
    ax.loglog(L_km, [decoy_rate_per_pulse(e) for e in eta], lw=2, label="decoy-state BB84 (~η)")
    ax.loglog(L_km, [mdi_rate_per_pulse(e) for e in eta], lw=2, label="MDI-QKD (~η, no detector side channels)")
    ax.loglog(L_km, [twin_field_rate_per_pulse(e) for e in eta], lw=2, label="twin-field (~√η)")
    ax.loglog(L_km, [max(cv_rate_per_symbol(e, 0.01), 1e-13) for e in eta], lw=2, ls="--", label="CV-QKD GG02, ξ = 1 % (asymptotic)")
    ax.set(xlabel="fiber length at 0.2 dB/km (km)", ylabel="secret bits per pulse", ylim=(1e-12, 2),
           title="Which QKD protocol wins at which loss")
    ax.legend(fontsize=8, loc="lower left")
    ax.text(0.98, 0.97, "What to look for: decoy and MDI follow the bound's slope and sit below it;\ntwin-field has half the slope and crosses the bound near a few hundred km;\nall three die at the dark-count floor.", transform=ax.transAxes, ha="right", va="top", fontsize=8, color="0.3")
    finish(fig, args)


if __name__ == "__main__":
    main()
