# Math toolkit: one page of what you actually need

| Need | Tool | Where it shows up |
|---|---|---|
| Vectors, inner products, eigen-decomposition | linear algebra over $\mathbb C$ | states, observables, gates |
| Tensor products, partial trace | multilinear algebra | entanglement, reduced states, no-signaling |
| Matrix exponential, Lie algebras $\mathfrak{su}(2)$ | $e^{-i\theta\hat n\cdot\vec\sigma/2}=\cos\frac\theta2 I-i\sin\frac\theta2\,\hat n\cdot\vec\sigma$ | every single-qubit gate |
| Fourier transforms | $\hat f(k)=\int f(x)e^{-ikx}dx$ | position–momentum, QFT, pulse shaping, phase estimation |
| Probability, Bayes, entropy | $h_2$, $S(\rho)$, mutual information | measurement, QKD rates, tomography |
| Ordinary and stochastic differential equations | Schrödinger, Lindblad, Bloch equations | dynamics, noise |
| Complex analysis (residues, contour) | Fourier/Laplace inversion, susceptibilities | response functions, filters |
| Group theory basics | Pauli group, Clifford group, $SU(2)\to SO(3)$ | stabilizer codes, Bloch rotations |
| Linear programming / convex optimization | semidefinite programs | entanglement witnesses, DI bounds |
| Numerical linear algebra | `numpy.linalg.eigh`, sparse solvers | every simulator we pin (Aer, QuTiP, Stim) |

## Identities worth memorizing
$$e^{i\theta X}=\cos\theta\,I+i\sin\theta\,X,\qquad (\vec a\cdot\vec\sigma)(\vec b\cdot\vec\sigma)=(\vec a\cdot\vec b)I+i(\vec a\times\vec b)\cdot\vec\sigma$$
$$\mathrm{Tr}(A\otimes B)=\mathrm{Tr}A\,\mathrm{Tr}B,\qquad (A\otimes B)(C\otimes D)=AC\otimes BD,\qquad \mathrm{Tr}_B\big(\lvert\psi\rangle\langle\psi\rvert\big)=\sum_k\lambda_k^2\lvert u_k\rangle\langle u_k\rvert$$
$$\lvert\Phi^+\rangle=\tfrac1{\sqrt2}\sum_i\lvert ii\rangle\ \Rightarrow\ (A\otimes I)\lvert\Phi^+\rangle=(I\otimes A^T)\lvert\Phi^+\rangle\ \text{(the transpose trick behind teleportation)}$$

## Texts
- Nielsen & Chuang (2010), ch. 2 (all the linear algebra you need, in 60 pages).
- Watrous, J. (2018). *The Theory of Quantum Information*. Cambridge University Press (rigorous).
- Strang, G. (2016). *Introduction to Linear Algebra* (5th ed.). Wellesley-Cambridge.
