# Thesis Outline

Chapter map with the files and figures that already back each section. A section with no file listed has nothing behind it yet.

| Ch. | Section | Backed by | Status |
|---|---|---|---|
| 1 | Introduction: the question, the catch, the three flagships | README §Six Sentences, `experiments/flagship/README.md`, `figures/overview_storyboard.svg`, `flagship_overview.svg` | drafted in README |
| 2 | Background: quantum mechanics for the link | `learn/00_foundations/*` (15 files) | 80 % written |
| 2 | Background: qubit platforms compared | `learn/02_qubit_modalities/*`, `modality_radar.svg` | 80 % written |
| 2 | Background: communication theory | `learn/03_quantum_communication/*` | 80 % written |
| 3 | Method: systems-engineering V, requirements, traceability | `research/thesis/DESIGN_PROCESS.md`, `systems/*` | written |
| 3 | Method: physics-first modular code, invariants, tests | `docs/physics_module_design.md`, `qll/`, CI | written; Phase 2 implemented |
| 4 | Results I: circuits (teleportation, swapping, CHSH, noise) | `tests/test_phase2_*`, `notebooks/01_circuits.ipynb` | Phase 2 done |
| 4 | Results II: links (budgets, F2 reproduction) | Phase 3 (C12–C14) | not started |
| 4 | Results III: memories and repeaters (crossover, REQ-CAP-001) | Phase 4 (C15–C16), `repeater_rate_explorer.svg`, S02 | simulation only |
| 4 | Results IV: Earth–Mars scheduling and messenger | Phase 5–6 (C17–C18), `mars_light_time_cycle.svg` | not started |
| 5 | Experiments: P01/P02 bench data (E2), E6 QRNG bases | `experiments/protocols/`, `data/` (to be created) | **no data yet** |
| 6 | Discussion: what scaled, contested claims, open problems | `experiments/lessons/*`, `research/cutting_edge/02` | written |
| 7 | Conclusion and future work | `research/thesis/BACKLOG.md`, `NEXT_100.md` | drafted |
| A | Reference database | `docs/references.md` (272 entries) | needs DOI verification pass (R1) |

Word budget (typical MSSE): 60–100 pages; chapters 2 and 3 are already over-supplied and should be *condensed* from the library, not expanded.
