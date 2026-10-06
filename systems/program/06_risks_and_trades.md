# 06 Risks and trade studies

## Risk register

Likelihood (L) and consequence (C) on a 1–5 scale; the score is their product. Each risk names the milestone where it is retired or the trigger that says it is happening. The mission-level risks of the Earth–Mars architecture are in [`../risk_register.md`](../risk_register.md).

| ID | Risk | L | C | Score | Mitigation | Retired at / trigger |
|---|---|---|---|---|---|---|
| MR-R1 | SiPM dark counts higher than the datasheet (light leaks, warm room), so the two-room error rate exceeds 11 % | 3 | 4 | 12 | measure in a dark box first (P10 stage 3); shorter gate; a $10 Peltier plate; work at night | M1.4; trigger: dark rate above 860 kHz |
| MR-R2 | The four-diode source's diodes differ in wavelength, timing, or beam shape, so the states are partly distinguishable (a side channel) | 4 | 2 | 8 | state it as a limitation; match drive pulses; spatial filter through one pinhole; the paper claims a demonstration, not security | M1.6 (documented) |
| MR-R3 | No entangled source can be borrowed | 3 | 4 | 12 | ask early (now), starting with CSUDH's physics department, whose faculty publish on teleportation (T16); offer co-authorship; P03 build as fallback ($5k–15k), only with a grant | M2.1; trigger: no agreement by Gate G1 |
| MR-R4 | The cloud processor's free allowance shrinks or changes | 2 | 2 | 4 | the analysis runs on any backend; simulator and fake-device results are publishable controls; other providers | M1.2 |
| MR-R5 | A crosstalk "signal" on the processor is misread as signalling | 2 | 5 | 10 | controls in every run; distance dependence; E16 measured the same day; the paper's claim is a bound | M1.2 |
| MR-R6 | Laser eye injury during alignment | 1 | 5 | 5 | 405 nm goggles, beam below eye level, alignment only at low power, sign on the door (P10, Safety) | every session |
| MR-R7 | Calendar slips because one person runs everything | 4 | 3 | 12 | serial calendar planned (01); recruit classmates for parallel milestones; drop optional stages | schedule performance index below 0.8 |
| MR-R8 | Rooftop and building-to-building links need permission and night access | 3 | 3 | 9 | ask facilities early; P04 starts on a balcony or a long corridor | M3.2 |
| MR-R9 | Satellite access depends on partners who say no | 4 | 4 | 16 | M3.1 needs no partner; publish the ground-station work; propose to several teams; CubeSat Launch Initiative with a university team | M3.5 |
| MR-R10 | University intellectual-property policy claims work done with university resources | 3 | 3 | 9 | read the policy before S2; keep personal and university work separate; disclose early | S2 |
| MR-R11 | Over-claiming: the work is read as secure communication or as signalling | 2 | 5 | 10 | requirement MR-X.1; every document says what is simulated, what is measured, and what is not claimed | every paper and gate |
| MR-R12 | Export-control rules on quantum-communication hardware complicate sales abroad | 2 | 3 | 6 | check the Export Administration Regulations before any international sale; start with domestic teaching labs | S3 |

## Trade studies

Weights reflect this mission: a student budget, a short calendar, and evidence that transfers to later phases. Scores run from 1 (poor) to 5 (best), and the totals are weighted sums. The judgments are the author's, and the facts behind them are cited where they exist.

### T-1. The two-room quantum channel

| Option | Cost (0.3) | Works with SiPMs at 405 nm (0.3) | Transfers to Phase 3 (0.2) | Effort (0.2) | Total |
|---|---|---|---|---|---|
| **Free space across a hallway** | 5 | 5 (twin: accepted, about 12,800 bits per 10 s) | 5 (the same optics go outdoors) | 4 | **4.8** |
| Single-mode fiber through the wall at 405 nm | 3 | 1 (twin: rejected; coupling loss lets dark counts win) | 2 | 3 | 2.2 |
| Telecom fiber with InGaAs detectors (Tier 3) | 1 | 1 (needs InGaAs detectors instead) | 3 | 2 | 1.6 |

**Choice:** free space first. Fiber returns in Phase 2 for entangled photons near 810 nm, where silicon detectors are better and single-mode coupling is standard.

### T-2. Single-photon detectors for Phase 1

| Option | Cost (0.4) | Dark counts (0.3) | Efficiency at 405 nm (0.2) | Ease (0.1) | Total |
|---|---|---|---|---|---|
| **SiPM with a comparator, four channels** (about $50 per sensor [onsemi2022microfc]) | 5 | 2 (about 300 kHz) | 4 (31 %) | 3 | **3.7** |
| Used single-photon avalanche diode modules | 2 | 5 | 3 | 5 | 3.4 |
| Photomultiplier tubes | 3 | 4 | 3 | 2 | 3.2 |

**Choice:** SiPMs, because the twin says their dark counts are survivable with a 5 ns gate and decoy pulses. Avalanche-diode modules move to Phase 2 (often in the borrowed kit).

### T-3. Encoding the four states

| Option | Cost (0.3) | Random per pulse (0.4) | Side channels (0.3) | Total |
|---|---|---|---|---|
| **Four diodes behind fixed polarizers** | 4 | 5 | 2 | **3.8** |
| One diode and a servo-turned waveplate | 5 | 1 (a few changes per second) | 4 | 3.1 |
| One diode and an electro-optic modulator | 1 | 5 | 5 | 3.8 |

**Choice:** four diodes, with the side channel stated (MR-R2). An electro-optic modulator ties on score but costs about a semester's budget; it is the upgrade path when there is outside funding.

### T-4. The first step toward orbit

| Option | Cost (0.35) | What it teaches about orbit (0.35) | Independence from partners (0.3) | Total |
|---|---|---|---|---|
| **Link budgets and pass schedules from public data (M3.1)** | 5 | 3 | 5 | **4.3** |
| Building-to-building free-space link at night (M3.3) | 4 | 4 | 4 | 4.0 |
| Optical ground-station prototype (M3.4) | 2 | 5 | 4 | 3.7 |
| Time on an operating mission's ground station | 4 | 5 | 1 | 3.5 |
| A CubeSat source (M3.6) | 1 | 5 | 1 | 2.4 |

**Choice:** all of the first three, in that order. A satellite is pursued only through partners and funding (Gate G3); SpooQy-1 shows a 3U entangled-source CubeSat is possible [villar2020], and Micius shows what a downlink needs [yin2017].

### T-5. The first product (startup)

| Option | Capital needed (0.35) | Validated by this mission (0.35) | Existing demand (0.3) | Total |
|---|---|---|---|---|
| **Two-room kit plus twin software for teaching labs** | 4 | 5 | 3 | **4.1** |
| Simulation and digital-twin software alone | 5 | 4 | 2 | 3.8 |
| Testbed integration services for universities and companies | 4 | 3 | 3 | 3.4 |
| QKD hardware for customers | 1 | 2 | 3 | 2.0 |
| Satellite ground-station services | 1 | 2 | 2 | 1.7 |

**Choice:** the kit and its twin, tested in customer discovery (S1) before anything is built for sale. [07](07_startup_path.md) explains.
