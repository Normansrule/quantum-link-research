# Wave mechanics: the Schrödinger equation and the four solvable problems

## Definitions
- **Wavefunction** $\psi(x,t)$: the position-basis components of $\lvert\psi\rangle$; $\lvert\psi\rvert^2$ is the probability density.
- **Time-dependent Schrödinger equation** $i\hbar\,\partial_t\psi=\hat H\psi$, $\hat H=-\frac{\hbar^2}{2m}\nabla^2+V$.
- **Stationary states** $\psi(x,t)=\phi(x)e^{-iEt/\hbar}$ with $\hat H\phi=E\phi$.
- **Uncertainty**: $\Delta x\,\Delta p\ge\hbar/2$ follows from $[\hat x,\hat p]=i\hbar$; it is a property of states, not of measurement clumsiness.
- **Tunneling**: non-zero amplitude in classically forbidden regions; the mechanism of the Josephson junction (`02_qubit_modalities/01`) and of donor ionization in silicon.

## Equations: the four problems everything else is built from
1. **Particle in a box** (length $L$): $E_n=\frac{n^2\pi^2\hbar^2}{2mL^2}$; a quantum dot is a 3-D box, which is why dot energy levels scale as $1/L^2$ (`02_qubit_modalities/02`).
2. **Harmonic oscillator**: $E_n=\hbar\omega(n+\tfrac12)$; ladder operators $a,a^\dagger$ with $[a,a^\dagger]=1$. Every mode of light, every LC circuit, every phonon mode is one; the equal spacing is *why* a linear oscillator cannot be a qubit and why the transmon needs the Josephson nonlinearity.
3. **Hydrogen atom**: $E_n=-\frac{13.6\ \text{eV}}{n^2}$, quantum numbers $n,l,m$; Rydberg states with $n\sim50$–100 have radii $\propto n^2$ and polarizabilities $\propto n^7$, which is the origin of the Rydberg blockade (`02_qubit_modalities/05`).
4. **Two-level system**: any pair of levels far from others, $H=\frac{\hbar\omega_0}{2}Z$; the qubit itself.

Tunneling through a barrier of height $V_0$ and width $a$: $T\approx e^{-2\kappa a}$, $\kappa=\sqrt{2m(V_0-E)}/\hbar$; for a Josephson junction the Cooper-pair tunneling amplitude sets $E_J$.

## Visual
```mermaid
flowchart LR
  B[box: E ∝ n²/L²] --> QD[quantum dot qubit]
  HO[oscillator: E = ħω(n+½)] --> LC[LC resonator, photon mode] --> TM[+ Josephson nonlinearity = transmon]
  H[hydrogen: E ∝ −1/n²] --> RY[Rydberg atom qubit]
  TLS[two levels: H = ħω₀Z/2] --> Q[any qubit]
```

## Key papers and texts
- Schrödinger, E. (1926). Quantisierung als Eigenwertproblem. *Annalen der Physik*, 384, 361. https://doi.org/10.1002/andp.19263840404
- Heisenberg, W. (1927). Über den anschaulichen Inhalt der quantentheoretischen Kinematik und Mechanik. *Zeitschrift für Physik*, 43, 172.
- Griffiths, D. J., & Schroeter, D. F. (2018). *Introduction to Quantum Mechanics* (3rd ed.). Cambridge University Press. (Chapters 2 and 4.)
- Shankar, R. (1994). *Principles of Quantum Mechanics* (2nd ed.). Springer.

## In this repo
`qll/viz/transmon_levels.py` is problem 2 plus a cosine: exact diagonalization in the charge basis.

## Exercises
1. Compute the ground-state energy of an electron in a 10 nm box and compare with $k_BT$ at 1 K and 300 K.
2. Show that $\langle n\vert\hat x\vert n\pm1\rangle\ne0$ and all other matrix elements vanish for the oscillator, and explain why a microwave drive therefore cannot address only one transition of a *linear* oscillator.
