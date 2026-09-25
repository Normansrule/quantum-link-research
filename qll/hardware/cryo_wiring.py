"""The heat budget of the wiring in a dilution refrigerator: what limits qubit count before the chips do.

Physics
-------
Each control line is a coaxial cable running from 300 K through the 50 K, 4 K, still (~0.8 K), cold-plate (~0.1 K)
and mixing-chamber (~0.01 K) stages, with attenuators at the cold stages to thermalise the microwave noise. Two heat
loads per line [krinner2019]: passive conduction Q = (A/L) * integral k(T) dT between stages, with k the cable's
thermal conductivity (stainless steel or CuNi coax for drive lines, NbTi for readout), and active dissipation of the
attenuators, P_in (1 - 10^(-A/10)). The stage cooling powers of a large dilution unit are of order 40 W at 50 K, 1 W at
4 K, 10 mW at the still, 100 uW at the cold plate, and 10-20 uW at the mixing chamber. The mixing-chamber stage, not
the 4 K stage, typically saturates first for high-power drive lines; readout lines add isolators and amplifiers at 4 K.
The numbers below are representative integrals of k(T) (W/m) for common coax [krinner2019, Table 2] (TODO: verify
against the paper's table); they reproduce the paper's conclusion that ~1000 lines fit a large system.
"""
from __future__ import annotations

from dataclasses import dataclass

# Conductivity integrals ∫k dT (W/m) per stage interval, per cable type, for a 2.19 mm coax (outer + inner + dielectric).
# Values are order-of-magnitude representative; each entry is (300->50 K, 50->4 K, 4->0.8 K, 0.8->0.1 K, 0.1->0.01 K).
COAX_K_INTEGRAL_W_PER_M = {
    "stainless": (1.0e3, 3.0e1, 1.5e0, 6.0e-2, 4.0e-4),
    "cuni": (2.5e3, 6.0e1, 3.0e0, 1.5e-1, 1.0e-3),
    "nbti": (1.0e3, 3.0e1, 1.0e-1, 1.0e-3, 1.0e-5),
}
STAGES = ("50K", "4K", "still", "cold_plate", "mxc")
COOLING_POWER_W = {"50K": 40.0, "4K": 1.0, "still": 10e-3, "cold_plate": 100e-6, "mxc": 15e-6}
CABLE_AREA_OVER_LENGTH_M = {"50K": 2.2e-6 / 0.25, "4K": 2.2e-6 / 0.25, "still": 2.2e-6 / 0.2, "cold_plate": 2.2e-6 / 0.15, "mxc": 2.2e-6 / 0.15}


@dataclass(frozen=True)
class Line:
    kind: str = "drive"            # 'drive' | 'flux' | 'readout_in' | 'readout_out'
    cable: str = "stainless"
    attenuation_db: tuple[float, ...] = (0.0, 20.0, 0.0, 0.0, 20.0)   # dB at each stage (50K, 4K, still, CP, MXC)
    input_power_w: float = 1e-6    # average microwave power entering at 300 K (drive ~ -30 dBm avg)


def passive_load_w(line: Line) -> dict[str, float]:
    ks = COAX_K_INTEGRAL_W_PER_M[line.cable]
    return {s: CABLE_AREA_OVER_LENGTH_M[s] * k for s, k in zip(STAGES, ks)}


def active_load_w(line: Line) -> dict[str, float]:
    P = line.input_power_w
    out = {}
    for s, A in zip(STAGES, line.attenuation_db):
        diss = P * (1 - 10 ** (-A / 10))
        out[s] = diss
        P -= diss
    return out


def total_load_w(lines: list[Line]) -> dict[str, float]:
    tot = {s: 0.0 for s in STAGES}
    for ln in lines:
        for s in STAGES:
            tot[s] += passive_load_w(ln)[s] + active_load_w(ln)[s]
    return tot


def max_lines(line: Line, margin: float = 0.5) -> tuple[int, str]:
    """How many identical lines fit within `margin` of each stage's cooling power; returns (n, limiting stage)."""
    per = {s: passive_load_w(line)[s] + active_load_w(line)[s] for s in STAGES}
    n = {s: int(margin * COOLING_POWER_W[s] / per[s]) for s in STAGES if per[s] > 0}
    s = min(n, key=n.get)
    return n[s], s
