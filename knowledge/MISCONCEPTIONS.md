# Common misconceptions, corrected

| Misconception | Correction | Where the repo enforces it |
|---|---|---|
| "Entanglement lets you send messages instantly." | Bob's statistics are unchanged by anything Alice does until a classical message arrives; teleportation costs 2 bits at $\le c$. | `light_time_delay.ClassicalMessage`, INV-1, INV-3 |
| "Teleportation moves matter." | It moves the *state*; the original is destroyed by the Bell measurement (no-cloning). | INV-2 |
| "Qubits are 0 and 1 at the same time." | A qubit is a unit vector in $\mathbb C^2$; measurement in a basis gives one outcome with Born-rule probability; "both at once" is a metaphor for superposition amplitudes. | `00_foundations/03` |
| "Quantum computers try all answers in parallel." | Interference must concentrate amplitude on the right answer; that works for structured problems (factoring), gives only $\sqrt N$ for unstructured search, and nothing for most NP-hard problems. | `01_quantum_computing_core/05` |
| "QKD is unbreakable." | The *protocol* is information-theoretically secure; the *devices* have been hacked (detector blinding). MDI and DI protocols close device gaps; authentication still needs a pre-shared key. | `03_quantum_communication/01`, `05_experiments/lessons/01` |
| "A quantum repeater amplifies the signal." | Amplification would clone; repeaters swap entanglement and purify. | `03_quantum_communication/03` |
| "Colder is always better." | Below $\hbar\omega/k_B$ the occupation is already negligible; stray radiation and TLS defects dominate. For optical carriers room temperature is already 'zero'. | `noise/thermal.py` |
| "A six-hour memory means a six-hour repeater." | Coherence time ≠ storage efficiency; rare-earth memories retrieve well below 1% at hours. Report both numbers. | `memory_decoherence.py` |
| "Supremacy/advantage was proven in 2019." | It is a moving target against classical algorithms; the durable claim is scaling of fidelity with size. | `05_experiments/lessons/01` |
| "Majorana qubits exist." | Signatures are contested; a 2018 claim was retracted; no logical topological qubit has been demonstrated. | `02_qubit_modalities/07` |
| "Satellites beat fiber because space is empty." | They win because diffraction loss is $1/L^2$ versus exponential in glass; the atmosphere still costs 3–10 dB and daylight adds background. | `03_quantum_communication/04` |
| "The measurement problem is solved by decoherence." | Decoherence explains the disappearance of interference, not the selection of an outcome; interpretations differ on the rest and agree on all predictions here. | `00_foundations/13` |
