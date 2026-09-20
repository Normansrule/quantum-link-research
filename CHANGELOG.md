# Changelog

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
