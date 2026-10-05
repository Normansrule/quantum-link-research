# 04 Cost model and funding

## How costs are estimated

- **Three points per milestone.** Every milestone has a low, likely, and high cash cost. The low assumes borrowed or owned equipment; the likely uses planning prices from vendor pages; the high assumes the expensive version of each part. The PERT mean $(a + 4m + b)/6$ and standard deviation $(b - a)/6$ summarize each one [malcolm1959].
- **Monte Carlo for each phase.** Every milestone is sampled from a triangular distribution on its three points, and the 50th and 80th percentiles of each phase's total are reported. Planning to the 80th percentile is the usual confidence for a budget that must not be exceeded [nasa2015ceh].
- **Out of pocket and outside funding are kept apart.** A milestone marked *outside funding* (the CubeSat mission, photonic teleportation between rooms) never enters the out-of-pocket budget. It goes ahead only with a grant, partner, or award.
- **Time is counted, not priced.** Weeks assume about ten hours a week of your own time; nothing in the plan pays for labor. A real company would price that labor, and [07](07_startup_path.md) does.

The numbers are in [01](01_phases_and_milestones.md). In short: sharing quantum states between two rooms is about $670 likely ($1,370 if everything goes wrong). Entanglement between the rooms adds about $450 with a borrowed source. Everything up to a ground-station prototype stays under about $6,000 likely, spread over more than a year.

## How costs are controlled

**Gates.** Phase money is committed only after the previous gate passes (01, Gates). A failed gate costs only the milestones already done, and each of those produced a result or a paper.

**Earned value, lightly.** Keep one line per milestone in a spreadsheet:

| Milestone | Planned cost (likely) | Planned finish week | Actual cost to date | Done? | Earned value (planned cost if done) |
|---|---|---|---|---|---|

The two ratios to watch:

- **Cost performance index:** earned value divided by actual cost. Below 0.8 means the estimates are optimistic; re-estimate the rest of the phase before the next purchase.
- **Schedule performance index:** earned value divided by the planned cost of the milestones due by today. Below 0.8 means the calendar needs a decision: drop a parallel milestone, or move the gate.

**Twin before purchase.** Parts are bought only after the twin says the design works with them (P10 stage 0). The twin already moved the first design from fiber to free space, saving about $300 (planning) in fiber collimators and a session design that could not have worked.

## How to keep it cheap

| Strategy | Where it applies | Typical saving |
|---|---|---|
| Free cloud quantum time: up to 10 minutes every 28 days on IBM's open plan, with a one-time 180-minute offer after 20 minutes of use (March 2026 terms) [ibm2026openplan] | M1.2, M4.1–M4.3, and the first paper | the whole cost of those milestones |
| Public satellite data and the repository's tested link budget | M3.1 | $0 instead of a station |
| Borrowing an entangled-photon teaching kit, or partnering with a physics teaching lab | M2.1 | $15,000 or more |
| Hobby-grade parts where the twin says they suffice: SiPMs instead of single-photon avalanche diode modules, film polarizers, 3D-printed mounts, small FPGA boards | Phase 1 | about 80 % against Tier 3's $2,000–8,000 |
| Used equipment (detectors, time taggers, mounts) from university surplus and auction sites | Phases 2–3 | often 50–80 % |
| Makerspaces and university machine shops | mounts and enclosures | tooling |
| Running independent milestones in parallel with classmates or a lab group | calendar, not cash | about a third of the calendar |

## Where money can come from

| Source | What it gives | Fit | Status of the facts |
|---|---|---|---|
| Your own budget | the Phase 1–2 bench, about $1,100 likely | everything before Gate G2 | — |
| University student research grants and department equipment loans | small grants, and access to lab equipment | Phase 2 source, Phase 3 telescopes | ask CSUDH's research office and physics department |
| NSF I-Corps | regional programs through a university site; national Teams of $50,000 (sub-award through VentureWell; stipends up to $15,000 for the entrepreneurial lead and $10,000 for the technical lead) [nyu2026icorps] | customer discovery (S1, S4) | 2026 structure, from a university summary; confirm with NSF |
| NSF SBIR/STTR (America's Seed Fund) | Phase I up to $305,000, Phase II up to $1,250,000, after a required project pitch [bwco2026nsfsbir] | after a company exists and a validated bench is in hand (S4) | 2026 figures from a secondary source; confirm on NSF's site |
| NASA CubeSat Launch Initiative | a launch for selected missions of educational institutions and nonprofits; the team pays for the satellite itself [nasa2021csli] | M3.6, with a university CubeSat team | check the current call |
| Rideshare launch, for reference | about $6,500 per kilogram on SpaceX Transporter missions in 2023 [payload2023rideshare] | sizing M3.6 (a 3U CubeSat of about 4 kg: on the order of $26,000 for launch alone) | 2023 price; check current |
| Partners: quantum-communication companies and university groups with sources, stations, or satellites | equipment, ground-station time, co-authorship | Phases 2–3 | relationship-driven; start with the authors of the papers you cite |

## Life-cycle view

A company would count every cost from concept to retirement: development, production of kits, support, and the satellite's operations. Phases 0–2 are the concept and technology-development stages, with tiny costs and high learning. The money question becomes real at Phase 3, which is exactly where the plan stops paying out of pocket.
