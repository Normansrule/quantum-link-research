"""Site B: random measurement bases, detection with finite efficiency, background clicks, and misalignment.

Model
-----
A photon that arrives produces a click with probability 10^(-loss_rx/10) eta_det. Where Site B's basis matches the
basis the photon carries, the result is that bit, flipped with the misalignment probability e_mis; otherwise it is
random [bennett1984]. A gate without a signal click fires on background (dark counts plus cross-talk) with
probability p_bg and gives a random bit. Double clicks, afterpulsing, dead time, and detector-efficiency mismatch are
not modelled (systems/see510/03_assumptions.md).
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from qll.link.config import LinkConfig
from qll.link.models import background_click_prob
from qll.link.quantum_channel import ChannelOutput


@dataclass(frozen=True)
class Detections:
    detected: np.ndarray        # bool: any click in the gate
    signal: np.ndarray          # bool: the click came from the photon
    bits: np.ndarray            # int8 results (meaningful where detected)
    bases: np.ndarray           # int8 Site B bases


class SiteB:
    def __init__(self, c: LinkConfig, rng: np.random.Generator):
        self.c, self.rng = c, rng

    def measure(self, ch: ChannelOutput) -> Detections:
        c, n = self.c, len(ch.arrived)
        bases = self.rng.integers(0, 2, n, dtype=np.int8)
        eta_b = 10 ** (-c.receiver_loss_db / 10) * c.detector_efficiency
        if ch.photons_arrived is None:
            signal = ch.arrived & (self.rng.random(n) < eta_b)
        else:                                                   # any of k arriving photons may fire the detector
            signal = self.rng.random(n) < 1 - (1 - eta_b) ** ch.photons_arrived
        background = ~signal & (self.rng.random(n) < background_click_prob(c))
        random_bits = self.rng.integers(0, 2, n, dtype=np.int8)
        flips = self.rng.random(n) < c.misalignment_error
        bits = np.where(bases == ch.states.bases, ch.states.bits, random_bits)
        bits = np.where(signal & flips, 1 - bits, bits)
        bits = np.where(background, random_bits, bits).astype(np.int8)
        return Detections(signal | background, signal, bits, bases)
