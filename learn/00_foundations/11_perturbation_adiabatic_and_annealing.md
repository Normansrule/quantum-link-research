# Perturbation theory, the adiabatic theorem, and quantum annealing

## Definitions
- **Time-independent perturbation theory**: $E_n\approx E_n^{(0)}+\langle n\vert V\vert n\rangle+\sum_{m\ne n}\frac{\lvert\langle m\vert V\vert n\rangle\rvert^2}{E_n^{(0)}-E_m^{(0)}}$. The dispersive shift $\chi=g^2/\Delta$ of circuit QED and the AC Stark shift are second-order results.
- **Time-dependent perturbation theory / Fermi's golden rule**: transition rate $\Gamma=\frac{2\pi}{\hbar}\lvert\langle f\vert V\vert i\rangle\rvert^2\rho(E_f)$; spontaneous emission, and hence $T_1$, is this rule with the vacuum as the perturbation. Placing an emitter in a cavity changes $\rho(E_f)$: the **Purcell effect**, $\Gamma_{\rm cav}/\Gamma_0=\frac{3}{4\pi^2}\left(\frac\lambda n\right)^3\frac{Q}{V}$, which is how SiV nanocavities raise the zero-phonon-line emission rate (`02_qubit_modalities/03`).
- **Adiabatic theorem**: a system in an eigenstate of a slowly varying $H(t)$ stays in the corresponding instantaneous eigenstate if the rate of change is small compared with the gap: $\hbar\lvert\langle m\vert\dot H\vert n\rangle\rvert/\Delta_{mn}^2\ll1$.
- **Landau–Zener**: probability of a non-adiabatic transition through an avoided crossing $P=e^{-2\pi\Delta^2/(\hbar v)}$; the physics of adiabatic gates in spin qubits and of fast-flux transmon gates.
- **Quantum annealing / adiabatic quantum computation**: encode a problem in the ground state of $H_P$, start in the ground state of an easy $H_0$, interpolate $H(s)=(1-s)H_0+sH_P$ slowly enough. Equivalent in power to the circuit model in principle; in practice limited by the minimum gap, which can close exponentially fast.

## Equations
$$\chi=\frac{g^2}{\Delta}\ \text{(two-level)},\qquad \chi_{\rm transmon}=\frac{g^2}{\Delta}\frac{\alpha}{\Delta+\alpha},\qquad P_{\rm LZ}=e^{-2\pi\Delta^2/(\hbar v)},\qquad t_{\rm anneal}\gtrsim\frac{\hbar\,\lVert\dot H\rVert}{\Delta_{\min}^2}$$

## Key papers and texts
- Born, M., & Fock, V. (1928). Beweis des Adiabatensatzes. *Zeitschrift für Physik*, 51, 165. https://doi.org/10.1007/BF01343193
- Landau, L. (1932). *Phys. Z. Sowjetunion*, 2, 46; Zener, C. (1932). Non-adiabatic crossing of energy levels. *Proc. R. Soc. A*, 137, 696.
- Purcell, E. M. (1946). Spontaneous emission probabilities at radio frequencies. *Physical Review*, 69, 681.
- Farhi, E., et al. (2001). A quantum adiabatic evolution algorithm applied to random instances of an NP-complete problem. *Science*, 292, 472. https://doi.org/10.1126/science.1057726
- Albash, T., & Lidar, D. A. (2018). Adiabatic quantum computation. *Rev. Mod. Phys.*, 90, 015002. https://doi.org/10.1103/RevModPhys.90.015002
- Rønnow, T. F., et al. (2014). Defining and detecting quantum speedup. *Science*, 345, 420. https://doi.org/10.1126/science.1252319

## In this repo
The dispersive-readout formula belongs in `02_qubit_modalities/01`; the Purcell factor enters `qll/hardware/nv_node.py` as the cavity enhancement of $\eta_{\rm ZPL}$.

## Exercises
1. Derive $\chi=g^2/\Delta$ from the Jaynes–Cummings Hamiltonian in the dispersive limit.
2. For a spin qubit swept through an avoided crossing with $\Delta/h=10$ MHz at $v/h=10^{14}$ Hz/s, compute $P_{\rm LZ}$; is the gate adiabatic?
