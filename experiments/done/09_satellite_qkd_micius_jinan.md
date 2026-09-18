# Satellite quantum communication (Micius 2017–2020; Jinan-1 2025)

**Original.** Micius (2016 launch, 600 kg) distributed entangled pairs to two ground stations 1200 km apart, received a teleported qubit from the ground, and ran decoy-state QKD to Earth at kbit/s. Jinan-1 (2022 launch, 23 kg payload) ran real-time QKD with 100 kg portable ground stations, up to ~1 Mbit of key per pass, and relayed a key 12,900 km between China and South Africa.

**Physics.** `learn/03_quantum_communication/04`: diffraction-limited link budget, pointing, background, decoy-state rate. Step-by-step: `experiments/bench/hardware_guide.md` §3.4.

**Simple recreation.** Rooftop-to-rooftop free-space link across campus with the SPDC source, 50 mm beam expanders, 3 nm filters, and a GPS-disciplined clock for timing (Tier 1); measure $\eta$ vs distance and daylight background, fit to `free_space_diffraction.py` and `thermal_background.py`. Software: reproduce the published loss budgets with `link_budget.py` (Phase 3 must-pass target) and use the Jinan-1 per-pass key data (Zenodo 10.5281/zenodo.14732295) in `relay_constellation.py`.

**What went wrong historically.** Early proposals (1990s–2000s) assumed link losses that turned out optimistic; Micius needed years of ground testing on Qinghai Lake (100 km) and hot-air-balloon tests to validate pointing and timing before launch.

**Repo hook.** Phase 3 `link_budget.py`, Phase 5 `qll/space/`.

- Yin, J., et al. (2017). *Science*, 356, 1140. Ren, J.-G., et al. (2017). *Nature*, 549, 70. Liao, S.-K., et al. (2017). *Nature*, 549, 43. Yin, J., et al. (2020). *Nature*, 582, 501. https://doi.org/10.1038/s41586-020-2401-y
- Li, Y., et al. (2025). *Nature*, 640, 47. https://doi.org/10.1038/s41586-025-08739-z
