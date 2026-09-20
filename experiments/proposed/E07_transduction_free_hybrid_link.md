# E7 — Transduction-free hybrid: photons transport, rare-earth memories store

**Gap.** Transduction reviews frame microwave-to-optical conversion as the bottleneck for connecting processors. A link that never puts a qubit in the microwave domain (SPDC or quantum-dot photons for transport, Eu:YSO absorptive memories for storage, optical processing at the ends) sidesteps it. Absorptive-memory entanglement was shown in 2021; nobody has combined it with hour-scale ZEFOZ storage in a link-level demonstration.

**Cheapest version.** Simulation in `qll/network/memory_decoherence.py` and `repeater_chain.py` with published storage efficiencies and lifetimes; compare end-to-end rate and fidelity against a transduction-based architecture with today's $\eta_t$, $n_{\rm add}$.

**Cheapest version implemented (0.15.0).** `simulations/s07_transduction_free_vs_through.py` with `qll/hardware/transduction.py`: through a 2020-class transducer (η_t ≈ 10⁻³, n_add ≈ 1) the teleportation fidelity after the link is 0.50, and even an optimistic η_t = n_add = 0.1 device gives 0.65, both below the classical 2/3; a target device (η_t = 0.5, n_add = 0.01) preserves F = 0.95 and would out-rate a bare NV emitter. The transduction-free line is flat at F = 0.967 because the emitter already speaks optics; its cost is rate through the zero-phonon fraction, which cavities recover. Verdict for the trade study: design around transduction today, revisit when n_add ≪ η_t is demonstrated.

**Verifies.** Trade study "memory vs T"; risk R-2 (a 2–4 K rare-earth memory needs a flown cooler class, not a dilution refrigerator).

**Key references.** Liu, X., et al. (2021). Heralded entanglement distribution between two absorptive quantum memories. *Nature*, 594, 41. Lauk et al. (2020); Mirhosseini et al. (2020).
