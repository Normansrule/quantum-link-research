# Thesis Outline

Chapter map with the files and figures that already back each section. A section with no file listed has nothing behind it yet.

| Ch. | Section | Backed by | Status |
|---|---|---|---|
| 1 | Introduction: the question, the catch, the three flagships | [`chapters/01_introduction.md`](chapters/01_introduction.md) | **drafted** |
| 2 | Background (condensed) | [`chapters/02_background.md`](chapters/02_background.md) ← `learn/` | **drafted** |
| 2 | Background: qubit platforms compared | `learn/02_qubit_modalities/*`, `modality_radar.svg` | 80 % written |
| 2 | Background: communication theory | `learn/03_quantum_communication/*` | 80 % written |
| 3 | Method: systems-engineering V, requirements, traceability | [`chapters/03_method.md`](chapters/03_method.md), `DESIGN_PROCESS.md`, `systems/*` | **drafted** |
| 3 | Method: physics-first modular code, invariants, tests | `docs/physics_module_design.md`, `qll/`, CI | written; Phase 2 implemented |
| 4 | Results I–IV: all six phases | [`chapters/04_results.md`](chapters/04_results.md), [`results/tables.md`](results/tables.md) (generated) | **drafted from code** |
| 4 | Results II: links (budgets, F2 reproduction) | Phase 3 (C12–C14) | not started |
| 4 | Results III: memories and repeaters (crossover, REQ-CAP-001) | Phase 4 (C15–C16), `repeater_rate_explorer.svg`, S02 | simulation only |
| 4 | Results IV: Earth–Mars scheduling and messenger | Phase 5–6 (C17–C18), `mars_light_time_cycle.svg` | not started |
| 5 | Experiments: simulations performed, bench prepared, proposals | [`chapters/05_experiments.md`](chapters/05_experiments.md) | drafted; **bench data pending** |
| 6 | Discussion | [`chapters/06_discussion.md`](chapters/06_discussion.md) | **drafted** |
| 7 | Conclusion | [`chapters/07_conclusion.md`](chapters/07_conclusion.md) | **drafted** |
| A | Reference database | `docs/references.md` (272 entries) | needs DOI verification pass (R1) |

Word budget (typical MSSE): 60–100 pages; chapters 2 and 3 are already over-supplied and should be *condensed* from the library, not expanded.

Assemble the full draft with `python scripts/build_thesis.py` → `THESIS_DRAFT.md` (chapters + generated tables + verification plan); convert with pandoc for a Word file.
