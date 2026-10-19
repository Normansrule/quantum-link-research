"""How close to instantaneous communication can get, anywhere: the light-time floor, the routes that approach it, and
what security and teleportation add on top.

The project's goal is communication that is as close to instantaneous as physics allows, wherever the two ends are.
Physics sets the limit exactly. No signal outruns light, and entanglement does not change that: whatever Alice does to
her half of a shared pair, Bob's local statistics are unchanged until a classical message arrives [eberhard1989]
[ghirardi1980] [peres2004]. So "almost instantaneous" means three things this module computes:

1. **The floor.** The one-way delay can never be less than d/c, with d the straight-line distance [bipm2019]. On Earth
   a signal that stays above the ground follows at least the great circle, R*theta, so that is the practical floor;
   the chord 2R sin(theta/2) through the planet is the absolute one. Earth radius R = 6371.0088 km, the IUGG mean
   radius [moritz2000]; the Moon at its mean distance [williams2024moon]; Mars and Jupiter from the tested Kepler ephemeris (Jupiter: 33 to 54
   minutes one way).
2. **The route.** Each medium and path stretches the floor:
   - terrestrial fiber: group index n = 1.47 (the repository's fiber value) times a route that wanders by a factor s
     over the great circle (s = 1.5 here, an assumed planning value; measured paths vary [bozkurt2015]);
   - hollow-core fiber: light at about 99.7 % of its vacuum speed, n = 1.003 [poletti2013], on the same route;
   - a low-Earth-orbit laser mesh at altitude h: up, along the arc at radius R + h, and down, L = 2h + (R + h)*theta,
     at n = 1, which beats terrestrial fiber over long distances [handley2018];
   - a geostationary relay above the path's midpoint: up 35,786 km and down again, at n = 1;
   - free space between bodies: the straight line at n = 1.
   The stretch (route delay over the floor) is at least 1 by construction and is the figure of merit: 1 is the floor.
3. **What waits on top.** A message that must be encrypted with fresh key waits for that key. Counting one-way trips
   from the moment the sender decides to send:
   - banked key (one-time pad or AES under QKD key distilled earlier): the ciphertext goes now, 1 trip;
   - QKD on demand: photons out (1), bases back (2), reconciliation and authentication out with the ciphertext (3);
     3 trips before the receiver can decrypt;
   - a fresh TCP connection with a full TLS 1.3 handshake: TCP's handshake (2) [rfc9293], TLS's (2) [rfc8446], then
     the data (1); 5 trips;
   - teleportation with pairs banked in memories: only the two classical bits travel, 1 trip [bennett1993]; with no
     banked pair, the photon must first be sent from one end, 2 trips.
   Banking (key now, entanglement when memories allow it) is therefore what makes "regardless of location" mean "at
   the floor for that distance": the work is moved to before the message exists.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

from qll.channels.light_time_delay import one_way_delay_s
from qll.constants.astro import EARTH_MARS_MAX_M, EARTH_MARS_MIN_M
from qll.network.teleport_across import FIBER_INDEX
from qll.space.ephemeris import jupiter_range_envelope_m

EARTH_RADIUS_M = 6_371_008.8                 # IUGG mean radius R1 [moritz2000]
MOON_MEAN_DISTANCE_M = 384_400e3              # mean Earth-Moon distance [williams2024moon]
GEO_ALTITUDE_M = 35_786e3                     # geostationary altitude, from GM and the sidereal day [petit2010]
LEO_ALTITUDE_M = 550e3                        # a typical laser-mesh shell (assumed planning value) [handley2018]
HOLLOW_CORE_INDEX = 1.003                     # about 99.7 % of c [poletti2013]
JUPITER_MIN_M, JUPITER_MAX_M = jupiter_range_envelope_m()   # from the mean-element ephemeris: 3.95 to 6.45 au
FIBER_ROUTE_STRETCH = 1.5                     # assumed: real fiber paths wander from the great circle [bozkurt2015]

# Trips of one-way delay before the receiver can read the message (see the module docstring).
SECURITY_TRIPS = {"banked key": 1, "QKD on demand": 3, "TCP + TLS 1.3, new connection": 5}
TELEPORT_TRIPS = {"banked pairs": 1, "pair sent on demand": 2}


@dataclass(frozen=True)
class Site:
    name: str
    lat_deg: float | None = None              # a point on Earth's surface ...
    lon_deg: float | None = None
    range_m: float | None = None              # ... or a body at this straight-line distance from Earth

    def __post_init__(self):
        on_earth = self.lat_deg is not None and self.lon_deg is not None
        if on_earth == (self.range_m is not None):
            raise ValueError(f"{self.name}: give either a latitude and longitude or a range, not both or neither")
        if on_earth and not (-90 <= self.lat_deg <= 90 and -180 <= self.lon_deg <= 180):
            raise ValueError(f"{self.name}: latitude must lie in [-90, 90] and longitude in [-180, 180]")
        if self.range_m is not None and not (math.isfinite(self.range_m) and self.range_m > 0):
            raise ValueError(f"{self.name}: range must be positive and finite")

    @property
    def on_earth(self) -> bool:
        return self.range_m is None


SITES = {s.name: s for s in (
    Site("Carson, CA (CSUDH)", 33.864, -118.255), Site("Los Angeles", 34.052, -118.244), Site("New York", 40.713, -74.006),
    Site("London", 51.507, -0.128), Site("Tokyo", 35.676, 139.650), Site("Singapore", 1.352, 103.820),
    Site("Sydney", -33.869, 151.209), Site("São Paulo", -23.551, -46.633), Site("Cape Town", -33.925, 18.424),
    Site("the Moon", range_m=MOON_MEAN_DISTANCE_M), Site("Mars at its closest", range_m=EARTH_MARS_MIN_M),
    Site("Mars at its farthest", range_m=EARTH_MARS_MAX_M),
    Site("Jupiter at its closest", range_m=JUPITER_MIN_M), Site("Jupiter at its farthest", range_m=JUPITER_MAX_M),
)}


def central_angle_rad(a: Site, b: Site) -> float:
    """Great-circle angle between two surface points (haversine form, accurate at small and large angles)."""
    p1, p2 = math.radians(a.lat_deg), math.radians(b.lat_deg)
    dp, dl = p2 - p1, math.radians(b.lon_deg - a.lon_deg)
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * math.asin(min(1.0, math.sqrt(h)))


def distances_m(a: Site, b: Site) -> dict[str, float]:
    """The great circle (the floor for a path above the ground) and the chord (the absolute floor) between two sites,
    or the straight line when one end is off Earth (an Earth site is taken at the planet's center for those ranges,
    which changes them by at most one Earth radius: 21 ms on 1.3 s for the Moon)."""
    if a.on_earth and b.on_earth:
        th = central_angle_rad(a, b)
        return {"angle_rad": th, "great_circle_m": EARTH_RADIUS_M * th, "chord_m": 2 * EARTH_RADIUS_M * math.sin(th / 2)}
    if a.on_earth or b.on_earth:
        r = (b if a.on_earth else a).range_m
        return {"angle_rad": float("nan"), "great_circle_m": r, "chord_m": r}
    raise ValueError("one end must be on Earth")


def routes(a: Site, b: Site, leo_altitude_m: float = LEO_ALTITUDE_M, fiber_stretch: float = FIBER_ROUTE_STRETCH) -> dict[str, dict]:
    """One-way delay of each route that can join the two sites, with its stretch over the floor."""
    if not (leo_altitude_m > 0 and fiber_stretch >= 1):
        raise ValueError("the LEO altitude must be positive and the fiber route stretch at least 1")
    d = distances_m(a, b)
    floor = one_way_delay_s(d["great_circle_m"])
    out: dict[str, dict] = {}

    def add(name: str, length_m: float, index: float, note: str):
        t = one_way_delay_s(index * length_m)
        out[name] = {"length_m": length_m, "index": index, "delay_s": t, "stretch": t / floor if floor > 0 else 1.0, "note": note}

    if a.on_earth and b.on_earth:
        th, gc = d["angle_rad"], d["great_circle_m"]
        add("terrestrial fiber", fiber_stretch * gc, FIBER_INDEX, f"n = {FIBER_INDEX}, route {fiber_stretch:g}× the great circle (assumed)")
        add("hollow-core fiber", fiber_stretch * gc, HOLLOW_CORE_INDEX, f"n = {HOLLOW_CORE_INDEX}, same route")
        add("LEO laser mesh", 2 * leo_altitude_m + (EARTH_RADIUS_M + leo_altitude_m) * th, 1.0, f"up, across at {leo_altitude_m / 1e3:,.0f} km, down")
        rg = EARTH_RADIUS_M + GEO_ALTITUDE_M                 # relay above the midpoint of the great circle
        leg = math.sqrt(EARTH_RADIUS_M ** 2 + rg ** 2 - 2 * EARTH_RADIUS_M * rg * math.cos(th / 2))
        if th / 2 < math.acos(EARTH_RADIUS_M / rg):       # both ends see the relay above their horizon
            add("geostationary relay", 2 * leg, 1.0, "up to 35,786 km above the midpoint and down")
    else:
        add("free space", d["great_circle_m"], 1.0, "the straight line, n = 1")
    return {"distances": d, "floor_s": floor, "chord_floor_s": one_way_delay_s(d["chord_m"]), "routes": out}


def best_route(r: dict) -> tuple[str, dict]:
    return min(r["routes"].items(), key=lambda kv: kv[1]["delay_s"])


def message_latency_s(route_delay_s: float) -> dict[str, dict[str, float]]:
    """When the receiver can read a message, for each way of securing it and of teleporting a qubit."""
    if not (math.isfinite(route_delay_s) and route_delay_s >= 0):
        raise ValueError("route delay must be finite and non-negative")
    return {"secure message": {k: n * route_delay_s for k, n in SECURITY_TRIPS.items()},
            "teleported qubit": {k: n * route_delay_s for k, n in TELEPORT_TRIPS.items()}}


def report(a_name: str, b_name: str) -> dict:
    a, b = SITES[a_name], SITES[b_name]
    r = routes(a, b)
    name, best = best_route(r)
    return {"from": a_name, "to": b_name, **r, "best": name, "best_delay_s": best["delay_s"], "best_stretch": best["stretch"],
            "latency": message_latency_s(best["delay_s"])}


def antipodal_floor_s() -> dict[str, float]:
    """The worst case on Earth: two antipodal points (the farthest any two places on the planet can be)."""
    return {"great_circle_s": one_way_delay_s(math.pi * EARTH_RADIUS_M), "chord_s": one_way_delay_s(2 * EARTH_RADIUS_M)}


def leo_crossover_km(index: float = FIBER_INDEX, fiber_stretch: float = FIBER_ROUTE_STRETCH, leo_altitude_m: float = LEO_ALTITUDE_M) -> float:
    """Surface distance beyond which the low-orbit mesh beats a fiber route of this index and stretch. Setting
    2h + (R + h) theta = n s R theta gives theta* = 2h / (n s R - (R + h)); infinite when the fiber is no slower per
    kilometer than the orbit's arc, so the climb is never repaid [handley2018]."""
    slope = index * fiber_stretch * EARTH_RADIUS_M - (EARTH_RADIUS_M + leo_altitude_m)
    return math.inf if slope <= 0 else EARTH_RADIUS_M * (2 * leo_altitude_m / slope) / 1e3
