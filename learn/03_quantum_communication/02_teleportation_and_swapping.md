# Teleportation, entanglement swapping, and the no-signaling theorem

## Definitions
- **Teleportation**: transfer of an unknown qubit using one shared Bell pair, a Bell-state measurement (BSM), and two classical bits [Bennett et al. 1993]. Nothing physical moves faster than light; the classical bits are essential and travel at $\le c$.
- **No-signaling**: Bob's reduced density matrix is independent of anything Alice does until her bits arrive; a corollary of linearity and the partial trace.
- **Entanglement swapping**: a BSM on one half of each of two Bell pairs entangles the two remaining halves, which never interacted [Żukowski et al. 1993]; this is the repeater primitive.
- **Classical limit**: measure-and-prepare achieves average fidelity $2/3$; beating it proves the quantum channel worked [Massar & Popescu 1995].
- **Unconditional / deterministic** teleportation: every input is teleported (matter-qubit BSM) versus post-selected photonic schemes with $\le50\%$ BSM success.

## Equations
$$\lvert\psi\rangle_1\lvert\Phi^+\rangle_{23}=\tfrac12\sum_{ij}\lvert\beta_{ij}\rangle_{12}\,X^jZ^i\lvert\psi\rangle_3,\qquad F_{\rm avg}=\frac{2f+1}{3}$$
Swapped-pair fidelity from two Werner pairs of fidelity $F$: $F'=F^2+\frac{(1-F)^2}{3}$ for the singlet fraction (the Briegel et al. recurrence). Every herald and correction is a `ClassicalMessage` bounded by $d/c$.

## Visual
The Earth–Mars sequence diagram in the README §6 is this protocol with the light-time made explicit.

## Landmark experiments
Bouwmeester 1997 (photons) → Furusawa 1998 (CV, unconditional) → Riebe/Barrett 2004 (ions) → Pfaff 2014 (NV, unconditional solid state) → Ren 2017 (ground-to-satellite) → Hermans 2022 (non-neighbouring nodes via swapping and memory). Details and step-by-step accounts: `experiments/bench/hardware_guide.md` §3.

## Key papers
- Bennett, C. H., et al. (1993). *Physical Review Letters*, 70, 1895. https://doi.org/10.1103/PhysRevLett.70.1895
- Żukowski, M., Zeilinger, A., Horne, M. A., & Ekert, A. K. (1993). "Event-ready-detectors" Bell experiment via entanglement swapping. *Physical Review Letters*, 71, 4287. https://doi.org/10.1103/PhysRevLett.71.4287
- Massar, S., & Popescu, S. (1995). *Physical Review Letters*, 74, 1259. https://doi.org/10.1103/PhysRevLett.74.1259
- Bouwmeester, D., et al. (1997). Experimental quantum teleportation. *Nature*, 390, 575. https://doi.org/10.1038/37539
- Furusawa, A., et al. (1998). Unconditional quantum teleportation. *Science*, 282, 706. https://doi.org/10.1126/science.282.5389.706
- Riebe, M., et al. (2004). Deterministic quantum teleportation with atoms. *Nature*, 429, 734. Barrett, M. D., et al. (2004). Deterministic quantum teleportation of atomic qubits. *Nature*, 429, 737.
- Pirandola, S., et al. (2015). Advances in quantum teleportation. *Nature Photonics*, 9, 641. https://doi.org/10.1038/nphoton.2015.154
- Peres, A., & Terno, D. R. (2004). Quantum information and relativity theory. *Rev. Mod. Phys.*, 76, 93. https://doi.org/10.1103/RevModPhys.76.93

## In this repo
Phase 2: `qll/circuits/teleportation.py`, `bell_measurement.py`, `entanglement_swapping.py`; invariants INV-1 and INV-3.

## Exercises
1. Verify the four-term identity above by expanding $\lvert\psi\rangle=\alpha\lvert0\rangle+\beta\lvert1\rangle$.
2. Alice teleports to Mars at opposition (0.37 au). At what time after her BSM can Bob first use the qubit, and what must his memory's $T_2$ exceed for $F>2/3$ if the initial singlet fraction is 0.95?
