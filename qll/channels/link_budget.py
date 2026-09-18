"""The whole link is a product of independent efficiencies plus additive background.

Physics
-------
eta_total = eta_geo * eta_atm * eta_point * eta_optics * eta_det; detected rate R = R_src * eta_total;
background N from thermal_background.py plus scattered light; QBER floor from background
Q_bg = N tau / (2 (R + N tau)) [ma2007]. In decibels, loss = -10 log10(eta). The class carries
distributions implicitly through elevation: a pass is a sweep of elevation angles, and the
must-pass target of Phase 3 is to land within +-3 dB of the published Micius and Jinan-1 losses
[yin2017] [liao2017] [li2025jinan].
"""
from __future__ import annotations

import math
from dataclasses import dataclass

from qll.channels.atmosphere import atmospheric_transmittance
from qll.channels.free_space_diffraction import beam_radius_m, geometric_transmittance
from qll.channels.pointing_jitter import pointing_efficiency

EARTH_RADIUS_M = 6_371_000.0


def slant_range_m(altitude_m: float, elevation_deg: float) -> float:
    """Range from a ground station to a satellite at altitude h seen at elevation e (spherical Earth)."""
    e = math.radians(elevation_deg)
    R = EARTH_RADIUS_M
    return -R * math.sin(e) + math.sqrt((R * math.sin(e)) ** 2 + 2 * R * altitude_m + altitude_m**2)


@dataclass(frozen=True)
class LinkBudget:
    lambda_m: float
    w0_m: float            # transmitter beam waist (effective)
    D_rx_m: float          # receiver aperture diameter
    sigma_point_rad: float # pointing jitter, per axis
    eta_optics: float      # transmitter + receiver optics, filters, coupling
    eta_det: float         # detector efficiency
    tau_zenith: float | None = None

    def factors(self, L_m: float, elevation_deg: float = 90.0) -> dict[str, float]:
        w = beam_radius_m(L_m, self.lambda_m, self.w0_m)
        return {
            "geo": geometric_transmittance(L_m, self.lambda_m, self.w0_m, self.D_rx_m),
            "atm": atmospheric_transmittance(elevation_deg, self.lambda_m, self.tau_zenith),
            "point": pointing_efficiency(self.sigma_point_rad, L_m, w),
            "optics": self.eta_optics,
            "det": self.eta_det,
        }

    def eta_total(self, L_m: float, elevation_deg: float = 90.0) -> float:
        out = 1.0
        for v in self.factors(L_m, elevation_deg).values():
            out *= v
        return out

    def loss_db(self, L_m: float, elevation_deg: float = 90.0) -> float:
        return -10.0 * math.log10(self.eta_total(L_m, elevation_deg))

    def detected_rate(self, R_src: float, L_m: float, elevation_deg: float = 90.0) -> float:
        return R_src * self.eta_total(L_m, elevation_deg)

    @staticmethod
    def qber_from_background(R_det: float, N_bg: float, gate_s: float, rep_rate_hz: float) -> float:
        """Background-induced error floor: per gated pulse the signal click probability is R_det/rep_rate and
        the background click probability is N_bg*gate; half of the background clicks are wrong [ma2007]."""
        p_sig, p_bg = R_det / rep_rate_hz, N_bg * gate_s
        return 0.5 * p_bg / (p_sig + p_bg) if (p_sig + p_bg) > 0 else 0.5


# Published configurations, for the must-pass tests. Values as reported or as documented in the reviews.
MICIUS_2017 = LinkBudget(lambda_m=810e-9, w0_m=0.026, D_rx_m=1.2, sigma_point_rad=1.2e-6, eta_optics=0.25, eta_det=0.5)
"""Micius entanglement downlink: 300 mm transmitter with the reported ~10 urad divergence (effective waist ~2.6 cm), 1.2 m Delingha receiver,
~1.2 urad fine pointing, night; reported total loss 64-82 dB over a pass at 500-2000 km [yin2017]."""

JINAN1_2025 = LinkBudget(lambda_m=850e-9, w0_m=0.06, D_rx_m=0.28, sigma_point_rad=1.0e-6, eta_optics=0.3, eta_det=0.55)
"""Jinan-1 decoy-state downlink: 23 kg payload, 280 mm portable receiver, ~1 urad fine pointing
[li2025jinan]; per-pass channel loss reported in the 40-60 dB range (TODO: verify exact figures)."""
