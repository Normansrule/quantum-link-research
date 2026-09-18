# T08 — Entanglement routing, multiplexing, and quality of service

**The idea.** In a network of many nodes and links, which path, how many parallel attempts, and which swap order maximize end-to-end entanglement rate at a target fidelity? Classical routing assumes packets that can be stored and retransmitted; entanglement decays while stored and is destroyed by measurement, so routing becomes a scheduling problem coupled to memory decoherence.

**Equations.** For a path of $k$ links each with success probability $p_i$ per time slot and swap success $q$, greedy protocols give end-to-end rate $\sim q^{k-1}\min_ip_i$ per slot with multiplexing gains from parallel links; fidelity after $k-1$ swaps of Werner pairs with parameter $w$ is $w^k$ (for the singlet weight), so QoS constraints cap $k$.

**Status.** Simulation studies (Pant et al. 2019; Chakraborty et al. 2019); discrete-event simulators (SeQUeNCe, NetSquid); no deployed multi-path quantum network.

**What it would change.** A relay constellation (E3) needs exactly this: path selection through orbital relays with time-varying availability and 6–45 minute classical control loops; existing algorithms assume ms-scale control and must be re-derived.

**Key papers.** Pant, M., et al. (2019). Routing entanglement in the quantum internet. *npj Quantum Inf.*, 5, 25. Chakraborty, K., Rozpędek, F., Dahlberg, A., & Wehner, S. (2019). Distributed routing in a quantum internet. arXiv:1907.11630 Coopmans, T., et al. (2021). NetSquid. *Commun. Phys.*, 4, 164. Wu, X., et al. (2021). SeQUeNCe. *Quantum Sci. Technol.*, 6, 045027. Azuma, K., et al. (2023). *Rev. Mod. Phys.*, 95, 045006.

**Repo hook.** `qll/network/routing.py`, `relay_constellation.py`, `sequence_adapter.py` (Phase 4–5).
