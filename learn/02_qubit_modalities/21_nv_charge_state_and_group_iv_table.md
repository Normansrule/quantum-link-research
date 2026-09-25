# NV Charge State and the Group-IV Centres

## The NV⁻/NV⁰ problem
The nitrogen-vacancy centre is a qubit only in its negative charge state NV⁻ (spin-1, zero-field splitting 2.87 GHz). Optical excitation, especially the resonant red excitation used for single-shot readout and entanglement, ionizes it to NV⁰ (a spin-½ centre with a 575 nm zero-phonon line and no useful spin readout) at a rate that grows with laser power; green light re-pumps NV⁰ → NV⁻ [aslam2013]. Every NV network experiment therefore includes a charge-state check (a resonant read to verify NV⁻) and a green re-pump in its duty cycle, which costs time and is one reason herald rates are 10–100 Hz rather than kHz [hensen2015] [pompili2021]. Surface termination and Fermi-level engineering (the diamond's nitrogen doping) shift the stable charge state; shallow NVs near surfaces suffer most.

## The group-IV alternatives
Silicon-, germanium-, tin-, and lead-vacancy centres are inversion-symmetric, so their optical transitions have no first-order Stark shift: spectral diffusion is small and photons from different emitters interfere without fine tuning, the property NV lacks (its 3 % zero-phonon fraction and 100 MHz-class spectral diffusion). The price is a small ground-state orbital splitting that demands low temperatures for spin coherence:

| Centre | Zero-phonon line | ZPL fraction | Ground orbital splitting | T for ms spin coherence | Status |
|---|---|---|---|---|---|
| NV⁻ | 637 nm | 3 % | — (spin-1, D = 2.87 GHz) | room temperature (spin), 4 K (network) | strongest network record |
| SiV⁻ | 737 nm | 70 % | 50 GHz | ~100 mK (strain raises it) | cavity nodes, 35 km link [knaut2024] |
| GeV⁻ | 602 nm | 60 % | 150 GHz | ~1 K | emerging |
| SnV⁻ | 619 nm | 60 % | 850 GHz | 1–4 K | spin–photon entanglement 2024 |
| PbV⁻ | ~520 nm | — | ~4 THz | 4 K+ | early |

Heavier atoms raise the orbital splitting (a spin-orbit effect), which suppresses phonon-driven dephasing at higher temperatures; SnV at 1–4 K is the compromise many groups pursue [bradac2019] [rosenthal2024].

## Key papers
- Aslam, N., Waldherr, G., Neumann, P., Jelezko, F., & Wrachtrup, J. (2013). Photo-induced ionization dynamics of the nitrogen vacancy defect in diamond investigated by single-shot charge state detection. *New Journal of Physics*, 15, 013064. https://doi.org/10.1088/1367-2630/15/1/013064
- Bradac, C., Gao, W., Forneris, J., Trusheim, M. E., & Aharonovich, I. (2019). Quantum nanophotonics with group IV defects in diamond. *Nature Communications*, 10, 5625. https://doi.org/10.1038/s41467-019-13332-w
- Rosenthal, E. I., et al. (2024). Single-shot readout and weak measurement of a tin-vacancy qubit in diamond. *Physical Review X*, 14, 041008. https://doi.org/10.1103/PhysRevX.14.041008
- Knaut, C. M., et al. (2024). *Nature*, 629, 573. https://doi.org/10.1038/s41586-024-07252-z

## In this repo
`learn/02/03`; `qll/hardware/nv_node.py` (charge-state overhead can be folded into `attempt_rate_hz`); P01 (the ODMR contrast is an NV⁻ signal; NV⁰ dilutes it).
