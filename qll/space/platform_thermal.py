"""Can the memory's operating temperature fly?

Physics
-------
Cooling power at temperature T is the binding constraint on a spacecraft: passive radiators reach ~40 K
(JWST class), flown 4-6 K coolers deliver only tens of milliwatts (Planck 4 K JT ~15 mW at 4.5 K, JWST MIRI ~50 mW at 6 K), unlike laboratory pulse tubes (~1 W), adiabatic
demagnetization ~50-100 mK with microwatts (Hitomi/XRISM), and dilution refrigerators have not flown for
optical payloads [shirron2014] [planck2011]. A memory platform is "flyable" when a flown cooler class reaches
its temperature with margin. Heat load on the coldest stage from an optical window and wiring is the design
driver; this module carries the cooler table and a heat-load check; it is data, not a thermal model.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Cooler:
    name: str
    T_min_K: float
    cooling_power_W: float
    flown: bool
    bibkey: str


COOLERS: tuple[Cooler, ...] = (
    Cooler("passive radiator (deep-space, shaded)", 40.0, 1.0, True, "jwst2023"),
    Cooler("pulse-tube / JT cryocooler (Planck 4K, JWST MIRI class)", 4.0, 0.02, True, "planck2011"),
    Cooler("3He sorption / Joule-Thomson", 0.3, 1e-3, True, "planck2011"),
    Cooler("adiabatic demagnetization refrigerator", 0.05, 1e-6, True, "shirron2014"),
    Cooler("dilution refrigerator (space-qualified)", 0.01, 1e-5, False, "TODO"),
)


def coolers_reaching(T_kelvin: float, margin: float = 1.2) -> list[Cooler]:
    return [c for c in COOLERS if c.T_min_K * margin <= T_kelvin]


def flyable(T_kelvin: float, heat_load_W: float, margin: float = 1.2) -> bool:
    return any(c.flown and c.cooling_power_W >= heat_load_W for c in coolers_reaching(T_kelvin, margin))
