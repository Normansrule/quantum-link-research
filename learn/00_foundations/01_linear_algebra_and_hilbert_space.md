# Linear algebra and Hilbert space

## Definitions
- **State vector** $\lvert\psi\rangle\in\mathcal H$, a unit vector in a complex inner-product space. For one qubit $\mathcal H=\mathbb C^2$; for $n$ qubits $\mathcal H=(\mathbb C^2)^{\otimes n}$, dimension $2^n$.
- **Bra** $\langle\psi\rvert$: the conjugate transpose. Inner product $\langle\phi\vert\psi\rangle$; outer product $\lvert\psi\rangle\langle\phi\rvert$ is an operator.
- **Hermitian operator** $A=A^\dagger$: real eigenvalues, orthogonal eigenvectors; these are observables.
- **Unitary** $U^\dagger U=I$: preserves inner products; these are closed-system evolutions and gates.
- **Tensor product**: $\lvert a\rangle\otimes\lvert b\rangle$, written $\lvert ab\rangle$. A state that cannot be written as a single product is **entangled**.
- **Pauli matrices** $X=\begin{pmatrix}0&1\\1&0\end{pmatrix}$, $Y=\begin{pmatrix}0&-i\\i&0\end{pmatrix}$, $Z=\begin{pmatrix}1&0\\0&-1\end{pmatrix}$; with $I$ they span all $2\times2$ matrices.

## Equations
$$\langle\psi\vert\psi\rangle=1,\qquad A=\sum_k a_k\lvert k\rangle\langle k\rvert,\qquad [X,Y]=2iZ,\quad \{X,Y\}=0,\quad X^2=Y^2=Z^2=I$$

Spectral theorem: any observable is a weighted sum of projectors onto its eigenvectors. The Schmidt decomposition of a bipartite pure state, $\lvert\psi\rangle_{AB}=\sum_k\lambda_k\lvert u_k\rangle\lvert v_k\rangle$, has one non-zero $\lambda$ if and only if the state is a product.

## Visual
The Pauli algebra is the coordinate system of the Bloch sphere: see `docs/figures/bloch_sphere.svg`.

## Key papers and texts
- Nielsen, M. A., & Chuang, I. L. (2010). *Quantum Computation and Quantum Information*, ch. 2. Cambridge University Press.
- Dirac, P. A. M. (1939). A new notation for quantum mechanics. *Math. Proc. Cambridge Philos. Soc.*, 35, 416.
- Axler, S. (2015). *Linear Algebra Done Right* (3rd ed.). Springer. (For the underlying mathematics.)

## In this repo
`qll/circuits/bell.py` (Phase 2) tests Schmidt coefficients $(1/\sqrt2,1/\sqrt2)$ for Bell states; `qll/circuits/fidelity.py` uses the spectral theorem for $\sqrt\rho$.

## Exercises
1. Show $HZH=X$ with $H=\frac1{\sqrt2}\begin{pmatrix}1&1\\1&-1\end{pmatrix}$.
2. Compute the Schmidt coefficients of $\frac{1}{\sqrt3}(\lvert00\rangle+\lvert01\rangle+\lvert10\rangle)$ and decide whether it is entangled.
