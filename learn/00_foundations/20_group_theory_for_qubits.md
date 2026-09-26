# Group Theory for Qubits

## The Pauli group
$\{I,X,Y,Z\}^{\otimes n}$ with phases $\pm1,\pm i$ forms a group; modulo phase it has $4^n$ elements, and every pair of elements either commutes or anticommutes. Stabilizer codes are abelian subgroups of it (`learn/01/11`), errors are elements of it, and a Pauli twirl averages any channel over it (`learn/01/09`).

## The Clifford group
Unitaries that map Paulis to Paulis under conjugation. Modulo phase there are **24** single-qubit Cliffords and **11 520** two-qubit Cliffords; `qll/circuits/groups.py` finds the first by closing $\{H,S\}$ under multiplication and counts the second by enumerating Stim tableaus [gottesman1998] [ozols2008]. Three facts follow:
- **Gottesman–Knill**: Clifford circuits on stabilizer states are classically simulable in polynomial time, which is why Stim can simulate thousands of qubits and why Cliffords alone give no quantum advantage.
- **Randomized benchmarking** draws uniformly from the Clifford group because it is a unitary 2-design: averaging any noise over it yields a depolarizing channel (`learn/01/10`).
- **Universality** needs one non-Clifford gate, usually $T$, whose cost in a code is magic-state distillation (`learn/01/12`).

## Beyond
Irreducible representations of SU(2) give spin and angular-momentum addition (the triplet/singlet structure of two spins, and the $|\Psi^-\rangle$ that every Bell test uses); the symmetric group governs bosonic interference (Hong–Ou–Mandel, boson sampling); and unitary $t$-designs quantify how well a finite gate set imitates Haar-random unitaries.

## Key papers
- Gottesman, D. (1998). The Heisenberg representation of quantum computers. arXiv:quant-ph/9807006
- Ozols, M. (2008). Clifford group. Lecture notes, University of Waterloo.
- Dankert, C., Cleve, R., Emerson, J., & Livine, E. (2009). Exact and approximate unitary 2-designs and their application to fidelity estimation. *Physical Review A*, 80, 012304. https://doi.org/10.1103/PhysRevA.80.012304

## In this repo
`qll/circuits/groups.py`; Stim throughout.
