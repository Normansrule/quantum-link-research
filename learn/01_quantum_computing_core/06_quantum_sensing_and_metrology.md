# Quantum sensing and metrology

## Definitions
- **Standard quantum limit (SQL)**: with $N$ independent probes the uncertainty scales as $1/\sqrt N$; with entangled probes (GHZ, squeezed) the **Heisenberg limit** $1/N$ is reachable in principle.
- **Ramsey magnetometry**: a spin precesses at $\gamma B$ for time $\tau$; phase $\phi=\gamma B\tau$; sensitivity $\eta_B\approx\frac{1}{\gamma C\sqrt{\tau\,R}}$ per $\sqrt{\rm Hz}$, with contrast $C$ and readout rate $R$. This is the NV magnetometer on the $100 bench.
- **Dynamical-decoupling sensing**: a CPMG sequence acts as a lock-in filter at $f=1/(2\tau)$; detects AC fields and single nuclear spins (nanoscale NMR).
- **Atomic clocks**: the most precise instruments ever built ($10^{-18}$ fractional); optical lattice and single-ion clocks; the Deep Space Atomic Clock (2019) is a flown trapped-ion device, relevant to the TRL of space ion hardware.
- **Squeezed light in interferometers**: LIGO uses 3–6 dB of squeezing to beat shot noise.
- **Quantum illumination and quantum radar**: entangled probe–idler pairs give a 6 dB error-exponent advantage in principle; practical advantage remains unproven at microwave frequencies.

## Equations
$$\delta\phi_{\rm SQL}=\frac{1}{\sqrt N},\qquad \delta\phi_{\rm HL}=\frac1N,\qquad \eta_B^{\rm NV}\approx\frac{\hbar}{g\mu_B}\frac{1}{C\sqrt{R\,T_2^*}}\ \Big(\sim\text{nT–µT}/\sqrt{\rm Hz}\ \text{for ensembles}\Big)$$
Quantum Fisher information $F_Q$ and the Cramér–Rao bound $\delta\theta\ge1/\sqrt{\nu F_Q}$ for $\nu$ repetitions.

## Why it is in a communication repo
Sensing is the first commercial payoff of the same hardware (NV magnetometers, atomic clocks, gravimeters) and the cheapest way to *learn* the hardware: every NV network node was a magnetometer first. Clock synchronization to nanoseconds between Earth and a relay is itself a metrology problem for the link (`03_quantum_communication/04`).

## Key papers
- Degen, C. L., Reinhard, F., & Cappellaro, P. (2017). Quantum sensing. *Rev. Mod. Phys.*, 89, 035002. https://doi.org/10.1103/RevModPhys.89.035002
- Giovannetti, V., Lloyd, S., & Maccone, L. (2011). Advances in quantum metrology. *Nature Photonics*, 5, 222. https://doi.org/10.1038/nphoton.2011.35
- Taylor, J. M., et al. (2008). High-sensitivity diamond magnetometer with nanoscale resolution. *Nature Physics*, 4, 810. https://doi.org/10.1038/nphys1075
- Ludlow, A. D., et al. (2015). Optical atomic clocks. *Rev. Mod. Phys.*, 87, 637. https://doi.org/10.1103/RevModPhys.87.637
- Burt, E. A., et al. (2021). Demonstration of a trapped-ion atomic clock in space. *Nature*, 595, 43. https://doi.org/10.1038/s41586-021-03571-7
- Tse, M., et al. (2019). Quantum-enhanced advanced LIGO detectors in the era of gravitational-wave astronomy. *Physical Review Letters*, 123, 231107.

## In this repo
Proposal E6 (QRNG bases) and E2 (NV $T_1,T_2$ vs $T$) are sensing experiments in disguise; the Uncut Gem build in `experiments/bench/hardware_guide.md` is a magnetometer.

## Exercises
1. For an NV ensemble with $C=0.02$, $R=10^{12}$ photons/s, $T_2^*=1\ \mu$s, compute $\eta_B$.
2. Why does a Hahn-echo sequence make the sensor blind to DC fields but sensitive at $1/2\tau$?
