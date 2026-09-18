# Spin and angular momentum

## Definitions
- **Angular momentum algebra** $[J_i,J_j]=i\hbar\epsilon_{ijk}J_k$; eigenvalues $J^2=\hbar^2j(j+1)$, $J_z=\hbar m$, $m=-j,\dots,j$.
- **Spin-1/2**: $j=\tfrac12$, two states, $\vec S=\frac\hbar2\vec\sigma$; electrons, protons, ¹³C, ³¹P, ¹⁷¹Yb⁺ hyperfine (effective).
- **Spin-1**: three states; the NV ground state, with the zero-field splitting $D S_z^2$ making $m_s=0$ and $\pm1$ non-degenerate even at $B=0$.
- **Zeeman effect**: $H=-\vec\mu\cdot\vec B=g\mu_B\vec S\cdot\vec B/\hbar$; $\gamma_e/2\pi=28.0$ GHz/T for the electron, 42.6 MHz/T for the proton, 10.7 MHz/T for ¹³C.
- **Hyperfine coupling** $A\,\vec S\cdot\vec I$: electron–nuclear interaction; the mechanism that turns nuclear spins into memory qubits addressable through the electron (NV ¹³C registers, ³¹P donors, trapped-ion hyperfine qubits).
- **Clock transitions**: $\partial f/\partial B=0$ points where the qubit frequency is first-order insensitive to field noise (ion hyperfine qubits at zero field; ZEFOZ points in Eu:YSO give the 6–13 hour coherence).

## Equations
$$S_\pm\lvert s,m\rangle=\hbar\sqrt{s(s+1)-m(m\pm1)}\lvert s,m\pm1\rangle,\qquad H_{\rm NV}=DS_z^2+\gamma_e\vec B\cdot\vec S+\sum_kA_k\vec S\cdot\vec I_k$$
Larmor precession: a spin in field $B$ precesses at $\omega=\gamma B$; the Ramsey fringe frequency in `04_two_level_dynamics_rabi_ramsey.md` is the detuning of this precession from the drive.
Addition of angular momenta $j_1\otimes j_2=\lvert j_1-j_2\rvert\oplus\dots\oplus(j_1+j_2)$: two spin-1/2 give singlet (the $\lvert\Psi^-\rangle$ Bell state, $j=0$) plus triplet ($j=1$); the singlet is rotationally invariant, which is why $E(a,b)=-\hat a\cdot\hat b$.

## Visual
```mermaid
flowchart TB
  S1[electron spin S = 1 (NV)] -->|D S_z²  2.87 GHz| L[m_s = 0 ; m_s = ±1]
  L -->|γ_e B| Z[±1 split by 2.8 MHz/G]
  S1 -->|A S·I| N[¹³C, ¹⁴N nuclear spins: memory qubits]
```

## Key papers and texts
- Uhlenbeck, G. E., & Goudsmit, S. (1925). Ersetzung der Hypothese vom unmechanischen Zwang. *Naturwissenschaften*, 13, 953.
- Sakurai, J. J., & Napolitano, J. (2020). *Modern Quantum Mechanics* (3rd ed.), ch. 3. Cambridge University Press.
- Doherty, M. W., et al. (2013). *Phys. Rep.*, 528, 1. https://doi.org/10.1016/j.physrep.2013.02.001 (the NV spin Hamiltonian in full).
- Zhong, M., et al. (2015). *Nature*, 517, 177. https://doi.org/10.1038/nature14025 (ZEFOZ clock transitions).

## In this repo
`qll/hardware/nv_node.py` (Phase 3) implements $H_{\rm NV}$; the singlet's rotational invariance is the reason `chsh.py` can use any pair of orthogonal axes.

## Exercises
1. Diagonalize $H_{\rm NV}$ for $B$ along the NV axis and off-axis (30°) at 100 G; sketch both ODMR spectra.
2. Show that the Bell singlet is invariant under $U\otimes U$ for any single-qubit unitary $U$.
