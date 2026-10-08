# Changelog

## 0.50.0 — 2026-10-08 (the lab: every build in 3D, the math in a terminal, as a web page and an installable app)
- **`docs/lab/`, a lab for the main experiment and the cloud circuits.** Each page shows the real build in 3D with every part where it would stand, a slider for every part you will measure, headline numbers, and a terminal that prints each formula, its substitution, its value, and its citation. Each climbs a ladder from a starter you can build this month to the real-world option.
  - **Two-room link** (`lab/link/`): starter bright-light analogue (T1, $40–120) → the two-room single-photon link (P10, $530–1,180) → avalanche-diode and fiber upgrade (T3) → entangled photons between the rooms (T4, BBM92 with a Bell test). The 3D view shows both rooms, the hallway, the four 405 nm diodes behind their polarizers, the three combining cubes, the pinhole and filters, room B's basis cube, polarizing cubes, half-wave plate and four SiPMs in their dark box, both FPGAs, the laptops, media converters, the fiber classical channel, the clock coax, and the optional eavesdropper's cart. Photons travel and are lost at the rate the twin predicts, and dark counts flash at the detectors.
  - **Build stages:** a slider reveals the parts in the order the protocol builds them (simulate, classical channel, receiver, source, receiver optics, sessions, eavesdropper). Clicking a part shows what it does, the bill-of-materials row that pays for it, its stage, and its twin knob.
  - **Sessions in the browser:** pulse-by-pulse sampling writes `room_a.csv` and `room_b.csv` in the per-site format of `qll/link/hardware_log.py`, checks them against the twin (click probability within 15 %, error rate within 1.5 points), and downloads them for `python -m qll.link.run ingest`.
  - **Cloud circuits** (`lab/circuits/`): the collapse code (P11), teleportation and superdense coding (P12), and Majorana parity teleportation with its error budget (P13), as exact density matrices, with Bob's Bloch vector, the desk, the cloud, and the processor (or the partner lab's refrigerator) in 3D, and the commands that run each on hardware.
  - **Gallery** (`lab/`): all 54 catalogued experiments, filterable by phase and status, each linked to its procedure, twin, and test, and to its lab tier where one exists.
  - **App:** a web manifest, icons, and a service worker make the lab installable and usable offline.
- **One source for the builds.** `qll/systems/lab_scenes.py` defines each tier's parts, positions, bill of materials, stages, sliders, commands, and claim; `scripts/build_lab.py` writes `docs/lab/scenes.json` and `catalog.json` (in the pre-commit hook and CI). Tests check that the P10 rows add up to the protocol's $530–1,180 exactly, that every part is paid for by a real row and every row pays for a part, that the benches are 10 m apart as in the twin, and that every procedure, command, and experiment id exists.
- **The math in the browser is the tested Python.** `docs/js/lab_twin.js` ports `models`, `two_room`, `decoy`, the Tier 1 closed form, and the CHSH helpers; `docs/js/lab_quantum.js` ports the collapse code, teleportation with depolarizing CX noise, superdense coding, and the Majorana model. `tests/test_lab_js.py` runs them under node: the link twins match to 1e-9, the quantum arithmetic to 1e-12 (teleportation and superdense coding also against Qiskit Aer density matrices), and a session sampled in JavaScript is read back by `read_site_logs` and passes `check_against_twin`. Every terminal line cites a bib key or a file that exists.
- **New Python, each tested against an analytic or Monte Carlo result:**
  - `qll/link/expected_session.py`: the protocol's session with every count replaced by its expectation, including the decoy bound and the key length; within 6 % of the full Monte Carlo for the two-room, Tier 3, and Tier 4 presets (12,005 against 12,774 bits for two rooms).
  - `qll/link/bench_tier1.py`: `expected_error`, the Tier 1 error rate in closed form with and without the intercept station, matching the bench's Monte Carlo.
  - `qll/qkd/e91.py`: `chsh_from_visibility` (S = 2√2 V) and `chsh_std`.
- **A correction in P10.** Four diodes need three combining cubes, not two; the parts list and stage 4 now say four non-polarizing beamsplitters (three to combine, one at room B), at the same planning cost.
- **Headless browser tests** for the gallery, the link lab (terminal against the Python twin, sliders, stages, tiers, a sampled session), and the circuits lab (no signalling, the 2/3 limit, one versus two parity bits). Landing page, README, program README, and P10 link to the lab.

## 0.49.0 — 2026-10-06 (Majorana measurement-only teleportation: Crogman, Dang, and Erenso 2025)
- **The paper in the repository.** Crogman, H. T., Dang, T., & Erenso, D. (2025), *Quantum Reports 7*, 42, from CSUDH's physics department, replaces the placeholder bibliography entry. It is read, reproduced, and built into the mission as Phase 4 milestone M4.6.
- **`qll/circuits/majorana_teleport.py`:** an exact fermionic model, with six Majorana operators on three modes (Jordan–Wigner) and parity projections.
  - **Two-bit version:** the paper's Theorem A4 (two commuting parities, four Pauli corrections, each a Majorana bilinear) teleports exactly. Corrections are Clifford and conserve fermion parity, and the sender is left maximally mixed (Theorem A2).
  - **One-bit version:** one parity measurement and one bit (the four steps of Section 4) reach at most the classical 2/3, and the correction as written gives 1/2.
  - **No bits:** Bob holds I/2 for every input.
  - **Entropy:** unchanged under ideal parity measurement of a commuting state, never lowered otherwise (Theorems A5, A6).
  - **Lemma A1, in its precise form:** a single Majorana anticommutes with its pair parity. It cannot read the qubit but can flip it.
- **`qll/circuits/majorana_cloud.py` and protocol P13.** Under Jordan–Wigner, P23 = −X_A X_B and P14 = Y_A Y_B, so the protocol is standard teleportation in a fermionic encoding; it is emulated on qubits after Huang et al. (2021).
  - Four modes, with state-by-state agreement with the fermionic model tested.
  - `run_frontier.py majorana`.
  - Rehearsal on a noisy device copy: 0.835, 0.641, 0.505, and 0.495.
- **`qll/hardware/majorana_error_budget.py`:** the paper's Equations 17–20 in dimensionless knobs (readout signal-to-noise, Δ/kT, poisoning per readout, L/ξ). The readout factor enters twice, because a full teleportation needs two parity measurements, and the hybridization exponent is a parameter.
- **New documents:**
  - **Theory note T16:** what was reproduced; five constructive points to raise with the authors (one bit or two, the no-feed-forward remark, Lemma A1's sign, conventions, parity superselection); an error-budget table; and where a Majorana node sits relative to the mission's photonic link.
  - **E18 and P13:** proposal and protocol (both catalogued); milestone M4.6 and requirement MR-4.6.
  - **Updates:** the learn file on topological qubits, the risk register (ask CSUDH Physics first about borrowing a source), the startup path, and thesis section 5.5.
- **Bibliography:** Crogman et al. (2025), Kitaev (2001), Karzig et al. (2017), Bravyi and Kitaev (2002), Huang et al. (2021), Cheng et al. (2012), Rainis and Loss (2012), Plugge et al. (2017), Bonderson et al. (2008), Dvir et al. (2023), and Albrecht et al. (2016).

## 0.48.0 — 2026-10-05 (the frontier on a free cloud processor, and paper 1's pipeline)
- **Teleportation as an experiment** (`qll/circuits/teleport_cloud.py`, mission milestone M4.1).
  - **Modes:** six cardinal states (a 2-design, so their mean is the average fidelity), each run three ways: with the two bits fed forward, with the corrections deferred, and with no bits.
  - **Closed form:** with a depolarized pair, F = (1 + (1 - p)^2)/2, checked against an exact density-matrix calculation.
  - **Rehearsal on a noisy copy of an IBM device:** 0.835 with feed-forward, 0.951 deferred, and 0.505 without the bits. The classical bits are necessary, and on that device copy the mid-circuit measurement costs fidelity.
- **Superdense coding** (`qll/circuits/superdense_cloud.py`, M4.2). Two bits per transmitted qubit; if the qubit is kept, a guess succeeds 25 % of the time and carries zero bits. Rehearsal: 0.79 success (1.1 bits per use) on the device copy.
- **`qll/circuits/cloud_run.py`:** one path for the ideal simulator, noisy device copies, and real devices (backend lookup, feed-forward support, coupling distance). P11's runner now records the qubit pair's coupling distance.
- **New runner and protocol:** `experiments/bench/frontier/run_frontier.py` (teleport, superdense, analyze), and protocol P12 (catalogued as replicable).
- **Paper 1 pipeline** (`qll/analysis/collapse_report.py`). The pre-registered analysis (Bonferroni-corrected tests, Clopper–Pearson rates, and the convexity bound on information per use) produces the results table and three figures from run files. Hardware data drops in unchanged.
- **Paper 1 draft** (`research/papers/P1_collapse_code/`). Rehearsal on simulators and a device copy:
  - six test runs, all null; tightest bound 1.1 × 10⁻⁴ bit per use;
  - the leak control detected, with its bias matching −γ/2;
  - the teleportation control as above.

  Tests keep the results table and the numbers quoted in the draft in step with the data.
- **Plan:** milestones now record progress (M1.1, M1.2, M4.1, M4.2).

## 0.47.0 — 2026-10-05 (the mission: from two rooms to orbit, on a student budget)
- **A phased mission plan** (`systems/program/`).
  - **Phases:**
    - Phase 0, foundations (done).
    - Phase 1, two rooms: a fiber classical channel and a single-photon quantum link.
    - Phase 2, entanglement between the rooms.
    - Phase 3, outdoors and toward orbit.
    - Phase 4, entanglement-assisted communication.
    - A parallel startup track.
  - **Gates G0–G3:** modelled on NASA's reviews; money is committed only after the previous gate passes. The G0 concept review is recorded.
  - **Milestones:** 29, each with weeks, a three-point cost, prerequisites, a technology readiness level, a verification with a pass criterion, and the experiments it builds on.
  - **Documents:** mission needs and 31 requirements with verification methods; a cost model and funding sources (free cloud time, I-Corps, SBIR, the CubeSat Launch Initiative, with dated and sourced figures); a risk register; five scored trade studies; a startup path; and a plan for the first three papers.
- **`qll/systems/program_plan.py`:**
  - PERT means, a critical-path schedule, and a Monte Carlo cost risk (50th and 80th percentiles).
  - Out-of-pocket and outside-funded milestones are kept apart, and a solo calendar is computed alongside the parallel one.
  - **Result:** two rooms sharing quantum states for about $670 likely ($1,370 at worst); entanglement between the rooms for about $450 more with a borrowed source.
- **`qll/systems/experiment_catalog.py`:**
  - Every experiment in the repository is catalogued, with its status, twin, test, cost, and role: 15 landmarks, P01–P11, the five ladder tiers, E01–E17, and F1–F3.
  - `scripts/build_program_docs.py` generates the phase tables, the research foundation, the feasibility numbers, and two figures.
  - Tests fail if an experiment file is missing from the catalog, or if a replicable entry lacks a procedure, a twin, or a test that uses it.
- **P11 and E17, the collapse code** (`qll/circuits/collapse_signalling.py`). Can the way a shared state collapses carry a message?
  - **Physics:** Bob's state is exactly unchanged by any instrument of Alice's, checked for random states and random instruments.
  - **Analysis:** a Monte Carlo of three encodings; a likelihood-ratio test; Clopper–Pearson intervals; an upper bound on the information per use from the convexity of mutual information; and a sample-size formula.
  - **Controls:** teleportation with and without its two bits, and an injected dissipative leak. A unitary leak would be invisible, because Bob's state is I/2.
  - **Hardware path:** Qiskit circuits, an Aer path, and a runner (`experiments/bench/E17_collapse_code/`) that rehearses on a fake IBM device and runs on real hardware within the free plan.
- **P10, the two-room link** (`qll/link/two_room.py`).
  - **Setup:** four 405 nm diodes behind polarizers with decoy drive, four silicon photomultipliers (datasheet-sourced), and FPGA gating.
  - **Twin:** builds the link configuration from the parts; `predict` and `check_against_twin` give PASS or CHECK line by line. The preset `systems/see510/hardware/two_room.json` is generated from the parts.
  - **Twin verdict:** free space across a hallway gives about 12,800 net key bits per ten-second session. Fiber through the wall at 405 nm does not, because the coupling loss lets dark counts win. Without decoys there is no key.
- **Per-site logs** (`hardware_log.write_site_logs`, `read_site_logs`, `run_from_site_logs`; `run ingest A.csv --bob B.csv`). Room A logs every pulse and room B only its clicks; joining them reproduces the simulated session bit for bit.
- **`qll/link/net_transport.py`:** the classical channel between the rooms over TCP (Ethernet, Wi-Fi, or fiber media converters), with HMAC-SHA256, sequence numbers, and rejection of tampering, replay, and wrong keys. A `probe` command reports round trips against the light's own.
- **Decoy alert:**
  - the honest-channel expectation now includes the vacuum gain, which matters at high dark counts;
  - a decoy gain far *above* expectation also raises an alert;
  - session metrics name the protocol by source model.
- **Other changes:**
  - configuration files may carry any `_`-prefixed notes;
  - `qiskit-ibm-runtime==0.50.0` pinned;
  - protocol and proposal indexes completed (P05–P08 were missing);
  - F1 gains stage S0.5 (two rooms);
  - the hardware ladder gains Tier 2½;
  - thesis section 5.5;
  - README mission section.
- **Bibliography:** Casella and Berger (2002); Clopper and Pearson (1934); Cover and Thomas (2006); Malcolm et al. (1959); Kelley and Walker (1959); NASA cost-estimating handbook (2015); onsemi MicroFC data sheet; Villar et al. (2020); and dated sources for IBM's open plan, NSF SBIR, I-Corps, the CubeSat Launch Initiative, and rideshare prices.

## 0.46.0 — 2026-10-02 (an operations day for the two-site link, and its console)
- **Authentication-key fix.** In 0.45.0 every session spent 381 bits of authentication key, including sessions rejected for their error rate or for too few detections, so an adversary who cut or disturbed the fiber could drain the pre-shared pool. Now:
  - only a session that has passed every other check is authenticated, so a rejected session spends nothing (a tampered session still spends its tags, because tampering is found by the check itself);
  - after acceptance, the pool is topped back up to `auth_pool_bits` from the new key before any key is delivered, which also repays a deficit left by an earlier short session;
  - new metrics `auth_bits_refilled` and `key_delivered_bits`.
- **Scenario 9, an operations day** (`qll/link/operations.py`; `python -m qll.link.run operations`):
  - **Setup:** a 10 km link runs a session every 15 minutes for 24 hours. Key stores and the authentication pool persist, and an application draws 330 keys of 256 bits per hour and is refused when the store is empty.
  - **Scripted events** from the CONOPS degraded and adversarial modes: polarization drift ramping from 1.5 % to 7.5 %, 20 % and 100 % intercept-and-resend, an 8 dB fiber bend, an altered classical message, and a one-hour fiber cut.
  - **Monitoring:** a new degraded status when detections fall below half of the morning baseline, which is the only indicator of the bend; an operator log of events, warnings, and alarms; and the minutes from each event to its first flag.
  - **Result:** 96 sessions, 87 accepted (10 with alerts, 2 with loss flagged), 9 rejected. Every attack was flagged in its first session, the drift after 30 minutes. 7,862 keys were delivered and 7,814 served. 106 requests were refused during the cut (fail closed), and the application resumed after the repair. The pool never fell below 3,715 bits.
  - **Outputs:** written to `systems/see510/evidence/operations/` (README, CSV, log, and a four-panel plot) and to `docs/link/ops.json`.
- **Operations console** (`docs/link/`):
  - **Replay:** a website page that replays the day, labelled as a replay of a simulation. It has play, pause, speed, scrub, and jump-to-event controls.
  - **Status tiles:** status shown with icons and labels, plus the error rate, detections against the baseline, key store, and application.
  - **Charts:** four stacked timelines with shaded events: the error rate with its abort and alert lines, key per session, keys in the store, and the authentication pool.
  - **Details:** a hover tooltip, the current session's full record, the operator log, and the event table with time to flag.
  - **Landing page:** linked from the landing page.
- **Traceability:** SN-04 is met in simulation per session and over a scripted day; live telemetry from hardware is future work. SN-03 is extended. Updated documents:
  - test case TC-10;
  - stage 20;
  - the architecture block table;
  - the authentication rule in the models;
  - the new metrics in inputs and outputs.
- **Evidence SVGs** are now byte-for-byte reproducible (stable element identifiers, no date), so a rerun with the same library versions leaves unchanged plots unchanged.
- **Fixes:**
  - the development-stages table no longer breaks after stage 16;
  - the browser-test server now closes its socket;
  - the slow scenarios test checks the committed plot set instead of a fixed count (it expected 10 plots after 0.45 added two);
  - the README now describes the 0.45 sources and authentication.

## 0.45.0 — 2026-10-02 (information-theoretic authentication; laser sources, decoy states, and photon-number splitting)
- **Wegman–Carter authentication** (`qll/link/authentication.py`; channel mode `wegman_carter`, now the default):
  - **Method:** a polynomial universal hash over GF(2¹²⁷ − 1) with one-time-pad masks. Each site tags its view of the whole transcript once, and the other checks the tag before any key is accepted, so a tampered message is caught at the end of the session.
  - **Cost:** a hash key and two pads, 381 bits per session, drawn from a pool of pre-shared key and replaced from the session's output.
  - **Net key:** new metrics `auth_bits_consumed`, `net_key_bits`, and `forgery_probability` (below 10⁻³² in every scenario session). Only net key reaches the key stores, and a session that nets nothing is flagged. HMAC remains as `auth_mode="hmac"`. SN-05 is now met in simulation.
- **Laser sources** (`source_model`: `weak_coherent`, `weak_coherent_decoy`):
  - Poisson photon numbers, photon-by-photon fiber loss, and click probability for several arriving photons.
  - Signal, weak-decoy, and vacuum intensities chosen at random per pulse.
  - `qll/link/decoy.py`: the vacuum-plus-weak-decoy bounds on the single-photon yield and error rate (Ma et al., 2005) with inverted Chernoff margins on every count, and the worst-case bound without decoys (GLLP). The key length now rests on the single-photon detections.
- **Photon-number-splitting adversary** (`eve_attack="pns"`):
  - **Attack:** keeps one photon of each multi-photon pulse, forwards the rest losslessly, and blocks single-photon pulses just enough to keep the signal gain honest; she cannot tell signal from decoy.
  - **Alert:** raised when the decoy gain falls more than five standard deviations below what the signal gain implies for an honest channel.
  - **Diagnostic:** `naive_key_bits`, the key an analysis ignoring multi-photon pulses would keep (simulation only).
- **Scenario 8** (25 km, 10⁷ pulses):
  - **Ideal source:** 160,180 bits.
  - **Laser without decoys:** rejected even on an honest channel. Under attack, a naive key of about 74,000 bits against about 74,000 known to the adversary.
  - **Laser with decoys:** 25,977 bits honestly, and 3,289 under attack, with an alert at −32 standard deviations.
  - **Decoy laser over distance:** key to 50 km.
- **Other additions:**
  - a net-key plot;
  - experiment logs gain an optional `alice_intensity` column, so a decoy experiment round-trips exactly;
  - the Tier 3 preset now uses the decoy model;
  - assumptions A-01, A-06, A-07, and A-10 updated, and A-15 added;
  - models, test cases (V13–V15, TC-8, TC-9), traceability, stages 18–19, limitations, and the ladder updated;
  - thesis 4.3 extended.
- **Bibliography:** Stinson (1994), Chernoff (1952).

## 0.44.0 — 2026-10-01 (the two-site link in the real world: an experiment ladder, and logs through the same code)
- **`systems/see510/10_real_world_experiments.md`**: five tiers from a tabletop analogue to a deployed link. Each tier has its setup, parts with planning prices, step-by-step build and measurement, a prediction from a preset configuration, pass criteria, what it proves and does not, and safety.
  - **Tier 1, a bright-light polarization analogue** ($40–120): laser pointer, polarizer film on servos, photodiode, Arduino; no security claim.
  - **Tier 2, fiber channel characterization** ($80–350): telecom transceivers, power meter, attenuator, spool, a wavelength multiplexer for coexistence.
  - **Tier 3, weak-coherent BB84 at the single-photon level** ($2,000–8,000; no decoy states yet).
  - **Tier 4, entanglement-based BBM92 with a Bell test** ($15,000–60,000, or a lent teaching kit).
  - **Tier 5, a commercial or testbed link** over deployed fiber.
- **`qll/link/hardware_log.py`**: a per-slot log format for experiments. `run_from_log` replaces steps 3–4 of a session with measured data and runs sifting, estimation, Cascade, verification, amplification, and delivery unchanged; a simulated session written as a log and read back reproduces exactly. New command: `python -m qll.link.run ingest LOG.csv --config ...`. `protocol_bb84.run_session` gains a `record` argument; `simulate_quantum` exposes the simulated record.
- **`qll/link/bench_tier1.py`** and **`experiments/bench/see510_tier1/see510_tier1.ino`**: the Tier 1 bench.
  - Its software twin models Malus's law, polarizer leakage, room light, and noise; with no interception the twin's error rate is near 0 %, and with full intercept-and-resend about 25 %, as the theory says.
  - An Arduino sketch and a serial driver with a three-command protocol.
  - Threshold calibration and a runner that writes the log.
- **Tier presets** (`systems/see510/hardware/`) for Tiers 1, 2, 3, and 4, each documenting its approximations: mean photon number as extra loss, entanglement visibility as misalignment, and accidentals as dark counts.
- **Tests:** a log reproduces the simulated session; malformed logs are refused; the Tier 1 twin with and without interception; the serial protocol against a fake port; the presets predict accepted keys.
- **Documents and traceability:** traceability SN-01, SN-07, SN-08, SN-10, SN-11, and SN-14 updated; development stage 17; the protocols index and flagship F1 link the ladder.
- **Bibliography:** Hecht (2017).

## 0.43.0 — 2026-10-01 (the SEE 510 case study: a two-site fiber key link, simulated end to end)
- **`qll/link/`**: the Scalable Two-Node Fiber-Optic Quantum Communication Link as a modular simulation, one module per block of the handoff's architecture:
  - **Configuration:** every input with ranges and a run identifier (`config.py`).
  - **Models:** closed-form expectations (`models.py`).
  - **Sites and channel:** Site A, the fiber channel, and Site B.
  - **Adversary:** intercept-and-resend on a chosen fraction of pulses, recording what she did.
  - **Classical channel:** HMAC-authenticated, with a transcript and a tampering option.
  - **Reconciliation:** Cascade with back-tracking, every disclosed parity counted, then hash verification.
  - **Protocol:** one BB84 session following CONOPS steps 1–10, with alert and abort thresholds, a Hoeffding margin on the error rate, and Toeplitz privacy amplification.
  - **Monitoring and logging:** status, events, per-run summary, evidence folders, and CSV tables.
  - **Key delivery:** stores with `status`, `get_key`, and `get_key_with_ids` after ETSI GS QKD 014, one store per peer site.
  - **Demonstration:** AES-256-GCM, failing closed with no key.
  - **Scenarios, plots, and a runner:** `python -m qll.link.run session|validate|scenarios|demo`.
- **Validation:** twelve controlled cases (V1–V12) match closed forms within four standard deviations:
  - detection probability, sifting fraction, and error rate at 0, 25, and 75 km;
  - 25 % under full interception;
  - an ideal channel giving identical keys;
  - exact reproducibility from configuration and seed;
  - rejection of tampered messages;
  - Cascade correcting every error within 1.1 to 1.4 times the Slepian–Wolf limit;
  - a fresh run reproducing the committed evidence.
- **Scenarios 1–6 and the demonstration** (`systems/see510/evidence/`, ten plots, generated report):
  - **Throughput:** about 45,000 key bits per second at 0 km and 11,600 at 25 km.
  - **Range:** a 10⁶-pulse block stops yielding key between 75 and 100 km, while ten-times-longer blocks reach 125 km.
  - **Interception:** the operator is alerted from about 10 % interception and the session rejected above about 40 %; accepted sessions lose more bits to privacy amplification than the adversary knew.
  - **Noise:** ordinary noise and interception are indistinguishable by error rate and detection rate.
  - **Key delivery:** only accepted key reaches the application.
- **`systems/see510/`**: the case-study documents:
  - architecture with the CONOPS mapping;
  - protocol selection;
  - fourteen assumptions;
  - every input and output;
  - the mathematical models;
  - test cases;
  - traceability from SN-01 to SN-15 (generated from a CSV and checked by tests);
  - the sixteen development stages with what each proves and does not;
  - limitations and the transition to hardware, with equipment parameters, hazards, and standards.
- **`qll/qkd/privacy_amplification.py`**: Toeplitz hashing gains an exact FFT path (200,000 bits in milliseconds), tested against the explicit matrix product.
- **Requirement REQ-F1-002**, verified in simulation with the hardware pending. Flagship F1 gains stage S0; thesis section 4.3 gains a paragraph on the two-site link; the README gains a section.
- **Bibliography:** Hoeffding (1963), FIPS 198-1, NIST SP 800-90A, ETSI GS QKD 014, Gisin et al. (2002), and Brassard et al. (2000).

## 0.42.0 — 2026-09-30 (the Mars link on a table: a bench to build, with a tested twin)
- **Protocol P09** (`experiments/protocols/P09_mars_link_on_a_table.md`): a lamp for the Sun, a matte white ball for Earth, a fiber tip for the Earth-end transmitter, and a fiber collimator for the Mars receiver, built in eight stages. Each stage has build steps, a prediction, a log format, and a pass criterion:
  - 0: simulate first;
  - 1: frame and lamp calibration;
  - 2: the ball's Lambert phase curve;
  - 3: radiance conservation, the filter law, and single-mode étendue λ² against multimode;
  - 4: off-axis rejection and the stray-light floor;
  - 5: ground source by day and night against a space source;
  - 6: background turning into errors;
  - 7: a synodic period compressed into a seven-minute run, and the key bank.

  Tiered from $0 (simulation) through photodiodes ($150–400) and photon counting (adds $150–400) to the P03 entangled source. Bill of materials, a configuration template, safety notes, and what the bench does and does not prove.
- `qll/systems/bench_twin.py`: the bench's digital twin, predicting every stage with the same functions that evaluate the Mars link. It includes the identity e = w e_opt + (1 − w)/2 = 2(1 − f)/3 between a classical bench's error fraction and the budget's Werner error rate.
- `qll/analysis/bench_fit.py` and `qll/analysis/bench_report.py`: the commands `predict`, `synthetic`, `schedule`, and `report`, which fit each logged stage, compare it with the twin, and print PASS or CHECK. A synthetic data set is in `data/_examples/bench/`.
- `qll/channels/planetshine.py`: `lambertian_radiance` (any lamp), `lambert_geometric_albedo` (p = 2A/3), and `multimode_etendue`.
- **Tests:**
  - the Lambert sphere's p = 2A/3 by integration;
  - the MMF/SMF ratio V²/4;
  - the single-mode background equal to the Mars formula;
  - the error-rate identity;
  - the report recovering a hidden bench (albedo, stray floor, polarization error) from synthetic data.
- **Other additions:**
  - requirement REQ-CHN-003 (verified for the model and analysis, hardware pending);
  - figure `bench_layout` (the bench from above and what stands in for what);
  - a README section "F3 on a table";
  - thesis section 3.4a, "A digital twin for every bench";
  - links from lessons 03/21, 03/22, and proposal E04.

## 0.41.0 — 2026-09-30 (key does not wait; the key bank)
*Includes all of 0.40.0, which had not reached GitHub when this was built; one overlay applies both.*
- **Correction.** The budget charged secret key for the memory wait. In BBM92 each end measures its photon on arrival and compares bases later, so key needs neither storage nor memories: its Werner error rate is set by f₀ and the background alone (3.3 % at closest approach, 5.1 % at the farthest), and key flows on every day with a link, 4.9 × 10⁵ to 2.2 × 10⁷ bits per day, 3.2 × 10⁹ per synodic period (ten times the old figure). `Budget.key_bits_per_day` counts every herald without the memory stage; `extra["key_error_rate"]`; the JavaScript port follows. Risk R-8 (no key near maximum range) is closed: it was an artifact of the error.
- `qll/app/key_bank.py`: the sequent-peak rule of reservoir design sizes the store that lets a fail-closed messenger spend uneven key evenly; a day-by-day bank; the largest demand for a given capacity. Tested against the square-wave result, a wrap-around dry season, the identity K − L_t = S_t, and a 1 % smaller bank that refuses.
- `qll/systems/key_ledger.py`: one synodic period of daily key from the budget, and the bank for a demand. A steady 10⁶ bits per day (125 kB of one-time pad, about 3,900 session keys) needs a 16.7 MB bank at each end; with no bank it is refused on 341 of 780 days. The most any bank can carry is the mean supply, 4.1 × 10⁶ bits per day.
- **Systems**: REQ-APP-003 (the bank carries the baseline demand through every day of the cycle; 35 requirements, 34 verified), trade TS-7 (spending the key), risk R-10 (banked key compromised at rest), R-8 closed, concept of operations steps 4 and 5 rewritten.
- **Link budget page**: a key-bank panel with a synodic period of daily key, the demand, the days a bank-less messenger refuses, and the level of the sequent-peak bank; a demand slider and four KPIs. `docs/js/key_bank.js` matches the Python to 10⁻¹² (Node test); the page test checks the bank against the ledger.
- learn 03/22 "The key bank: storing secrets through conjunction"; learn 03/21's key paragraph corrected; thesis 4.5 and 4.6; a README numbers row.
- Bibliography: Loucks and van Beek (2017), Vernam (1926), Shannon (1949).

## 0.40.0 — 2026-09-29 (the planet in the field of view: background light moves the source into space)
- `qll/channels/planetshine.py`: sunlight reflected by a planet into a single-mode receiver. The radiance of a sunlit Lambertian patch, A E cos z / π; the photons one diffraction-limited mode collects from an extended source, L Δλ λ² / (hc/λ) (étendue λ²); the flux of an unresolved planet, E p (R/d)² Φ(α), with the Lambert-sphere phase function; the Airy wing 8/(π x³); night-side hydroxyl airglow. Tested against direct integration of a Lambertian sphere, the blackbody occupation number 1/(e^{hν/kT} − 1) per mode, and the exact Airy pattern.
- `qll/space/dark_window.py`: the fraction of a day a ground station sees Mars above 40° with the Sun 12° down, clip(ε − 52°, 0, 100°)/360 for an equatorial station; tested against a sweep of the hour angle.
- `qll/systems/mars_budget.py`: a third architecture, `space_source` (the source and Earth-end memory on a spacecraft displaced from Earth, default the lunar distance), now the baseline; a background count per mode at the receiving aperture for every architecture; the herald purity w = S/(S+N); the delivered Werner fraction 1/4 + w(f − 1/4); heralds, teleportations, and key counted per herald; `required_rejection`. New design parameters: `tx_offset_m`, `filter_hz` (100 MHz), `stray_light` (10⁻⁹), `sun_depression_deg`, `night_radiance`.
- **Finding.** A 4 m receiver at 1550 nm resolves Earth from Mars (disk 32–190 µrad, λ/D 0.39 µrad), so it sees the ground around a terrestrial transmitter: in daylight about 190 photons/s per mode against a signal of 0.04–1.4, and over 99 % of heralds would be noise. At night the airglow is faint (99.9 % purity), but the dark-sky window is closed on 333 of 780 days, so the ground source fails REQ-CAP-003. From the lunar distance, Earth sits 1–6 mrad off axis and a 10⁻⁹ stray-light floor keeps ≥ 96 % of heralds clean every day with a link: 3.7 × 10⁷ pairs/day at closest (F 0.91) and 1.1 × 10⁶ at the farthest (F 0.72). A geostationary source is too close: 0.1 mrad at maximum range, where the diffraction wing alone leaks 4 × 10⁻⁹. At 810 nm the Earthshine per 100 MHz mode is lower, not higher, despite the brighter Sun.
- **Systems**: REQ-CAP-005 (stray-light rejection; 34 requirements, 33 verified), REQ-CAP-003 restated for the space source, risk R-9 (sunlit Earth swamps the heralds), TS-1 rewritten with three architectures and link-days, TS-2 with the background charged, TS-6 (transmitter offset × stray-light floor), and the concept of operations updated.
- **Link budget page**: three architectures; a background-light panel (filter bandwidth, stray-light floor, transmitter offset); "what the Mars receiver sees", Earth drawn at its true phase with the transmitter and the receiver's mode; herald purity and background KPIs; a "No dark sky" verdict for the ground station. `budget_core.js` ports the new physics and matches the Python to 10⁻⁹ on nine designs and six dates.
- learn 03/21 gains "The light that is not the signal" and two exercises; thesis 4.5 carries the finding; a README numbers row.
- Bibliography: Gueymard (2004), Russell (1916), Born and Wolf (1999), Hapke (2012), Rousselot et al. (2000), Meeus (1998).

## 0.39.0 — 2026-09-28 (the systems-engineering spine: requirements, trades, risks, traceability page)
- **Traceability matrix** gains a verification method (Test, Analysis, Demonstration, Inspection) and a parent stakeholder need for every row, and eight requirements from the recent work: REQ-NET-002 (rate credited only with F > 2/3), REQ-NET-003 (closed form within 10 % of exact sampling), REQ-CAP-003 (the baseline delivers ≥ 10⁵ useful pairs per day on every available day of a synodic period; new test), REQ-CAP-004 (architecture trade), REQ-HW-001 (CZ fidelity ≥ 0.999, leakage ≤ 10⁻³), REQ-HW-002 (idle-point ZZ below the Ramsey resolution), REQ-QEC-001 (threshold behaviour), REQ-WEB-001 (every published number from tested code). 33 requirements, 32 verified. `python -m qll.systems.traceability` now also fails if a named test function is missing or a row lacks a method or need.
- **Systems documents rewritten**: needs with stakeholders and measures of effectiveness; a concept of operations for the chosen architecture; five trade studies (link architecture, wavelength, memory platform, apertures, transduction) whose result tables `scripts/build_systems_docs.py` regenerates from the tested models; a risk register with likelihood, impact, mitigation, and status (R-1 to R-8); a technology-readiness table. `systems/requirements.md` is generated from the matrix and grouped by need. `tests/test_systems_docs.py` fails if either drifts; the generator runs in the pre-commit hook and CI.
- **Trade results**: the source-at-Earth architecture beats the L4 dual downlink by a factor of about 4 × 10¹⁰; 810 nm delivers 2.4× more pairs than 1550 nm in the budget, pending a daylight-background charge (TS-2 left open); the trapped-ion memory is the only platform fast and useful both to Mars and in fiber chains; rate scales as (transmit waist × receiver diameter)², and the baseline clears REQ-CAP-003 by a factor of about 9.
- **Traceability page** (`docs/systems/`): tickers for needs, requirements, verified, trades, open risks, and tests; a V model whose beams connect each level of decomposition to its verification; a filterable, searchable card for every requirement linking to its test on GitHub; the risk register coloured by status. Headless test. After Magic UI (AnimatedBeam, tickers), react-bits, and worldmonitor. A README section "Systems engineering" with a still of the page (`scripts/record_site.py` now also captures stills).
- Thesis chapter 3 describes the extended V: methods, parent needs, generated documents, trades, and risks.

## 0.38.0 — 2026-09-28 (the Earth–Mars link budget)
- `qll/systems/mars_budget.py`: the end-to-end budget of flagship F3 as a product of tested stages (source and multiplexing, transmit optics, atmosphere, Gaussian-beam diffraction, pointing jitter, receiver and heralding detector, memories at both ends, conjunction and duty), then the memory wait for Earth's two bits, the teleportation fidelity after it, and BBM92 key at the Werner error rate. Two architectures: a source at Earth (one astronomical crossing) and an L4 relay sending one photon to each planet (two crossings).
- **Results** (default design: 10¹² pairs/s across 1000 modes, 0.5 m waist, 4 m receiver, 100 nrad pointing, trapped-ion memories): 2.9 × 10⁷ useful pairs per day at closest approach and 8.7 × 10⁵ at the farthest, fidelity 0.91 and 0.73; diffraction is 87 of the 95 dB; secret key only near closest approach (Werner error rate 27 % at the farthest); the two-downlink relay delivers about 7 × 10⁻⁴ pairs per day, so a relay's role is store-and-forward. The rare-earth crystals deliver ten thousand times fewer pairs, but better ones. A new row in the README's numbers table; a paragraph in thesis section 4.5.
- **Link budget page** (`docs/budget/`): a stream of particles through every stage, its band narrowing with the logarithm of the rate (red where it dies), the Earth–Mars range over two synodic periods with conjunctions shaded, architecture and memory selectors, telescope, pointing, source, and multiplexing sliders, the arriving pairs, fidelity, and key, and the same link with every memory. `docs/js/budget_core.js` ports the budget and its channel models; `tests/test_site.py` holds it to the Python on 25 design-date cases and a headless test checks the page. After Remotion and Magic UI (the flowing stream), llm-viz (real numbers at each stage), and worldmonitor.
- learn 03/21 "The Earth–Mars link budget, stage by stage", with the stage table, the memory trade, the architecture argument, and three exercises.
- The CZ-gate simulation computes every step's exponential in one batched diagonalization and multiplies them by pairwise reduction: identical results, the CZ tests from 20 s to 3 s.
- README: a ninth interactive page with its recording (`anim_budget.gif`, 0.40 MB) and button; the landing page's "Eight ways in"; every page links the budget.
- Bibliography: Bennett, Brassard, and Mermin (1992).

## 0.37.0 — 2026-09-28 (the QEC lab; the surface code under bit flips; the repeater findings in the thesis)
- `qll/circuits/surface_code_capacity.py`: the distance-d rotated surface code's Z checks, independent bit flips, and minimum-weight matching with PyMatching, keeping every shot's errors, syndrome, matched pairs, and correction. Tested: (d²−1)/2 checks of weight 2 and 4, every correction clears its syndrome, ⌊(d−1)/2⌋ errors are always corrected, the curves cross between 8.5 % and 10.5 % (about 9.7 % for d = 9–21, near the 10.3 % asymptotic threshold), and the failure rate falls about eightfold when p halves at d = 5. `surface_code_capacity` figure.
- **QEC lab** (`docs/qec/`): a distance-3, 5, or 7 lattice at five error rates; each of 16 stored shots per setting steps through errors, lit parity checks, the decoder's pairing, and the correction, ending in "intact" or a red string across the lattice; the logical-error curves beside it. `docs/js/qec_core.js` recomputes each syndrome and residual on the page and agrees with the Python on all 240 shots (tested in Node and in headless Chromium). After llm-viz and transformer-explainer, Magic UI, and react-bits. Completes NEXT_100 #97.
- **Thesis** chapter 4.4 now carries the repeater findings of 0.35–0.36: the 0.58 crossover fidelity, the minimum memory times, and the architecture-dependent ranking of memories (a relay rewards coherence, a nested chain rewards retrieval).
- learn 01/15 gains "The surface code, one shot at a time".
- README: an eighth interactive page with its recording (`anim_qec.gif`, 0.26 MB) and button; the landing page's "Seven ways in"; every page links the lab. `record_site.py` pads frames of elements that change height and can record tall panels.
- Bibliography: Wang, Harrington, and Preskill (2003).

## 0.36.0 — 2026-09-26 (purification between levels; where a fiber repeater is worth building)
*Includes all of 0.35.0, which had not reached GitHub when this was built; one overlay applies both.*
- `qll/network/purified_chain.py`: BBPSSW rounds at any nesting level, added to the same closed-form bookkeeping as the plain chain (two pairs per round, success p(f), a classical round trip per round); with no rounds it reproduces `memory_chain` to machine precision. `best_useful_chain` searches up to 16 segments and 0–2 rounds per level for the fastest configuration with teleportation fidelity above 2/3; `minimum_useful_memory_s` and `useful_distance_range_km` answer the design questions.
- **Results**: the 393 km headline chain cannot be made useful by any schedule; a chain that is useful and faster than direct fiber needs memories of at least 4.6 s at 500 km, 39 s at 1000 km, and 23 min at 2000 km, and none helps below about 385 km. Counting retrieval efficiency at every swap, only the ¹⁷¹Yb⁺ (389–2242 km) and NV ¹³C (409–897 km) memories in the table qualify; Eu:YSO fails despite hours of coherence because 0.5–1 % retrieval makes swaps fail. `repeater_design_space` figure; a new row in the README's numbers table.
- **Repeater lab**: purification rounds (on elementary pairs or after every swap too), the pairs spent per delivered pair, the best useful configuration at the current distance, the minimum memory needed there, and a "600 km, 10 s, purify once" preset. The JavaScript port of the purified chain, the search, and the bisection is held to the Python to 10⁻¹²; distance and memory sliders keep preset values exactly.
- learn 03/20 "Where a fiber repeater is worth building", with the table of minimum memory times and the memory ranking, and three exercises.
- Bibliography: Dür et al. (1999); the Bennett et al. (1996) entry gains its DOI and is marked confident.

## 0.35.0 — 2026-09-26 (the repeater lab; the closed form checked by sampling; rate is not enough)
- **Repeater lab** (`docs/repeater/`): one random run of the nested repeater protocol plays out (segments heralding, stored pairs fading as they decay, swaps joining them into longer arcs, failed swaps flashing red) beside the average rate against distance for the memory chain, direct transmission, the repeaterless (PLOB) bound, and an all-photonic chain. Sliders for distance, nesting, memory time, swap success, source efficiency, and pair fraction; KPIs for time to a pair, rate, teleportation fidelity, and the crossover; a verdict that says when the chain is stalled, faster but useless, or winning. After llm-viz and transformer-explainer, Magic UI's AnimatedBeam, and react-bits. Completes NEXT_100 #98.
- `docs/js/repeater_core.js`: a line-by-line port of `repeater_chain.py`, `swapping_scheduler.py`, the swapping and storage recurrences, fiber transmittance, and the PLOB bound; `tests/test_site.py` holds it to the Python to 10⁻¹² on 60 cases, and its sampler to the Python Monte Carlo within 3 %.
- `qll/network/repeater_montecarlo.py`: samples the protocol exactly and finds the closed-form waiting time exact without nesting (0.993 ± 0.007) and conservative with it (0.964 with 4 segments, 0.919 with 8, at P_s = 0.5; 0.81 at P_s = 1). `repeater_sampled` figure.
- **Rate is not enough**: at the 393 km crossover with 1 s memories the delivered pairs have teleportation fidelity 0.58, below the classical 2/3. The README's numbers table now says so, generated from the code; learn 03/19 explains it, and the lab shows that f₀ = 0.99 with 100 s memories and 16 segments gives 0.11 pairs/s at fidelity 0.87 over 1000 km, against 5 × 10⁻¹³ direct.
- learn 03/19 "Repeater chains, sampled" with a table, the figure, and three exercises.
- README: a seventh interactive page with its recording (`anim_repeater.gif`, 0.15 MB), a button, and the sampling figure; the landing page's "Six ways in"; every page links the new lab; the landing navigation hides its section links below 1380 px so it never overflows.

## 0.34.0 — 2026-09-26 (a simulated CZ gate, a ZZ experiment, the coupler lab)
- `qll/hardware/cz_gate.py`: the adiabatic controlled-Z (CZ) gate between two three-level transmons, integrated exactly. A slow pulse follows the adiabatic integral −2π∫ZZ dt to within 1 %, with a residue that halves when the pulse doubles (the super-adiabatic correction); the calibrated 59.5 ns pulse, shaped in the |11⟩–|20⟩ mixing angle after Martinis and Geller, is a CZ with leakage 8 × 10⁻⁵ and coherent fidelity 0.99998, while the same ramps shaped in frequency and recalibrated leave 3.6 % in |20⟩. `cz_pulse` figure. Completes NEXT_100 #32.
- `qll/circuits/zz_ramsey.py`: the conditional-Ramsey experiment that measures static ZZ. Hardware circuits use `delay`; the Qiskit Aer simulation injects RZZ and a phase-damping channel; the fit recovers ±50–80 kHz to within 1.5 kHz and the coupler model's ZZ to within 3 %, and cannot tell the idle point from zero. `zz_ramsey` figure.
- **Proposal E16**: measure ZZ crosstalk across a free cloud quantum processor with those circuits.
- **Coupler lab** (`docs/coupler/`): drag the coupler frequency and watch the ZZ and the Ramsey fringes change, park it at the idle point, and play the CZ gate (flux pulse, avoided crossing, populations, conditional-phase dial) in both pulse shapes. All curves come from `site_data.json`, written by the tested models; a headless test parks it at zero ZZ and checks the gate's phase, fidelity, and leakage. After llm-viz and transformer-explainer (the real internal state at every step), Magic UI (border beams, tickers), and react-bits (glow cards); animation with GSAP.
- README: a sixth gallery entry and button for the coupler lab, the CZ figure in the gallery, and the ZZ-Ramsey figure under More figures. The landing page links the lab ("Five ways in") and its navigation now fits on one line down to 860 px.
- `scripts/record_site.py` stores GIF frames as transparent differences over a palette built from three frames: the five existing recordings shrink from 5.7 MB to 2.6 MB with truer colours, and the new coupler recording is 0.18 MB.
- learn 02/22 gains the CZ gate and "Measuring ZZ yourself", two exercises, and four references (Strauch 2003, DiCarlo 2009, Martinis and Geller 2014, Negîrneac 2021); Pedersen 2007 for the gate-fidelity formula.

## 0.33.0 — 2026-09-26 (a visual README, tunable couplers, no silent complex casts)
- **README redesigned around generated, animated images** (`scripts/make_readme_art.py`), every number taken from `docs/site_data.json` and `docs/status.json`: a numbers card with counting tickers and shine borders (after Magic UI NumberTicker/BentoGrid and react-bits), a log-time chart of which memory outlasts which round trip (after llm-viz and transformer-explainer), the `qll` stack with animated beams (Magic UI AnimatedBeam), a marquee of the fifteen landmark experiments (Magic UI Marquee), and the five equations typeset by matplotlib. Animations are SMIL, which GitHub renders; each starts from the finished picture, so static renderers show the true values.
- Call-to-action buttons, **shields.io endpoint badges** written by `scripts/build_status.py` to `docs/badges/` (version, tests, requirements, references, lessons), a library strip, a two-by-two website gallery with a new **link-monitor recording** (`anim_monitor.gif`, the dashboard through two conjunctions), collapsible detail sections, and a table crediting all twelve inspiring projects. CREDITS.md now says which README image each project shaped.
- `tests/test_readme_art.py`: the art is valid SVG, shows the tested values in its static frame, marks exactly the Mars-capable memories, has one marquee pill per landmark file, every local README link resolves, and the badges follow the endpoint schema. The art regenerates in the pre-commit hook and in CI.
- `qll/hardware/tunable_coupler.py`: static ZZ between transmons by exact diagonalisation of coupled Duffing oscillators, the second-order formula held to it (0.2 % at J = 3 MHz), and a qubit–coupler–qubit model whose ZZ vanishes at the idle point ω_c = 5.221 GHz; `zz_coupler` figure; learn 02/22 (NEXT_100 #32).
- Fix: `gf2_rank` and `repetition_memory` reject complex input (the owner's run showed two ComplexWarnings from the no-cloning scan), and `pyproject.toml` now turns any `ComplexWarning` into a test failure, so this class of bug cannot return silently.
- `experiments/README.md` diagram said ten landmark experiments; there are fifteen.

## 0.32.0 — 2026-09-26 (decoders, quantum volume, Bloch–Redfield, qLDPC, Clifford group)
- `qll/circuits/decoders.py`: circuit-level repetition-code memory in Stim decoded by minimum-weight perfect matching (PyMatching, now pinned in environment.yml); the d = 3, 5, 7 curves cross near p ≈ 0.08 (`decoder_threshold` figure); matching beats undecoded readout fivefold at p = 0.03.
- `qll/circuits/quantum_volume.py`: heavy-output test in Aer (ideal limit (1 + ln 2)/2; n = 4 passes ideal, fails at 15 % CNOT depolarization).
- `qll/circuits/bloch_redfield.py`: QuTiP Bloch–Redfield with an ohmic thermal bath reproduces T₁(T) = T₁(0)/(2n̄+1) to 10⁻³, an independent derivation of the Phase 1 thermal law.
- `qll/circuits/qldpc.py`: hypergraph products with GF(2) ranks; surface codes (13,1), (41,1), (85,1) and the Hamming product (58,16).
- `qll/circuits/groups.py`: 24 single-qubit and 11 520 two-qubit Cliffords.
- learn: 01/15 decoders and thresholds, 01/16 quantum volume and benchmarks, 01/17 qLDPC codes, 00/19 open quantum systems, 00/20 group theory (NEXT_100 #12, #20, #22, #25, #30).

## 0.31.0 — 2026-09-26 (offline site, page tests, README animations, social card)
- **Vendored libraries** (`docs/vendor/`): three.js 0.186.1 (minified with esbuild), GSAP 3.15.0 with ScrollTrigger, KaTeX 0.18.9 with its fonts, each with its licence; no page loads anything from a CDN (enforced by `tests/test_site.py`).
- **Headless page tests** (`tests/test_pages_headless.py`, marker `browser`) in Chromium: every page loads with no JavaScript error; the landing page typesets all equations, renders the capability matrix, and ticks the round trip to 44.6 min; the explainer reaches fidelity 1.000000 with a zero outcome-averaged Bloch vector; the monitor refuses messages through the first conjunction without relays and none through the second with them; the simulator reports light time. A new CI job runs them on every push.
- **README animations**: `scripts/record_site.py` records the real pages with Playwright into GIFs (hero, Mars simulator, teleportation steps, interference lab) using one shared palette per GIF so unchanged pixels cost nothing (Mars: 3.3 → 1.1 MB).
- **Social card** (`docs/og.png`) and Open Graph / Twitter tags on every page.

## 0.30.0 — 2026-09-25 (teleportation explainer, link monitor, interference lab, stack diagram)
*Includes all of 0.29.0, which was not applied on the owner's machine (the overlay was not in Downloads).*
- **Teleportation explainer** (`docs/teleport/`): scroll-driven steps with the exact eight-amplitude state (`docs/js/teleport_core.js`, checked against Qiskit to 10⁻¹²), each outcome at probability ¼, Bob's outcome-averaged Bloch vector at zero (no signalling), the bits' flight at the chosen light time, and fidelity 1 after correction. After llm-viz and transformer-explainer; steps driven by GSAP ScrollTrigger.
- **Link monitor** (`docs/monitor/`): status tiles, a two-synodic-period light-time timeline with blackouts, an event feed, and a fail-closed messenger with finite key storage; with the defaults a conjunction refuses 4 258 messages and the L4/L5 relays refuse none. Buffer rule ported from `qll.app.messenger` and checked against it. After worldmonitor and gods-eye-view.
- **Interference lab** on the landing page: a WebGL fragment shader sums the two slit waves exactly, pointer sets the relative phase, which-path marking removes the cross term (P06). After WebGL-Fluid-Simulation.
- **Stack diagram** with animated beams and a **landmark marquee** (after Magic UI's AnimatedBeam and Marquee); an Explore section linking the four interactive pages.
- README gains a website gallery (screenshots from headless Chromium) and names every inspiring project; CREDITS.md maps each project to the feature it shaped.
- Fix: `quantum_walk.std` rejects complex input instead of casting it (the owner's run showed two ComplexWarnings from the no-cloning scan).

## 0.29.0 — 2026-09-25 (the front door: website, Mars simulator, README, proposals E11–E15)
- **Website rebuilt** (`docs/index.html`, `docs/space.css`, `docs/js/`): a three.js hero of the inner Solar System driven by the Kepler ephemeris, with entangled photons from an L4 relay and the classical bits at c, and a live range / light-time / Sun-angle panel; GSAP scroll reveals and number tickers; nine KaTeX equation cards each showing the tested module's output; bento flagships; the memory capability matrix rendered from data; an interactive three.js Bloch sphere. Techniques inspired by react-bits, Magic UI, Animate UI, motion-primitives and others, re-implemented without copying (CREDITS.md). Verified by headless-Chromium screenshots with no console errors.
- **Mars link simulator** (`docs/mars/`): orbits, conjunction blackout, L4/L5 relays, live light time and round trip, and which memories outlive the current round trip.
- **One source of truth**: `scripts/build_site_data.py` computes every displayed number from `qll` into `docs/site_data.json` and regenerates the README's answer table; `docs/js/ephemeris.js` is a port of the Python ephemeris that agrees to 10⁻¹⁵; `tests/test_site.py` enforces data freshness, JS/Python agreement, script syntax, local links, and the banner.
- **README** redesigned around an animated SVG banner (`scripts/make_banner.py`, numbers from the site data), the computed-answer table, five equations, the flagships, a contents grid, and a figure gallery.
- Proposals E11 (blind computation under latency), E12 (erasure-aware atom repeater), E13 (frequency-multiplexed heralding), E14 (relativistic timing sanity test), E15 (radiation screening).

## 0.28.0 — 2026-09-25 (decompositions, MBQC, filter functions, walks, Landauer, Wigner)
- `qll/circuits/decompositions.py`: ZYZ angles reconstruct random unitaries exactly; KAK CNOT counts (0/1/3/3 for I, CNOT, SWAP, generic); one-bit teleportation on a cluster state matches X^m H Rz(φ).
- `qll/circuits/noise/filter_functions.py`: filter functions for arbitrary pulse sequences (FID and echo closed forms verified), CPMG times, decay exponent against a spectrum (more pulses → more coherence for 1/f noise), passband frequency.
- `qll/circuits/quantum_walk.py`: Hadamard walk vs classical walk; ballistic t versus diffusive √t scaling asserted (σ ≈ 0.54 t).
- `qll/circuits/thermodynamics.py`: Landauer energy and reset-power bound.
- `qll/viz/cat_state_wigner.py`: Wigner functions of coherent, squeezed, and even-cat states with negativity (linked from T03).
- learn: 01/13 gate decompositions and MBQC, 01/14 noise spectroscopy and decoupling, 00/18 quantum walks and thermodynamics (NEXT_100 #13, #14, #15, #23, #26, #28).

## 0.27.0 — 2026-09-25 (landmarks 11–15, lessons 03–05, P08)
- experiments/done: 11 Aspect 1982 (time-varying analyzers), 12 Furusawa 1998 (CV teleportation), 13 Bhaskar 2020 (memory-enhanced communication), 14 Jinan-1 2025 (microsatellite QKD), 15 Bluvstein 2024 (logical atom processor), each with physics, cheap recreation, what went wrong, and the repository hook.
- experiments/lessons: 03 timelines that slipped, 04 reproducibility checklist, 05 the QKD hacking–countermeasure cycle.
- experiments/protocols: P08 time-bin encoding and a phase-locked fibre interferometer (NEXT_100 #69, #76–80, #86–88).

## 0.26.0 — 2026-09-25 (theories T11–T15, modality notes)
- research/theories: T11 communication complexity and fingerprinting, T12 position verification, T13 quantum-secured time transfer, T14 error-corrected memories in space (with the distance-25 arithmetic for a 45-minute hold), T15 ML decoders and remote calibration; each with claim, mechanism, Mars relevance, design change, evidence/TRL, cheap version, references.
- learn/02: 20 silicon spins in depth; 21 NV charge state and the group-IV table (NEXT_100 #35, #38, #39, #89–93).

## 0.25.0 — 2026-09-25 (computing core: codes, QFT, H2, magic states, oscillators)
- `qll/circuits/stabilizer_codes.py`: repetition, five-qubit, and Steane codes with syndromes from Stim Pauli algebra (five-qubit code shown perfect: 16/16 syndromes), and a Stim bit-flip memory experiment reproducing 3p².
- `qll/circuits/algorithms.py`: QFT verified against the Fourier matrix for n = 2–4 in Qiskit's little-endian convention (a first draft had the ordering wrong); phase estimation reads 0.375 exactly with 4 bits and 0.3 to one bit with 5.
- `qll/circuits/chemistry_h2.py`: two-qubit H₂ Hamiltonian; electronic −1.851 Ha + nuclear repulsion 0.714 Ha = −1.137 Ha, the experimental value; a one-parameter VQE ansatz reaches it exactly.
- `qll/circuits/magic_states.py`: 15-to-1 distillation (35p³), rounds and raw states per T, algorithm budgets.
- `qll/circuits/oscillator_states.py`: coherent and squeezed statistics in QuTiP pinned to closed forms.
- learn: 01/11 stabilizer codes hands-on, 01/12 QFT/phase estimation/H₂/magic states, 00/17 oscillator states (NEXT_100 #2, #17, #18, #19, #21).

## 0.24.0 — 2026-09-25 (foundations: measures, Mermin, channel catalogue, RB)
- `qll/circuits/entanglement_measures.py`: partial transpose, negativity (Werner: max(0, f − ½)), PPT test, witness; all three agree on the f = ½ threshold.
- `qll/circuits/mermin.py`: three-qubit Mermin value exact and Stim-sampled; |M| = 4 for GHZ, ≤ 2 for products.
- `qll/circuits/noise/catalogue.py`: twelve named channels (bit/phase/bit-phase flip, Pauli, depolarizing, amplitude and generalized amplitude damping, phase damping, complete dephasing, reset, coherent rotation error, its Pauli twirl), each CPTP-checked on construction; twirling preserves average fidelity, shown by test.
- `qll/circuits/benchmarking.py`: single-qubit randomized benchmarking in Aer with the 24-element Clifford group; decay fit recovers the error per Clifford (slow test).
- learn: 00/16 entanglement measures and multipartite Bell; 01/09 channel catalogue; 01/10 randomized benchmarking in practice (NEXT_100 #9–11, #24).

## 0.23.0 — 2026-09-24 (wiring budget, ion gates, four library files)
- `qll/hardware/cryo_wiring.py`: passive (conduction) and active (attenuator) heat loads per stage for a list of lines, total load against stage cooling powers, and the limiting stage / maximum line count (representative conductivity integrals, flagged for calibration against Krinner et al. Table 2).
- `qll/hardware/trapped_ion.py`: Lamb–Dicke parameter (∝ 1/√(mω)), Mølmer–Sørensen gate time, and the heating/scattering/off-resonant budget with its speed trade.
- learn: 02/17 cryogenic wiring budget, 02/18 ion gates and QCCD, 02/19 quantum-dot sources and integrated photonics, 03/18 twin-field derivation (NEXT_100 #41, #42, #45, #46, #49, #54).

## 0.22.0 — 2026-09-24 (processor physics, CV-QKD, protocols P05–P07)
- `qll/hardware/superconducting.py`: fluxonium and transmon spectra by diagonalisation (transmon matches √(8E_JE_C)−E_C; fluxonium drops tenfold at half flux), dispersive shift, and a readout SNR/fidelity budget with an optimal measurement time against T₁ and amplifier noise.
- `qll/hardware/rydberg.py`: blockade radius (7.5 µm at 5 MHz for Rb 70S), interaction, gate-infidelity budget, blackbody lifetime scaling.
- `qll/qkd/cv_qkd.py`: GG02 asymptotic rate with trusted homodyne noise; below PLOB at every transmittance; the tolerance is to excess noise rather than loss (ξ = 1 % positive at any loss, ξ = 10 % dead beyond ~10 dB). CV curve added to the protocol explorer.
- learn: 02/15 fluxonium and readout, 02/16 Rydberg gates and arrays, 03/17 CV-QKD; protocols P05 (anticorrelation), P06 (quantum eraser), P07 (BB84 over a spool with QRNG bases, F1 stage S2). NEXT_100 #31, #34, #43, #44, #55, #66–68.

## 0.21.0 — 2026-09-24 (memories, conversion, cavities, detectors)
- `qll/network/afc_memory.py`: AFC forward/backward efficiency laws (54 % forward limit at d/F = 2 verified), temporal-mode count, `AfcMemory`.
- `qll/channels/frequency_conversion.py` (Phase 3 stub filled): DFG target wavelength (NV + 1064 nm → 1588 nm), sin² conversion law with P_max ≈ 150 mW for a 4 cm PPLN waveguide, converter noise and the QBER floor it implies; the signal-to-noise ratio falls monotonically with pump, so the operating point is a rate/QBER trade.
- `qll/hardware/nv_node.py`: Purcell factor and cooperativity (Q = 10⁴, V = (λ/n)³ → F_P ≈ 760).
- learn: 03/16 AFC memories and rare-earth crystals; 02/13 frequency conversion and cavities; 02/14 detectors and radiation (NEXT_100 #40, #47, #48, #50, #58, #59).

## 0.20.0 — 2026-09-24 (relativity, turbulence, four library files, PS4)
- `qll/space/relativity.py`: gravitational redshift (Sun + planets; +3.5e-9 Mars vs Earth), range rate from the ephemeris (up to ~17 km/s), first- and second-order Doppler, Shapiro delay (~150 µs at conjunction), and a timing budget per minute of uncorrected clock; tests pin the textbook magnitudes.
- `qll/channels/atmosphere.py`: Hufnagel–Valley 5/7 profile, C_n² integral, Fried parameter checked against site values (5 cm at 500 nm), Rytov variance, scintillation index, aperture averaging, uplink beam wander.
- learn/03: 12 Turbulence and Adaptive Optics, 13 Relativistic Effects on the Link, 14 Side Channels and Countermeasures, 15 Standards and Roadmaps (NEXT_100 #53, #61, #64, #65).
- Problem Set 4 (space segment and application) with machine-checked answers.

## 0.19.0 — 2026-09-24 (DEJMPS, E3 pipeline, problem sets)
- `network/purification.py`: DEJMPS map and an exact numeric DEJMPS; the two agree round by round. **Correction:** earlier drafts of Chapter 4 and learn 03/11 stated BBPSSW from F = 0.8 to 0.99 costs "3 rounds and 18 pairs"; the computed values are 10 rounds and ~2 900 pairs (DEJMPS: 4 rounds, ~32 pairs). Text, figure, and tests now carry the computed numbers.
- `space/relay_constellation.py`: `load_pass_table`, `fit_lognormal`, bootstrap daily key totals — E3 runs on the real Jinan-1 table once downloaded; synthetic campaign file included.
- `learn/assignments/`: three problem sets (qubits and temperature; entanglement and teleportation; links, keys, memories) with `answers.py` and `tests/test_assignments.py`, whose reference values are computed from `qll` and self-tested.

## 0.18.0 — 2026-09-23 (course syllabus; purification and repeater generations)
- `learn/COURSE_SYLLABUS.md`: a 15-week course built from the repository — readings, computations, laboratories, final project, budget tiers, instructor notes.
- `learn/03/11` Purification and Repeater Generations with two generated figures (`purification_recurrence`, `repeater_generations`) — NEXT_100 #56–57.

## 0.17.0 — 2026-09-22 (E9 multiplexing number; E4 prefactor closed)
- `thermal_background.py`: the mode-counting prefactor verified against an independent Planck-radiance derivation (exactly 1 per polarization, 2 for both), the Phase 1 TODO removed, a `polarizations` argument added, and `background_from_spectral_radiance` for measured daylight sky radiance (E4's input). REQ-CHN-003 prefactor verified; the absolute daylight level remains a bench item.
- `simulations/s08_multiplexing_at_au_scale.py`: the multiplexing factor Mars needs, replacing "10³–10⁶" with computed values: ≈2×10³ for 1 pair/s at Mars max with 1 m → 10 m optics (≈50 for a 1 kbit/day key), ≈2×10⁶ with 30 cm optics; scalings D²w₀² asserted in tests.

## 0.16.1 — 2026-09-22 (thesis synchronized with the code)
- Results tables gain sections 9 (device-independent certification under latency) and 10 (transduction trade), generated from the code; Chapter 4 gains §4.7 (proposals settled in software) and §4.8 (pipelines waiting for data); Chapters 5 and 6 updated for S06/S07 and the six proposals with code.

## 0.16.0 — 2026-09-20 (P02 analysis pipeline, P01 bill of materials)
- `qll/analysis/relaxation_fit.py`: Rabi, Ramsey, Hahn-echo, and T1 fits; the Orbach + Raman phonon model for T1(T) [jarmola2012]; the Phase 1 bath-occupation prediction for comparison. Tests recover every parameter from synthetic data and show the two temperature laws differ by orders of magnitude, so P02 step 8 can close REQ-THM-003 with data. (Verification corrected my first claim: the bath law does move T1 by the linear factor 2n̄+1, about 4.5× over 77–350 K; phonons move it by 10³ or more.)
- `experiments/bench/P01_bill_of_materials.md`: itemized parts, quantities, planning prices, verified links, assembly order, and what to record.

## 0.15.0 — 2026-09-20 (E7: transduction trade study)
- `qll/hardware/transduction.py`: transducer model (efficiency, added noise, signal fraction η_t/(η_t+n_add) as the entanglement-fidelity bound, matched-cooperativity efficiency) with representative device points flagged for verification.
- `simulations/s07_transduction_free_vs_through.py`: through a 2020-class or even an optimistic 2025-class transducer the link fidelity falls below the classical 2/3; a target device would win on rate; the transduction-free architecture is confirmed as the baseline in `systems/trade_studies.md`.

## 0.14.0 — 2026-09-20 (E10: device-independent certification under latency)
- `qll/qkd/e91.py`: finite-key DI rate with a simplified statistical penalty (converges to the asymptotic rate; documented as a scheduling model, not a security proof) and the minimum rounds for a positive key.
- `simulations/s06_di_certification_under_latency.py`: CHSH rounds sampled with a declared entropy source, records sealed for the light time, S and finite-key rate evaluated only after arrival; result: an S = 0.95·2√2 device needs ≈ 2 500 rounds, one Mars-max round trip at 1 pair/s supplies ≈ 2 700, so the pair rate decides certifiability.
- REQ-SEC-001 added and verified at model level; 25 requirements, 24 verified.

## 0.13.1 — 2026-09-20 (learning material against the implemented code)
- learn/03: Security Proofs 101 (uncertainty relation → min-entropy → key length, mapped to `qll.qkd`) and Post-Processing With Code (sifting, Cascade vs LDPC at Mars latency, Toeplitz hashing, authentication) — NEXT_100 #51–52.
- Notebooks 02 (BB84 session step by step, intercept-resend, protocol comparison) and 03 (memory capability matrix, purification cost, chain-vs-direct crossover); `tests/test_notebooks.py` executes every notebook headlessly (slow).
- pre-commit hooks now `always_run`.

## 0.13.0 — 2026-09-20 (self-updating status, pre-commit, link check)
- `scripts/build_status.py` → `docs/status.json` and `docs/status.md`: version, test count, requirements verified, references (and how many verified), file counts; README badges/status line and the website hero and a new Status section now come from it.
- `.pre-commit-config.yaml`: fast tests plus regeneration of the references index and status on every commit.
- `.github/workflows/links.yml`: weekly external-link check (lychee) over the video list, the reference index, and the hardware guide.

## 0.12.1 — 2026-09-20 (complete thesis first draft)
- Chapters 2 (background condensed from `learn/`), 5 (experiments: simulations performed, bench prepared, proposals), 6 (discussion), 7 (conclusion) drafted; `scripts/build_thesis.py` assembles all chapters, the generated results tables, and the verification plan into `research/thesis/THESIS_DRAFT.md`.

## 0.12.0 — 2026-09-20 (thesis: results generated from code)
- `scripts/build_results_tables.py` → `research/thesis/results/tables.md`: thermal occupation, channels and light time, satellite link budgets, key rates, the REQ-CAP-001 memory capability matrix, repeater crossovers and purification cost, space segment, messenger buffer — every number computed by the tested functions; a test regenerates the file and checks the headline values.
- `research/thesis/chapters/`: drafts of Chapter 1 (Introduction), Chapter 3 (Method), and Chapter 4 (Results, citing only the generated tables).
- Tests 356.

## 0.11.1 — 2026-09-19 (citation pass, continued)
- Verified against publisher records: `clauser1969` (PRL 23, 880), `ekert1991` (PRL 67, 661); `cirelson1980` DOI recorded from a citing bibliography and marked confident. Remaining code-cited TODOs: 28, listed by `python -c` in the session log.

## 0.11.0 — 2026-09-19 (simulator adapters)
- `qll/hardware/perceval_adapter.py`: Perceval computes the HOM output distribution for a source of indistinguishability V (matches $(1-V)/2$ to 1e-9) and the linear-optics polarization Bell analyser's success (exactly 1/2: Ψ± identified, Φ± confused).
- `qll/network/sequence_adapter.py`: SeQUeNCe two-router meet-in-the-middle link from a generated topology; delivery times and fidelities returned; every delivery time exceeds the herald round trip (INV-1 inside a third-party simulator); delivery slows with distance.
- `tests/test_adapters.py` (marked slow; skipped when the libraries are absent). Tests 355.

## 0.10.2 — 2026-09-19 (citation integrity)
- `tests/test_citations.py`: every `[bibkey]` cited in a `qll` docstring must exist in the BibTeX files, and braces must balance. The check found seven keys cited from code without entries (Holevo-capacity papers, GLLP, JPL mean elements, Planck/JWST/ADR coolers, DSOC); all added, `giovannetti2004` verified against the publisher record. 281 entries.

## 0.10.1 — 2026-09-19 (bench-data scaffold)
- `qll/analysis/odmr_fit.py` (multi-Lorentzian fit, D and B_∥ extraction, sensitivity, temperature-corrected D check, synthetic spectra) and `odmr_report.py` (CLI: fit, print, flag, figure); `data/` with README, naming and sidecar conventions, and a synthetic example; tests recover D to 0.5 MHz and B to 0.5 G.

## 0.10.0 — 2026-09-18 (Phase 6: application layer; all six phases implemented)
- `qll/app/hybrid_kem.py`: ML-KEM-768 (kyber-py, FIPS 203) combined with a QKD share through HKDF; one exchange costs one classical round trip.
- `qll/app/aes_gcm_layer.py`: AES-256-GCM with counter nonces bound to a key id, replay rejection, tamper detection, and a per-key message budget.
- `qll/app/messenger.py`: `KeyBuffer` refilled at the physical key rate, `Messenger` that establishes hybrid sessions, transports every envelope as a `ClassicalMessage`, and **refuses to send when the QKD buffer is empty** (REQ-APP-001 verified); buffer sizing rule for a round trip of unacknowledged traffic.
- `qll/app/benchmark.py`: the three honest numbers (key per day, round trip, refusals) from a simulated conversation; `qll/viz/messenger_latency.py`.
- Requirements REQ-APP-001 and REQ-APP-002 verified: 22 of 24. Tests 343.

## 0.9.0 — 2026-09-18 (Phase 5: space segment)
- `qll/space/ephemeris.py`: Kepler mean-element orbits for Earth and Mars (Newton solver for Kepler's equation, verified perihelion/aphelion radii), range and light time versus time, synodic period 779.9 d, range envelope matching `constants/astro` to 1 % (closes that TODO to the mean-element level); Horizons CSV loader.
- `qll/space/conjunction.py`: Sun–Earth–Mars angle, blackout windows at a SEP threshold (≈ once per synodic period, ~20 days at 3°), availability.
- `qll/space/relay_constellation.py`: relays in Earth orbit, Sun–Earth L4/L5, Mars orbit; per-leg range and SEP; long-leg pair yield from the diffraction law; short-leg log-normal pass yields (Jinan-1-shaped, TODO fit); constellation availability (L4/L5 keep > 99.9 % through conjunction).
- `qll/space/platform_thermal.py`: flown cooler classes with realistic cooling power (tens of mW at 4–6 K, µW at 50–100 mK; no flown dilution refrigerator); `flyable(T, heat_load)`.
- `qll/space/classical_link.py`: Holevo capacity of the pure-loss channel, DSOC-class received photon rate and PPM data rate with the terminal's rate cap (tens of Mb/s beyond 2 au reproduced).
- `qll/viz/relay_constellation_explorer.py`; `mars_light_time_cycle` now uses the Kepler ephemeris.
- Requirements REQ-SPC-001..003 added and verified; tests 338; verified 20 of 23.

## 0.8.0 — 2026-09-18 (Phase 4: memories and repeaters)
- `network/memory_decoherence.py`: memory table (six demonstrated platforms with lifetime, efficiency, temperature, wavelength, bibkey), exact stored-pair channel from the Phase 2 Kraus maps, closed-form fractions for depolarizing and dephasing memories (the dephasing result $f_\infty=(2f_0+1)/6$ corrected during verification), crossover times, and the REQ-CAP-001 capability matrix against six baselines.
- `network/purification.py`: BBPSSW recurrence and a full 16×16 numerical BBPSSW (bilateral CNOT + post-selection) agreeing to 1e-12; rounds-to-target and pair cost; classical time per round.
- `network/swapping_scheduler.py`: exact expectation of the max of two geometric waits (Monte Carlo checked) and the nested schedule vs the 3/2 rule.
- `network/repeater_chain.py`: memory-based nested chain with memory cutoff and fidelity after swaps and storage; all-photonic chain with redundancy; crossover distance (REQ-NET-001 verified: exists for a 1 s memory, absent for 1 ms).
- `network/routing.py`: widest-path routing with a fidelity floor on networkx.
- `qll/viz/memory_crossover.py` (REQ-CAP-001 in one figure); `repeater_rate_explorer` now uses the tested chain model.
- Tests: 331; requirements verified 17 of 20.

## 0.7.0 — 2026-09-18 (Phase 3 part 2: QKD protocols)
- `qll/qkd`: `sifting.py` (with biased-basis fraction), `error_correction.py` (leak f·n·h2(Q); LDPC one-way vs Cascade four round trips, each a `ClassicalMessage`), `privacy_amplification.py` (final length with ε, Toeplitz two-universal hash), `bb84.py` (`run_bb84`: full session, intercept-resend gives 25 % QBER and zero key, classical time ≥ light time), `e91.py` (device-independent rate from S and Q), `decoy_state.py` (GLLP decoy rate ~η vs no-decoy ~η²), `mdi.py`, `twin_field.py` (~√η, crossover with PLOB), `rate_bounds.py` (`assert_below_plob`, INV-5).
- REQ-QKD-002 verified; `qll/viz/qkd_protocols_explorer.py` figure (which protocol wins at which loss).
- Tests: 312.

## 0.6.0 — 2026-09-18 (Phase 3 part 1: links and hardware; reference verification)
- `channels/free_space_diffraction.py`: exact Gaussian beam (Rayleigh range, w(L)) and the exact Gaussian-over-aperture transmittance; the old uniform-disc estimate kept as `_far_field` for teaching (it underestimates by 2×).
- `channels/atmosphere.py` (Beer–Lambert with airmass, Fried parameter), `pointing_jitter.py`, `link_budget.py` (`LinkBudget` with per-factor breakdown, slant range, background QBER floor per gated pulse); published configurations `MICIUS_2017` and `JINAN1_2025`. The Micius two-downlink loss (64–82 dB) is reproduced within 3 dB → REQ-F2-001 (Micius part) verified.
- `hardware/photon_source.py` (SPDC thermal statistics with numerically computed heralded g2 ≈ 2x, weak coherent Poisson with multiphoton fraction, single-emitter herald probabilities), `detector.py` (Si SPAD, InGaAs, SNSPD parameter sets), `beam_splitter.py` (unitary, HOM coincidence vs visibility and reflectivity, dip shape), `nv_node.py` (spin-1 Hamiltonian, exact ODMR lines, Purcell-enhanced herald rate, magnetometer sensitivity).
- References: `shor2000`, `liao2017`, `bourgoin2013` verified against publisher pages; memory-recalled arXiv ids added to 13 entries with explicit TODO flags.
- Tests: 304; REQ-CHN-002 tightened to the exact law.

## 0.5.0 — 2026-09-18 (Phase 2: circuits)
- `qll/circuits`: `noise/_kraus_base.py` (CPTP-checked `KrausChannel` with Aer and QuTiP adapters, average gate fidelity), `fidelity.py` (Uhlmann, trace distance, Fuchs–van de Graaf), `bell.py` (four Bell states, Qiskit and Stim builders, Werner states, Schmidt coefficients, concurrence), `bell_measurement.py` (deterministic and linear-optics), `teleportation.py` (`TeleportationRecord` with a `SealedQubit` that cannot be opened before the `ClassicalMessage` arrives; Haar-averaged fidelity; (2f+1)/3), `entanglement_swapping.py` (heralded, Briegel recurrence verified), `chsh.py` (analytic and Stim-sampled with a declared `EntropySource`), `superdense_coding.py`, `ghz.py` (Stim to 10³ qubits), `tomography.py` (linear inversion + Smolin projection), `no_cloning_guard.py`; noise: depolarizing, amplitude damping, phase damping with QuTiP Lindblad cross-checks.
- `qll/hardware/randomness.py`: `EntropySource` protocol, `NumpyPRNG` (labelled non-quantum), `SerialQrng` for the FPGA board, DI min-entropy from CHSH, SP 800-90B-style health checks.
- Tests: 34 new (phase2), including the no-cloning reflection guard and the import-DAG check; traceability rows REQ-PHY-002/003, REQ-CIR-001..003, REQ-THM-002 → verified; new REQ-CAP-002 and REQ-SYS-002. `notebooks/01_circuits.ipynb`.
- Thesis: `research/thesis/THESIS_OUTLINE.md` and `VERIFICATION_PLAN.md`.

## 0.4.0 — 2026-09-18 (website, simulations, reference database)
- Website: `docs/index.html` + `docs/site.css` — a clean landing page for GitHub Pages with an animated Earth→relay→Mars hero (photons in motion, a draggable distance slider that updates the light time), animated Bloch precession, cards for Learn / Experiments / Simulations / Research / Youtube / References, and figure galleries; the explorers page restyled to match.
- `simulations/`: S01 CHSH vs noise (Aer), S02 teleportation with light-time-delayed bits and a decaying memory (Aer + `ClassicalMessage` guard), S03 link-budget sweep, S04 repetition code in Stim (majority vote, Λ), S05 BB84 key per satellite pass vs background; each writes a figure and has a test asserting an analytic limit.
- References: `docs/references_additions_3.bib` (+95 entries) and `scripts/build_reference_index.py` → `docs/references.md`, 270 entries in 17 topics with verified / confident / TODO status; CI regenerates it.
- Headings cleaned everywhere (e.g. "Youtube", "Learn", "Experiments", "Start Here").

## 0.3.0 — 2026-09-18 (flagships and understanding-first visuals)
- `experiments/flagship/`: F1 Earth↔Earth (two computers, one city), F2 Earth↔satellite, F3 Earth↔Mars — each staged simulate → bench → field with pass numbers, requirements, and references; the README now leads with them.
- Figures (each with a "what to look for" callout): `flagship_overview`, `repeater_rate_explorer` (chain vs direct, memory slider), `mars_light_time_cycle` (synodic cycle with conjunction), `modality_radar` (generated from `learn/02_qubit_modalities/modalities.json`), `surface_code_lattice`.
- Browser app: Bloch-sphere panel with X/Y/Z/H/S/T gate buttons.
- learn/: Micius link budget line by line, clock synchronization for quantum networks, deep-space optical communication (DSOC) as the classical half of F3.
- NEXT_100 items implemented: 60, 62, 63, 96–100.

## 0.2.1 — 2026-09-18 (videos and roadmap)
- `youtube/README.md`: ~45 verified video links (searched and confirmed 2026-09-18) grouped by topic and mapped to `learn/` files; TU Delft qutube.nl bonuses; a "still missing" list.
- `research/thesis/NEXT_100.md`: the next hundred additions by door.

## 0.2.0 — 2026-09-18 (repository redesign: three doors)
- Structure: `knowledge/` split into `learn/` (settled physics, 3 learning paths, per-folder indexes), `experiments/` (bench guide moved here; new `protocols/` P01–P04 lab procedures with safety, parts, build, align, measure, analyze; `done/`, `proposed/`, `lessons/`; `_TEMPLATE.md`), and `research/` (`cutting_edge/` with a 2026 watchlist; `theories/` T01–T10 frontier ideas each with "what it would change for a Mars link"; `thesis/DESIGN_PROCESS.md` systems-engineering loop and decision record; `thesis/BACKLOG.md` what to work on next, by workstream).
- README rewritten as a short visual front door (three doors table, storyboard, repo map figure, six sentences, knobs, 60-second numbers, phases); the equation-heavy content moved to `docs/physics_overview.md`; `START_HERE.md` added.
- `qll/viz/repo_map.py`; figures regenerated; link-integrity tests cover all three doors.

## 0.1.3 — 2026-09-18 (foundations deepened, visual introduction)
- README: newcomer introduction (the idea in six sentences, who-this-is-for table, how-the-pieces-fit diagram, 60-second tour of the numbers) and a six-panel storyboard figure drawn from the tested functions.
- `learn/`: +13 files. Foundations: history in ten experiments, wave mechanics, spin and angular momentum, identical particles (Bose/Fermi, HOM from exchange symmetry), perturbation/adiabatic/annealing, quantum optics states of light, decoherence and interpretations, math toolkit. Computing core: complexity and limits, sensing and metrology, quantum simulation and chemistry, software stack. Modalities: control electronics and readout chain, cryogenics/vacuum/environment (with what has flown in space), materials and fabrication. Plus GLOSSARY.md and MISCONCEPTIONS.md.
- `qll/viz/overview_storyboard.py`; tests 178.

## 0.1.2 — 2026-09-17 (knowledge base)
- `learn/`: 53-file curriculum from foundations to the 2026 frontier; every qubit modality (transmon/SQUID, silicon spin, diamond NV/SiV, ion, Rydberg atom, photonic, Majorana, bosonic) with build, model, results, failures, and link relevance; communication theory; timeline, open problems, reading list; ten landmark experiments with bench recreations; ten proposed experiments E1–E10; contested-claims and what-scaled lessons.
- `qll/viz`: `bloch_sphere`, `rabi_ramsey`, `transmon_levels` (exact charge-basis diagonalization of the transmon Hamiltonian).
- Tests: 143 (knowledge-base link integrity and reference checks; three new render tests).

## 0.1.1 — 2026-09-17 (Phase 1, visual release)
- README rewritten: equations rendered by GitHub math, five committed figures, landmark-experiment table, linked DOIs.
- `qll/viz`: five runnable explorers (thermal occupation, link loss vs PLOB, light time vs memory lifetime, BB84 rate, level map) with matplotlib sliders and a headless `--save` mode; `scripts/make_figures.py` regenerates `docs/figures/`.
- `docs/apps/index.html`: single-file browser app for GitHub Pages mirroring the same formulas with live sliders.
- Docs: hardware and experiments guide, physics-first module design specification, two BibTeX addition files.
- Tests: 33 (5 new headless render tests).

## 0.1.0 — 2026-09-16 (Phase 1)
- Scaffold: `qll` package, pinned conda environment, CI on Ubuntu and Windows.
- Constants (2019 SI, IAU 2012 au), channels (fiber loss, free-space diffraction, deep-space geometry,
  light-time delay, thermal background), thermal qubit model (Bose-Einstein occupation, T1(T),
  generalized amplitude damping), QKD theory (binary entropy, BB84 rate and 11% threshold, PLOB bound).
- Machine-checked requirements traceability matrix (17 requirements) and NASA TRL table.
- 28 analytic pytest tests.
