"""Generate the mission documents that must not drift from the code: the phases and milestones with their costs and
schedule (qll/systems/program_plan.py), the research foundation (qll/systems/experiment_catalog.py), the feasibility
numbers (computed by the tested models), and two figures.

    python scripts/build_program_docs.py
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
OUT = ROOT / "systems" / "program"
GH = "https://github.com/Normansrule/quantum-link-research/blob/main/"

from qll.systems import program_plan as P  # noqa: E402
from qll.systems.experiment_catalog import CATALOG, PHASES, by_id  # noqa: E402

BLUE, ORANGE, AQUA, MUTED, GRID, INK = "#2a78d6", "#eb6834", "#1baf7a", "#8a887f", "#e6e5df", "#2b2a27"
PHASE_COLOR = {0: MUTED, 1: BLUE, 2: AQUA, 3: ORANGE, 4: "#7a5bd6", P.STARTUP: "#b5862b"}


def usd(x: float) -> str:
    if x >= 1e6:
        return f"${x / 1e6:.1f}M"
    if x >= 1e4:
        return f"${x / 1e3:.0f}k"
    return f"${x:,.0f}"


def _rel(path: str) -> str:
    """Link from systems/program/ to a repository path."""
    return "../../" + path


def _link(eid: str) -> str:
    e = by_id(eid)
    return f"[{e.id}]({_rel(e.path)})"


# --------------------------------------------------------------------------------------------- 01 phases/milestones
def milestones_md() -> str:
    s, mc = P.schedule(), P.monte_carlo()
    out = ["# 01 Phases, milestones, gates, schedule, and cost", "",
           "*Generated from `qll/systems/program_plan.py` by `scripts/build_program_docs.py`; edit the plan, not this file.*", "",
           "Each milestone is small enough to finish on its own and ends in a verification with a pass criterion. Weeks "
           "assume about ten hours a week; costs are cash out of pocket in US dollars, as three-point estimates (low, "
           "likely, high) with the PERT mean (a + 4m + b)/6 [malcolm1959]. Start and finish weeks come from the "
           "critical-path method [kelley1959]: a milestone starts when its last prerequisite finishes. Technology "
           "readiness levels (TRL) follow NASA's scale [nasa2016seh]. Milestones marked *outside funding* go ahead only "
           "with a grant, partner, or award, never out of pocket.", "",
           "![schedule](figures/schedule.svg)", ""]
    for ph, title in P.TRACKS.items():
        ms = [m for m in P.MILESTONES if m.phase == ph]
        name = f"Phase {ph}: {title}" if ph != P.STARTUP else title
        out += [f"## {name}", "",
                "| ID | Milestone | Weeks (start–finish) | Cost low / likely / high | PERT mean | After | TRL | Verification | Builds on |",
                "|---|---|---|---|---|---|---|---|---|"]
        for m in ms:
            a, b = s[m.id]
            when = "done" if m.done else f"{a:g}–{b:g}"
            cost = "—" if m.cost[2] == 0 else " / ".join(usd(c) for c in m.cost)
            flag = " *(outside funding)*" if m.outside else ""
            out.append(f"| {m.id} | {m.name}{flag} | {when} | {cost} | {usd(m.pert_mean) if m.cost[2] else '—'} | "
                       f"{', '.join(m.after) or '—'} | {m.trl or '—'} | {m.verify} | {', '.join(_link(x) for x in m.builds_on) or '—'} |")
        pc = P.phase_cost(ph)
        if pc["high"] > 0:
            out += ["", f"Out of pocket: likely {usd(pc['likely'])}, PERT mean {usd(pc['pert_mean'])} ± {usd(pc['pert_sd'])}; "
                        f"Monte Carlo 50th percentile {usd(mc[ph]['p50'])}, 80th {usd(mc[ph]['p80'])}."]
        po = P.phase_cost(ph, outside=True)
        if po["high"] > 0:
            out += ["", f"With outside funding: likely {usd(po['likely'])} (range {usd(po['low'])}–{usd(po['high'])})."]
        out.append("")
    out += ["## Gates", "", "Money for a phase is committed only when the gate before it passes.", "",
            "| Gate | After phase | Pass criteria | Unlocks |", "|---|---|---|---|"]
    out += [f"| {g.id} | {g.after_phase} | {g.criteria} | {g.unlocks} |" for g in P.GATES]
    b1, b2, b4 = P.bootstrap_budget(1), P.bootstrap_budget(2), P.bootstrap_budget(4)
    cp = P.critical_path(end="M2.5")
    out += ["", "## Budget at a glance", "", "![budget](figures/budget.svg)", "",
            "| Through | Likely cash | PERT mean | If everything goes wrong | Calendar, in parallel | Calendar, one milestone at a time |", "|---|---|---|---|---|---|",
            f"| Phase 1 (two rooms, quantum states shared) | {usd(b1['likely'])} | {usd(b1['pert_mean'])} | {usd(b1['high'])} | week {b1['weeks']:g} | week {P.serial_weeks(1):g} |",
            f"| Phase 2 (entanglement between the rooms) | {usd(b2['likely'])} | {usd(b2['pert_mean'])} | {usd(b2['high'])} | week {b2['weeks']:g} | week {P.serial_weeks(2):g} |",
            f"| Phases 3–4, out of pocket only | {usd(b4['likely'])} | {usd(b4['pert_mean'])} | {usd(b4['high'])} | week {b4['weeks']:g} | week {P.serial_weeks(4):g} |",
            "", "The critical-path calendar assumes independent milestones run side by side (with classmates, an advisor's "
                "student, or a collaborator). Alone at ten hours a week, take them one at a time: the last column.",
            "", "The PERT mean of Phase 2 sits far above its likely value because milestone M2.1 ranges from a free loan to "
                "buying a source ($15k). Securing the loan before Gate G1 removes that risk; it is the most valuable "
                "phone call in the plan.", "",
            f"Critical path to the end of Phase 2: {' → '.join(cp)}. M1.2 (the first paper), M3.1 (satellite budgets from "
            "public data), M4.1–M4.3 (cloud processor), and S1 (customer discovery) are off the critical path and can run "
            "in parallel at no cost.", ""]
    return "\n".join(out)


# ------------------------------------------------------------------------------------------- 02 research foundation
def foundation_md() -> str:
    out = ["# 02 Research foundation: every experiment so far, and what each gives the mission", "",
           "*Generated from `qll/systems/experiment_catalog.py` by `scripts/build_program_docs.py`.*", "",
           "Nothing done so far is dropped. Each phase below lists the experiments it builds on: landmark experiments "
           "summarized with a cheap recreation, lab procedures, the two-site link's hardware ladder, proposals, and the "
           "three flagships. **Replicable** means four things exist: a step-by-step procedure, a digital twin in `qll/` "
           "that predicts the result, a test that checks the twin, and a data format the twin reads, so anyone can "
           "repeat the experiment and compare it with the prediction. The rule for this mission is that every physical "
           "experiment is replicable in that sense before it is built.", "",
           "| Status | Count |", "|---|---|"]
    for st in ("replicable", "procedure", "landmark", "proposed", "flagship"):
        out.append(f"| {st} | {sum(e.status == st for e in CATALOG)} |")
    out.append("")
    for ph, title in PHASES.items():
        out += [f"## Phase {ph}: {title}", "", "| ID | Experiment | Status | Twin | Test | Cost | What it gives the mission |", "|---|---|---|---|---|---|---|"]
        for e in [e for e in CATALOG if ph in e.phases]:
            twin = f"[`{Path(e.twin).name}`]({_rel(e.twin)})" if e.twin else "—"
            test = f"[`{Path(e.test).name}`]({_rel(e.test)})" if e.test else "—"
            out.append(f"| {_link(e.id)} | {e.title} | {e.status} | {twin} | {test} | {('$' + e.cost) if e.cost else '—'} | {e.role or '—'} |")
        out.append("")
    out += ["## How to replicate any entry", "",
            "1. Read the file in the ID column; procedures list parts, steps, and expected numbers.",
            "2. Run its twin's test (`python -m pytest <test file>`) to see the prediction checked against closed forms.",
            "3. Build or borrow the setup, log data in the twin's format (for the link: `qll/link/hardware_log.py`, one file per site), and run the same analysis.",
            "4. Compare measurement and prediction; record both, with the configuration and seed, as the evidence.",
            "5. Follow [`experiments/lessons/04_reproducibility_checklist.md`](../../experiments/lessons/04_reproducibility_checklist.md).", ""]
    return "\n".join(out)


# ---------------------------------------------------------------------------------------------- 05 feasibility
def feasibility_md() -> str:
    import numpy as np

    from qll.channels.free_space_diffraction import geometric_transmittance
    from qll.channels.link_budget import JINAN1_2025, MICIUS_2017, LinkBudget, slant_range_m
    from qll.circuits import collapse_signalling as C
    from qll.link import two_room as T
    from qll.link.protocol_bb84 import run_session
    from qll.qkd.plob_bound import plob_bits_per_use

    free, fiber = T.TwoRoomParts(), T.TwoRoomParts(channel="fiber")
    pf, px = T.predict(free), T.predict(fiber)
    mf, mx = run_session(T.config(free)).metrics, run_session(T.config(fiber)).metrics
    msg = np.random.default_rng(1).integers(0, 2, 100)
    bounds = {n: C.analyze(*(lambda r: (r.x, r.b))(C.simulate(msg, n // 100, "basis", seed=5))).mi_upper for n in (10_000, 100_000, 1_000_000)}
    det = {d: C.uses_to_detect(d) for d in (0.01, 0.001)}
    cube = LinkBudget(lambda_m=785e-9, w0_m=0.02, D_rx_m=0.3, sigma_point_rad=2e-6, eta_optics=0.3, eta_det=0.5)
    sat, loss30 = [], {}
    for name, lb, d_rx in (("Micius (published configuration)", MICIUS_2017, "1.2 m"), ("Jinan-1 (published configuration)", JINAN1_2025, "0.28 m"),
                           ("CubeSat source, student station", cube, "0.3 m")):
        z, t30 = lb.loss_db(slant_range_m(500e3, 90), 90), lb.loss_db(slant_range_m(500e3, 30), 30)
        sat.append(f"| {name} | {d_rx} | {z:.0f} dB | {t30:.0f} dB | {2 * t30:.0f} dB |")
        loss30[name.split()[0]] = t30
    fs = []
    for L in (10, 100, 1000, 10_000):
        for w0, D in ((1e-3, 0.025), (5e-3, 0.05)):
            loss = -10 * math.log10(geometric_transmittance(L, 405e-9, w0, D))
            fs.append(f"| {L:,} m | {2 * w0 * 1e3:g} mm | {D * 1e3:g} mm | {'below 0.1 dB' if loss < 0.05 else f'{loss:.1f} dB'} |")
    plob = lambda db: plob_bits_per_use(10 ** (-db / 10))
    L = ["# 05 Feasibility: the physics and the numbers behind each phase", "",
         "*Generated by `scripts/build_program_docs.py`; every number is computed by tested code at generation time.*", "",
         "## The boundary: what a collapse can and cannot carry", "",
         "The idea at the far end of this mission is communication through how shared entangled states collapse. "
         "Quantum mechanics settles part of it exactly. Whatever Alice does to her half of an entangled pair (measure "
         "in any basis, do nothing, apply any operation) is a set of Kraus operators $K_k$ with "
         "$\\sum_k K_k^\\dagger K_k = I$, and Bob's state afterwards is",
         "", "$$\\rho_B' = \\mathrm{Tr}_A\\Big[\\sum_k (K_k\\otimes I)\\rho_{AB}(K_k\\otimes I)^\\dagger\\Big] = \\mathrm{Tr}_A\\,\\rho_{AB} = \\rho_B,$$", "",
         "so no statistic Bob can collect depends on Alice's choice: the no-signalling theorem [ghirardi1980] [nielsen2010]. "
         "The outcomes are correlated, perfectly so in a shared basis, but each side alone sees a fair coin, and the "
         "correlation appears only when the two records are compared over an ordinary channel. A \"Morse code\" in the "
         "collapses therefore carries zero bits. This is checked for random states and random instruments in `tests/test_collapse_signalling.py`, "
         "and it is the first experiment of the mission (P11), because measuring it properly is publishable and "
         "teaches every tool the later phases need.", "",
         "What entanglement does give, and what the frontier of this mission is built on:", "",
         "| Resource | What it delivers | Classical channel needed | Reference |", "|---|---|---|---|",
         "| Shared correlations | identical random bits at both ends, secret if the Bell test passes: a key | yes, to compare a sample and to correct errors | [ekert1991] [bennett1992bbm] |",
         "| Teleportation | an unknown qubit moved without moving the carrier | 2 classical bits per qubit, at light speed or slower | [bennett1993] |",
         "| Superdense coding | 2 classical bits per qubit that is sent | the qubit itself must travel | [bennett1992] |",
         "| Collapse alone | nothing: information per use is exactly 0 | — | [ghirardi1980] |", "",
         "## The collapse code (P11): how many uses to say something", "",
         "A null result is a measured upper bound on the information per use, which shrinks as $1/n$:", "",
         "| Uses per message value | Upper bound on information per use (99 %) |", "|---|---|"]
    L += [f"| {n // 2:,} | {v:.1e} bit |" for n, v in bounds.items()]
    L += ["", f"To detect a bias of 1 % in Bob's outcomes at the 1 % level with 90 % power needs {det[0.01]:,} uses per message "
          f"value; a bias of 0.1 % needs {det[0.001]:,}. On a cloud processor, crosstalk between neighboring qubits is "
          "the effect such a test can actually find (E16); the experiment runs on near and far qubit pairs to tell it "
          "from anything else. Only a dissipative or readout disturbance can show: Bob's reduced state is $I/2$, which "
          "every unitary leaves unchanged.", "",
          "## Phase 1: the two-room link (P10)", "",
          "A 405 nm diode attenuated to 0.5 photons per pulse, polarization BB84 with decoy pulses, and four silicon "
          "photomultipliers (3 mm, photon detection efficiency 31 % at 420 nm, dark rate about 300 kHz at 21 °C "
          "[onsemi2022microfc]), gated for 5 ns at 1 MHz. The twin (`qll/link/two_room.py`) predicts:", "",
          "| Path | Loss | Click probability per pulse | Clicks per second | Error rate (model) | Simulated 10 s session |", "|---|---|---|---|---|---|",
          f"| Free space across a hallway | {pf['path_loss_db']:.1f} dB | {pf['click_prob_per_pulse']:.4f} | {pf['clicks_per_s']:,.0f} | {100 * pf['expected_qber']:.2f} % | "
          f"{'accepted, ' + format(mf.net_key_bits, ',') + ' net key bits' if mf.accepted else 'rejected (' + mf.reject_reason + ')'} |",
          f"| Single-mode fiber through the wall | {px['path_loss_db']:.1f} dB | {px['click_prob_per_pulse']:.4f} | {px['clicks_per_s']:,.0f} | {100 * px['expected_qber']:.2f} % | "
          f"{'accepted, ' + format(mx.net_key_bits, ',') + ' net key bits' if mx.accepted else 'rejected (' + mx.reject_reason + ')'} |", "",
          "The twin's verdict shapes the build: start across a hallway in free space. At 405 nm the fiber's coupling "
          "loss lets the SiPMs' dark counts win; fiber becomes worthwhile with cooled sensors, shorter gates, or a "
          "telecom wavelength and InGaAs detectors (Tier 3, far costlier). Without decoy pulses the worst-case "
          "analysis finds no key at all, because a 0.5-photon pulse carries two or more photons 9 % of the time, "
          "more often than a pulse clicks.", "",
          f"The PLOB bound caps any point-to-point key at {plob(pf['path_loss_db'] + free.receiver_loss_db):.2f} bits per pulse at "
          f"the hallway's {pf['path_loss_db'] + free.receiver_loss_db:.1f} dB [pirandola2017]; the link sits far below it "
          "because of detector efficiency, dark counts, and finite sessions, which is where engineering gains are.", "",
          "## Phase 3: free space and orbit", "",
          "Geometric loss of a Gaussian beam at 405 nm into a receiver lens (diffraction only; turbulence and pointing "
          "add more) [siegman1986]:", "", "| Distance | Beam diameter at the transmitter | Receiver | Geometric loss |", "|---|---|---|---|"]
    L += fs
    L += ["", "Downlink from 500 km (night, the repository's tested link budget [yin2017] [liao2017] [li2025jinan]):", "",
          "| Configuration | Receiver | Loss at zenith | At 30° elevation | Entangled pair to two stations at 30° |", "|---|---|---|---|---|"]
    L += sat
    c30 = loss30["CubeSat"]
    L += ["", f"A CubeSat source with a 4 cm beam into a 30 cm amateur-class telescope loses {c30 - loss30['Jinan-1']:.0f} dB more "
          f"than Jinan-1 and {c30 - loss30['Micius']:.0f} dB more than Micius at 30° elevation, and only if the satellite points to "
          f"about 2 µrad; that pointing, not the optics, is the hard part. The PLOB ceiling there is {plob(c30):.1e} bits per "
          f"pulse, or {plob(c30) * 1e8 / 1e3:.1f} kbit/s from a 100 MHz source; real links reach a small fraction of a ceiling "
          "like this. Only an entangled source "
          "in orbit gives two ground stations shared states without trusting the satellite (Micius did this over "
          "1,200 km [yin2017]); SpooQy-1 showed an entangled-photon source survives on a 3U CubeSat [villar2020].", "",
          "## Requirements these numbers set", "",
          "- The two-room receiver must keep dark counts per gate below about $3\\times10^{-3}$ (SiPM at room temperature, 5 ns gate) and its polarization error below 2 %.",
          "- The source must reach 0.5 photons per pulse with a decoy at 0.1 and vacuum pulses, switched at random per pulse.",
          "- A satellite segment needs about 2 µrad pointing and a ground telescope of 0.3 m or more; it waits for Gate G3.",
          "- Every phase keeps the classical channel; no requirement anywhere depends on signalling through collapse.", ""]
    return "\n".join(L)


# ------------------------------------------------------------------------------------------------------- figures
def figures() -> list[Path]:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    (OUT / "figures").mkdir(parents=True, exist_ok=True)
    s = P.schedule()
    ms = [m for m in P.MILESTONES if not m.done and m.id != "M3.6"]
    fig, ax = plt.subplots(figsize=(10.4, 0.28 * len(ms) + 1.4))
    for i, m in enumerate(ms[::-1]):
        a, b = s[m.id]
        ax.barh(i, b - a, left=a, color=PHASE_COLOR[m.phase], height=0.62, hatch="//" if m.outside else None, edgecolor="white")
        ax.text(b + 0.4, i, f"{m.id} {m.name[:58]}{'…' if len(m.name) > 58 else ''}", va="center", fontsize=7, color=INK)
    ax.set_yticks([]); ax.set_xlim(0, 75)
    ax.set_xlabel("weeks from now (about ten hours a week)")
    ax.set_title("Mission schedule by the critical-path method (M3.6, a funded satellite mission, runs two more years)", loc="left", fontsize=10)
    for ph, col in PHASE_COLOR.items():
        if ph:
            ax.barh(-5, 0, color=col, label=(f"Phase {ph}" if ph != P.STARTUP else "startup track"))
    ax.barh(-5, 0, color="white", edgecolor=MUTED, hatch="//", label="outside funding")
    ax.legend(frameon=False, fontsize=7, ncol=7, loc="upper left", bbox_to_anchor=(0, -0.09))
    ax.set_ylim(-0.8, len(ms) - 0.2)
    ax.grid(axis="x", color=GRID); ax.set_axisbelow(True)
    for sp in ("top", "right", "left"):
        ax.spines[sp].set_visible(False)
    fig.tight_layout()
    p1 = OUT / "figures" / "schedule.svg"
    with matplotlib.rc_context({"svg.hashsalt": "schedule"}):
        fig.savefig(p1, metadata={"Date": None})
    plt.close(fig)

    mc = P.monte_carlo()
    tracks = [1, 2, 3, 4, P.STARTUP]
    labels = ["Phase 1\ntwo rooms", "Phase 2\nentanglement", "Phase 3\nout of pocket", "Phase 4\nout of pocket", "Startup\ntrack"]
    fig, ax = plt.subplots(figsize=(8.4, 3.8))
    x = np.arange(len(tracks))
    likely = [P.phase_cost(t)["likely"] for t in tracks]
    p50 = [mc[t]["p50"] for t in tracks]; p80 = [mc[t]["p80"] for t in tracks]
    ax.bar(x - 0.2, likely, 0.38, color=BLUE, label="likely (every milestone at its most likely cost)")
    ax.bar(x + 0.2, p80, 0.38, color=ORANGE, label="80th percentile (Monte Carlo)")
    for i in range(len(tracks)):
        ax.text(x[i] - 0.2, likely[i] * 1.02 + 60, usd(likely[i]), ha="center", fontsize=8)
        ax.text(x[i] + 0.2, p80[i] * 1.02 + 60, usd(p80[i]), ha="center", fontsize=8)
    ax.set_xticks(x, labels, fontsize=8)
    ax.set_ylim(0, 1.25 * max(p80))
    ax.annotate("the risk of buying an\nentangled source (M2.1)", (x[1] + 0.2, p80[1] * 0.75), (x[1] + 0.75, p80[1] * 0.95),
                fontsize=7, color=INK, arrowprops={"arrowstyle": "->", "color": MUTED})
    ax.set_ylabel("US dollars, cash")
    ax.set_title("Out-of-pocket cost by phase (a funded satellite mission and photonic teleportation excluded)", loc="left", fontsize=10)
    ax.legend(frameon=False, fontsize=8, loc="upper right")
    ax.grid(axis="y", color=GRID); ax.set_axisbelow(True)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    fig.tight_layout()
    p2 = OUT / "figures" / "budget.svg"
    with matplotlib.rc_context({"svg.hashsalt": "budget"}):
        fig.savefig(p2, metadata={"Date": None})
    plt.close(fig)
    return [p1, p2]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "01_phases_and_milestones.md").write_text(milestones_md(), encoding="utf-8")
    (OUT / "02_research_foundation.md").write_text(foundation_md(), encoding="utf-8")
    (OUT / "05_feasibility.md").write_text(feasibility_md(), encoding="utf-8")
    figs = figures()
    print(f"wrote systems/program/01, 02, 05 and {len(figs)} figures")


if __name__ == "__main__":
    main()
