# The qubit and the Bloch sphere

## Definitions
- **Qubit**: any two-level quantum system whose two levels can be prepared, coherently controlled, and read out, and which is sufficiently isolated from the other levels and the environment (DiVincenzo criteria 1–5 in `02_qubit_modalities/README.md`).
- **Computational basis** $\lvert0\rangle,\lvert1\rangle$; general pure state $\lvert\psi\rangle=\cos\frac\theta2\lvert0\rangle+e^{i\varphi}\sin\frac\theta2\lvert1\rangle$.
- **Bloch vector** $\vec r=(\langle X\rangle,\langle Y\rangle,\langle Z\rangle)$; pure states have $\lvert\vec r\rvert=1$, mixed states $\lvert\vec r\rvert<1$, the maximally mixed state $I/2$ is the center.
- **Global phase** is unobservable: $\lvert\psi\rangle$ and $e^{i\alpha}\lvert\psi\rangle$ are the same point.

## Equations
$$\rho=\tfrac12\left(I+\vec r\cdot\vec\sigma\right),\qquad \mathrm{Tr}\,\rho^2=\tfrac12(1+\lvert\vec r\rvert^2)$$

A unitary $U=e^{-i\alpha\,\hat n\cdot\vec\sigma/2}$ rotates $\vec r$ by angle $\alpha$ about axis $\hat n$: every single-qubit gate is a rotation of the sphere. $H$ is a $\pi$ rotation about $(\hat x+\hat z)/\sqrt2$; $X$ is a $\pi$ rotation about $\hat x$; the phase gate $S$ is $\pi/2$ about $\hat z$.

Relaxation and dephasing move the vector inside the sphere: with the Bloch equations, $\langle X\rangle,\langle Y\rangle\propto e^{-t/T_2}$ and $\langle Z\rangle\to z_{\rm eq}=1-2p_{\rm exc}(T)$ with rate $1/T_1$, where $p_{\rm exc}$ comes from the thermal occupation in `qll/circuits/noise/thermal.py`.

## Visual
![bloch](../../docs/figures/bloch_sphere.svg)

Run `python -m qll.viz.bloch_sphere` to regenerate. Left: the pure state as a surface point. Right: the decay of $\lvert+\rangle$ under $T_1=50\,\mu$s, $T_2=30\,\mu$s at a 50 mK bath.

## Key papers and texts
- Bloch, F. (1946). Nuclear induction. *Physical Review*, 70, 460. https://doi.org/10.1103/PhysRev.70.460
- Feynman, R. P., Vernon, F. L., & Hellwarth, R. W. (1957). Geometrical representation of the Schrödinger equation for solving maser problems. *J. Appl. Phys.*, 28, 49.
- DiVincenzo, D. P. (2000). The physical implementation of quantum computation. *Fortschritte der Physik*, 48, 771. arXiv:quant-ph/0002077

## In this repo
`qll/viz/bloch_sphere.py`; `qll/circuits/noise/{amplitude_damping,phase_damping}.py` (Phase 2) implement the two decay directions as Kraus maps.

## Exercises
1. Find $\theta,\varphi$ for $\lvert-i\rangle=(\lvert0\rangle-i\lvert1\rangle)/\sqrt2$.
2. Show $T_2\le2T_1$ from the requirement that $\rho$ stays positive semidefinite.
