# 07 The startup path

**The idea in one line.** Quantum networks will need people and teaching labs that can build, measure, and trust them. This mission produces a validated bench that costs under $1,000, a digital twin that predicts it, and the procedures to run both. The first business is putting those in the hands of the teaching labs and testbeds that need them. The long game is entanglement-assisted secure communication between any two points on Earth, through fiber, free space, and satellites.

**What the company does not sell.** Communication through collapse (it carries no information, [05](05_feasibility.md)); "unhackable" anything (deployed quantum key distribution has been attacked through its hardware many times; see [`experiments/lessons/05_the_qkd_hacking_cycle.md`](../../experiments/lessons/05_the_qkd_hacking_cycle.md)); or key distribution hardware to customers before the company can certify it.

## Who might pay (hypotheses for customer discovery)

| Segment | Their problem (hypothesis) | What we would offer | What would prove us wrong |
|---|---|---|---|
| University physics and engineering teaching labs | quantum-optics teaching kits from established vendors cost thousands per station; few kits teach quantum key distribution end to end with real post-processing | the two-room kit (bill of materials under $1,000), the twin software, and lab procedures that match | labs say price is not the barrier, or that their existing kits already cover key distribution |
| Community colleges and quantum workforce programs | they need hands-on quantum labs but have no optics expertise | a kit with a twin that tells a student what each reading should be, and a course | they want software-only labs |
| Research groups building testbeds | integrating sources, detectors, timing, and post-processing takes a student-year | open post-processing and twin software, integration help | they already have in-house pipelines |
| Companies piloting quantum-safe networking | they need to understand what quantum key distribution would and would not do for them | assessments, simulations of their links, and training | they buy from established vendors directly |

**Customer discovery (S1).** Hold 30 interviews before forming anything. Ask about the problem and today's workaround, not about the product. Your university's I-Corps site, if it has one, runs regional programs built for exactly this; national I-Corps Teams then gives $50,000 for a deeper round [nyu2026icorps]. Record every interview, and set the go/no-go rule in advance: for example, proceed if at least 8 of 30 describe the problem unprompted and at least 3 would pilot.

## Product ladder

| Step | Product | Capital | Built on |
|---|---|---|---|
| 1 | Open-source twin software and curriculum (this repository), with paid support and workshops | very low | Phases 0–1 |
| 2 | The two-room kit: source, receiver, timing boards, mounts, procedures (P10) | low; parts are under $1,000 | M1.6, S3 |
| 3 | The entanglement extension (Phase 2) and the outdoor kit (Phase 3) | moderate | M2.3, M3.2 |
| 4 | Testbed integration and link-assessment services | low capital, labor-heavy | the whole mission |
| 5 | Ground-station and satellite-link services with partners | high; outside funding | Phase 3, Gate G3 |

Open source and a business can coexist: the code and procedures stay open (they are the credibility), and the company sells assembled, tested hardware, support, training, and services.

## Steps from bench to company

| Step | When | What |
|---|---|---|
| S1 Customer discovery | now, in parallel with Phase 1 | 30 interviews; a decision to continue or stop |
| S2 Formation and intellectual property | after M1.6 and a "continue" from S1 | read the university's intellectual-property policy first (MR-S.2); choose an entity; file an invention disclosure or a provisional patent only if a specific invention emerges (the four-diode decoy driver, a gating design, the twin-matching method) |
| S3 First product | after paper 2 (M1.7) | a pilot with one teaching lab; the kit matches its twin in their hands (MR-S.3) |
| S4 Outside funding | after S2 and S3 | national I-Corps; then an NSF SBIR project pitch and Phase I proposal (up to $305,000; Phase II up to $1,250,000, 2026 figures to confirm [bwco2026nsfsbir]) |

## Unit economics for the kit (planning)

| Item | Planning value |
|---|---|
| Parts per two-room kit | $530–1,180 (P10), likely about $600 |
| Assembly and test, at 10 hours and a placeholder rate of $40 per hour | $400 |
| Cost of goods | about $1,000 |
| Price to test in discovery | $2,500–4,000 per kit, with the curriculum |
| Gross margin at $3,000 | about 67 % |

These figures are hypotheses to test in S1 and S3, not forecasts.

## Things to check before selling

- **Intellectual property.** The university's policy on work done with its resources (MR-S.2).
- **Laser safety.** A product with a Class 3R diode inside needs labeling and an interlock design.
- **Export controls.** Quantum-communication items can fall under the Export Administration Regulations. Check them before any international sale (risk MR-R12).
- **Claims.** Marketing says "teaching and testbed equipment," never "secure communication product," until the company can certify the latter.
