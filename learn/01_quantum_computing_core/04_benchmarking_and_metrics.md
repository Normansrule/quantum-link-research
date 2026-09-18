# Benchmarking and metrics

## Definitions
- **Gate fidelity** via **randomized benchmarking (RB)**: run random Clifford sequences of length $m$, fit survival $Ap^m+B$, error per Clifford $r=(1-p)(1-1/d)$. Insensitive to state-preparation-and-measurement (SPAM) error.
- **Cross-entropy benchmarking (XEB)**: fidelity of random circuits from sampled bitstring probabilities; the metric behind the 2019 "supremacy" claim.
- **Quantum volume** $V_Q=2^n$: largest square random circuit (width = depth = $n$) passed with heavy-output probability $>2/3$.
- **Logical error per cycle**, $\Lambda$: the error-correction metrics (previous file).
- **Gate speed vs coherence**: the useful number is $T_2/t_{\rm gate}$, the number of operations before decoherence.
- **Two-qubit gate fidelity ≥ 99.9%** is roughly where the surface code becomes practical; state of the art by platform is tabulated in `02_qubit_modalities/README.md`.

## Equations
$$F_{\rm seq}(m)=Ap^m+B,\qquad r_{\rm Clifford}=\frac{(1-p)(d-1)}{d},\qquad F_{\rm XEB}=2^n\langle P_{\rm ideal}(x)\rangle_{x\sim\text{device}}-1$$

## Key papers
- Magesan, E., Gambetta, J. M., & Emerson, J. (2011). Scalable and robust randomized benchmarking of quantum processes. *Physical Review Letters*, 106, 180504. https://doi.org/10.1103/PhysRevLett.106.180504
- Cross, A. W., et al. (2019). Validating quantum computers using randomized model circuits. *Physical Review A*, 100, 032328. https://doi.org/10.1103/PhysRevA.100.032328
- Arute, F., et al. (2019). Quantum supremacy using a programmable superconducting processor. *Nature*, 574, 505. https://doi.org/10.1038/s41586-019-1666-5
- Proctor, T., et al. (2022). Measuring the capabilities of quantum computers. *Nature Physics*, 18, 75.

## In this repo
`qll/circuits/tomography.py` and `process_tomography.py` (Phase 2) are the small-system versions of these ideas; the traceability matrix is the systems-engineering analogue: a claim is verified only when its test exists and passes.

## Exercises
1. Simulate RB on a depolarizing channel with $p=0.995$ in Aer and recover $r$.
2. Why can XEB be spoofed by classical sampling at modest depth, and what does that say about "supremacy" claims? (See `../../experiments/lessons/01_contested_claims.md`.)
