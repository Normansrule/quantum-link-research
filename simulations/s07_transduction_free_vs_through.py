"""S07 — Transduction-free hybrid link versus a transduction-based one (proposal E7; trade study 'memory vs T').

Architecture A (through transduction): a microwave processor emits a qubit-entangled microwave photon,
a transducer converts it with efficiency eta_t and added noise n_add, then the optical channel carries it.
Architecture B (transduction-free): a native optical emitter (NV/SiV, ion, or rare-earth ensemble) emits
directly into the same channel. Per attempt, A's herald probability is scaled by eta_t and its fidelity is
capped by eta_t/(eta_t + n_add) [lauk2020]; B pays instead with its emitter's zero-phonon-line fraction and
its memory's efficiency (memory_decoherence table). Both feed the same Werner-state teleportation fidelity
(2f+1)/3. Reference: Lauk et al. (2020); Mirhosseini et al. (2020).
"""
from __future__ import annotations

import numpy as np

from qll.channels.free_space_diffraction import geometric_transmittance
from qll.circuits.teleportation import analytic_average_fidelity
from qll.hardware.nv_node import NvNode
from qll.hardware.transduction import OPTIMISTIC_2025, STATE_OF_THE_ART_2020, TARGET, Transducer

CHANNEL_ETA = geometric_transmittance(1.2e6, 1550e-9, 0.15, 1.0) * 0.1     # a LEO-class optical leg incl. optics


def architecture_a(t: Transducer, f_source: float = 0.95, attempts_hz: float = 1e6, eta_det: float = 0.7) -> tuple[float, float]:
    """(pairs per second, teleportation fidelity) through a transducer."""
    p_herald = 0.5 * (t.efficiency * CHANNEL_ETA * eta_det) ** 2
    f = f_source * t.signal_fraction()
    return p_herald * attempts_hz, analytic_average_fidelity(max(f, 0.25))


def architecture_b(node: NvNode, f_source: float = 0.95, eta_det: float = 0.7) -> tuple[float, float]:
    eta = node.effective_zpl() * node.collection_efficiency * eta_det * CHANNEL_ETA
    return 0.5 * eta**2 * node.attempt_rate_hz, analytic_average_fidelity(f_source)


def main() -> None:
    from _common import report, save
    import matplotlib.pyplot as plt

    rows = []
    for t in (STATE_OF_THE_ART_2020, OPTIMISTIC_2025, TARGET):
        r, F = architecture_a(t)
        rows.append((f"A via {t.name}", f"{r:.2e} pairs/s, F = {F:.3f}, {'entanglement survives' if t.preserves_entanglement() else 'NO entanglement'}"))
    for node, lab in ((NvNode(), "B: bare NV (ZPL 3 %)"), (NvNode(purcell_factor=30), "B: NV in cavity (Purcell 30)"), (NvNode(zpl_fraction=0.9, collection_efficiency=0.3, purcell_factor=1.0), "B: SiV-class emitter")):
        r, F = architecture_b(node)
        rows.append((lab, f"{r:.2e} pairs/s, F = {F:.3f}"))
    report("S07 transduction-free vs through-transduction (LEO-class optical leg)", rows)

    fig, ax = plt.subplots(figsize=(7.5, 4.4))
    eta_t = np.logspace(-4, 0, 200)
    for n_add in (1.0, 0.1, 0.01):
        F = [analytic_average_fidelity(max(0.95 * e / (e + n_add), 0.25)) for e in eta_t]
        ax.semilogx(eta_t, F, lw=2, label=f"through transducer, n_add = {n_add}")
    ax.axhline(2 / 3, ls=":", color="k"); ax.text(1.2e-4, 0.675, "classical limit 2/3", fontsize=8)
    ax.axhline(analytic_average_fidelity(0.95), ls="--", color="C3"); ax.text(1.2e-4, analytic_average_fidelity(0.95) + 0.01, "transduction-free (same source, f = 0.95)", fontsize=8, color="C3")
    for t in (STATE_OF_THE_ART_2020, OPTIMISTIC_2025, TARGET):
        ax.plot(t.efficiency, analytic_average_fidelity(max(0.95 * t.signal_fraction(), 0.25)), "o", color="0.3"); ax.text(t.efficiency * 1.2, analytic_average_fidelity(max(0.95 * t.signal_fraction(), 0.25)) - 0.03, t.name.split(" [")[0], fontsize=7)
    ax.set(xlabel="transducer efficiency η_t", ylabel="teleportation fidelity after the link", ylim=(0.45, 1.0), title="S07: what a transducer costs in fidelity (rate is a separate ×η_t² penalty)")
    ax.legend(fontsize=8, loc="lower right")
    ax.text(0.01, 0.03, "What to look for: a transducer helps only when n_add ≪ η_t; the transduction-free line\nis flat because the emitter already speaks optics. Rate through a transducer falls as η_t².", transform=ax.transAxes, fontsize=8, color="0.3")
    save(fig, "transduction_tradeoff")


if __name__ == "__main__":
    import sys; sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent)); main()
