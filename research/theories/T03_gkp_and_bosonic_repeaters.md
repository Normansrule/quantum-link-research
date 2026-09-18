# T03 — GKP and bosonic-code repeaters

**The idea.** Encode a qubit in the phase space of a light mode (GKP grid states or cat states) so that photon loss becomes a small, correctable displacement rather than a lost qubit. Repeaters then correct loss at each station with homodyne measurements and displacements, and can be combined with discrete codes for the residual errors.

**Equations.** GKP code space: eigenstates of $e^{2i\sqrt\pi\hat x}$ and $e^{2i\sqrt\pi\hat p}$; a loss channel of transmissivity $\eta$ followed by amplification is a Gaussian displacement with variance $\sigma^2=(1-\eta)/\eta$; correctable when $\sigma\lesssim0.3$–0.6 (squeezing of ~10–15 dB required).

**Status.** GKP states prepared in trapped-ion motion (2019) and microwave cavities (2020, error correction beyond break-even 2023); optical GKP states remain the bottleneck; repeater schemes analyzed (Rozpędek et al. 2021; Fukui et al. 2021).

**What it would change.** Loss on the AU-scale channel is 90–110 dB, far beyond what displacement correction handles per hop, so GKP helps only inside relay segments, not across the full span; but it could make relay-node memories unnecessary for short hops.

**Key papers.** Gottesman, Kitaev, & Preskill (2001). *PRA*, 64, 012310. https://doi.org/10.1103/PhysRevA.64.012310 Flühmann, C., et al. (2019). Encoding a qubit in a trapped-ion mechanical oscillator. *Nature*, 566, 513. Campagne-Ibarcq, P., et al. (2020). Quantum error correction of a qubit encoded in grid states of an oscillator. *Nature*, 584, 368. Rozpędek, F., et al. (2021). Quantum repeaters based on concatenated bosonic and discrete-variable quantum codes. *npj Quantum Inf.*, 7, 102. Sivak, V. V., et al. (2023). *Nature*, 616, 50.

**Repo hook.** `learn/01_quantum_computing_core/03` for the codes; a Phase 4 note in `repeater_chain.py` on where displacement correction applies.
