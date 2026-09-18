# Two-level dynamics: Rabi, Ramsey, and echo

## Definitions
- **Rabi oscillation**: population transfer under a resonant drive; the Rabi frequency $\Omega$ is set by drive amplitude and dipole coupling. A $\pi$ pulse ($\Omega t=\pi$) is an $X$ gate; a $\pi/2$ pulse makes $\lvert+\rangle$.
- **Rotating-wave approximation (RWA)**: drop terms oscillating at $\omega_0+\omega_d$; valid when $\Omega,\lvert\Delta\rvert\ll\omega_0$.
- **Ramsey experiment**: $\pi/2$, free evolution $\tau$, $\pi/2$, measure. Fringe frequency = detuning $\Delta$; envelope decay = $T_2^*$ (includes slow noise).
- **Hahn echo**: insert a $\pi$ pulse at $\tau/2$; slow noise refocuses and the envelope decays with $T_2\ge T_2^*$. CPMG/XY-n sequences with $N$ $\pi$ pulses extend $T_2$ further (`02_qubit_modalities/03_diamond_nv_and_group_iv.md`).

## Equations
In the rotating frame with detuning $\Delta=\omega_0-\omega_d$,
$$H_{\rm RWA}=\frac\hbar2\left(\Delta Z+\Omega X\right),\qquad P_1(t)=\frac{\Omega^2}{\Omega^2+\Delta^2}\sin^2\!\left(\frac{\sqrt{\Omega^2+\Delta^2}}{2}t\right)$$
$$P_1^{\rm Ramsey}(\tau)=\tfrac12\left[1+e^{-\tau/T_2^*}\cos\Delta\tau\right],\qquad A_{\rm echo}(\tau)=e^{-(\tau/T_2)^n}$$
with $n\approx1$ for a fast (Markovian) bath and $n\approx3$ for a slow bath [de Lange et al. 2010].

## Visual
![rabi](../../docs/figures/rabi_ramsey.svg)

## Key papers
- Rabi, I. I. (1937). Space quantization in a gyrating magnetic field. *Physical Review*, 51, 652. https://doi.org/10.1103/PhysRev.51.652
- Ramsey, N. F. (1950). A molecular beam resonance method with separated oscillating fields. *Physical Review*, 78, 695. https://doi.org/10.1103/PhysRev.78.695
- Hahn, E. L. (1950). Spin echoes. *Physical Review*, 80, 580. https://doi.org/10.1103/PhysRev.80.580
- de Lange, G., et al. (2010). Universal dynamical decoupling of a single solid-state spin from a spin bath. *Science*, 330, 60. https://doi.org/10.1126/science.1192739
- Sewani, V. K., et al. (2020). Coherent control of NV⁻ centers in diamond in a quantum teaching lab. *Am. J. Phys.*, 88, 1156. arXiv:2004.02643 (the cheapest way to run all three experiments yourself).

## In this repo
`qll/viz/rabi_ramsey.py`; Phase 2 `noise/phase_damping.py` encodes $1/T_2=1/2T_1+1/T_\varphi$; the NV teaching-lab build is Tier 1 in `docs/hardware_and_experiments_guide.md`.

## Exercises
1. Derive $H_{\rm RWA}$ from $H=\frac{\hbar\omega_0}{2}Z+\hbar\Omega\cos(\omega_d t)X$.
2. From a Ramsey fringe with 0.8 MHz oscillation and 1/e time 3 µs, extract $\Delta$ and $T_2^*$.
