"""The digital twin of the tabletop Mars-link bench (experiments/protocols/P09): what each stage should measure,
predicted by the same tested functions that evaluate the Earth-Mars link.

Method
------
The bench replaces the Sun with a lamp, Earth with a matte white ball, the Earth-end transmitter with an attenuated
laser (a bare single-mode fiber tip, so it is a point source), and the Mars receiver with a fiber collimator feeding a
single-mode (SMF) or multimode (MMF) fiber and a detector. It cannot reproduce the Mars numbers (the distances are
twelve orders of magnitude apart), but it reproduces the laws that decide them, each with the bench's own parameters:
  1. calibration: the lamp's spectral irradiance at the ball, E_lambda = I / (R_d A_d Delta_lambda) from a filtered
     photodiode's photocurrent I;
  2. the phase curve of a Lambertian sphere, P(alpha) = E_lambda Delta_lambda p (R/d)^2 Phi(alpha) A_det with
     p = 2A/3 and Phi the Lambert phase function [russell1916];
  3. radiance conservation and mode counting: a receiver whose field is filled by a lit card collects
     L Delta_lambda G, with L = A E cos z / pi [hapke2012] and G = lambda^2 for SMF or the fiber's etendue for MMF
     [siegman1986], independent of distance, proportional to the filter width, and G / lambda^2 times larger in MMF;
  4. off-axis rejection: the SMF's Gaussian acceptance exp(-2 (theta / theta_m)^2), theta_m = (MFD/2)/f, the MMF's
     field stop a/f, the lens's Airy wing [born1999], and the stray-light floor;
  5. herald purity w = S / (S + N) for a transmitter on the lit ball ("ground source, day"), on the dark side
     ("night"), and beside the ball ("space source"), with the signal from the Gaussian-beam model [siegman1986];
  6. the error fraction behind a polarizing beamsplitter, e = w e_opt + (1 - w)/2, because unpolarized background
     splits evenly; it equals the Werner error rate 2(1 - f)/3 of f = 1/4 + w (f0 - 1/4) used by the Mars budget;
  7. a synodic period compressed into a bench run: the source is attenuated day by day in proportion to the Mars link's
     signal, the key per step follows 1 - 2 h(e) [shor2000], and the key bank is sized by the sequent-peak rule
     [loucks2017].
Default parts are a Tier 1 bench at 650 nm (class 2 red laser, silicon photodiodes); every default is meant to be
replaced by the measured value of your own part.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from qll.app.key_bank import sequent_peak
from qll.channels.free_space_diffraction import geometric_transmittance
from qll.channels.planetshine import (airy_leakage, filter_width_nm, lambert_geometric_albedo, lambert_phase,
                                      lambertian_radiance, multimode_etendue)
from qll.constants.physical import C_LIGHT, H_PLANCK
from qll.qkd.binary_entropy import h2

FIBERS = ("smf", "mmf")


@dataclass(frozen=True)
class BenchDesign:
    wavelength_m: float = 650e-9
    filter_nm: float = 10.0                  # bandpass full width
    lamp_irradiance_nm: float = 0.2          # W m^-2 nm^-1 at the ball (Stage 1 measures it)
    albedo: float = 0.9                      # matte white paint, normal albedo (Stage 2 measures it)
    ball_diameter_m: float = 0.040
    distance_m: float = 1.5                  # ball to receiver
    phase_distance_m: float = 0.4            # ball to the bare photodiode of Stage 2
    lens_focal_m: float = 11e-3              # fiber collimator
    lens_diameter_m: float = 5.0e-3          # its clear aperture
    smf_mfd_m: float = 4.3e-6                # mode-field diameter of a 630-680 nm single-mode fiber
    mmf_core_radius_m: float = 25e-6
    mmf_na: float = 0.22
    coupling: float = 0.7                    # fiber coupling of a filled mode
    responsivity_a_per_w: float = 0.42       # silicon near 650 nm
    detector_area_m2: float = 7.5e-6         # BPW34-class photodiode (Stages 1-2)
    stray_light: float = 1e-5                # receiver floor (Stage 4 measures it)
    room_radiance_nm: float = 1e-7           # W m^-2 sr^-1 nm^-1 from a darkened room
    tx_power_w: float = 1e-3                 # laser power into the transmitter fiber, before attenuation
    tx_od: float = 5.0                       # neutral-density attenuation (brings the laser down to the lamp)
    e_opt: float = 0.02                      # polarization error with no background (Stage 6 measures it)
    detection_efficiency: float = 0.3        # photon counter (Tier 2), for data logged in photons per second
    signal_unit: str = "watts"               # or "photons_per_s": the unit of logged signal columns

    def __post_init__(self):
        for v in vars(self).values():
            if isinstance(v, complex):
                raise TypeError("bench parameters must be real")


def _fiber(fiber: str) -> None:
    if fiber not in FIBERS:
        raise ValueError(f"fiber must be one of {FIBERS}")


def photon_energy_j(b: BenchDesign) -> float:
    return H_PLANCK * C_LIGHT / b.wavelength_m


# Stage 1 ------------------------------------------------------------------------------------------------------------
def irradiance_from_photocurrent(b: BenchDesign, photocurrent_a: float) -> float:
    """Lamp spectral irradiance (W m^-2 nm^-1) from a filtered photodiode's photocurrent at the ball."""
    return photocurrent_a / (b.responsivity_a_per_w * b.detector_area_m2 * b.filter_nm)


# Stage 2 ------------------------------------------------------------------------------------------------------------
def ball_flux_w(b: BenchDesign, phase_rad: float, distance_m: float | None = None) -> float:
    """Power on a bare photodiode (area A_det) from the whole ball at phase angle alpha, at distance_m (default: the
    receiver distance; Stage 2 uses phase_distance_m)."""
    d = b.distance_m if distance_m is None else distance_m
    R = b.ball_diameter_m / 2
    p = lambert_geometric_albedo(b.albedo)
    return b.lamp_irradiance_nm * b.filter_nm * p * (R / d) ** 2 * lambert_phase(phase_rad) * b.detector_area_m2


# Stage 3 ------------------------------------------------------------------------------------------------------------
def etendue(b: BenchDesign, fiber: str) -> float:
    """Etendue (m^2 sr) the receiver accepts: lambda^2 for single-mode, the fiber or lens limit for multimode."""
    _fiber(fiber)
    if fiber == "smf":
        return b.wavelength_m**2
    return multimode_etendue(b.mmf_core_radius_m, b.mmf_na, b.lens_diameter_m, b.lens_focal_m)


def mode_ratio(b: BenchDesign) -> float:
    """How much more extended-source light the multimode receiver collects: G_mmf / lambda^2."""
    return etendue(b, "mmf") / etendue(b, "smf")


def field_of_view_rad(b: BenchDesign, fiber: str) -> float:
    """Angular radius of the receiver's field: the mode's (MFD/2)/f, or the multimode core's a/f."""
    _fiber(fiber)
    return (b.smf_mfd_m / 2 if fiber == "smf" else b.mmf_core_radius_m) / b.lens_focal_m


def surface_power_w(b: BenchDesign, fiber: str, zenith_rad: float = 0.0, filter_nm: float | None = None) -> float:
    """Power a receiver collects from a lit Lambertian surface that fills its field (independent of distance)."""
    dl = b.filter_nm if filter_nm is None else filter_nm
    L = lambertian_radiance(b.lamp_irradiance_nm, b.albedo, zenith_rad) + b.room_radiance_nm
    return L * dl * etendue(b, fiber) * b.coupling


# Stage 4 ------------------------------------------------------------------------------------------------------------
def rejection(b: BenchDesign, theta_rad: float, fiber: str) -> float:
    """Fraction of an on-axis point source's coupled power that remains when it sits theta off the receiver's axis.
    SMF: the Gaussian acceptance of the mode, then the lens's Airy wing beyond its first dark ring. MMF: everything
    inside the field stop a/f, then the Airy wing of the image's distance beyond the stop. Never below the floor."""
    _fiber(fiber)
    th = abs(float(theta_rad))
    if fiber == "smf":
        wing = airy_leakage(th, b.lens_diameter_m, b.wavelength_m)
        core = math.exp(-2 * (th / field_of_view_rad(b, "smf")) ** 2)
        return max(core, 0.0 if wing == 1.0 else wing, b.stray_light)
    stop = field_of_view_rad(b, "mmf")
    return max(1.0 if th <= stop else airy_leakage(th - stop, b.lens_diameter_m, b.wavelength_m), b.stray_light)


# Stage 5 ------------------------------------------------------------------------------------------------------------
def signal_power_w(b: BenchDesign, fiber: str) -> float:
    """Laser power the receiver couples from a bare single-mode fiber tip at the ball (a Gaussian point source)."""
    _fiber(fiber)
    tx = b.tx_power_w * 10 ** (-b.tx_od)
    return tx * geometric_transmittance(b.distance_m, b.wavelength_m, b.smf_mfd_m / 2, b.lens_diameter_m) * b.coupling


def background_power_w(b: BenchDesign, fiber: str, placement: str, phase_rad: float = 0.0, offset_radii: float = 0.0) -> float:
    """Background the receiver collects while aimed at the transmitter.
    placement "day": the tip on the ball's lit face (ground source in daylight), the lamp at phase angle alpha;
    "night": the tip on the dark face (lamp behind the ball); "space": the tip beside the ball, offset_radii ball radii
    from its centre as seen from the receiver (must be at least 2), with the ball an off-axis point."""
    _fiber(fiber)
    if placement == "day":
        return surface_power_w(b, fiber, zenith_rad=phase_rad)
    if placement == "night":
        return surface_power_w(b, fiber, zenith_rad=math.pi)
    if placement != "space":
        raise ValueError("placement must be 'day', 'night' or 'space'")
    if offset_radii < 2:
        raise ValueError("a 'space' transmitter must sit at least two ball radii from the centre")
    R = b.ball_diameter_m / 2
    theta = offset_radii * R / b.distance_m
    ball = ball_flux_w(b, phase_rad) / b.detector_area_m2          # W m^-2 at the receiver
    lens = math.pi * (b.lens_diameter_m / 2) ** 2
    room = b.room_radiance_nm * b.filter_nm * etendue(b, fiber) * b.coupling
    return ball * lens * rejection(b, theta, fiber) * b.coupling + room


def in_logged_unit(b: BenchDesign, power_w: float) -> float:
    """Convert a predicted power to the unit the data were logged in (watts, or detected photons per second)."""
    if b.signal_unit == "watts":
        return power_w
    if b.signal_unit == "photons_per_s":
        return power_w / photon_energy_j(b) * b.detection_efficiency
    raise ValueError("signal_unit must be 'watts' or 'photons_per_s'")


def purity(signal: float, background: float) -> float:
    return signal / (signal + background) if signal + background > 0 else 0.0


# Stage 6 ------------------------------------------------------------------------------------------------------------
def error_fraction(w: float, e_opt: float) -> float:
    """Fraction of detections in the wrong port of a polarizing beamsplitter: w e_opt + (1 - w)/2."""
    return w * e_opt + (1 - w) / 2


def werner_equivalent_error(w: float, f0: float) -> float:
    """The Mars budget's error rate 2(1 - f)/3 with f = 1/4 + w (f0 - 1/4); equal to error_fraction(w, 2(1 - f0)/3)."""
    f = 0.25 + w * (f0 - 0.25)
    return 2 * (1 - f) / 3


def key_fraction(e: float) -> float:
    """Asymptotic secret fraction per sifted detection, 1 - 2 h(e), zero above about 11 % [shor2000]."""
    return max(0.0, 1 - 2 * h2(e)) if e < 0.5 else 0.0


# Stage 7 ------------------------------------------------------------------------------------------------------------
def mars_schedule(relative_signal: np.ndarray) -> np.ndarray:
    """Neutral-density steps (OD above the base) that reproduce a relative signal profile, e.g. one synodic period of
    the Mars link's pairs per day divided by its maximum; zero-signal days (conjunction) become a closed shutter (inf)."""
    r = np.asarray(relative_signal, dtype=float)
    top = r.max()
    return np.where(r > 0, -np.log10(np.where(r > 0, r / top, 1.0)), np.inf)


def run_prediction(b: BenchDesign, extra_od: np.ndarray, fiber: str = "mmf", seconds_per_step: float = 5.0,
                   detection_efficiency: float = 0.3) -> dict[str, np.ndarray]:
    """Predicted per-step signal, background, purity, error fraction, and key bits for a bench run in which the
    transmitter ("space" placement, 6 radii) is attenuated by extra_od on each step."""
    N = background_power_w(b, fiber, "space", offset_radii=6.0)
    S0 = signal_power_w(b, fiber)
    E = photon_energy_j(b)
    S = np.where(np.isfinite(extra_od), S0 * 10 ** (-np.where(np.isfinite(extra_od), extra_od, 0.0)), 0.0)
    w = np.array([purity(s, N) for s in S])
    e = np.array([error_fraction(x, b.e_opt) for x in w])
    detections = (S + N) / E * detection_efficiency * seconds_per_step
    key = np.where(S > 0, 0.5 * detections * np.array([key_fraction(x) for x in e]), 0.0)
    return {"signal_w": S, "background_w": np.full_like(S, N), "purity": w, "error_fraction": e, "key_bits": key}


def bank_for_run(key_bits: np.ndarray, demand_fraction: float = 0.5) -> tuple[float, float]:
    """(demand per step, sequent-peak bank) for a constant demand equal to demand_fraction of the mean key per step."""
    k = np.asarray(key_bits, dtype=float)
    demand = demand_fraction * float(k.mean())
    return demand, sequent_peak(k, demand)
