"""A stored qubit decays; the stored *entanglement* decays with it, and so does the teleportation it can do.

Physics
-------
One half of a Bell pair held in a memory sees a single-qubit channel. For a depolarizing memory with
probability p(t) = 1 - exp(-t/T_mem) the fully entangled fraction of an initial Werner state f0 becomes
f(t) = 1/4 + (f0 - 1/4) exp(-t/T_mem) (exact, from the Kraus map of Phase 2); for a pure-dephasing memory
(off-diagonal decay exp(-t/T2)) acting on one qubit of a Werner state, |Phi+> mixes with |Phi->:
f(t) = (2 f0 + 1)/6 + (4 f0 - 1)/6 * exp(-t/T2), which tends to (2 f0 + 1)/6 < 1/2, so dephasing alone
also eventually destroys the usefulness of the pair (crossover at t = T2 ln((4 f0 - 1)/(2 - 2 f0))). Entanglement is gone at f < 1/2
[werner1989] and teleportation drops to the classical 2/3 at the same point [horodecki1996]. The memory
table records demonstrated (lifetime, efficiency) pairs; both numbers matter because a memory that stores
for hours but retrieves 1% of photons multiplies the rate by 0.01 [zhong2015] [wang2025memory] [knaut2024].
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from qll.channels.light_time_delay import round_trip_delay_s
from qll.circuits.bell import bell_state
from qll.circuits.noise.depolarizing import depolarizing
from qll.circuits.noise.phase_damping import phase_damping
from qll.constants.astro import AU_METERS, EARTH_MARS_MAX_M, EARTH_MARS_MIN_M

_I = np.eye(2, dtype=complex)


MODELS = ("depolarizing", "dephasing")


@dataclass(frozen=True)
class MemoryPlatform:
    """One memory, with each property's evidence kept apart (audit P02). `lifetime_s` is the coherence or storage time
    reported by the cited experiment (`bibkey`). `efficiency` is the photon write-and-read efficiency the models use; it
    is an ASSUMED operating point unless `efficiency_status` says otherwise, because the cited long-coherence results
    measure spin coherence, not the efficiency of storing and retrieving an incoming photon at that storage time.
    Combining the best numbers of different experiments does not make a demonstrated platform."""
    name: str
    lifetime_s: float          # coherence / storage time reported by the cited experiment
    efficiency: float          # photon write-and-read efficiency used by the models (see efficiency_status)
    T_kelvin: float
    wavelength_nm: float       # the memory's optical interface; links at other wavelengths need conversion
    bibkey: str                # source of lifetime_s
    model: str = "depolarizing"   # or "dephasing"
    efficiency_status: str = "assumed"   # "measured" only with a source that reports it at this storage time
    efficiency_ref: str = ""             # source for the efficiency when measured
    note: str = ""

    def __post_init__(self) -> None:
        if self.model not in MODELS:
            raise ValueError(f"memory model must be one of {MODELS}, got {self.model!r}")
        if self.efficiency_status not in ("assumed", "measured"):
            raise ValueError("efficiency_status must be 'assumed' or 'measured'")
        if self.efficiency_status == "measured" and not self.efficiency_ref:
            raise ValueError("a measured efficiency needs its source")


_ASSUMED = "efficiency is a model assumption, not reported at this storage time in the cited work"
MEMORY_TABLE: tuple[MemoryPlatform, ...] = (
    MemoryPlatform("Rb/Cs atomic ensemble (DLCZ)", 1e-3, 0.5, 300.0, 780, "liu2024", note=_ASSUMED),
    MemoryPlatform("SiV nuclear spin in cavity", 1.0, 0.9, 0.1, 737, "knaut2024", note=_ASSUMED),
    MemoryPlatform("NV 13C register", 60.0, 0.9, 4.0, 637, "bradley2019", note=_ASSUMED + "; NV photon collection is far lower"),
    MemoryPlatform("171Yb+ hyperfine", 3600.0, 0.99, 300.0, 369, "wang2021ion", note=_ASSUMED + "; the cited result is single-ion spin coherence"),
    MemoryPlatform("Eu:YSO nuclear spin, 6 h (ZEFOZ+DD)", 6 * 3600.0, 0.01, 2.0, 580, "zhong2015", note=_ASSUMED + "; the cited result is nuclear-spin coherence"),
    MemoryPlatform("Eu:YSO nuclear spin, 13.1 h", 13.1 * 3600.0, 0.005, 0.5, 580, "wang2025memory", note=_ASSUMED),
)

BASELINES: dict[str, float] = {   # classical round trip the memory must survive (s)
    "metro 25 km fiber": round_trip_delay_s(25e3 * 1.47),
    "LEO 1000 km": round_trip_delay_s(1.0e6),
    "GEO 36000 km": round_trip_delay_s(3.6e7),
    "Moon": round_trip_delay_s(3.844e8),
    "Mars min": round_trip_delay_s(EARTH_MARS_MIN_M),
    "Mars max": round_trip_delay_s(EARTH_MARS_MAX_M),
}


def stored_pair(f0_pair: np.ndarray, t_s: float, T_mem_s: float, model: str = "depolarizing") -> np.ndarray:
    """Apply the memory channel for time t to the second qubit of a 4x4 pair state (exact Kraus map)."""
    if model == "depolarizing":
        ch = depolarizing(1 - math.exp(-t_s / T_mem_s))
    elif model == "dephasing":
        ch = phase_damping(1 - math.exp(-2 * t_s / T_mem_s))
    else:
        raise ValueError("model must be 'depolarizing' or 'dephasing'")
    out = np.zeros_like(f0_pair, dtype=complex)
    for e in ch.ops:
        E = np.kron(_I, e)
        out += E @ f0_pair @ E.conj().T
    return out


def fully_entangled_fraction(rho: np.ndarray, kind: str = "phi+") -> float:
    b = bell_state(kind)
    return float(np.real(b.conj() @ rho @ b))


def _validate(f0: float, t_s: float, T_mem_s: float, model: str) -> None:
    if model not in MODELS:
        raise ValueError(f"memory model must be one of {MODELS}, got {model!r}")
    if not 0.25 <= f0 <= 1 or t_s < 0 or not T_mem_s > 0:
        raise ValueError("need 1/4 <= f0 <= 1, t >= 0, and T_mem > 0")


def fraction_after_storage_analytic(f0: float, t_s: float, T_mem_s: float, model: str = "depolarizing") -> float:
    _validate(f0, t_s, T_mem_s, model)
    if model == "depolarizing":
        return 0.25 + (f0 - 0.25) * math.exp(-t_s / T_mem_s)
    return (2 * f0 + 1) / 6 + (4 * f0 - 1) / 6 * math.exp(-t_s / T_mem_s)


def teleportation_fidelity_after_storage(f0: float, t_s: float, T_mem_s: float, model: str = "depolarizing") -> float:
    return (2 * fraction_after_storage_analytic(f0, t_s, T_mem_s, model) + 1) / 3


def crossover_time_s(f0: float, T_mem_s: float, model: str = "depolarizing") -> float:
    """Storage time at which the pair stops being useful for teleportation (f = 1/2, F = 2/3)."""
    _validate(max(f0, 0.25), 0.0, T_mem_s, model)
    if f0 <= 0.5:
        return 0.0
    if model == "depolarizing":
        return T_mem_s * math.log((f0 - 0.25) / 0.25)
    if f0 >= 1.0:
        return math.inf
    return T_mem_s * math.log((4 * f0 - 1) / (2 - 2 * f0))


def survives(platform: MemoryPlatform, baseline_s: float, f0: float = 0.95) -> bool:
    return crossover_time_s(f0, platform.lifetime_s, platform.model) >= baseline_s


def capability_matrix(f0: float = 0.95) -> dict[str, dict[str, bool]]:
    """REQ-CAP-001: which demonstrated memory outlasts which classical round trip."""
    return {p.name: {b: survives(p, t, f0) for b, t in BASELINES.items()} for p in MEMORY_TABLE}
