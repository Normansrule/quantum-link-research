# E8 — Modality trade study for a Mars memory node, with data

**Gap.** The survey in `02_qubit_modalities/` shows no platform meets all of: optical interface, > 45 min storage, high retrieval efficiency, flown-class cryogenics, radiation tolerance. A systems-engineering trade (weighted criteria, sensitivity analysis) with literature values and uncertainty has not been published for the interplanetary case.

**Cheapest version.** Pure literature and software: build the trade matrix (criteria: storage time, efficiency at that time, wavelength, operating temperature and cooler TRL, mass, radiation data, herald rate) for NV/SiV, Eu:YSO, Er:YSO, trapped ions, atomic ensembles; run `memory_decoherence.py` for each against the light-time baselines; report a ranked list with the sensitivity of the ranking to each weight.

**Verifies.** REQ-CAP-001 gets a platform recommendation; feeds `systems/trade_studies.md`.

**Expected result.** Rare-earth crystals win on storage time, ions on efficiency and maturity in space (Deep Space Atomic Clock heritage), color centers on interface simplicity; the honest answer is likely a heterogeneous node, which is itself a research direction.

**Key references.** Zhong, M., et al. (2015). *Nature*, 517, 177. Knaut, C. M., et al. (2024). *Nature*, 629, 573. Wang, P., et al. (2021). *Nat. Commun.*, 12, 233. Burt, E. A., et al. (2021). Demonstration of a trapped-ion atomic clock in space. *Nature*, 595, 43. Muralidharan, S., et al. (2016). *Sci. Rep.*, 6, 20463.
