# The postulates and measurement

## Definitions
- **Postulate 1 (state)**: a closed system is described by a unit vector in a Hilbert space.
- **Postulate 2 (evolution)**: $\lvert\psi(t)\rangle=U(t)\lvert\psi(0)\rangle$ with $U=e^{-iHt/\hbar}$ for a time-independent Hamiltonian $H$ (Schrödinger equation $i\hbar\,\partial_t\lvert\psi\rangle=H\lvert\psi\rangle$).
- **Postulate 3 (measurement)**: a measurement is a set of operators $\{M_m\}$ with $\sum_m M_m^\dagger M_m=I$; outcome $m$ occurs with probability $p(m)=\langle\psi\vert M_m^\dagger M_m\vert\psi\rangle$ and leaves the state $M_m\lvert\psi\rangle/\sqrt{p(m)}$. Projective measurements have $M_m=P_m$; POVMs (Positive Operator-Valued Measures) keep only $E_m=M_m^\dagger M_m$.
- **Postulate 4 (composition)**: composite systems live in the tensor product.
- **Born rule**: $p(m)=\lvert\langle m\vert\psi\rangle\rvert^2$ for a projective measurement in basis $\{\lvert m\rangle\}$.

## Equations
$$U(t)=e^{-iHt/\hbar},\qquad p(m)=\mathrm{Tr}(E_m\rho),\qquad \rho\to\frac{M_m\rho M_m^\dagger}{\mathrm{Tr}(M_m\rho M_m^\dagger)}$$

Measurement is the only postulate that is non-unitary, irreversible, and probabilistic; every "quantum weirdness" in later folders (no-cloning, no-signaling, Bell violations) follows from the four postulates plus linearity.

## Visual
```mermaid
flowchart LR
  P[prepare |ψ⟩] --> U[unitary U = e^{-iHt/ħ}] --> M{measure in basis m}
  M -->|p(m) = |⟨m|ψ⟩|²| R[classical outcome m]
  M --> S[post-measurement state |m⟩]
```

## Key papers and texts
- von Neumann, J. (1932/1955). *Mathematical Foundations of Quantum Mechanics*. Princeton University Press.
- Born, M. (1926). Zur Quantenmechanik der Stoßvorgänge. *Zeitschrift für Physik*, 37, 863.
- Nielsen & Chuang (2010), §2.2.
- Peres, A. (1995). *Quantum Theory: Concepts and Methods*. Kluwer. (Best treatment of POVMs and measurement.)

## In this repo
Every `pytest` in `tests/` is a Born-rule check in disguise: the analytic probabilities are what the simulators must reproduce. `qll/circuits/tomography.py` (Phase 2) reconstructs $\rho$ from Pauli measurement statistics.

## Exercises
1. Show the two-outcome POVM $E_0=\frac23\lvert0\rangle\langle0\rvert$, $E_1=I-E_0$ is valid and compute its outcome probabilities on $\lvert+\rangle$.
2. Prove that no measurement on qubit B can reveal whether qubit A was measured (this is the no-signaling theorem; see `03_quantum_communication/02_teleportation_and_swapping.md`).
