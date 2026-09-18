# Contested, retracted, and over-claimed results: what to learn

| Claim | What happened | Lesson for this project |
|---|---|---|
| **D-Wave quantum speedup (2013–2014)** | Claims of speedup on 512-qubit annealers were tested by Rønnow et al. (2014), who found no scaling advantage over classical optimizers; later work found narrow advantages on specific problems. | Define the classical baseline before claiming advantage; report scaling, not single runtimes. |
| **Quantized Majorana conductance (2018)** | *Nature* paper retracted 2021 after independent reanalysis showed data selection; earlier "signatures" explained by trivial Andreev states. | Share raw data; a theory-predicted signature is not the theory's confirmation; the field's corrective mechanism worked but took three years. |
| **Quantum supremacy, 2019** | 53-qubit random-circuit sampling estimated at 10,000 years classically; tensor-network methods brought this to days (2021) and then hours; the 2023 follow-up at 70 qubits restored a gap. | "Supremacy" is a moving target against classical algorithms; the durable claim is the *scaling* of fidelity with size. |
| **Boson-sampling advantage (2020–2022)** | Classical spoofing algorithms matched or approached benchmark scores on Jiuzhang and Borealis. | Same lesson; and choose verification metrics that cannot be spoofed. |
| **Room-temperature superconductivity (2020, 2023)** | *Nature* papers retracted after data irregularities; not a quantum-computing result but the same community. | Extraordinary materials claims need independent samples. |
| **Early QKD "unconditional security" marketing (2000s)** | Detector-blinding and Trojan-horse attacks broke commercial systems (Lydersen et al. 2010) that were secure in theory. | Security proofs cover models, not devices; hence MDI and DI protocols. |
| **NISQ advantage for optimization and chemistry (2019–2024)** | Many VQE/QAOA advantage claims did not survive better classical methods; error rates limited useful circuit depth. | Report where classical methods stand today, not in the original paper. |
| **Memory time headlines** | "Six-hour coherence" (2015) is real but at storage efficiencies far below what a repeater needs; headlines dropped the efficiency. | Always report the pair (time, efficiency at that time); `memory_decoherence.py` requires both. |

**Rules this repository derives from the table.** Every number carries a source and a year; every claim in code has an analytic test; capacity bounds are asserted, not assumed (INV-5); and the risk register keeps R-6 "over-claiming feasibility" as a live risk.

- Rønnow, T. F., et al. (2014). Defining and detecting quantum speedup. *Science*, 345, 420. https://doi.org/10.1126/science.1252319
- Frolov, S. (2021). Quantum computing's reproducibility crisis: Majorana fermions. *Nature*, 592, 350.
- Pan, F., Chen, K., & Zhang, P. (2022). Solving the sampling problem of the Sycamore quantum circuits. *Physical Review Letters*, 129, 090502.
- Lydersen, L., et al. (2010). Hacking commercial quantum cryptography systems by tailored bright illumination. *Nature Photonics*, 4, 686. https://doi.org/10.1038/nphoton.2010.214
