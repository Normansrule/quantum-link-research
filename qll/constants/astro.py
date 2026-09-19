"""Solar-system distances used as envelope values until an ephemeris arrives in Phase 5.

Physics
-------
The astronomical unit is exact by IAU 2012 Resolution B2 [iau2012]. The Earth-Mars extrema
are approximate envelope values (TODO: verify vs JPL Horizons) and must not be used for any
result that depends on the date.
"""
AU_METERS: float = 149_597_870_700.0     # exact [iau2012]
EARTH_MARS_MIN_M: float = 0.372 * AU_METERS   # matches the mean-element Kepler envelope (qll.space.ephemeris) to 1 %; TODO: Horizons
EARTH_MARS_MAX_M: float = 2.68 * AU_METERS    # matches the mean-element Kepler envelope to 1 %; TODO: Horizons
EARTH_MARS_MEAN_M: float = 1.52 * AU_METERS   # TODO: verify vs JPL Horizons


def earth_mars_envelope_m() -> tuple[float, float]:
    """Return (minimum, maximum) Earth-Mars range in meters."""
    return EARTH_MARS_MIN_M, EARTH_MARS_MAX_M
