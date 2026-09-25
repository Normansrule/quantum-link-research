# Bhaskar 2020: memory-enhanced quantum communication

**Original.** A silicon-vacancy centre in a diamond nanophotonic cavity acted as a quantum memory that stored a photonic qubit and enabled a Bell-state measurement between two photons that arrived at different times. Because the memory removed the need for both photons to arrive within the same short window, the effective rate of a two-photon QKD-like protocol exceeded what the same link achieved without the memory — the first demonstration that a memory *helps* a real communication task [bhaskar2020]. Cooperativity above 100 in the cavity made the spin–photon interface efficient.

**Physics.** Two photons that must coincide arrive together with probability $\propto\eta^2$; with a memory the first waits for the second, and the success scales as $\eta\cdot\eta$ over a longer window, i.e. effectively $\propto\eta$ per unit time. This is the elementary step of a gen-1 repeater (`learn/03/03`) done with one node. The cavity's Purcell enhancement (`qll/hardware/nv_node.purcell_factor`) is what made the spin–photon gate work; the memory time (~ms electron, ~s nuclear) set the window.

**Simple recreation (Tier 3).** Nanophotonic diamond at 100 mK is a national-lab experiment. The classroom version is a simulation: `qll/network/repeater_chain.memory_chain` with one segment versus `direct_rate_hz` shows the $\eta$ vs $\eta^2$ crossover; the bench analogue is P03's HOM setup with a fibre delay line acting as a "memory" of fixed duration.

**What went wrong historically.** Earlier memory demonstrations stored and retrieved photons but never beat the memoryless link on a task; the SiV's strain sensitivity and 100 mK requirement limit how many nodes can be built.

**Repo hook.** REQ-NET-001 (chain beats direct) is the generalized version of this result; the SiV row of the memory table; S07's cavity node.

- Bhaskar, M. K., et al. (2020). Experimental demonstration of memory-enhanced quantum communication. *Nature*, 580, 60. https://doi.org/10.1038/s41586-020-2103-5
- Nguyen, C. T., et al. (2019). Quantum network nodes based on diamond qubits with an efficient nanophotonic interface. *Physical Review Letters*, 123, 183602. https://doi.org/10.1103/PhysRevLett.123.183602
- Knaut, C. M., et al. (2024). *Nature*, 629, 573. https://doi.org/10.1038/s41586-024-07252-z
