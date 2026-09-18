# T02 — All-photonic quantum repeaters

**The idea.** Replace matter memories with photonic cluster states: each repeater node prepares a large entangled "repeater graph state" of photons; loss is tolerated because the state is redundantly encoded and measurements adaptively route around lost photons. No memory time, no cryogenics, but many photons per pair and deterministic sources.

**Equations.** Rate scales polynomially with distance like a memory-based repeater, with the memory time replaced by a photon-number overhead $\sim\mathrm{poly}(\log L)$ per node; requires source and detector efficiencies above ~90% and fusion gates with feed-forward.

**Status.** Proposed by Azuma, Tamaki, and Lo (2015); proof-of-principle time-reversed demonstrations (Li et al. 2019); fusion-based computing (PsiQuantum) is the same toolbox.

**What it would change.** A Mars relay could be a photonic terminal at room temperature (detectors at 1–4 K), which removes risk R-2 (cryogenics) but multiplies the photon budget where photons are scarcest; the 20-minute herald delay disappears because there is nothing to hold. This is the strongest alternative to the memory-based CONOPS and belongs in the trade study E8.

**Key papers.** Azuma, K., Tamaki, K., & Lo, H.-K. (2015). All-photonic quantum repeaters. *Nat. Commun.*, 6, 6787. https://doi.org/10.1038/ncomms7787 Li, Z.-D., et al. (2019). Experimental quantum repeater without quantum memory. *Nature Photonics*, 13, 644. Bartolucci, S., et al. (2023). Fusion-based quantum computation. *Nat. Commun.*, 14, 912. Hilaire, P., et al. (2021). Resource requirements for efficient quantum communication using all-photonic graph states generated from a few matter qubits. *Quantum*, 5, 397.

**Repo hook.** A Phase 4 stretch: `repeater_chain.py` with a photonic-node variant parameterized by source efficiency instead of memory time.
