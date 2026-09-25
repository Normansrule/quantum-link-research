# Fluxonium and Dispersive Readout

## Fluxonium
$H=4E_Cn^2-E_J\cos\varphi+\tfrac{E_L}{2}(\varphi-\varphi_{\rm ext})^2$ with a large inductance ($E_L\ll E_J$) shunting the junction [manucharyan2009]. At half flux quantum the two lowest states sit in the two wells of a double-well potential: the qubit frequency falls to hundreds of MHz, the matrix element for charge noise is small, and $T_1$ of a millisecond and coherence-limited gates above 99.99 % have been shown [somoroff2023]. The price is a low frequency (the thermal occupation at 15 mK is no longer negligible: the qubit must be actively reset) and slower gates. `qll/hardware/superconducting.py` diagonalises the Hamiltonian in the phase basis; with $E_C=1,E_J=4,E_L=1$ GHz the model gives $f_{01}=0.58$ GHz at half flux and 5.4 GHz at zero flux, the characteristic ten-fold drop.

## Dispersive readout
A transmon coupled with $g$ to a resonator detuned by $\Delta$ shifts its frequency by $\chi=\dfrac{g^2}{\Delta}\dfrac{\alpha}{\Delta+\alpha}$ [blais2004] [blais2021]; the qubit state is read by the phase of a probe tone. The signal-to-noise ratio grows as $\sqrt{n\kappa\tau}$ (photons, resonator linewidth, time) and is degraded by the amplifier chain's added noise: a Josephson parametric amplifier (JPA) or traveling-wave parametric amplifier (TWPA) near the quantum limit ($n_{\rm add}\approx0.5$) versus a HEMT alone ($n_{\rm add}\sim20$) [macklin2015]. Because the qubit decays during the measurement, there is an optimal $\tau$: in the model, $\chi/2\pi=1.7$ MHz, $\kappa=2\chi$, five photons, and a quantum-limited chain give 98 % assignment fidelity in 1.6 µs against $T_1=50$ µs; the HEMT-only chain does markedly worse. This is the readout budget every processor node carries, and it is why every dilution refrigerator with a quantum processor has a parametric amplifier at its 10 mK plate and an isolator chain behind it (`learn/02/09`).

## Key papers
- Manucharyan, V. E., Koch, J., Glazman, L. I., & Devoret, M. H. (2009). Fluxonium: single Cooper-pair circuit free of charge offsets. *Science*, 326, 113. https://doi.org/10.1126/science.1175552
- Somoroff, A., et al. (2023). Millisecond coherence in a superconducting qubit. *Physical Review Letters*, 130, 267001. https://doi.org/10.1103/PhysRevLett.130.267001
- Blais, A., Huang, R.-S., Wallraff, A., Girvin, S. M., & Schoelkopf, R. J. (2004). Cavity quantum electrodynamics for superconducting electrical circuits. *Physical Review A*, 69, 062320. https://doi.org/10.1103/PhysRevA.69.062320
- Blais, A., Grimsmo, A. L., Girvin, S. M., & Wallraff, A. (2021). *Reviews of Modern Physics*, 93, 025005. https://doi.org/10.1103/RevModPhys.93.025005
- Macklin, C., et al. (2015). *Science*, 350, 307. https://doi.org/10.1126/science.aaa8525

## In this repo
`qll/hardware/superconducting.py` (`fluxonium_spectrum`, `transmon_spectrum`, `dispersive_shift`, `ReadoutBudget`); `learn/02/01`, `02/09`.
