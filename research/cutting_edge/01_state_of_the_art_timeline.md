# State of the art: a timeline to judge new claims against

Dates are publication years; numbers are as reported and must be re-verified before use in the thesis.

| Year | Milestone | Platform | Why it mattered |
|---|---|---|---|
| 1982 | Aspect Bell test with time-varying analyzers | photons | first serious closure of the locality loophole |
| 1994–95 | Shor's algorithm; Shor and Steane codes | theory | quantum computing becomes a cryptographic threat and error correction becomes possible |
| 1995 | Cirac–Zoller gate; first CNOT (Monroe) | ions | first two-qubit gate |
| 1997 | Photonic teleportation (Bouwmeester) | photons | teleportation is physical |
| 1998 | Loss–DiVincenzo; Kane | theory | semiconductor qubit blueprints |
| 1999 | Cooper-pair-box coherence (Nakamura) | superconducting | a macroscopic circuit is a qubit |
| 2001 | NMR factoring of 15; KLM; DLCZ; Kitaev chain | several | algorithms, photonic computing, repeaters, topology |
| 2004 | Circuit QED (Wallraff) | superconducting | qubit strongly coupled to a resonator: the readout paradigm |
| 2007 | Transmon (Koch) | superconducting | charge-noise problem solved |
| 2012 | Surface-code engineering roadmap (Fowler); Majorana "signatures" (Mourik) | theory / topological | the scaling plan; and the start of a cautionary tale |
| 2013–15 | NV remote entanglement 3 m; loophole-free Bell test 1.3 km | diamond | solid-state network nodes; local realism refuted with loopholes closed |
| 2016 | 99.9% two-qubit gates | ions | fidelity ceiling raised above the surface-code threshold |
| 2017 | Micius: 1200 km entanglement, teleportation to orbit, satellite QKD | photons/space | the space segment is real |
| 2018 | Twin-field QKD; TF beats PLOB (later) | photons | rate–loss law broken without memories |
| 2019 | Random-circuit sampling "supremacy" (Sycamore, 53 qubits) | superconducting | contested, but a scale marker |
| 2020 | Memory-enhanced communication (SiV); entanglement-based satellite QKD without trust | SiV / space | a repeater node beats direct transmission |
| 2021 | Three-node NV network; fault-tolerant control of an ion logical qubit; Majorana quantized-conductance paper retracted | several | networks; FT operations; the reproducibility mechanism works |
| 2022 | Silicon spin gates > 99.5% (three groups); Borealis GBS; teleportation between non-neighbouring NV nodes | Si / photons / diamond | silicon crosses threshold; network teleportation |
| 2023 | Surface code d = 5 beats d = 3 (Google); GKP beyond break-even (Yale); 99.5% Rydberg gates; 1000-atom arrays | several | error correction starts to work |
| 2024 | 48 logical qubits on neutral atoms; NV entanglement over 25 km deployed fiber; SiV over 35 km Boston fiber; qLDPC "gross code"; **below-threshold surface code, Λ ≈ 2.14 (Willow)** | several | logical processors and metropolitan quantum networks |
| 2025 | Microsatellite real-time QKD with portable stations (Jinan-1); 13.1 h nuclear-spin coherence; Majorana parity measurement claim (contested) | space / memory / topological | cheap space QKD; memories exceed planetary light-times |
| 2026 | (to be filled as verified: Eagle-1 launch status, further below-threshold results, 400+ km memory–memory entanglement journal publication) | | |

## How to place a new paper
1. Which DiVincenzo criterion does it move, and by how much (numbers with error bars)?
2. Is the claim about a *physical* metric (T1, fidelity) or a *logical* one (Λ, logical error per cycle)? Logical results are the ones that scale.
3. Is it independently reproduced? (See `experiments/lessons/01_contested_claims.md`.)
4. For network papers: was the entanglement heralded, stored, and consumed, and over what deployed distance?
