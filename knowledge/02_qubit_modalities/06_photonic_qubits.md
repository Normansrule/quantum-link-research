# Photonic qubits

## The two levels
A single photon in one of two modes: polarization ($\lvert H\rangle,\lvert V\rangle$), path (dual-rail), time-bin (early/late), or frequency. There is no decoherence in flight and no thermal noise at optical frequencies ($\bar n\approx4\times10^{-14}$ at 300 K for 1550 nm), which is why photons are the only flying qubit. The cost is that photons do not interact: two-qubit gates are probabilistic (linear optics plus measurement) or need a nonlinearity (an atom, an NV, or squeezing).

Continuous-variable (CV) encodings use squeezed states of a mode; GKP (Gottesman–Kitaev–Preskill) states encode a qubit in an oscillator's grid states.

## Equations
Beam splitter: $a_1\to\frac{a_1+a_2}{\sqrt2}$, $a_2\to\frac{a_1-a_2}{\sqrt2}$. Hong–Ou–Mandel: two identical photons never exit separate ports, coincidence $\propto1-V$ with visibility $V=\lvert\langle\phi_1\vert\phi_2\rangle\rvert^2$.
Linear-optics Bell measurement succeeds with probability $\le1/2$ without ancillas [Calsamiglia & Lütkenhaus 2001]; KLM showed near-deterministic gates are possible with ancilla photons and feed-forward, at large overhead; fusion-based and measurement-based schemes reduce it.
SPDC pair generation: probability $p$ per pulse with multipair probability $\sim p^2$; heralded $g^{(2)}(0)\approx2p$ sets the purity–brightness trade.

## Visual
```mermaid
flowchart LR
  S[source: SPDC / quantum dot / squeezer] --> LO[linear optics: BS, PBS, phase shifters, delay lines]
  LO --> D[detectors: SPAD / SNSPD / homodyne]
  D -->|feed-forward| LO
```

## How it is built
Bulk optics on a bench (the $5k Bell test in `docs/hardware_and_experiments_guide.md`), or integrated photonics: silicon nitride or lithium niobate waveguides, on-chip sources and interferometers, superconducting-nanowire single-photon detectors (SNSPD, 1–4 K, > 95% efficiency). Companies: PsiQuantum (fusion-based, silicon photonics), Xanadu (CV, Borealis Gaussian boson sampling 2022), Quandela (quantum-dot sources), ORCA (memories).

## Best published results (verify)
- Gaussian boson sampling with 216 squeezed modes claiming quantum advantage (Madsen et al. 2022); Jiuzhang photonic advantage (Zhong et al. 2020).
- Quantum-dot single-photon sources with > 95% indistinguishability; 12-photon entanglement.
- All satellite QKD and all long-distance teleportation experiments are photonic (see `03_quantum_communication/`).

## What has failed or is hard
- Loss is the error: every component removes photons and loss is not correctable without redundancy; deterministic sources and near-unity detectors are prerequisites.
- Probabilistic gates make circuits enormous without multiplexing; boson-sampling "advantage" claims are pursued by classical spoofing algorithms.

## What it means for a link
Photons *are* the link. Every channel model in `qll/channels/` is a photon model; the Phase 3 `hardware/photon_source.py`, `detector.py`, `beam_splitter.py` and the Perceval adapter live here.

## Key papers
- Hong, C. K., Ou, Z. Y., & Mandel, L. (1987). *Physical Review Letters*, 59, 2044. https://doi.org/10.1103/PhysRevLett.59.2044
- Kwiat, P. G., et al. (1995). New high-intensity source of polarization-entangled photon pairs. *Physical Review Letters*, 75, 4337. https://doi.org/10.1103/PhysRevLett.75.4337
- Knill, E., Laflamme, R., & Milburn, G. J. (2001). A scheme for efficient quantum computation with linear optics. *Nature*, 409, 46. https://doi.org/10.1038/35051009
- Gottesman, D., Kitaev, A., & Preskill, J. (2001). Encoding a qubit in an oscillator. *Physical Review A*, 64, 012310. https://doi.org/10.1103/PhysRevA.64.012310
- Kok, P., et al. (2007). Linear optical quantum computing with photonic qubits. *Rev. Mod. Phys.*, 79, 135. https://doi.org/10.1103/RevModPhys.79.135
- Hadfield, R. H. (2009). Single-photon detectors for optical quantum information applications. *Nature Photonics*, 3, 696. https://doi.org/10.1038/nphoton.2009.230
- Zhong, H.-S., et al. (2020). Quantum computational advantage using photons. *Science*, 370, 1460. https://doi.org/10.1126/science.abe8770
- Madsen, L. S., et al. (2022). Quantum computational advantage with a programmable photonic processor. *Nature*, 606, 75. https://doi.org/10.1038/s41586-022-04725-x
- Bartolucci, S., et al. (2023). Fusion-based quantum computation. *Nat. Commun.*, 14, 912.

## Exercises
1. Show that a 50:50 beam splitter maps $\lvert1,1\rangle$ to $(\lvert2,0\rangle-\lvert0,2\rangle)/\sqrt2$.
2. For $p=0.01$ per pulse and 80 MHz repetition, compute heralded single-photon rate and $g^{(2)}(0)$.
