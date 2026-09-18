# Changelog

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
