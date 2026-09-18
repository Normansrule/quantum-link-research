# Start Here

1. **Read the six sentences** in [README.md](README.md). That is the whole project.
2. **Look at one picture**: `docs/figures/overview_storyboard.svg` (top of the README). Panel 5 is the thesis question.
3. **Pick your door**
   - Want to understand? [`learn/README.md`](learn/README.md), choose a learning path, tick boxes.
   - Want to build? [`experiments/protocols/P01_odmr_nv_bench.md`](experiments/protocols/P01_odmr_nv_bench.md), a $100–500 qubit readout in a weekend.
   - Want to work on the project? [`research/thesis/BACKLOG.md`](research/thesis/BACKLOG.md), pick a row.
4. **Run the code** (10 minutes for the environment): `conda env create -f environment.yml && conda activate qll && pytest -q`.
5. **Turn a knob**: https://Normansrule.github.io/quantum-link-research/apps/ or `python -m qll.viz.light_time_explorer`.

Three rules you will see everywhere: nothing signals faster than light (`ClassicalMessage` refuses early reads), nothing is cloned, teleportation costs two classical bits. Three files you will come back to: [`learn/00_GLOSSARY.md`](learn/00_GLOSSARY.md), [`docs/physics_overview.md`](docs/physics_overview.md), [`docs/physics_module_design.md`](docs/physics_module_design.md).
