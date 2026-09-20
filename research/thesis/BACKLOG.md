# Backlog

Pick a row, open its links, do it, add the test, move the row to `CHANGELOG.md`. Difficulty: ★ an afternoon · ★★ a week · ★★★ a semester. Rows are grouped by workstream; within a group they are in dependency order.

## Code — Phase 2 (circuits) — **done in 0.5.0** (C1–C9, C11); C10 remains

| # | Task | Diff. | Read first | Verifies |
|---|---|---|---|---|
| C1 | `circuits/noise/_kraus_base.py`: `KrausChannel` with the CPTP check | ★ | learn 00/06 | INV-4 |
| C2 | `circuits/fidelity.py`: pure, Uhlmann, Fuchs–van de Graaf test | ★ | learn 00/07 | groundwork REQ-CIR-002 |
| C3 | `circuits/bell.py` + `bell_measurement.py` (deterministic; linear-optics 50%) | ★★ | learn 00/05, 02/06 | REQ-CIR-001 |
| C4 | `circuits/teleportation.py` → `TeleportationRecord` with a `ClassicalMessage` that refuses early reads | ★★ | learn 03/02 | REQ-PHY-002, INV-1, INV-3 |
| C5 | Kraus noise: depolarizing, amplitude, phase damping + QuTiP Lindblad cross-checks incl. thermal | ★★ | learn 00/06 | REQ-THM-002 extended |
| C6 | `circuits/chsh.py` + `hardware/randomness.py` (`EntropySource`, `SerialQrng`) | ★★ | learn 00/05, T10 | REQ-CIR-003, INV-7 |
| C7 | `entanglement_swapping.py`, `superdense_coding.py`, `ghz.py` (Stim), `tomography.py` | ★★ | learn 01/01 | REQ-PHY-003 groundwork |
| C8 | No-cloning guard test over `qll.circuits` | ★ | learn 00/02 | REQ-PHY-003 |
| C9 | Noisy-teleportation sweep vs temperature; `notebooks/01_circuits.ipynb`; CHANGELOG 0.2.0 | ★★ | C4, C5 | REQ-CIR-002 |
| C10 | ~~Exact Gaussian beam forms~~ done in 0.6.0 | ★ | learn 03/04 | REQ-CHN-002 verified |
| C11 | `check_import_dag()` and `check_module_cards()` in `systems/traceability.py` | ★ | design spec §0 | new REQ-SYS-002 |

## Code — Phases 3 to 6 (after Phase 2 lands)
| # | Task | Diff. | Read first |
|---|---|---|---|
| C12 | ~~atmosphere, pointing, link budget; Micius reproduced within 3 dB~~ done in 0.6.0; Jinan-1 exact figures still to verify | ★★ | learn 03/04, done/09 |
| C13 | ~~QKD protocol family with post-processing as `ClassicalMessage` rounds~~ done in 0.7.0 | ★★★ | learn 03/01 |
| C14 | ~~photon_source, detector, beam_splitter, nv_node~~ done in 0.6.0; Perceval adapter added in 0.11.0 | ★★ | learn 00/12, 02/03, 02/06 |
| C15 | ~~memory_decoherence with the memory table; REQ-CAP-001 figure~~ done in 0.8.0 | ★★ | learn 03/03 |
| C16 | ~~purification, swapping_scheduler, repeater_chain (memory + all-photonic), routing~~ done in 0.8.0; SeQUeNCe adapter added in 0.11.0 | ★★★ | learn 03/03, T02, T08 |
| C17 | ~~qll/space: Kepler ephemeris, conjunction, relay constellation, platform thermal, classical link~~ done in 0.9.0; Horizons CSV loader present, relativistic corrections and Jinan-1 fit remain | ★★★ | learn 02/10, T05, T06 |
| C18 | ~~hybrid KEM, AES-GCM, fail-closed messenger, benchmark~~ done in 0.10.0 (E5 cheap version) | ★★ | learn 03/01, E5 |

## Bench
| # | Task | Diff. | Cost | Protocol |
|---|---|---|---|---|
| B1 | Build the NV bench, see the 2.87 GHz dip | ★★ | $100–500 | [P01](../../experiments/protocols/P01_odmr_nv_bench.md) |
| B2 | Split the dip; fit $D\pm\gamma_eB$ | ★ | $0 | P01 |
| B3 | Pulsed control: Rabi, Ramsey, echo, $T_1$ | ★★★ | ~$10k | [P02](../../experiments/protocols/P02_pulsed_nv_control.md) |
| B4 | $T_1(T)$ 77–350 K (E2) | ★★ | $0 above B3 | P02 step 8 |
| B5 | QRNG board as basis source (E6) | ★★ | $0 | P03 step 8 |
| B6 | SPDC source, HOM, CHSH, BB84 | ★★★ | $5–15k | [P03](../../experiments/protocols/P03_spdc_bell_test.md) |
| B7 | Rooftop link and daylight background (E4) | ★★ | $0 above B6 | [P04](../../experiments/protocols/P04_rooftop_free_space_link.md) |

## Research and writing
| # | Task | Diff. | Output |
|---|---|---|---|
| R1 | Verify every **TODO** DOI in `docs/references*.bib`; move confirmed keys to `references.bib` | ★★ | clean bibliography |
| R2 | E8 modality trade study with data and sensitivity analysis | ★★★ | `systems/trade_studies.md` + figure |
| R3 | E3 constellation scheduling on Jinan-1 pass data | ★★★ | `qll/network/relay_constellation.py` + figure |
| R4 | E10 DI certification under latency (Stim + `DelayQueue`) | ★★ | `qll/qkd/e91.py` + REQ-SEC-001 |
| R5 | Fill the 2026 row of the timeline with verified items; track T02–T10 status | ★ | `research/cutting_edge/01` |
| R6 | Thesis chapters: Introduction (README §"six sentences"), Background (learn/), Method (design process), Results (Phases 2–4), Experiments (E1, E2, E6), Discussion (lessons, open problems) | ★★★ | thesis draft |

## Infrastructure
| # | Task | Diff. |
|---|---|---|
| I1 | GitHub Pages: confirm the app and the `learn/` tree render; add a `docs/index.md` landing page | ★ |
| I2 | Pre-commit hooks: `ruff`, link test, figure regeneration | ★ |
| I3 | Zenodo DOI for releases (CITATION.cff is ready) | ★ |
