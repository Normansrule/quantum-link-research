"""BB84 secret fraction r(Q) = 1 − 2h₂(Q) [shor2000] and the 11% threshold, next to the
PLOB capacity K(η) = −log₂(1 − η) [pirandola2017]."""
from __future__ import annotations

import numpy as np

from qll.qkd.key_rate import bb84_qber_threshold, bb84_rate_per_sifted_bit
from qll.qkd.plob_bound import plob_bits_per_use
from qll.viz._common import cli, finish


def main() -> None:
    args = cli(__doc__)
    import matplotlib.pyplot as plt

    fig, (a, b) = plt.subplots(1, 2, figsize=(9, 3.8))
    Q = np.linspace(0, 0.2, 400)
    a.plot(Q * 100, [bb84_rate_per_sifted_bit(q) for q in Q], lw=2)
    qt = bb84_qber_threshold()
    a.axvline(qt * 100, ls="--", color="0.5")
    a.text(qt * 100 + 0.3, 0.6, f"threshold {qt*100:.2f}%", color="0.4")
    a.set(xlabel="QBER Q (%)", ylabel="secret bits per sifted bit", title="r = 1 − 2 h₂(Q)")
    eta = np.logspace(-8, -0.01, 400)
    b.loglog(eta, [plob_bits_per_use(e) for e in eta], lw=2, label="PLOB  −log₂(1−η)")
    b.loglog(eta, eta / np.log(2), ls=":", label="η / ln 2 (η ≪ 1)")
    b.set(xlabel="channel transmittance η", ylabel="secret bits per use", title="repeaterless capacity")
    b.legend()
    finish(fig, args)


if __name__ == "__main__":
    main()
