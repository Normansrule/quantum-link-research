# T16 — Measurement-Only Teleportation With Majorana Zero Modes

**Claim.** Crogman, Dang, and Erenso (2025) propose teleportation between qubits stored in Majorana zero modes using only joint parity measurements and Clifford corrections, with no braiding [crogman2025]. The qubits are stored nonlocally in the fermion parity of separated modes, so errors from hybridization fall exponentially with the modes' separation, as $\Gamma \sim \Delta^2 e^{-2L/\xi}$ [cheng2012]. Teleportation then becomes a robust way to move logical states between nodes. The first two authors are in the Department of Physics at California State University, Dominguez Hills.

**Mechanism.** Three logical qubits A, B, C each live in a pair of Majorana operators $(\gamma_1,\gamma_2), (\gamma_3,\gamma_4), (\gamma_5,\gamma_6)$:
1. B and C are prepared in $|\Phi^+\rangle$ by a parity projection.
2. Alice measures parities that join A and B.
3. She sends the outcomes over a classical channel.
4. Bob applies a parity-preserving correction to C, which is a Pauli operator [crogman2025] [bonderson2008].

**Why it matters for this mission.** It is the node layer of a future network, and the mission builds the layer under it.
- **Where it sits:** the photonic link of Phases 1–3 (fiber, free space, orbit) carries entanglement between sites. A Majorana node would hold and move it locally with intrinsic protection.
- **The bridge:** the paper names the photon-to-parity interface as an open problem, and its Figure 4 shows an entangled photon pair linking two Majorana chips. That interface is exactly where this repository's link layer would meet a topological node.
- **The classical channel:** the protocol needs it, like every teleportation, which matches the no-signalling result of paper 1 (P11).
- **Where Phase 4 is headed:** teleportation as a primitive that moves states between protected memories.

**What we reproduced** ([`qll/circuits/majorana_teleport.py`](../../qll/circuits/majorana_teleport.py), [`tests/test_majorana_teleport.py`](../../tests/test_majorana_teleport.py)). The model uses six Majorana operators on three fermion modes (Jordan–Wigner), exact parity projections, and the paper's protocol step by step.

| Result | Status in the model |
|---|---|
| Teleportation with two commuting parity measurements, $P_{23} = i\gamma_2\gamma_3$ and $P_{14} = i\gamma_1\gamma_4$, and four Pauli corrections (each a Majorana bilinear) | exact: fidelity 1 for every input and outcome, each outcome with probability 1/4 |
| All corrections are Clifford operations and conserve total fermion parity (Theorem A4) | confirmed |
| The sender is left maximally mixed, so nothing is copied (Theorem A2) | confirmed, outcome by outcome |
| An ideal non-selective parity measurement leaves the entropy unchanged when the state commutes with the parity, and never lowers it otherwise (Theorems A5, A6, Remark A1) | confirmed |
| Without any classical bits, Bob's qubit is $I/2$ for every input | confirmed: no signalling |
| Under Jordan–Wigner, $P_{23} = -X_AX_B$ and $P_{14} = Y_AY_B$ | the protocol is standard teleportation in a fermionic encoding; topological protection comes from the hardware that stores the modes |
| Emulation on a qubit processor, after Huang et al. (2021) [huang2021] | [`qll/circuits/majorana_cloud.py`](../../qll/circuits/majorana_cloud.py), protocol [P13](../../experiments/protocols/P13_majorana_teleportation_on_a_cloud_processor.md) |

**Points to raise with the authors.** The model raises these questions. Each may be a convention, or simply something we have not understood, and is worth a conversation.

1. **One bit or two.** The four steps in the paper's Section 4 use one parity measurement ($P_{23}$, one bit) and the correction $X_C = i\gamma_4\gamma_5$ (Equations 9–12).
   - In the model, one parity bit leaves Bob holding only one Bloch component of $|\psi\rangle$, with a sign that the bit reveals. The best correction for that outcome then reaches an average fidelity of 2/3, the classical limit [massar1995]. The $X_C$ correction as written gives 1/2.
   - The paper's Theorem A4 uses two parity measurements and four outcomes, and the model confirms that version teleports exactly. That matches the two classical bits per qubit that teleportation requires [bennett1993], so the Section 4 description may need the second measurement.
2. **The no-feed-forward remark.** The note after Equation 14 says that without feed-forward the map on C is dephasing in the $X_C$ basis.
   - Conditioned on a *known* outcome, that matches the model.
   - Averaged over outcomes Bob does not know, his state is exactly $I/2$, as no-signalling requires. Stating which case is meant would prevent a misreading.
3. **Lemma A1.** A single Majorana operator *anticommutes* with its pair parity: $\gamma_1(i\gamma_1\gamma_2) = -(i\gamma_1\gamma_2)\gamma_1$. So Equation A14's "commutes" appears to be a sign slip.
   - The conclusion survives in a precise form. $\gamma_1$ has zero diagonal elements, so it cannot *read* the qubit, but it does *flip* it, which is exactly quasiparticle poisoning.
   - The protection comes from parity conservation: the only parity-preserving operator supported on one mode is the identity (tested).
4. **Conventions.**
   - Equation 2 normalizes $c = (\gamma_1 + i\gamma_2)/\sqrt{2}$, while the appendix uses $1/2$; with $\{\gamma_j,\gamma_k\} = 2\delta_{jk}$, only $1/2$ gives $\{c, c^\dagger\} = 1$.
   - With $c = (\gamma_1+i\gamma_2)/2$, $i\gamma_1\gamma_2 = 2n - 1$, the opposite sign of Section 3's $1 - 2n$.
   - The hybridization exponent is $2L/\xi$ in Equation 17 but $L/\xi$ in bound A12.
5. **Superselection.** A qubit made of one pair of modes cannot hold a superposition of fermion parities in an isolated system [bravyi2002]. Hardware proposals therefore use four modes per qubit at fixed total parity (tetrons and box qubits) [karzig2017] [plugge2017]. The algebra above is unchanged, but the physical layout doubles the modes.

**Error budget** ([`qll/hardware/majorana_error_budget.py`](../../qll/hardware/majorana_error_budget.py), from the paper's Equations 17–20, in dimensionless knobs). The readout factor enters twice because a full teleportation needs two parity measurements.

| Readout signal-to-noise at 0 K | $\Delta/k_BT$ | Poisoning probability per readout | $L/\xi$ | Teleportation fidelity bound |
|---|---|---|---|---|
| 3 | 10 | 0.01 | 3 | 0.985 |
| 5 | 10 | 0.01 | 6 | 0.990 |
| 10 | 10 | 0.001 | 6 | 0.999 |
| 5 | 10 | 0.1 | 6 | 0.902 |

Poisoning dominates once the modes are a few coherence lengths apart. Hybridization alone costs $10^{-3}$ at $L/\xi \approx 3.5$ and $10^{-6}$ at about 6.9.

**What would change the design.** A node that stores entanglement with intrinsic protection would ease the memory requirement that dominates the long-distance budget (`systems/trade_studies.md`). The price is three things: millikelvin cryogenics, a photon-to-parity interface that does not yet exist, and a Clifford-only gate set that needs outside resources for universality.

**Evidence and status.** The evidence so far comes in pieces:
- minimal Kitaev chains in coupled quantum dots [dvir2023];
- exponential protection signatures in Majorana islands [albrecht2016];
- an emulation of the protocol on a superconducting processor [huang2021].

A full Majorana teleportation has not been demonstrated (the paper says so), and the field's history calls for independent replication ([`learn/02_qubit_modalities/07_topological_majorana.md`](../../learn/02_qubit_modalities/07_topological_majorana.md), [`experiments/lessons/01_contested_claims.md`](../../experiments/lessons/01_contested_claims.md)). Readiness level 2–3.

**Cheap version.** Proposal [E18](../../experiments/proposed/E18_majorana_parity_teleportation_emulated.md) and protocol P13: emulate the one-bit and two-bit versions on a free cloud processor, and set the measured fidelities against the error budget. This is a concrete, low-cost collaboration to offer the paper's authors at CSUDH.

**References.** Crogman, H. T., Dang, T., & Erenso, D. (2025). Topologically protected quantum teleportation via Majorana zero modes: A perspective on scalability and decoherence immunity. *Quantum Reports, 7*(3), 42. https://doi.org/10.3390/quantum7030042 · Huang, H.-L., et al. (2021). Emulating quantum teleportation of a Majorana zero mode qubit. *Physical Review Letters, 126*, 090502. https://doi.org/10.1103/PhysRevLett.126.090502 · Karzig, T., et al. (2017). *Physical Review B, 95*, 235305. https://doi.org/10.1103/PhysRevB.95.235305 · Bravyi, S. B., & Kitaev, A. Y. (2002). Fermionic quantum computation. *Annals of Physics, 298*, 210–226. https://doi.org/10.1006/aphy.2002.6254 · Bonderson, P., Freedman, M., & Nayak, C. (2008). *Physical Review Letters, 101*, 010501. https://doi.org/10.1103/PhysRevLett.101.010501
