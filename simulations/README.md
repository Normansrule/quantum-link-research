# Simulations

Run these before building anything. Each simulation is the **S1 stage** of a flagship experiment: it predicts the number the bench must later reproduce, using only the pinned simulators and the tested `qll` functions. Every script prints a short report and writes a figure to `docs/figures/sim_*.svg`; every script has a test.

| # | Simulation | Predicts | Flagship stage | Simulator |
|---|---|---|---|---|
| [S01](s01_chsh_with_noise.py) | CHSH value of a Bell pair as depolarizing noise grows | the $S$ a noisy source will give; where it drops below 2 | F1 · S1 | Qiskit Aer |
| [S02](s02_teleportation_with_light_time.py) | Teleportation fidelity when the two classical bits are delayed by a light time and the memory decays | the $F(t)$ curve E1 measures; the $2/3$ crossing | F3 · S1 | Qiskit Aer + `light_time_delay` |
| [S03](s03_link_budget_sweep.py) | Photons per second reaching a receiver vs distance for fiber, LEO, and Mars | the loss F2 must reproduce; the pair rate F3 starts from | numpy (`qll.channels`) |
| [S04](s04_repetition_code_stim.py) | Logical error of a repetition code vs distance and physical error (majority-vote decoder) | whether errors are below threshold, the concept behind Λ | Stim |
| [S05](s05_bb84_key_over_a_pass.py) | Secret bits from one satellite pass vs background count rate and sun angle | the key-per-pass F2 measures | numpy (`qll.qkd`) |

```bash
conda activate qll
python simulations/s01_chsh_with_noise.py          # each prints a report and writes a figure
python -m pytest tests/test_simulations.py -q
```

Adding a simulation: copy the header of any script (docstring with the physics, the flagship stage, and the reference), keep it to one idea, print numbers, save a figure, add a test that asserts one analytic limit.
