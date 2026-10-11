"""The Phase 1 link taken outdoors (milestones M3.2 and M3.3): the same 405 nm source and silicon photomultipliers,
now with a small transmitting telescope on one roof and a receiving telescope on another, a free-space path of
hundreds of metres to two kilometres, and the sky as a background.

Model
-----
The path transmittance is the product of independent factors [bourgoin2013]:
    geometric   eta_geo = 1 - exp(-2 (D/2)^2 / w(L)^2),  w(L) = w0 sqrt(1 + (L/z_R)^2)      (free_space_diffraction.py)
    pointing    eta_pt  = w^2 / (w^2 + 4 sigma^2 L^2)                                       (pointing_jitter.py)
    air         eta_air = 10^(-alpha L / 10), alpha in dB/km at ground level (Beer-Lambert) [andrews2005]
    coupling    the receiving telescope's field stop and fiber or detector coupling, in dB,
and the twin of qll/link/two_room.py takes their product as its path loss. The sky adds background through the
receiving telescope: a sky of spectral radiance L_lambda seen by an aperture A with a field of view Omega through a
filter of width d_lambda delivers N = L_lambda A Omega d_lambda / (h c / lambda) photons per second
(thermal_background.background_from_spectral_radiance), of which the receiver optics pass eta_rx and the detectors
see eta_det. Unpolarized skylight is shared evenly by the four detectors, so a basis pair receives half of it, and
a gate of tau adds 1 - exp(-N tau / 2) to the pair's dark-click probability. The sky radiance spans eight orders of
magnitude between a sunlit day and a dark night; the presets are orders of magnitude to be replaced by the
background you measure (P04, step 2). Turbulence makes the received power fluctuate (scintillation) around this
mean; for links of a few kilometres at night the mean is what sets the key [bourgoin2013].
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field, replace

from qll.channels.free_space_diffraction import beam_radius_m, geometric_transmittance
from qll.channels.pointing_jitter import pointing_efficiency
from qll.channels.thermal_background import background_from_spectral_radiance
from qll.link import models
from qll.link.config import LinkConfig
from qll.link.expected_session import expected_session
from qll.link.two_room import TwoRoomParts, config as two_room_config

SKY = {"sunlit day": 1e-1, "twilight": 1e-3, "city night": 1e-6, "dark site, moonless": 1e-8}   # W m^-2 sr^-1 nm^-1, orders of magnitude
RECEIVERS = {
    "sipm": TwoRoomParts(),                                                        # the P10 receiver, as built
    "spad": replace(TwoRoomParts(), sipm_pde=0.30, sipm_dark_hz=300.0, sipm_afterpulse=0.005),   # used avalanche-diode modules (Tier 3)
}


@dataclass(frozen=True)
class OutdoorParts:
    distance_m: float = 300.0
    tx_waist_m: float = 0.01               # beam waist after a small beam expander on the sending roof
    rx_aperture_m: float = 0.05            # receiving telescope (a 50 mm lens to start, a 100 mm telescope later)
    pointing_urad: float = 10.0            # residual jitter per axis on tripods with manual fine adjustment
    air_db_per_km: float = 1.0             # Rayleigh scattering at 405 nm plus a clear-air aerosol load
    coupling_loss_db: float = 3.0          # field stop and coupling onto the detectors
    sky_radiance: float = 1e-6             # W m^-2 sr^-1 nm^-1 (city night)
    filter_nm: float = 3.0                 # interference filter in front of the receiver
    fov_mrad: float = 1.0                  # full field of view set by the field stop
    receiver: TwoRoomParts = field(default_factory=TwoRoomParts)


def factors(p: OutdoorParts) -> dict[str, float]:
    lam = p.receiver.wavelength_m
    w = beam_radius_m(p.distance_m, lam, p.tx_waist_m)
    return {"beam_radius_m": w,
            "geometric": geometric_transmittance(p.distance_m, lam, p.tx_waist_m, p.rx_aperture_m),
            "pointing": pointing_efficiency(p.pointing_urad * 1e-6, p.distance_m, w),
            "air": 10 ** (-p.air_db_per_km * p.distance_m / 1000 / 10),
            "coupling": 10 ** (-p.coupling_loss_db / 10)}


def path_loss_db(p: OutdoorParts) -> float:
    f = factors(p)
    return -10 * math.log10(f["geometric"] * f["pointing"] * f["air"] * f["coupling"])


def sky_counts_per_s(p: OutdoorParts) -> float:
    """Skylight photons per second reaching all four detectors together."""
    r = p.receiver
    area = math.pi * (p.rx_aperture_m / 2) ** 2
    omega = math.pi * (p.fov_mrad * 1e-3 / 2) ** 2
    eta_rx = 10 ** (-r.receiver_loss_db / 10) * r.sipm_pde
    return background_from_spectral_radiance(p.sky_radiance * 1e9, r.wavelength_m, p.filter_nm * 1e-9, area, omega, eta_rx)


def config(p: OutdoorParts = OutdoorParts(), seed: int = 2028) -> LinkConfig:
    base = two_room_config(replace(p.receiver, channel="free_space", path_m=p.distance_m, free_space_loss_db=path_loss_db(p)), seed=seed,
                           scenario="outdoor")
    sky_pair = 1 - math.exp(-sky_counts_per_s(p) / 2 * p.receiver.gate_s)
    pd = 1 - (1 - base.dark_count_prob) * (1 - sky_pair)
    p_click = p.receiver.mu * models.signal_click_prob(base) + pd
    return base.with_(dark_count_prob=pd, crosstalk_click_prob=p.receiver.sipm_afterpulse * p_click)


def predict(p: OutdoorParts = OutdoorParts()) -> dict:
    c = config(p)
    s = expected_session(c)
    return {"path_loss_db": path_loss_db(p), **factors(p), "sky_counts_per_s": sky_counts_per_s(p), "dark_prob_per_gate": c.dark_count_prob,
            "click_prob_per_pulse": s["click_prob_per_pulse"], "qber": s["qber"], "key_bits": s["key_bits"], "accepted": s["accepted"]}
