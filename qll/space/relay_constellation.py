"""Relays that carry entanglement or keys between Earth and Mars, with pass statistics.

Physics
-------
A relay is a spacecraft with a pair source and a memory (or a trusted key store). Three placements are
compared: Earth orbit (short Earth leg, full Mars leg), Sun-Earth L4/L5 (a 60 deg lead/lag point: never in
conjunction at the same time as Earth, keeps a link when the direct one is blacked out), and Mars orbit.
Per-pass yield follows the empirical microsatellite statistics of Jinan-1 for the *short* leg: the reported
20-pass campaign delivered up to ~1 Mbit of key per pass with large pass-to-pass variation [li2025jinan]; we
model yield per pass as log-normal with median m and sigma s (defaults: m = 250 kbit, s = 0.8, fitted loosely
to the published spread, TODO: fit to the Zenodo table 10.5281/zenodo.14732295). The long (AU) leg yield is
the link-budget pair rate times the pass duration. End-to-end availability is the fraction of time at least
one relay has both legs above their SEP thresholds; the honest metric is pairs (or key bits) per day.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from qll.channels.free_space_diffraction import geometric_transmittance
from qll.constants.astro import AU_METERS
from qll.space.ephemeris import heliocentric_xy_au, EARTH, MARS


@dataclass(frozen=True)
class Relay:
    name: str
    placement: str            # 'earth_orbit' | 'L4' | 'L5' | 'mars_orbit'
    aperture_m: float = 1.0
    source_rate_hz: float = 1e8
    lambda_m: float = 1550e-9
    w0_m: float = 0.15


def relay_position_au(relay: Relay, t_days: float) -> tuple[float, float]:
    ex, ey = heliocentric_xy_au(EARTH, t_days)
    mx, my = heliocentric_xy_au(MARS, t_days)
    if relay.placement == "earth_orbit":
        return ex, ey
    if relay.placement == "mars_orbit":
        return mx, my
    ang = math.atan2(ey, ex) + (math.pi / 3 if relay.placement == "L4" else -math.pi / 3)
    r = math.hypot(ex, ey)
    return r * math.cos(ang), r * math.sin(ang)


def _sep_deg(observer, target) -> float:
    sun = -np.asarray(observer); tgt = np.asarray(target) - np.asarray(observer)
    c = float(np.dot(sun, tgt) / (np.linalg.norm(sun) * np.linalg.norm(tgt)))
    return math.degrees(math.acos(max(-1.0, min(1.0, c))))


def legs(relay: Relay, t_days: float) -> dict[str, dict[str, float]]:
    """Range and SEP angle of the Earth-relay and relay-Mars legs."""
    e = heliocentric_xy_au(EARTH, t_days); m = heliocentric_xy_au(MARS, t_days); r = relay_position_au(relay, t_days)
    return {
        "earth": {"range_m": math.dist(e, r) * AU_METERS, "sep_deg": _sep_deg(e, r) if math.dist(e, r) > 1e-6 else 180.0},
        "mars": {"range_m": math.dist(r, m) * AU_METERS, "sep_deg": _sep_deg(r, m) if math.dist(r, m) > 1e-6 else 180.0},
    }


def long_leg_pairs_per_day(relay: Relay, range_m: float, receiver_m: float = 10.0, eta_other: float = 0.05, duty: float = 0.3) -> float:
    eta = geometric_transmittance(range_m, relay.lambda_m, relay.w0_m, receiver_m) * eta_other
    return relay.source_rate_hz * eta * 86400 * duty


def short_leg_key_bits_per_day(rng: np.random.Generator, passes_per_day: float = 4.0, median_bits: float = 250e3, sigma: float = 0.8) -> float:
    n = rng.poisson(passes_per_day)
    return float(np.sum(rng.lognormal(math.log(median_bits), sigma, size=n))) if n else 0.0


def constellation_availability(relays: list[Relay], t_days: np.ndarray, sep_threshold_deg: float = 3.0) -> float:
    ok = np.zeros(len(t_days), dtype=bool)
    for i, t in enumerate(t_days):
        for r in relays:
            lg = legs(r, t)
            if lg["earth"]["sep_deg"] >= sep_threshold_deg and lg["mars"]["sep_deg"] >= sep_threshold_deg:
                ok[i] = True
                break
    return float(ok.mean())


def best_relay_pairs_per_day(relays: list[Relay], t_days: float, sep_threshold_deg: float = 3.0, **kw) -> float:
    best = 0.0
    for r in relays:
        lg = legs(r, t_days)
        if lg["earth"]["sep_deg"] < sep_threshold_deg or lg["mars"]["sep_deg"] < sep_threshold_deg:
            continue
        best = max(best, long_leg_pairs_per_day(r, max(lg["earth"]["range_m"], lg["mars"]["range_m"]), **kw))
    return best


# --- E3: real pass statistics -------------------------------------------------------------------------------
def load_pass_table(path: str, key_column: str = "key_bits", duration_column: str | None = None) -> np.ndarray:
    """Load per-pass key yields (bits) from a CSV such as the Jinan-1 campaign table (Zenodo 10.5281/zenodo.14732295;
    TODO: confirm column names when downloaded). Returns the yields as an array; passes with zero key are kept."""
    import csv

    out = []
    with open(path, newline="") as fh:
        for row in csv.DictReader(fh):
            v = row.get(key_column, "").strip()
            if v:
                out.append(float(v))
    return np.asarray(out, dtype=float)


def fit_lognormal(yields: np.ndarray) -> tuple[float, float]:
    """(median_bits, sigma) of a log-normal fitted to the positive yields; used by short_leg_key_bits_per_day."""
    y = np.asarray(yields, dtype=float)
    y = y[y > 0]
    logs = np.log(y)
    return float(np.exp(logs.mean())), float(logs.std(ddof=1)) if len(logs) > 1 else 0.0


def key_bits_per_day_from_table(yields: np.ndarray, passes_per_day: float, rng: np.random.Generator, days: int = 365) -> np.ndarray:
    """Bootstrap daily key totals by resampling measured passes (empirical distribution, no model)."""
    y = np.asarray(yields, dtype=float)
    return np.array([y[rng.integers(0, len(y), size=rng.poisson(passes_per_day))].sum() for _ in range(days)])
