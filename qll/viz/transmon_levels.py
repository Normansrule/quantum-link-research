"""Transmon energy levels versus E_J/E_C: charge dispersion falls exponentially while
anharmonicity approaches −E_C, which is why transmons sit near E_J/E_C ≈ 50 [koch2007]."""
from __future__ import annotations

import numpy as np

from qll.viz._common import cli, finish


def transmon_levels(EJ: float, EC: float, ng: float, ncut: int = 30) -> np.ndarray:
    """Eigenvalues of H = 4E_C (n − n_g)² − E_J cos φ in the charge basis (exact diagonalization)."""
    n = np.arange(-ncut, ncut + 1)
    H = np.diag(4 * EC * (n - ng) ** 2) - 0.5 * EJ * (np.eye(2 * ncut + 1, k=1) + np.eye(2 * ncut + 1, k=-1))
    return np.linalg.eigvalsh(H)


def main() -> None:
    args = cli(__doc__)
    import matplotlib.pyplot as plt

    EC = 1.0
    ratios = np.linspace(1, 100, 120)
    disp, anh = [], []
    for r in ratios:
        e0 = transmon_levels(r * EC, EC, 0.0)[:3]
        e5 = transmon_levels(r * EC, EC, 0.5)[:3]
        disp.append(abs((e5[1] - e5[0]) - (e0[1] - e0[0])))
        anh.append((e0[2] - e0[1]) - (e0[1] - e0[0]))
    fig, (a, b) = plt.subplots(1, 2, figsize=(9.5, 3.8))
    a.semilogy(ratios, np.array(disp) / EC, lw=2)
    a.axvline(50, ls="--", color="0.5")
    a.set(xlabel="E_J / E_C", ylabel="charge dispersion of f01  (units of E_C)", title="charge noise sensitivity")
    b.plot(ratios, np.array(anh) / EC, lw=2, color="C1")
    b.axhline(-1, ls=":", color="0.5")
    b.axvline(50, ls="--", color="0.5")
    b.set(xlabel="E_J / E_C", ylabel="anharmonicity α / E_C", title="α → −E_C: still addressable")
    fig.suptitle("H = 4E_C (n − n_g)² − E_J cos φ   [Koch et al. 2007]")
    finish(fig, args)


if __name__ == "__main__":
    main()
