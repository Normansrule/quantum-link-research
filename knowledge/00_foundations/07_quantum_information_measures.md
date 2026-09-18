# Quantum information measures

## Definitions
- **Shannon entropy** $H(X)=-\sum p\log_2p$; **binary entropy** $h_2(p)$.
- **von Neumann entropy** $S(\rho)=-\mathrm{Tr}\rho\log_2\rho$; zero for pure states, $n$ bits for $I/2^n$.
- **Fidelity** $F(\rho,\sigma)=\left(\mathrm{Tr}\sqrt{\sqrt\rho\,\sigma\sqrt\rho}\right)^2$; for a pure target $F=\langle\psi\vert\rho\vert\psi\rangle$.
- **Trace distance** $D=\frac12\lVert\rho-\sigma\rVert_1$; Fuchs–van de Graaf: $1-\sqrt F\le D\le\sqrt{1-F}$.
- **Holevo bound**: $n$ qubits carry at most $n$ classical bits: $I(X{:}Y)\le S(\rho)-\sum_xp_xS(\rho_x)\le n$.
- **Mutual information**, **conditional entropy** (can be negative for entangled states, which is the resource behind superdense coding and teleportation).

## Equations
$$h_2(x)=-x\log_2x-(1-x)\log_2(1-x),\qquad S(\rho_{AB})\le S(\rho_A)+S(\rho_B)$$
$$F_{\rm avg}(\text{teleportation with singlet fraction }f)=\frac{2f+1}{3},\qquad F_{\rm classical}=\frac23$$

## Visual
See `docs/figures/qkd_rate_explorer.svg` for $h_2$ at work in the BB84 rate.

## Key papers
- Shannon, C. E. (1948). A mathematical theory of communication. *Bell System Technical Journal*, 27, 379.
- Holevo, A. S. (1973). Bounds for the quantity of information transmitted by a quantum communication channel. *Probl. Inf. Transm.*, 9, 177.
- Uhlmann, A. (1976). *Rep. Math. Phys.*, 9, 273. https://doi.org/10.1016/0034-4877(76)90060-4
- Jozsa, R. (1994). Fidelity for mixed quantum states. *J. Mod. Opt.*, 41, 2315. https://doi.org/10.1080/09500349414552171
- Fuchs, C. A., & van de Graaf, J. (1999). *IEEE Trans. Inf. Theory*, 45, 1216. https://doi.org/10.1109/18.761271
- Horodecki, M., Horodecki, P., & Horodecki, R. (1999). General teleportation channel, singlet fraction, and quasidistillation. *Physical Review A*, 60, 1888. https://doi.org/10.1103/PhysRevA.60.1888
- Wilde, M. M. (2017). *Quantum Information Theory* (2nd ed.). Cambridge University Press.

## In this repo
`qll/qkd/binary_entropy.py`, `qll/qkd/key_rate.py` (done); `qll/circuits/fidelity.py` (Phase 2) with the Fuchs–van de Graaf inequality as a test.

## Exercises
1. Compute $S(\rho_A)$ for $\lvert\Phi^+\rangle$ and for $\cos\theta\lvert00\rangle+\sin\theta\lvert11\rangle$.
2. Show that superdense coding saturates Holevo when the shared state is maximally entangled.
