# Gate Decompositions and Measurement-Based Computing

## Single qubits
Every single-qubit unitary is $U=e^{i\alpha}R_z(\beta)R_y(\gamma)R_z(\delta)$ (three rotations about two axes) [nielsen2010]; `qll/circuits/decompositions.zyz_angles` uses Qiskit's Euler decomposer and the test reconstructs random unitaries exactly. Hardware compiles everything to this form: a superconducting qubit's native gates are $R_z$ (a virtual frame change, free) and one calibrated $\sqrt X$ pulse, so any single-qubit gate costs at most two physical pulses.

## Two qubits
Any two-qubit unitary needs at most three CNOTs plus single-qubit gates, by the KAK decomposition of SU(4) [kraus2001] [vatan2004]; the identity needs 0, CNOT itself 1, SWAP 3, and a generic random unitary 3 (`cnot_count`, checked by test). Since two-qubit gates are ten to a hundred times noisier than single-qubit ones, the CNOT count is the cost of a circuit, and compilers optimize it.

## Approximating with a finite set
Fault-tolerant hardware has a discrete gate set (Cliffords and $T$); the Solovay–Kitaev theorem guarantees any unitary to accuracy $\epsilon$ with $O(\log^c(1/\epsilon))$ gates, $c\approx3.97$ in the original construction, and later methods reach the optimal $O(\log(1/\epsilon))$ for single-qubit rotations from $\{H,T\}$ [dawson2006] [ross2016]. The $T$ count is the number that magic-state factories must supply (`learn/01/12`).

## Measurement-based computation
A cluster state (qubits in $|+\rangle$ joined by CZ gates) plus adaptive single-qubit measurements is universal [raussendorf2001]. The elementary step, one-bit teleportation, is in `one_bit_teleportation`: measuring the first qubit of a two-qubit cluster in the basis rotated by $\varphi$ leaves the second in $X^mHR_z(\varphi)|\psi\rangle$, so the rotation angle is chosen by the measurement and the random outcome $m$ is corrected by adapting later measurements. All entanglement is created up front; computation is measurement. This is the model of photonic quantum computing and of the all-photonic repeater (T02), where the "cluster" is a graph state of photons and the "measurements" are the fusions at each node.

## Key papers
- Kraus, B., & Cirac, J. I. (2001). Optimal creation of entanglement using a two-qubit gate. *Physical Review A*, 63, 062309. https://doi.org/10.1103/PhysRevA.63.062309
- Vatan, F., & Williams, C. (2004). Optimal quantum circuits for general two-qubit gates. *Physical Review A*, 69, 032315. https://doi.org/10.1103/PhysRevA.69.032315
- Dawson, C. M., & Nielsen, M. A. (2006). The Solovay–Kitaev algorithm. *Quantum Information & Computation*, 6, 81. arXiv:quant-ph/0505030
- Ross, N. J., & Selinger, P. (2016). Optimal ancilla-free Clifford+T approximation of z-rotations. *Quantum Information & Computation*, 16, 901. arXiv:1403.2975
- Raussendorf, R., & Briegel, H. J. (2001). A one-way quantum computer. *Physical Review Letters*, 86, 5188. https://doi.org/10.1103/PhysRevLett.86.5188

## In this repo
`qll/circuits/decompositions.py`; `learn/01/01`; T02.
