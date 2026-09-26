# Quantum Volume and Other Whole-Device Benchmarks

## Quantum volume
Run random "square" circuits (width $n$, depth $n$, layers of random two-qubit unitaries on random pairs) and record how often the device lands on the *heavy* outputs, those whose ideal probability exceeds the median. An ideal device scores $(1+\ln2)/2\approx0.85$ as $n$ grows; a fully depolarized one 0.5. A device passes width $n$ if its heavy-output probability exceeds 2/3 with confidence, and its quantum volume is $2^n$ for the largest passing $n$ [cross2019]. `qll/circuits/quantum_volume.py` runs the test in Qiskit Aer: at $n=4$ the ideal circuits score well above 2/3, and a 15 % depolarizing error on each CNOT pushes them below.

## What it measures and what it hides
Quantum volume folds gate error, connectivity, crosstalk, and compiler quality into one number, which is its virtue and its limit: it saturates for devices with many qubits but modest fidelity (a 1 000-qubit device and a 20-qubit device can have the same score), and it says nothing about a specific application. Complementary benchmarks are layer fidelity and error per layered gate (EPLG) for large devices [mckay2023], cross-entropy benchmarking (XEB) for random-circuit sampling, application-oriented suites, and the logical-level benchmarks that matter once error correction runs. For this thesis the relevant device numbers are different again: memory time at a given efficiency, herald rate, and teleportation fidelity (`learn/03`).

## Key papers
- Cross, A. W., Bishop, L. S., Sheldon, S., Nation, P. D., & Gambetta, J. M. (2019). Validating quantum computers using randomized model circuits. *Physical Review A*, 100, 032328. https://doi.org/10.1103/PhysRevA.100.032328
- McKay, D. C., et al. (2023). Benchmarking quantum processor performance at scale. arXiv:2311.05933
- Arute, F., et al. (2019). Quantum supremacy using a programmable superconducting processor. *Nature*, 574, 505. https://doi.org/10.1038/s41586-019-1666-5

## In this repo
`qll/circuits/quantum_volume.py` (slow test), `qll/circuits/benchmarking.py` (randomized benchmarking).
