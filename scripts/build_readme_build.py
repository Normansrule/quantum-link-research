"""Write the README's closing build guide from the code, so its prices, predictions, and results never drift:

    1. the main experiment (P10, the two-room single-photon link) with the Phase 1 bill of materials and budget,
       from qll/systems/lab_scenes.py, qll/systems/program_plan.py, and the two-room twin;
    2. the experiment that scales the Majorana research of Crogman, Dang, and Erenso (2025), from one hop (P13) to a
       chain (E20), with the latest device-copy rehearsals and the readout a long chain needs, from
       qll/circuits/majorana_chain.py and experiments/bench/frontier/rehearsal/.

The text between the markers below is replaced; tests/test_readme_build.py checks the committed README is current.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
START, END = "<!-- build-guide:start -->", "<!-- build-guide:end -->"


def usd(lo: float, hi: float) -> str:
    return "owned" if hi == 0 else f"${lo:,.0f}–{hi:,.0f}"


def _latest(pattern: str) -> dict | None:
    files = sorted((ROOT / "experiments/bench/frontier/rehearsal").glob(pattern))
    return json.loads(files[-1].read_text(encoding="utf-8")) if files else None


def phase1() -> str:
    from qll.link import two_room
    from qll.link.expected_session import expected_session
    from qll.systems import lab_scenes as L
    from qll.systems import program_plan as P

    c = two_room.config()
    s, p = expected_session(c), two_room.predict()
    lo, hi = L.bom_total(L.two_room())
    ms = [m for m in P.MILESTONES if m.phase == 1]
    tot = [sum(m.cost[i] for m in ms) for i in range(3)]
    rows = "\n".join(f"| {item} | {use} | {usd(a, b)} |" for item, use, a, b in L.P10_BOM)
    mrows = "\n".join(f"| {m.id} | {m.name} | ${m.cost[0]:,.0f} | ${m.cost[1]:,.0f} | ${m.cost[2]:,.0f} |" for m in ms)
    steps = "\n".join(f"{i}. **{a}.** {b}" for i, (a, b) in enumerate(L.P10_STAGES))
    return f"""## Build the main experiment: Phase 1

The main experiment is [P10](experiments/protocols/P10_two_room_single_photon_link.md): single photons between two rooms. Weak 405 nm pulses at about half a photon each carry four polarizations across a hallway, decoy pulses guard against photon-number attacks, and four silicon photomultipliers read them in the other room. A fiber classical channel carries the authenticated protocol. The digital twin predicts the run before you buy a part: a click on {p['click_prob_per_pulse'] * 100:.2f} % of pulses, an error rate of {s['qber'] * 100:.1f} %, and an expected {round(s['key_bits'], -3):,.0f} or so secret bits from each ten-second session. The [link lab](https://normansrule.github.io/quantum-link-research/lab/link/#two_room) shows every part in 3D at the price below.

**Bill of materials (planning prices, October 2026; verify before buying)**

| Item | For | Cost |
|---|---|---|
| Two laptops with Ethernet | the two sites | owned |
{rows}
| **Total** | | **${lo:,.0f}–{hi:,.0f}** |

**Phase 1 budget by milestone** (low, likely, and high, from [`qll/systems/program_plan.py`](qll/systems/program_plan.py)). The milestones count what each step adds, including the $40–120 bright-light analogue that comes first and the open-access fee for the paper. The likely total is ${tot[1]:,.0f}, and the high case stays within ${tot[2]:,.0f}.

| Milestone | What | Low | Likely | High |
|---|---|---|---|---|
{mrows}
| **Phase 1** | | **${tot[0]:,.0f}** | **${tot[1]:,.0f}** | **${tot[2]:,.0f}** |

**Build order.** Each stage is checked against the twin before the next one starts.

{steps}

```
python -m qll.link.run session --config systems/see510/hardware/two_room.json         # predict and write a synthetic run ($0)
python -m qll.link.run ingest room_a.csv --bob room_b.csv --config systems/see510/hardware/two_room.json   # your real logs
```
"""


def majorana() -> str:
    from qll.circuits import majorana_chain as MC

    one, ch = _latest("majorana_fake_*.json"), _latest("chain_fake_*.json")
    f1 = one["runs"]["two_bit"]["verdict"]["average_fidelity"] if one else None
    fb = one["runs"]["one_bit"]["verdict"]["average_fidelity"] if one else None
    chain_f = [ch["runs"][k]["verdict"]["average_fidelity"] for k in sorted(ch["runs"], key=int)] if ch else []
    s, k, nmax = (ch["shrink_per_hop"], ch["offset_k"], ch["max_hops_above_two_thirds"]) if ch else (None, None, None)
    req = "\n".join(f"| {n} | {MC.required_snr(n):.2f} | {_r(MC.required_snr(n, target=0.9))} | {_r(MC.required_snr(n, target=0.99))} |" for n in (1, 4, 16, 64, 128))
    chain_txt = ", ".join(f"{f:.3f}" for f in chain_f)
    return f"""## Scale the Majorana research: from one hop to a chain

Crogman, Dang, and Erenso (2025) teleport a qubit between Majorana-encoded qubits using joint parity measurements alone. The repository emulates their protocol on a free cloud processor, then scales it from one hop to a chain of hops. Each hop is the same local Bell measurement wherever it sits in the chain, because the Jordan–Wigner strings of neighbouring modes cancel, and each hop needs its own two classical bits. The chain's fidelity falls as $F_N = \\tfrac12(1 + k\\,s^N)$, and the paper's error budget turns a target chain length into a requirement on the device.

| Step | What | Hardware | Cost | Status |
|---|---|---|---|---|
| 1. [P13](experiments/protocols/P13_majorana_teleportation_on_a_cloud_processor.md) (M4.6) | The paper's protocol, one hop: two parity bits against one | 3 qubits on a free cloud processor | $0 | device-copy rehearsal: {f1:.3f} with two bits, {fb:.3f} with one; hardware run next |
| 2. [E20](experiments/proposed/E20_majorana_parity_teleportation_chain.md) (M4.8) | The same protocol along 1, 2, 3, … hops; fit the loss per hop | 2N + 1 qubits in a line | $0 | device-copy rehearsal: {chain_txt} for 1–{len(chain_f)} hops; *s* ≈ {s:.2f}, *k* ≈ {k:.2f}, about {nmax} hops above 2/3; hardware run next |
| 3. Device requirement | Readout and poisoning a chain of N hops needs | the error budget | $0 | table below |
| 4. Tetron devices | Four Majorana modes per qubit at fixed parity, with the CSUDH authors and a device group | a partner's dilution refrigerator | outside funding | research version of E18 and E20 |

**What a Majorana chain needs.** Assume a gap Δ/*kT* = 5, poisoning 0.001 per readout window, and *L*/ξ = 6. The table gives the smallest parity-readout signal-to-noise ratio μ₀/σ that keeps the chain above each fidelity:

| Hops | Above 2/3 | Above 0.9 | Above 0.99 |
|---|---|---|---|
{req}

Where a cell says "not reachable", poisoning alone caps every hop and no readout can compensate. Scaling the protocol therefore asks first for longer quasiparticle-poisoning times, and only then for better readout.

```
python experiments/bench/frontier/run_frontier.py majorana --backend aer                      # one hop (P13)
python experiments/bench/frontier/run_frontier.py chain --backend aer --hops 1 2 3            # the chain (E20)
python experiments/bench/frontier/run_frontier.py chain --backend ibm_torino --layout 0 1 2 3 4 5 6 7 8 --hops 1 2 3 4
```
"""


def _r(x: float) -> str:
    return "not reachable" if x == float("inf") else f"{x:.2f}"


def section() -> str:
    return f"{START}\n\n{phase1()}\n{majorana()}\n{END}"


def main() -> None:
    path = ROOT / "README.md"
    text = path.read_text(encoding="utf-8")
    new = section()
    if START in text:
        text = text[:text.index(START)] + new + text[text.index(END) + len(END):]
    else:
        text = text.rstrip("\n") + "\n\n" + new + "\n"
    path.write_text(text, encoding="utf-8")
    print(f"wrote the build guide into {path}")


if __name__ == "__main__":
    main()
