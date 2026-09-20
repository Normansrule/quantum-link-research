"""Converting a microwave qubit to an optical photon: efficiency, added noise, and what survives.

Physics
-------
A transducer maps an input microwave mode to an optical mode with efficiency eta_t and adds n_add noise
photons referred to the input [lauk2020]. For a single-photon (or single-excitation) state the output is a
mixture of the converted photon and noise; the fraction of detected photons that are signal, and hence an
upper bound on the fidelity of any entanglement carried through the transducer, is
F <= eta_t / (eta_t + n_add) [lauk2020] [mirhosseini2020]. Entanglement survives only when n_add < eta_t
(roughly: more signal than noise per attempt); reported devices (2020-2025) span eta_t ~ 1e-3 to 1e-1 with
n_add from ~1 down to ~0.1 in the best pulsed demonstrations (TODO: verify current best). Cavity
electro-optomechanics at matched cooperativities: eta_t = 4 C_om C_em / (1 + C_om + C_em)^2, which reaches 1
only in the limit of large equal cooperativities [andrews2014].
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Transducer:
    efficiency: float          # eta_t, microwave photon -> optical photon
    added_noise: float         # n_add, noise photons per attempt referred to input
    bandwidth_hz: float = 1e6
    name: str = "transducer"

    def signal_fraction(self) -> float:
        """Upper bound on entanglement fidelity through the device: eta_t / (eta_t + n_add)."""
        return self.efficiency / (self.efficiency + self.added_noise) if (self.efficiency + self.added_noise) > 0 else 0.0

    def preserves_entanglement(self, threshold: float = 0.5) -> bool:
        return self.signal_fraction() > threshold


def matched_cooperativity_efficiency(C_om: float, C_em: float) -> float:
    return 4 * C_om * C_em / (1 + C_om + C_em) ** 2


# Representative points on the reported (eta_t, n_add) landscape; verify before citing in the thesis.
STATE_OF_THE_ART_2020 = Transducer(1e-3, 1.0, name="piezo-optomechanical 2020 [mirhosseini2020]")   # TODO: verify n_add
OPTIMISTIC_2025 = Transducer(0.1, 0.1, name="optimistic 2025 electro-optic (TODO: verify)")
TARGET = Transducer(0.5, 0.01, name="target for a network node")
