"""Generate the systems-engineering documents that must not drift from the code: the requirements document from the
traceability matrix, and the result tables of the trade studies from the tested models.

    python scripts/build_systems_docs.py      # writes systems/requirements.md and the tables in systems/trade_studies.md
"""
from __future__ import annotations

import re
from dataclasses import replace
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
GH = "https://github.com/Normansrule/quantum-link-research/blob/main/"

NEED_TITLES = {
    "N-1": "Confidential Earth–Mars messaging whose security does not rest on computational assumptions alone",
    "N-2": "A quantitative account of what temperature, loss, and light time do to every link in the chain",
    "N-3": "An honest separation of what is achievable today from what is open research",
    "N-4": "Reproducible, citable models suitable for a master's thesis and for teaching",
    "N-5": "An open-source artifact others can extend",
}
PREFIXES = ("PHY physics invariants · THM thermal · CHN channel · CIR circuit · QKD key distribution · NET network · "
            "CAP capability · APP application · SYS systems · SPC space segment · SEC security · F1 flagship F1 · F2 flagship F2 · "
            "HW hardware node · QEC error correction · WEB website and README")


def requirements_md() -> str:
    from qll.systems.traceability import load_matrix

    rows = load_matrix()
    verified = sum(r["status"].lower().startswith("verified") for r in rows)
    out = ["# Requirements", "",
           "*Generated from `traceability_matrix.csv` by `scripts/build_systems_docs.py`; edit the matrix, not this file.*", "",
           f"{len(rows)} requirements, {verified} verified. A requirement is verified only when its test exists, the named "
           "test function exists in it (checked by `python -m qll.systems.traceability`), and the test passes in CI. "
           "Verification methods follow the classic set: **Test** (the implementation is exercised), **Analysis** (a "
           "tested model is evaluated against the requirement), **Demonstration** (a simulation shows the behaviour end "
           "to end), and **Inspection** (the code or documents are checked mechanically).", "",
           f"Prefixes: {PREFIXES}.", ""]
    for need, title in NEED_TITLES.items():
        mine = [r for r in rows if r["need"] == need]
        if not mine:
            continue
        out += [f"## {need}: {title}", "", "| ID | Requirement | Phase | Method | Verified by | Status |", "|---|---|---|---|---|---|"]
        for r in mine:
            tp = r["test_path"]
            link = f"[`{tp.split('::')[-1] if '::' in tp else tp}`]({GH}{tp.split('::')[0]})" if tp and tp != "TBD" else "—"
            out.append(f"| {r['req_id']} | {r['statement']} | {r['phase']} | {r['method']} | {link} | {r['status']} |")
        out.append("")
    return "\n".join(out)


def trade_tables() -> dict[str, str]:
    from qll.network.memory_decoherence import MEMORY_TABLE
    from qll.network.purified_chain import useful_distance_range_km
    from qll.space.ephemeris import earth_mars_range_m
    from qll.channels.planetshine import airy_leakage
    from qll.systems.mars_budget import MarsLinkDesign, budget, required_rejection

    d = MarsLinkDesign()
    days = np.arange(0.0, 800.0, 1.0)
    r = np.array([float(earth_mars_range_m(t)) for t in days])
    tc, tf = float(days[np.argmin(r)]), float(days[np.argmax(r)])
    f = lambda x: f"{x:.2g}" if x < 1e4 else f"{x:.1e}"
    T = {}
    link_days = lambda dd: sum(1 for t in days[:780] if budget(dd, float(t)).pairs_per_day > 0)
    rows = ["| architecture | pairs/day, closest | pairs/day, farthest | days with a link (of 780) | herald purity, farthest | loss at closest |",
            "|---|---|---|---|---|---|"]
    for arch, name in (("space_source", "source in space, lunar distance from Earth (baseline)"),
                       ("earth_source", "source at a ground station, night only"), ("relay_dual", "relay at L4, two downlinks")):
        dd = replace(d, architecture=arch)
        a, b = budget(dd, tc), budget(dd, tf)
        rows.append(f"| {name} | {f(a.pairs_per_day)} | {f(b.pairs_per_day)} | {link_days(dd)} | {b.purity:.3f} | {a.total_db:.0f} dB |")
    T["architecture"] = "\n".join(rows)
    rows = ["| wavelength | pairs/day, farthest | diffraction factor | Earthshine per mode, farthest | herald purity, farthest | ground atmosphere factor |",
            "|---|---|---|---|---|---|"]
    for lam in (810e-9, 1550e-9):
        b = budget(replace(d, wavelength_m=lam), tf)
        diff = next(s.factor for s in b.stages if "diffraction" in s.name)
        atm = next(s.factor for s in budget(replace(d, wavelength_m=lam, architecture="earth_source"), tf).stages if "atmosphere" in s.name)
        rows.append(f"| {lam * 1e9:.0f} nm | {f(b.pairs_per_day)} | {diff:.2e} | {b.noise_per_mode_s:.2g} /s | {b.purity:.3f} | {atm:.2f} |")
    T["wavelength"] = "\n".join(rows)
    rows = ["| transmitter offset from Earth | angle at farthest | floor 1e-8 | floor 1e-9 (baseline) | floor 1e-10 | Airy wing alone |",
            "|---|---|---|---|---|---|"]
    for off, name in ((4.2e7, "geostationary, 42,000 km"), (3.84e8, "lunar distance, 384,000 km (baseline)"), (1.5e9, "Sun–Earth L1/L2, 1.5 million km")):
        cells = [f"{budget(replace(d, tx_offset_m=off, stray_light=c), tf).purity:.3f}" for c in (1e-8, 1e-9, 1e-10)]
        wing = airy_leakage(off / budget(d, tf).range_m, d.rx_diameter_mars_m, d.wavelength_m)
        rows.append(f"| {name} | {off / budget(d, tf).range_m * 1e3:.2f} mrad | " + " | ".join(cells) + f" | {wing:.1e} |")
    T["needed"] = (f"A purity of 0.99 at the farthest point needs a total off-axis rejection of "
                   f"{required_rejection(d, tf):.1e}; at the closest point, where Earth shows its night side to Mars, "
                   f"{required_rejection(d, tc):.1e} suffices.")
    T["background"] = "\n".join(rows)
    rows = ["| memory | coherence | retrieval | pairs/day to Mars, farthest | fidelity after storage | useful fiber-repeater range |",
            "|---|---|---|---|---|---|"]
    for p in MEMORY_TABLE:
        b = budget(replace(d, memory=p.name), tf)
        rng = useful_distance_range_km(p.lifetime_s, p.efficiency)
        rows.append(f"| {p.name} | {p.lifetime_s:g} s | {100 * p.efficiency:g} % | {f(b.pairs_per_day)} | {b.teleport_fidelity:.2f} | "
                    f"{'none' if rng is None else f'{rng[0]:.0f}–{rng[1]:.0f} km'} |")
    T["memory"] = "\n".join(rows)
    rows = ["| Mars receiver | transmit waist 0.15 m | 0.5 m (baseline) | 1.5 m |", "|---|---|---|---|"]
    for D in (1.0, 2.0, 4.0, 8.0, 16.0):
        rows.append(f"| {D:g} m | " + " | ".join(f(budget(replace(d, rx_diameter_mars_m=D, tx_waist_m=w), tf).pairs_per_day)
                                                  for w in (0.15, 0.5, 1.5)) + " |")
    T["aperture"] = "\n".join(rows)
    from qll.systems.key_ledger import daily_key_bits, ledger
    key = daily_key_bits(d)
    mean = float(key.mean())
    rows = ["| daily demand | one-time pad per day | 256-bit session keys per day | days refused with no bank | key bank needed |",
            "|---|---|---|---|---|"]
    for dem in (1e5, 3e5, 1e6, 2e6, mean):
        L = ledger(d, dem, key)
        tag = " (the mean supply: the most any bank can carry)" if dem == mean else " (baseline)" if dem == 1e6 else ""
        rows.append(f"| {dem:.2g} bits{tag} | {L.otp_bytes_per_day / 1e3:,.0f} kB | {L.sessions_per_day:,.0f} | "
                    f"{L.refused_days_without_bank} of 780 | {L.capacity_bits / 8e6:.2f} MB |")
    T["keyspend"] = "\n".join(rows)
    return T


def fill_trade_studies(text: str, tables: dict[str, str]) -> str:
    for key, table in tables.items():
        text = re.sub(rf"(<!-- trade:{key}:start -->).*?(<!-- trade:{key}:end -->)",
                      lambda m: m.group(1) + "\n" + table + "\n" + m.group(2), text, flags=re.S)
    return text


def see510_traceability_md() -> str:
    """systems/see510/07_traceability.md from systems/see510/traceability.csv: the chain from problem to evidence."""
    import csv
    rows = list(csv.DictReader((ROOT / "systems" / "see510" / "traceability.csv").read_text(encoding="utf-8").splitlines()))
    link = lambda p: f"[`{p.split('::')[-1]}`]({GH}{p.split('::')[0]})"
    ev = lambda p: f"[{p.split('/')[-1] or p}]({p})"
    L = ["# 07 Traceability: stakeholder needs to simulation evidence", "",
         "Generated by `scripts/build_systems_docs.py` from [`traceability.csv`](traceability.csv); a test fails if any "
         "named test or evidence file is missing. The chain is Problem → Stakeholders (the developer-operator, technical "
         "reviewers, and the external user system) → Stakeholder Needs SN-01 to SN-15 → Statement of Need → CONOPS "
         "(01, session sequence) → Simulation function (module) → Test case (06) → Evidence (`evidence/`).", "",
         "| Need | Simulation capability | Module | Test | Evidence | Status |", "|---|---|---|---|---|---|"]
    for r in rows:
        L.append(f"| **{r['need']}** {r['need_text']} | {r['capability']} | `{r['module']}` | {link(r['test'])} | {ev(r['evidence'])} | {r['status']} |")
    met = sum(1 for r in rows if r["status"].startswith("met"))
    L += ["", f"{met} of {len(rows)} needs are met in simulation; the others are partially met or addressed in the hardware "
          "plan, and their status says what is missing. Met in simulation means the modelled system satisfies the need "
          "under the assumptions of 03; it does not mean the hardware does."]
    return "\n".join(L)


def main() -> None:
    (ROOT / "systems" / "see510" / "07_traceability.md").write_text(see510_traceability_md() + "\n", encoding="utf-8")
    (ROOT / "systems" / "requirements.md").write_text(requirements_md() + "\n", encoding="utf-8")
    ts = ROOT / "systems" / "trade_studies.md"
    ts.write_text(fill_trade_studies(ts.read_text(encoding="utf-8"), trade_tables()), encoding="utf-8")
    print("wrote systems/requirements.md and the trade-study tables")


if __name__ == "__main__":
    main()
