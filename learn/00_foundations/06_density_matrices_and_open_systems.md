# Density matrices and open quantum systems

## Definitions
- **Density operator** $\rho=\sum_i p_i\lvert\psi_i\rangle\langle\psi_i\rvert$: Hermitian, positive semidefinite, trace 1. Purity $\mathrm{Tr}\rho^2\le1$.
- **Partial trace** $\rho_A=\mathrm{Tr}_B\rho_{AB}$: what a local observer sees.
- **Quantum channel** (CPTP map): $\mathcal E(\rho)=\sum_k E_k\rho E_k^\dagger$ with $\sum_k E_k^\dagger E_k=I$ (Kraus form). Every physical noise process is one.
- **Lindblad master equation**: the continuous-time generator of a Markovian channel.
- **$T_1$** (energy relaxation), **$T_\varphi$** (pure dephasing), **$T_2$** (total transverse decay): $1/T_2=1/(2T_1)+1/T_\varphi$.

## Equations
$$\dot\rho=-\frac i\hbar[H,\rho]+\sum_j\left(L_j\rho L_j^\dagger-\tfrac12\{L_j^\dagger L_j,\rho\}\right)$$
Relaxation at temperature $T$: $L_\downarrow=\sqrt{\Gamma(\bar n+1)}\,\sigma_-$, $L_\uparrow=\sqrt{\Gamma\bar n}\,\sigma_+$, giving $T_1(T)=T_1(0)/(2\bar n+1)$; pure dephasing: $L_\varphi=\sqrt{1/2T_\varphi}\,Z$. The three canonical single-qubit channels (depolarizing, amplitude damping, phase damping) and their Kraus operators are in `docs/physics_module_design.md` §3.

## Visual
```mermaid
flowchart LR
  rho[ρ(0)] -->|unitary part -i[H,ρ]/ħ| rho2[ρ(t)]
  rho -->|L_↓ (n̄+1)Γ| rho2
  rho -->|L_↑ n̄Γ| rho2
  rho -->|L_φ| rho2
  T[bath temperature T] --> nbar[n̄ = 1/(e^{ħω/kT}−1)] --> rho2
```

## Key papers and texts
- Lindblad, G. (1976). On the generators of quantum dynamical semigroups. *Commun. Math. Phys.*, 48, 119. https://doi.org/10.1007/BF01608499
- Gorini, V., Kossakowski, A., & Sudarshan, E. C. G. (1976). *J. Math. Phys.*, 17, 821.
- Kraus, K. (1983). *States, Effects, and Operations*. Springer.
- Breuer, H.-P., & Petruccione, F. (2002). *The Theory of Open Quantum Systems*. Oxford University Press.
- Clerk, A. A., et al. (2010). Introduction to quantum noise, measurement, and amplification. *Rev. Mod. Phys.*, 82, 1155. https://doi.org/10.1103/RevModPhys.82.1155
- Johansson, J. R., Nation, P. D., & Nori, F. (2012). QuTiP. *Comput. Phys. Commun.*, 183, 1760. (The library that integrates the master equation for us.)

## In this repo
`qll/circuits/noise/thermal.py` (done, Phase 1) is the temperature-dependent version; Phase 2 adds `_kraus_base.py` with the CPTP check (invariant INV-4) and QuTiP cross-checks of every Kraus map against its Lindblad form.

## Exercises
1. Show that amplitude damping for time $t$ followed by time $s$ equals amplitude damping for $t+s$ (semigroup property).
2. Integrate the Lindblad equation for $L_\varphi$ alone and confirm the off-diagonal element decays as $e^{-t/T_\varphi}$.
