# Glossary

Plain-language first, precise second. Acronyms written out on first use.

- **Amplitude damping** — energy loss from a qubit toward its ground state; time constant $T_1$.
- **Bell state / Bell pair** — one of four maximally entangled two-qubit states; the raw material of teleportation and repeaters.
- **Bell-state measurement (BSM)** — a joint measurement that asks "which Bell state are these two qubits in?"; deterministic with matter qubits, at most 50% successful with linear optics.
- **Bloch sphere** — the picture of a qubit as an arrow in a unit ball; surface = pure, interior = mixed.
- **BB84, E91, MDI, TF** — QKD protocol families: prepare-and-measure, entanglement-based, measurement-device-independent, twin-field.
- **CHSH** — the Clauser–Horne–Shimony–Holt inequality: $S\le2$ classically, $2\sqrt2$ quantum.
- **Coherence time** — $T_2$: how long a superposition keeps its phase; $T_2^*$ includes slow drifts, $T_2$ (echo) removes them.
- **Cooper pair** — two electrons bound in a superconductor; behaves as a boson; tunnels through a Josephson junction.
- **CPTP map / Kraus operators** — the general form of any physical noise process.
- **Decoy state** — random intensity variation that makes weak-laser QKD secure against photon-number-splitting attacks.
- **Dilution refrigerator** — the machine that reaches 10 mK for superconducting qubits.
- **Entanglement swapping** — a BSM on two halves of two pairs entangles the two remaining halves; the repeater step.
- **Fidelity** — how close a state is to the target; 1 is perfect, $2/3$ is the classical teleportation ceiling.
- **Herald** — a detector click that announces "an entangled pair now exists"; travels classically at $\le c$.
- **Hong–Ou–Mandel (HOM)** — identical photons on a beam splitter leave together; the basis of photonic BSMs.
- **Josephson junction** — a thin insulating barrier between superconductors; a nonlinear inductor; the heart of the transmon.
- **Light time** — $d/c$; 3–22 minutes one way to Mars; the only latency source in this repo.
- **NV center** — nitrogen-vacancy defect in diamond; a spin-1 qubit that works at room temperature and talks to photons at 637 nm.
- **No-cloning** — an unknown quantum state cannot be copied.
- **No-signaling** — entanglement carries no message by itself.
- **PLOB bound** — the maximum secret-key rate of any repeaterless link, $-\log_2(1-\eta)$.
- **QBER** — quantum bit error rate; BB84 dies at 11%.
- **QKD** — quantum key distribution; growing a shared secret key whose security rests on physics.
- **Quantum memory** — a device that stores a photonic qubit and releases it later; lifetimes from ms (ensembles) to hours (rare-earth nuclear spins).
- **Quantum repeater** — a chain of memory nodes that beats direct transmission by swapping and purifying.
- **Rabi / Ramsey / Hahn echo** — the three basic pulse experiments that calibrate a qubit.
- **Rydberg blockade** — one excited atom prevents its neighbor from being excited; the neutral-atom two-qubit gate.
- **SPDC** — spontaneous parametric down-conversion; a pump photon splits into an entangled pair in a crystal.
- **SQUID** — superconducting quantum interference device; two junctions in a loop; flux-tunable inductance.
- **Surface code** — the leading error-correcting code: 2-D grid, nearest-neighbor checks, ~1% threshold.
- **Teleportation** — moving an unknown qubit using one Bell pair and two classical bits.
- **Transduction** — converting a microwave qubit's information to an optical photon; the missing link for superconducting networks.
- **Transmon** — a Josephson junction shunted by a large capacitor; insensitive to charge noise; the most common superconducting qubit.
- **TRL** — Technology Readiness Level, NASA's 1–9 scale; the interplanetary link is at 1–2.
- **Werner state** — a Bell pair mixed with white noise; the standard model of an imperfect link.
- **Zero-phonon line (ZPL)** — the fraction of an emitter's photons that carry no phonon and are therefore usable for interference; ~3% for NV, which is why NV heralds are slow.
