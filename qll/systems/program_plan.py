"""The mission plan as data: phases, milestones, gates, three-point costs, a critical-path schedule, and a Monte Carlo
cost risk, so systems/program/ is generated from one tested source instead of typed by hand.

Method
------
Each milestone carries a three-point cost estimate (low, likely, high) in US dollars. Its PERT mean and standard
deviation are (a + 4m + b)/6 and (b - a)/6 [malcolm1959]. The schedule is the critical-path method [kelley1959]:
a milestone starts when the last of its prerequisites finishes, the program ends when the last milestone finishes,
and the critical path is the chain of milestones with no slack. Cost risk is a Monte Carlo over triangular
distributions on (low, likely, high), reported as the 50th and 80th percentiles of each phase's total, the confidence
levels NASA's cost-estimating practice asks for [nasa2015ceh]. Durations assume about ten hours a week of one
person's time; costs are cash out of pocket (borrowed equipment and free cloud time cost nothing but appear as
risks). Every figure is planning, to be replaced by quotes and measurements as each milestone starts.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from qll.systems.experiment_catalog import PHASES


@dataclass(frozen=True)
class Milestone:
    id: str
    phase: int                     # 0-4 mission phases, or 9 for the startup track
    name: str
    weeks: float                   # elapsed weeks at about ten hours a week
    cost: tuple[float, float, float]   # low, likely, high, US dollars, cash
    after: tuple[str, ...] = ()    # prerequisites
    trl: int = 0                   # NASA technology readiness level reached when done [nasa2016seh]
    verify: str = ""               # verification method and pass criterion
    builds_on: tuple[str, ...] = ()  # experiment_catalog ids it reuses
    done: bool = False
    outside: bool = False          # proceeds only with outside funding (a grant, partner, or award), never out of pocket
    progress: str = ""             # what exists so far, for milestones under way

    @property
    def pert_mean(self) -> float:
        a, m, b = self.cost
        return (a + 4 * m + b) / 6

    @property
    def pert_sd(self) -> float:
        return (self.cost[2] - self.cost[0]) / 6


@dataclass(frozen=True)
class Gate:
    id: str
    after_phase: int
    criteria: str
    unlocks: str


STARTUP = 9
TRACKS = {**PHASES, STARTUP: "Startup track: from a validated bench to a company"}

MILESTONES: tuple[Milestone, ...] = (
    Milestone("M0.1", 0, "Simulation library, flagships, and evidence (qll, F1-F3)", 0, (0, 0, 0), trl=3, done=True,
              verify="Test: 700+ analytic tests pass in CI", builds_on=("F1", "F2", "F3", "D09")),
    Milestone("M0.2", 0, "Two-site link simulation, operations day, and experiment catalog", 0, (0, 0, 0), ("M0.1",), trl=3, done=True,
              verify="Test: SN-01 to SN-15 traced; scenarios 1-9 reproduce", builds_on=("T1", "T2", "T3", "T4", "P09")),
    # ------------------------------------------------------------------------------------------------ Phase 1
    Milestone("M1.1", 1, "Fiber classical channel between the rooms (media converters, patch cord, authenticated frames)",
              2, (40, 70, 150), ("M0.2",), trl=4, builds_on=("T2",), progress="software ready (net_transport); hardware to buy",
              verify="Test: 10,000 frames with zero authentication failures; 99th-percentile round trip under 5 ms"),
    Milestone("M1.2", 1, "The collapse code on a cloud processor (P11) and paper 1", 6, (0, 0, 0), ("M0.1",), trl=3,
              progress="analysis, figures, and draft rehearsed on simulators; hardware run next",
              builds_on=("P11", "E17", "E16", "D11"),
              verify="Analysis: information per use bounded below 1e-3 bit at 99 % on hardware; the leak control detected"),
    Milestone("M1.3", 1, "Tier 1 bright-light analogue across the rooms", 3, (40, 80, 120), ("M1.1",), trl=4, builds_on=("T1",),
              verify="Demonstration: the log runs through the protocol; honest error rate near 0, intercept-resend near 25 %"),
    Milestone("M1.4", 1, "Silicon photomultiplier receiver, characterized against its datasheet", 4, (150, 250, 400), ("M1.3",), trl=4,
              builds_on=("P10", "T3"), verify="Test: dark-count rate, relative efficiency, and afterpulsing measured and written into the twin"),
    Milestone("M1.5", 1, "Pulsed 405 nm source with decoy drive, mean photon number calibrated", 4, (80, 150, 300), ("M1.4",), trl=4,
              builds_on=("P10", "D02"), verify="Test: mean photon number within 10 % of target from power and repetition rate"),
    Milestone("M1.6", 1, "Two-room single-photon BB84 with decoys (P10), matched to its twin", 6, (60, 120, 250), ("M1.5", "M1.1"), trl=4,
              builds_on=("P10", "T3", "E06"),
              verify="Test: measured click rate and error rate inside the twin's prediction intervals; a session accepted"),
    Milestone("M1.7", 1, "Paper 2: a twin-validated single-photon link for under $1,000", 6, (0, 0, 150), ("M1.6",), trl=4,
              verify="Inspection: data, code, and twin published; an outside reader repeats the analysis from the files"),
    # ------------------------------------------------------------------------------------------------ Phase 2
    Milestone("M2.1", 2, "Access to an entangled-photon source (borrow a teaching kit, or partner)", 8, (0, 0, 15000), ("M1.6",), trl=4,
              builds_on=("P03", "T4"), verify="Inspection: a written loan or collaboration agreement"),
    Milestone("M2.2", 2, "Bell test across the rooms through fiber", 6, (100, 300, 800), ("M2.1", "M1.1"), trl=4,
              builds_on=("D03", "D11", "P03"), verify="Test: CHSH above 2 by at least five standard deviations"),
    Milestone("M2.3", 2, "Entanglement-based key (BBM92) across the rooms, same protocol code", 6, (0, 100, 300), ("M2.2",), trl=5,
              builds_on=("T4",), verify="Test: key accepted; measured error rate inside the twin's interval"),
    Milestone("M2.4", 2, "The collapse code with photons in two rooms", 4, (0, 50, 200), ("M2.2",), trl=4,
              builds_on=("P11", "P06", "D11"), verify="Analysis: information per use bounded; correlations appear only after the records are compared"),
    Milestone("M2.5", 2, "Paper 3: entanglement between two rooms on a student budget", 6, (0, 0, 150), ("M2.3", "M2.4"), trl=5,
              verify="Inspection: data and analysis published"),
    # ------------------------------------------------------------------------------------------------ Phase 3
    Milestone("M3.1", 3, "Satellite link budgets and pass schedules from public data", 6, (0, 0, 0), ("M0.1",), trl=3,
              builds_on=("D09", "D14", "E03"), verify="Analysis: Micius and Jinan-1 losses reproduced within 3 dB"),
    Milestone("M3.2", 3, "Rooftop free-space link with the Phase 1 hardware", 6, (100, 300, 800), ("M1.6",), trl=5,
              builds_on=("P04", "E04"), verify="Test: loss and daylight background against the twin"),
    Milestone("M3.3", 3, "Building-to-building link at night (0.5-2 km)", 8, (300, 800, 2000), ("M3.2",), trl=5,
              builds_on=("P04",), verify="Test: key accepted over the measured free-space loss"),
    Milestone("M3.4", 3, "Optical ground-station prototype: tracking telescope and GPS-disciplined timing", 12, (1000, 3000, 8000), ("M3.3",), trl=5,
              builds_on=("E14", "D14"), verify="Demonstration: tracks a satellite pass; timestamps agree with a second clock within 10 ns"),
    Milestone("M3.5", 3, "Satellite partnership or hosted-payload proposal", 12, (0, 200, 1000), ("M3.1", "M2.2"), trl=5,
              builds_on=("D09", "D14"), verify="Inspection: proposal submitted (CubeSat Launch Initiative with a university team, or ground-station time on an operating mission)"),
    Milestone("M3.6", 3, "CubeSat entangled-source mission (only with outside funding)", 104, (250_000, 600_000, 1_500_000), ("M3.5", "M3.4"), trl=7,
              builds_on=("D09", "D14"), verify="Test: in-orbit entanglement and a downlink to the ground station", outside=True),
    # ------------------------------------------------------------------------------------------------ Phase 4
    Milestone("M4.1", 4, "Teleportation with feed-forward on a cloud processor", 4, (0, 0, 0), ("M1.2",), trl=3,
              builds_on=("P12", "D07", "E01"), progress="circuits, runner, and device-copy rehearsal done; hardware run next", verify="Test: average fidelity above 2/3 with the two bits, 1/2 without"),
    Milestone("M4.2", 4, "Superdense coding on a cloud processor", 2, (0, 0, 0), ("M1.2",), trl=3,
              builds_on=("P12", "D07"), progress="circuits, runner, and device-copy rehearsal done; hardware run next", verify="Test: two bits per transmitted qubit decoded above chance; none without sending the qubit"),
    Milestone("M4.3", 4, "Teleportation with a delayed classical channel (E01)", 6, (0, 0, 0), ("M4.1",), trl=3,
              builds_on=("E01", "E02"), verify="Analysis: fidelity versus delay against the memory model"),
    Milestone("M4.4", 4, "Three-node entanglement-assisted key network (twin, then two rooms plus one)", 8, (0, 200, 2000), ("M2.3",), trl=4,
              builds_on=("D08", "D13"), verify="Test: keys between every pair through a trusted node and through swapping in the twin"),
    Milestone("M4.6", 4, "Majorana parity teleportation emulated on a cloud processor (with the CSUDH authors)", 4, (0, 0, 0), ("M4.1",), trl=3,
              builds_on=("P13", "E18"), progress="exact fermionic model, circuits, error budget, and simulator rehearsal done; hardware run next",
              verify="Test: two-bit average fidelity above 2/3 on hardware; one-bit at or below 2/3; no-bits at 1/2"),
    Milestone("M4.5", 4, "Photonic teleportation between rooms", 26, (2000, 8000, 30000), ("M2.2", "M4.1"), trl=5,
              builds_on=("D06", "D07"), verify="Test: fidelity above 2/3 with Bell-state measurement and the classical bits", outside=True),
    # ------------------------------------------------------------------------------------------------ startup track
    Milestone("S1", STARTUP, "Customer discovery: 30 interviews (regional I-Corps)", 8, (0, 200, 1000), (), trl=0,
              verify="Inspection: interview log; a stated problem worth paying for, or a decision to stop"),
    Milestone("S2", STARTUP, "Formation and intellectual property (company, provisional filing)", 4, (100, 900, 3000), ("S1", "M1.6"), trl=0,
              verify="Inspection: entity formed; disclosure or provisional filed"),
    Milestone("S3", STARTUP, "First product: the two-room kit and its twin software for teaching labs", 16, (500, 1500, 4000), ("S1", "M1.7"), trl=6,
              builds_on=("P10", "T1", "P09"), verify="Demonstration: a pilot course or lab runs the kit and matches the twin"),
    Milestone("S4", STARTUP, "National I-Corps and SBIR Phase I applications", 12, (0, 500, 2000), ("S2", "S3"), trl=6,
              verify="Inspection: project pitch and proposals submitted"),
)

GATES: tuple[Gate, ...] = (
    Gate("G0", 0, "the simulation reproduces every analytic case and the evidence regenerates", "Phase 1 purchases (about $500 likely)"),
    Gate("G1", 1, "M1.6 passes (measured inside the twin's intervals) and M1.2's paper is drafted",
         "Phase 2: ask to borrow an entangled source; buy only fibers and couplers"),
    Gate("G2", 2, "CHSH above 2 between the rooms and an accepted BBM92 key",
         "Phase 3 outdoor work and the satellite proposal; Phase 4 photonic teleportation"),
    Gate("G3", 3, "a ground station that tracks and timestamps, and a partner or award in hand",
         "a satellite mission, paid for by that partner or award, never out of pocket"),
)


def by_id(mid: str) -> Milestone:
    for m in MILESTONES:
        if m.id == mid:
            return m
    raise KeyError(mid)


def schedule(milestones=MILESTONES) -> dict[str, tuple[float, float]]:
    """Earliest (start, finish) week of every milestone by the critical-path method; done milestones take no time."""
    out: dict[str, tuple[float, float]] = {}
    pending = list(milestones)
    while pending:
        progressed = False
        for m in list(pending):
            if all(p in out for p in m.after):
                start = max((out[p][1] for p in m.after), default=0.0)
                out[m.id] = (start, start + (0.0 if m.done else m.weeks))
                pending.remove(m); progressed = True
        if not progressed:
            raise ValueError(f"cycle or unknown prerequisite among {[m.id for m in pending]}")
    return out


def critical_path(milestones=MILESTONES, end: str | None = None) -> list[str]:
    """The chain of milestones with no slack that ends at `end` (default: the last to finish)."""
    s = schedule(milestones)
    ids = {m.id: m for m in milestones}
    cur = end or max(s, key=lambda k: s[k][1])
    path = [cur]
    while ids[cur].after:
        cur = max(ids[cur].after, key=lambda p: s[p][1])
        path.append(cur)
    return path[::-1]


def phase_cost(phase: int, milestones=MILESTONES, outside: bool = False) -> dict[str, float]:
    """Totals for one track: out-of-pocket milestones by default, or only the outside-funded ones."""
    ms = [m for m in milestones if m.phase == phase and m.outside == outside]
    return {"low": sum(m.cost[0] for m in ms), "likely": sum(m.cost[1] for m in ms), "high": sum(m.cost[2] for m in ms),
            "pert_mean": sum(m.pert_mean for m in ms), "pert_sd": float(np.sqrt(sum(m.pert_sd ** 2 for m in ms)))}


def monte_carlo(milestones=MILESTONES, n: int = 20_000, seed: int = 2026) -> dict[int, dict[str, float]]:
    """Percentiles of each track's out-of-pocket cash cost, sampling every milestone from a triangular distribution."""
    rng = np.random.default_rng(seed)
    out = {}
    for ph in sorted({m.phase for m in milestones}):
        ms = [m for m in milestones if m.phase == ph and m.cost[2] > 0 and not m.outside]
        total = np.zeros(n)
        for m in ms:
            a, c, b = m.cost
            total += rng.triangular(a, c, b, n) if b > a else np.full(n, c)
        out[ph] = {"p50": float(np.percentile(total, 50)), "p80": float(np.percentile(total, 80)), "mean": float(total.mean())}
    return out


def bootstrap_budget(through_phase: int = 2, milestones=MILESTONES) -> dict[str, float]:
    """Out-of-pocket cash for every mission phase up to and including `through_phase`."""
    ms = [m for m in milestones if m.phase <= through_phase and not m.outside]
    return {"likely": sum(m.cost[1] for m in ms), "pert_mean": sum(m.pert_mean for m in ms),
            "high": sum(m.cost[2] for m in ms), "weeks": max(schedule(milestones)[m.id][1] for m in ms)}


def serial_weeks(through_phase: int = 2, milestones=MILESTONES) -> float:
    """Calendar weeks if one person does one milestone at a time: the sum of the out-of-pocket mission milestones'
    durations through a phase. The critical-path schedule assumes parallel work; this is the solo bound."""
    return float(sum(m.weeks for m in milestones if m.phase <= through_phase and not m.outside and not m.done))
