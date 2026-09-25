# Lessons 03 — Timelines That Slipped

A systems engineer estimating a quantum link should know how the field's own estimates have fared.

| Year | Claim | What happened | Lesson |
|---|---|---|---|
| 1994–1996 | After Shor's algorithm, "a useful quantum computer within a decade or two" was a common expectation | thirty years later, no cryptographically relevant factoring; the largest RSA-style factorizations by quantum hardware remain toy-sized | algorithmic possibility says nothing about engineering time |
| 2001 | Liquid-state NMR factored 15; scaling to dozens of qubits seemed a matter of chemistry | NMR abandoned for scalable computing by 2005 (signal falls exponentially with qubit count) | a platform that demonstrates first is not the platform that scales |
| 2004–2010 | Commercial QKD systems sold as "unconditionally secure" | detector-blinding and other side-channel attacks broke deployed systems (2010) | proofs cover models; hardware is not the model (learn 03/14) |
| 2012 | Majorana signatures in nanowires; topological qubits "within years" | key results retracted (2021); the 2025 topological claim contested | a signature is not a qubit |
| 2015–2019 | Quantum supremacy declared (2019) with a claimed 10 000-year classical runtime | classical simulation reduced the gap to days, then hours, within two years | benchmarks must be defined against the best classical algorithm, which improves |
| 2017 | Satellite QKD (Micius) → "a global quantum internet by the mid-2020s" | one microsatellite QKD demonstration with a portable station (2025); no operational service | one mission is an existence proof, not a network |
| 2019–2021 | Quantum advantage in optimization and machine learning | most claimed advantages dequantized or matched classically | the burden of proof is on the quantum claim |
| 2023–2025 | Below-threshold error correction; fault tolerance "on track" | true and important, at Λ ≈ 2 with ~100 physical qubits per logical one; a useful machine needs ~10⁶ | the exponent is right, the constant is enormous |

## How this repository responds
Every requirement carries the method that verifies it; technology readiness levels are assigned conservatively (F3 at TRL 1–2); the frontier watchlist records claims with a "verify by" date; and the thesis reports three numbers rather than one so that throughput cannot hide latency. Estimates for the Mars link are given as ranges with the assumption that produces each end.

## Sources
- Lessons distilled from `research/cutting_edge/01_state_of_the_art_timeline.md` and `experiments/lessons/01_contested_claims.md`; historical claims paraphrased, not quoted.
- Preskill, J. (2018). Quantum computing in the NISQ era and beyond. *Quantum*, 2, 79. https://doi.org/10.22331/q-2018-08-06-79
- Rønnow, T. F., et al. (2014). Defining and detecting quantum speedup. *Science*, 345, 420. https://doi.org/10.1126/science.1252319
