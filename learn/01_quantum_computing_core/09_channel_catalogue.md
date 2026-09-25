# Channel Catalogue

Twelve named single-qubit channels, each an operator-sum $\rho\mapsto\sum_kE_k\rho E_k^\dagger$ whose Kraus operators are checked for $\sum E_k^\dagger E_k=I$ on construction (`qll/circuits/noise/catalogue.py`; INV-4). Average gate fidelity $F_{\rm avg}=(dF_{\rm pro}+1)/(d+1)$ with $F_{\rm pro}=\sum_k|\mathrm{Tr}E_k|^2/d^2$ [nielsen2002].

| Channel | Kraus operators | Physics | $F_{\rm avg}$ |
|---|---|---|---|
| bit flip | $\sqrt{1-p}I,\ \sqrt pX$ | $X$ error with probability $p$ | $1-2p/3$ |
| phase flip | $\sqrt{1-p}I,\ \sqrt pZ$ | $Z$ error | $1-2p/3$ |
| bit-phase flip | $\sqrt{1-p}I,\ \sqrt pY$ | $Y$ error | $1-2p/3$ |
| Pauli | $\sqrt{p_0}I,\sqrt{p_x}X,\sqrt{p_y}Y,\sqrt{p_z}Z$ | general stochastic Pauli error | $1-\tfrac23(p_x+p_y+p_z)$ |
| depolarizing | as Pauli with $p/4$ each | replace by $I/2$ with probability $p$ | $1-p/2$ |
| amplitude damping | $\begin{pmatrix}1&0\\0&\sqrt{1-\gamma}\end{pmatrix},\begin{pmatrix}0&\sqrt\gamma\\0&0\end{pmatrix}$ | $T_1$ relaxation at zero temperature | $1-\gamma/2+\ldots$ |
| generalized amplitude damping | four operators weighted by the bath ground weight | $T_1$ at finite temperature (`thermal.py`) | |
| phase damping | $\begin{pmatrix}1&0\\0&\sqrt{1-\lambda}\end{pmatrix},\begin{pmatrix}0&0\\0&\sqrt\lambda\end{pmatrix}$ | $T_\varphi$ dephasing | |
| complete dephasing | phase damping with $\lambda=1$ | a measurement whose result is discarded | $2/3$ |
| reset | $|0\rangle\langle0|,\ |0\rangle\langle1|$ | active reset to $|0\rangle$ | $1/2$ |
| coherent rotation error | one unitary $e^{-i\theta X/2}$ | miscalibrated pulse | $1-\tfrac23\sin^2(\theta/2)$ |
| Pauli-twirled rotation error | Pauli channel with the same diagonal | what randomized compiling turns it into [wallman2016] | same $F_{\rm avg}$ |

The last two rows carry the lesson: a coherent error and its twirled stochastic version have the *same* average fidelity, but coherent errors add in amplitude across a circuit (an over-rotation of $\theta$ repeated $n$ times is an error of $n\theta$, infidelity $\propto n^2$), while stochastic errors add in probability ($\propto n$). Randomized compiling deliberately twirls, trading a worst case for an average case that error correction can handle [wallman2016] [hashim2021].

## Key papers
- Nielsen, M. A. (2002). A simple formula for the average gate fidelity of a quantum dynamical operation. *Physics Letters A*, 303, 249. https://doi.org/10.1016/S0375-9601(02)01272-0
- Wallman, J. J., & Emerson, J. (2016). Noise tailoring for scalable quantum computation via randomized compiling. *Physical Review A*, 94, 052325. https://doi.org/10.1103/PhysRevA.94.052325
- Hashim, A., et al. (2021). Randomized compiling for scalable quantum computing on a noisy superconducting quantum processor. *Physical Review X*, 11, 041039. https://doi.org/10.1103/PhysRevX.11.041039

## In this repo
`qll/circuits/noise/{catalogue,_kraus_base,depolarizing,amplitude_damping,phase_damping,thermal}.py`; `learn/00/06`.
