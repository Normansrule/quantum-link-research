"""The quantum channel: a fiber of configurable length and attenuation, with an optional adversary at its input.

Model
-----
Each photon survives the fiber independently with probability T_ch = 10^(-(alpha L + loss_extra)/10)
[qll/channels/fiber_loss.py]; the polarization (or time-bin) state that survives is unchanged, because the
misalignment error is charged at Site B. Attenuation alone does not describe a real fiber: polarization drift,
dispersion, and Raman noise from co-propagating classical channels are represented only through the misalignment
error and the cross-talk click probability (systems/see510/03_assumptions.md).
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from qll.link.adversary import AdversaryRecord, InterceptResend
from qll.link.config import LinkConfig
from qll.link.models import channel_transmittance
from qll.link.site_a import PreparedStates


@dataclass(frozen=True)
class ChannelOutput:
    states: PreparedStates       # what arrives (after any adversary)
    arrived: np.ndarray          # bool mask: at least one photon survived the fiber
    adversary: AdversaryRecord | None
    photons_arrived: np.ndarray | None = None   # weak-coherent sources: photons reaching Site B per pulse


class FiberChannel:
    def __init__(self, c: LinkConfig, rng: np.random.Generator, adversary: InterceptResend | None = None):
        self.c, self.rng, self.adversary = c, rng, adversary
        self.transmittance = channel_transmittance(c)

    def transmit(self, s: PreparedStates) -> ChannelOutput:
        rec, bypass = None, None
        if self.adversary is not None:
            out = self.adversary.act(s)
            s, rec = out[0], out[1]
            bypass = out[2] if len(out) > 2 else None      # pulses the adversary forwards over her own lossless line
        if s.photons is None:
            arrived = self.rng.random(len(s.bits)) < self.transmittance
            return ChannelOutput(s, arrived, rec)
        k = self.rng.binomial(s.photons, self.transmittance)   # each photon survives independently
        if bypass is not None:
            k = np.where(bypass, s.photons, k)
        return ChannelOutput(s, k > 0, rec, k)
