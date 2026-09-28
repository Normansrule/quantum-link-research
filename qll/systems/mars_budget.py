"""The end-to-end budget of the Earth-Mars link: from pairs emitted per second to useful teleportations per day, one
multiplicative stage at a time, for two architectures.

Physics
-------
Every stage multiplies the rate by a tested factor from the lower layers:
  - source: R_src pairs per second in each of M multiplexed modes (time bins, frequencies) [sinclair2014];
  - transmit optics eta_tx; for a ground station, the atmosphere at elevation e, exp(-tau airmass(e)) [atmosphere.py];
  - diffraction: the exact Gaussian-beam fraction caught by a receiver of diameter D at range L,
    1 - exp(-2 (D/2)^2 / w(L)^2), w(L) = w0 sqrt(1 + (L/z_R)^2) [free_space_diffraction.py];
  - pointing jitter sigma: w^2 / (w^2 + 4 sigma^2 L^2) [bourgoin2013];
  - receive optics and heralding detection eta_rx eta_det; memory write-and-read efficiency at each end that stores
    (the photon kept at the source end goes straight into its memory);
  - availability: zero when the Sun is within 3 degrees of a leg's line of sight (conjunction), times a weather and
    operations duty cycle.
Two architectures are compared:
  "earth_source"  the pair source sits at the Earth station; one photon is stored locally, the other crosses the
                  Earth-Mars distance once;
  "relay_dual"    a source on a Sun-Earth L4 relay sends one photon to each planet (the Micius dual-downlink
                  pattern [yin2017]); both photons cross astronomical distances, so the diffraction loss is paid twice.
The Mars half must wait in its memory until Earth's two classical bits arrive; the storage time is taken as
storage_factor x the one-way light time (default 2, the round trip, as in requirement REQ-CAP-001), and the pair's
Werner fraction decays as f = 1/4 + (f0 - 1/4) exp(-t/T_mem) [memory_decoherence.py]. The delivered pair is useful for
teleportation if (2f + 1)/3 > 2/3, and yields BBM92 key at the asymptotic rate 1 - 2 h(Q) per sifted pair with the
Werner error rate Q = 2(1 - f)/3 [bennett1992bbm92] [shor2000]. This is a budget, not a simulation: every factor is an
average, and the result is only as good as the least certain stage, which is why each stage is shown.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field, replace

from qll.channels.atmosphere import atmospheric_transmittance
from qll.channels.free_space_diffraction import beam_radius_m, geometric_transmittance
from qll.channels.light_time_delay import one_way_delay_s
from qll.channels.pointing_jitter import pointing_efficiency
from qll.network.memory_decoherence import MEMORY_TABLE, fraction_after_storage_analytic
from qll.qkd.binary_entropy import h2
from qll.space.ephemeris import earth_mars_range_m, sun_earth_mars_angle_deg
from qll.space.relay_constellation import Relay, legs

SEP_THRESHOLD_DEG = 3.0


@dataclass(frozen=True)
class MarsLinkDesign:
    architecture: str = "earth_source"      # or "relay_dual"
    source_rate_hz: float = 1e9             # pairs per second per mode
    modes: int = 1000                       # multiplexed modes
    wavelength_m: float = 1550e-9
    tx_waist_m: float = 0.5                 # Gaussian waist at the transmitter (about a 1.4 m telescope)
    rx_diameter_earth_m: float = 4.0
    rx_diameter_mars_m: float = 4.0
    pointing_rad: float = 1e-7              # per-axis jitter
    eta_tx: float = 0.8
    eta_rx: float = 0.7
    eta_det: float = 0.9
    earth_elevation_deg: float = 40.0
    duty: float = 0.5                       # weather, daylight, operations
    memory: str = "171Yb+ hyperfine"
    f0: float = 0.95
    storage_factor: float = 2.0

    def platform(self):
        for p in MEMORY_TABLE:
            if p.name == self.memory:
                return p
        raise ValueError(f"unknown memory {self.memory!r}")


@dataclass(frozen=True)
class Stage:
    name: str
    factor: float
    rate_per_s: float                       # rate after this stage

    @property
    def db(self) -> float:
        return 10 * math.log10(self.factor) if self.factor > 0 else -math.inf


@dataclass(frozen=True)
class Budget:
    design: MarsLinkDesign
    t_days: float
    range_m: float
    stages: tuple[Stage, ...]
    storage_s: float
    fraction: float
    teleport_fidelity: float
    key_bits_per_pair: float
    extra: dict = field(default_factory=dict)

    @property
    def pairs_per_day(self) -> float:
        return self.stages[-1].rate_per_s * 86400

    @property
    def useful(self) -> bool:
        return self.teleport_fidelity > 2 / 3

    @property
    def teleportations_per_day(self) -> float:
        return self.pairs_per_day if self.useful else 0.0

    @property
    def key_bits_per_day(self) -> float:
        return self.pairs_per_day * self.key_bits_per_pair

    @property
    def total_db(self) -> float:
        return sum(s.db for s in self.stages[1:])


def _leg(L_m: float, d: MarsLinkDesign, D_rx: float, ground: bool) -> list[tuple[str, float]]:
    out = []
    if ground:
        out.append(("Earth atmosphere", atmospheric_transmittance(d.earth_elevation_deg, d.wavelength_m)))
    out.append(("diffraction", geometric_transmittance(L_m, d.wavelength_m, d.tx_waist_m, D_rx)))
    out.append(("pointing", pointing_efficiency(d.pointing_rad, L_m, beam_radius_m(L_m, d.wavelength_m, d.tx_waist_m))))
    out.append(("receiver and detector", d.eta_rx * d.eta_det))
    return out


def budget(d: MarsLinkDesign, t_days: float) -> Budget:
    """The stage-by-stage budget on day t_days after J2000."""
    for v in (d.source_rate_hz, d.tx_waist_m, d.pointing_rad, d.f0, t_days):
        if isinstance(v, complex):
            raise TypeError("design parameters must be real")
    if d.architecture not in ("earth_source", "relay_dual"):
        raise ValueError("architecture must be 'earth_source' or 'relay_dual'")
    L = float(earth_mars_range_m(t_days))
    mem = d.platform()
    factors: list[tuple[str, float]] = [("transmit optics", d.eta_tx)]
    if d.architecture == "earth_source":
        factors += [(f"Earth to Mars: {n}", f) for n, f in _leg(L, d, d.rx_diameter_mars_m, ground=True)]
        available = sun_earth_mars_angle_deg(t_days) >= SEP_THRESHOLD_DEG
        extra = {"legs_m": [L]}
    else:
        lg = legs(Relay("L4 relay", "L4", source_rate_hz=d.source_rate_hz, lambda_m=d.wavelength_m, w0_m=d.tx_waist_m), t_days)
        LE, LM = lg["earth"]["range_m"], lg["mars"]["range_m"]
        factors += [(f"relay to Earth: {n}", f) for n, f in _leg(LE, d, d.rx_diameter_earth_m, ground=True)]
        factors += [(f"relay to Mars: {n}", f) for n, f in _leg(LM, d, d.rx_diameter_mars_m, ground=False)]
        available = min(lg["earth"]["sep_deg"], lg["mars"]["sep_deg"]) >= SEP_THRESHOLD_DEG
        extra = {"legs_m": [LE, LM]}
    factors.append(("memories (write and read, both ends)", mem.efficiency**2))
    factors.append(("availability (conjunction x duty)", d.duty if available else 0.0))
    rate = d.source_rate_hz * d.modes
    stages = [Stage(f"source: {d.modes:g} modes x {d.source_rate_hz:.3g} pairs/s", 1.0, rate)]
    for name, f in factors:
        rate *= f
        stages.append(Stage(name, f, rate))
    t_store = d.storage_factor * one_way_delay_s(L)
    f = fraction_after_storage_analytic(d.f0, t_store, mem.lifetime_s, mem.model)
    F = (2 * f + 1) / 3
    Q = 2 * (1 - f) / 3
    key = max(0.0, 1 - 2 * h2(Q)) if Q < 0.5 else 0.0
    return Budget(d, t_days, L, tuple(stages), t_store, f, F, key, extra)


def compare_memories(d: MarsLinkDesign, t_days: float) -> list[tuple[str, float, float]]:
    """(memory, pairs per day, teleportation fidelity) for every memory in the table, other stages unchanged."""
    return [(p.name, (b := budget(replace(d, memory=p.name), t_days)).pairs_per_day, b.teleport_fidelity) for p in MEMORY_TABLE]
