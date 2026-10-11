"""A satellite pass over a ground station (milestones M3.4 to M3.6): where the satellite is, how far, how much light
arrives, and how much key a decoy-state downlink could make, second by second.

Geometry
--------
A circular orbit at altitude h has angular rate omega = sqrt(G M / (R + h)^3), with the IERS value of G M [petit2010]. For a pass straight
overhead (the best case; Earth's rotation ignored over a few minutes), the satellite is at central angle
theta = omega t from the zenith point, and the station sees it at
    elevation e = atan2(cos theta - R / (R + h), sin theta),     range from link_budget.slant_range_m(h, e).
The pass lasts while e is above a minimum elevation (typically 10-20 degrees, set by buildings and air mass).

Light and key
-------------
The downlink transmittance at each moment is the published-configuration link budget of
qll/channels/link_budget.py (geometry, pointing, air mass, optics, detector) [bourgoin2013], whose Micius preset
reproduces the reported losses within 3 dB (tests/test_phase3_links.py) [yin2017]. Background at night is the dark
count plus moonless sky through the telescope, a vacuum yield Y0 per pulse. The key per pulse is the asymptotic
decoy-state rate of qll/qkd/decoy_state.py [lo2005] [ma2005]; summed over the pass at the source's pulse rate it is
the key one pass could give with ideal finite-size statistics, an upper estimate to compare with what the
reported missions distilled.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

from qll.channels.link_budget import EARTH_RADIUS_M, JINAN1_2025, MICIUS_2017, LinkBudget, slant_range_m
from qll.qkd.decoy_state import decoy_rate_per_pulse

GM_EARTH = 3.986004418e14            # m^3 s^-2, IERS Conventions 2010


@dataclass(frozen=True)
class Downlink:
    budget: LinkBudget = MICIUS_2017
    altitude_m: float = 500e3
    min_elevation_deg: float = 15.0
    rep_rate_hz: float = 100e6        # decoy-state source pulse rate
    mu: float = 0.5
    y0: float = 1e-6                  # background clicks per pulse at night (dark counts and sky)
    e_det: float = 0.01               # optical misalignment of the downlink


PRESETS = {"micius": Downlink(MICIUS_2017, 500e3), "jinan1": Downlink(JINAN1_2025, 500e3, rep_rate_hz=625e6 / 10)}


def angular_rate(altitude_m: float) -> float:
    return math.sqrt(GM_EARTH / (EARTH_RADIUS_M + altitude_m) ** 3)


def elevation_deg(theta: float, altitude_m: float) -> float:
    return math.degrees(math.atan2(math.cos(theta) - EARTH_RADIUS_M / (EARTH_RADIUS_M + altitude_m), math.sin(abs(theta))))


def pass_half_angle(altitude_m: float, min_elevation_deg: float) -> float:
    """Central angle at which the satellite sinks to the minimum elevation: cos(theta + e) = R cos e / (R + h)."""
    e = math.radians(min_elevation_deg)
    return math.acos(EARTH_RADIUS_M * math.cos(e) / (EARTH_RADIUS_M + altitude_m)) - e


def at_time(d: Downlink, t_s: float) -> dict:
    """The satellite t seconds after it passes overhead (negative t: before)."""
    theta = angular_rate(d.altitude_m) * t_s
    e = elevation_deg(theta, d.altitude_m)
    if e <= 0:
        return {"t_s": t_s, "elevation_deg": e, "range_m": float("nan"), "loss_db": float("inf"), "eta": 0.0, "key_per_pulse": 0.0}
    L = slant_range_m(d.altitude_m, e)
    eta = d.budget.eta_total(L, e)
    return {"t_s": t_s, "elevation_deg": e, "range_m": L, "loss_db": -10 * math.log10(eta), "eta": eta,
            "key_per_pulse": decoy_rate_per_pulse(eta, d.mu, d.y0, d.e_det), "factors": d.budget.factors(L, e)}


def pass_summary(d: Downlink, step_s: float = 1.0) -> dict:
    half = pass_half_angle(d.altitude_m, d.min_elevation_deg) / angular_rate(d.altitude_m)
    ts = [k * step_s for k in range(-int(half / step_s), int(half / step_s) + 1)]
    rows = [at_time(d, t) for t in ts]
    key = sum(r["key_per_pulse"] for r in rows) * d.rep_rate_hz * step_s
    return {"duration_s": 2 * half, "rows": rows, "key_bits": key,
            "min_loss_db": min(r["loss_db"] for r in rows), "max_loss_db": max(r["loss_db"] for r in rows)}
