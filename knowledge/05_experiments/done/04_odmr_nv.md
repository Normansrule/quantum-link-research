# Optically detected magnetic resonance of NV centers (Gruber et al. 1997)

**Original.** A single NV center was imaged confocally and its spin resonance detected as a dip in fluorescence when a 2.87 GHz microwave field was applied: the first single-spin ODMR in a solid, and the birth of the diamond qubit.

**Physics.** $H=DS_z^2+\gamma_e\vec B\cdot\vec S$; resonances at $D\pm\gamma_eB_\parallel$; contrast from the spin-dependent intersystem crossing.

**Simple recreation (Tier 0, one weekend, ~$100–$500).** Uncut Gem (open PCB, Arduino, ADF4351) or the Stegemann 3D-printed cubes: green laser or LED, fluorescent microdiamond, loop antenna, photodiode. Sweep 2.7–3.0 GHz, see the dip at 2.87 GHz, bring a magnet near and watch it split. Links and part numbers in `docs/hardware_and_experiments_guide.md` §2.2 and §5.

**What went wrong historically.** Ensembles were studied for decades (Loubser & van Wyk 1978) before single centers could be isolated; the confocal microscope and low-nitrogen diamond were the enabling tools.

**Repo hook.** `qll/hardware/nv_node.py` (Phase 3) uses $D$, $\gamma_e$, and the ODMR contrast; proposal E2 uses this bench for $T_1(T)$.

- Gruber, A., et al. (1997). *Science*, 276, 2012. https://doi.org/10.1126/science.276.5321.2012
- Stegemann, J., et al. (2023). *Eur. J. Phys.*, 44, 035402. https://doi.org/10.1088/1361-6404/acbe7c
- Carney, M., & Kumaran, V. (2025). Uncut Gem. arXiv:2509.18329; https://github.com/QuantumVillage/UncutGem
