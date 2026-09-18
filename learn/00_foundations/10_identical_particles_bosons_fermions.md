# Identical particles: bosons, fermions, and why photons bunch

## Definitions
- **Exchange symmetry**: swapping two identical particles can change the state only by a phase; in three dimensions that phase is $+1$ (bosons: photons, phonons, ⁴He, Cooper pairs) or $-1$ (fermions: electrons, protons, neutrons, ³He).
- **Pauli exclusion**: two fermions cannot occupy the same single-particle state; the reason atoms have shells, the reason a quantum dot holds a spin singlet with two electrons, and the reason Pauli spin blockade works as a spin readout.
- **Bose–Einstein and Fermi–Dirac statistics**: $\bar n_{\rm BE}=1/(e^{(E-\mu)/k_BT}-1)$, $\bar n_{\rm FD}=1/(e^{(E-\mu)/k_BT}+1)$. For photons $\mu=0$, giving the Planck occupation in `qll/circuits/noise/thermal.py`.
- **Second quantization**: creation and annihilation operators $a^\dagger,a$ with $[a,a^\dagger]=1$ (bosons) or $\{c,c^\dagger\}=1$ (fermions); Fock states $\lvert n\rangle$.
- **Anyons** (two dimensions only): exchange phases other than $\pm1$, including non-Abelian ones; the basis of topological quantum computing (`02_qubit_modalities/07`).

## Equations
Hong–Ou–Mandel from exchange symmetry: two identical bosons on a 50:50 beam splitter,
$$a_1^\dagger a_2^\dagger\to\tfrac12(a_3^\dagger+a_4^\dagger)(a_3^\dagger-a_4^\dagger)=\tfrac12\big(a_3^{\dagger2}-a_4^{\dagger2}\big),$$
the cross term cancels, so they never exit separately. Two fermions would do the opposite (always separate). The Planck law is Bose–Einstein statistics for a gas of photons: $u(\nu,T)=\frac{8\pi h\nu^3}{c^3}\bar n_{\rm BE}(\nu,T)$.

Cooper pairs are bosonic bound states of two fermions; their condensate is the superconductor whose macroscopic phase $\varphi$ is the transmon coordinate.

## Key papers and texts
- Bose, S. N. (1924). Plancks Gesetz und Lichtquantenhypothese. *Zeitschrift für Physik*, 26, 178. https://doi.org/10.1007/BF01327326
- Pauli, W. (1925). Über den Zusammenhang des Abschlusses der Elektronengruppen im Atom mit der Komplexstruktur der Spektren. *Zeitschrift für Physik*, 31, 765.
- Hong, C. K., Ou, Z. Y., & Mandel, L. (1987). *Physical Review Letters*, 59, 2044. https://doi.org/10.1103/PhysRevLett.59.2044
- Nayak, C., et al. (2008). Non-Abelian anyons and topological quantum computation. *Rev. Mod. Phys.*, 80, 1083. https://doi.org/10.1103/RevModPhys.80.1083
- Feynman Lectures Vol. III, ch. 4 ("Identical particles").

## In this repo
`qll/circuits/noise/thermal.py` and `qll/channels/thermal_background.py` are Bose–Einstein statistics applied twice; `qll/hardware/beam_splitter.py` (Phase 3) encodes the HOM algebra.

## Exercises
1. Derive the HOM result above and then repeat it for a beam splitter of reflectivity $R\neq1/2$; find the coincidence probability.
2. Explain why Pauli spin blockade lets you read out a spin by measuring a current.
