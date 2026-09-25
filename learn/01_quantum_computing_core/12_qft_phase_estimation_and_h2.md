# QFT, Phase Estimation, and the Hydrogen Molecule

## Quantum Fourier transform
$\mathrm{QFT}|j\rangle=\frac{1}{\sqrt{2^n}}\sum_ke^{2\pi ijk/2^n}|k\rangle$ with $n(n+1)/2$ gates: a Hadamard and a ladder of controlled phases per qubit, then a qubit-order reversal [coppersmith1994]. `qll/circuits/algorithms.py` builds it in Qiskit and the test checks the unitary against the Fourier matrix for $n=2,3,4$ — including the little-endian ordering trap that cost this repository one afternoon.

## Phase estimation
For $U|u\rangle=e^{2\pi i\varphi}|u\rangle$, apply controlled-$U^{2^k}$ from $t$ register qubits and an inverse QFT; the register reads $\varphi$ to $t$ bits, exactly when $\varphi$ is a $t$-bit fraction and within one bit with probability $\ge4/\pi^2$ otherwise [kitaev1995]. The model estimates $\varphi=0.375$ exactly with 4 bits and $0.3$ to within $2^{-5}$ with 5. Shor's algorithm is this primitive applied to modular multiplication; the resource estimates in `learn/01/02` count the controlled-$U^{2^k}$ arithmetic.

## The smallest chemistry
In the minimal basis with symmetry reduction, H₂ is a two-qubit Hamiltonian $H=g_0I+g_1Z_0+g_2Z_1+g_3Z_0Z_1+g_4X_0X_1+g_5Y_0Y_1$ [omalley2016]. Exact diagonalisation gives the electronic energy $-1.851$ Ha; adding the nuclear repulsion $1/R=0.714$ Ha gives $-1.137$ Ha, the experimental equilibrium value, which a variational eigensolver with the one-parameter ansatz $\cos\theta|01\rangle+\sin\theta|10\rangle$ reaches exactly (`chemistry_h2.py`). The naive Jordan–Wigner Hamiltonian of a molecule with $N$ spin-orbitals has $\sim N^4/8$ Pauli terms, which is why chemistry beyond a few atoms is a resource-estimation problem before it is a physics problem [mcardle2020].

## Magic states
Cliffords are cheap in a code; $T$ gates need magic states distilled from noisy ones: the 15-to-1 protocol maps error $p$ to $35p^3$, so $10^{-3}\to10^{-12}$ takes two rounds and 225 raw states per $T$ [bravyi2005]. An algorithm with $10^9$ $T$ gates therefore consumes $2\times10^{11}$ raw magic states, which is why factories dominate fault-tolerant footprints [gidney2021factor] (`magic_states.py`).

## Key papers
- Coppersmith, D. (1994). An approximate Fourier transform useful in quantum factoring. IBM Research Report RC 19642. arXiv:quant-ph/0201067
- Kitaev, A. Y. (1995). Quantum measurements and the Abelian stabilizer problem. arXiv:quant-ph/9511026
- O'Malley, P. J. J., et al. (2016). Scalable quantum simulation of molecular energies. *Physical Review X*, 6, 031007. https://doi.org/10.1103/PhysRevX.6.031007
- Peruzzo, A., et al. (2014). A variational eigenvalue solver on a photonic quantum processor. *Nature Communications*, 5, 4213. https://doi.org/10.1038/ncomms5213
- Bravyi, S., & Kitaev, A. (2005). Universal quantum computation with ideal Clifford gates and noisy ancillas. *Physical Review A*, 71, 022316. https://doi.org/10.1103/PhysRevA.71.022316
- Gidney, C., & Ekerå, M. (2021). How to factor 2048 bit RSA integers in 8 hours using 20 million noisy qubits. *Quantum*, 5, 433. https://doi.org/10.22331/q-2021-04-15-433

## In this repo
`qll/circuits/{algorithms,chemistry_h2,magic_states}.py`; `learn/01/02`, `01/07`.
