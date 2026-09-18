# Remote entanglement and networking with NV centers (Bernien 2013 → Hermans 2022)

**Original.** Two NV centers 3 m apart were entangled by interfering their emitted photons (Barrett–Kok two-photon scheme), then 1.3 km apart for the loophole-free Bell test, then three nodes with entanglement swapping, then teleportation between non-neighbouring nodes with a memory qubit protected by dynamical decoupling during the wait for the herald.

**Physics.** Spin–photon entanglement from spin-selective resonant excitation; heralding by a two-photon coincidence pattern; success $p\sim10^{-4}$–$10^{-6}$ per attempt; memory in ¹³C nuclear spins. Step-by-step protocol in `experiments/bench/hardware_guide.md` §3.3.

**Simple recreation.** Not on a student budget (4 K cryostats, resonant lasers, single-NV diamonds). The software recreation is exactly Phase 2–4 of this repo: Stim/Aer for the circuits, `nv_node.py` for herald statistics, `memory_decoherence.py` for the nuclear memory, and `light_time_delay.py` for the classical heralds. A scaled analogue on the SPDC bench is proposal E1 (delay the classical channel, not the qubit).

**What went wrong historically.** Charge-state instability and spectral diffusion of the NV optical line limited rates for a decade; deterministic delivery (2018) needed active phase stabilization of the interferometer over the fiber link; metropolitan links (2024) needed frequency conversion to telecom and stabilization over 25 km.

**Repo hook.** REQ-CIR-001..003, REQ-NET-001, REQ-CAP-001.

- Bernien, H., et al. (2013). *Nature*, 497, 86. https://doi.org/10.1038/nature12016
- Barrett, S. D., & Kok, P. (2005). *Physical Review A*, 71, 060310. https://doi.org/10.1103/PhysRevA.71.060310
- Humphreys, P. C., et al. (2018). *Nature*, 558, 268. https://doi.org/10.1038/s41586-018-0200-5
- Pompili, M., et al. (2021). *Science*, 372, 259. Hermans, S. L. N., et al. (2022). *Nature*, 605, 663. https://doi.org/10.1038/s41586-022-04697-y
- Stolk, A. J., et al. (2024). *Sci. Adv.*, 10, eadp6442.
