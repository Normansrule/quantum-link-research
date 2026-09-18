# The Micius link budget, line by line

Reproducing a published satellite budget is the Phase 3 must-pass target and the S1 stage of flagship F2. Numbers below are the 2017 entanglement-distribution experiment (Yin et al. 2017) as reported; the goal of `qll/channels/link_budget.py` is to land within ±3 dB.

| Line | Quantity | Value | Formula / source |
|---|---|---|---|
| 1 | Orbit altitude | ~500 km; slant range 500–2000 km during a pass | geometry |
| 2 | Wavelength | 810 nm (SPDC pairs, 5.9 MHz pair rate on board) | Yin 2017 |
| 3 | Transmitter aperture | 300 mm (two telescopes, one per ground station) | Yin 2017 |
| 4 | Divergence | ~10 µrad (near-diffraction-limited after beam expansion) | $\theta\approx\lambda/\pi w_0$ with $w_0\sim$ 3 cm effective |
| 5 | Spot at 1200 km | ~12 m radius | $w=\theta L$ |
| 6 | Receiver aperture | 1.2 m (Delingha) and 1.8 m (Lijiang) | Yin 2017 |
| 7 | Geometric loss | $(D_{\rm rx}/2w)^2\approx(1.2/24)^2\approx2.5\times10^{-3}$ → −26 dB | `free_space_diffraction.py` |
| 8 | Pointing loss | fine tracking ~1 µrad; a few dB | `pointing_jitter.py` |
| 9 | Atmosphere | 3–8 dB at elevation; night operation | `atmosphere.py` |
| 10 | Optics + detector | ~−10 dB (coupling, filters, SPAD ~50 %) | |
| 11 | Total per downlink | 64–82 dB reported over a pass (≈ $10^{-6.4}$ to $10^{-8.2}$) | Yin 2017 |
| 12 | Two-photon coincidence | product of two downlinks: ~$10^{-13}$–$10^{-16}$ | |
| 13 | Coincidences per pass | ~1 per second at best; 134 in 250 s reported for the 1203 km run | Yin 2017; fidelity 0.87 |
| 14 | Compare: fiber | $10^{-24}$ over 1200 km at 0.2 dB/km: 17 orders of magnitude worse | `fiber_loss.py` |

Reading the table: lines 7–10 multiply to the reported line 11 only if pointing and atmosphere are taken at their favorable end; the model must therefore carry *distributions*, not single numbers, and report the pass-averaged pair rate. Jinan-1 (Li et al. 2025) improves the transmitter (625 MHz decoy source at 850 nm, ~1 µrad fine pointing) and shrinks the receiver to a 280 mm portable station; its per-pass key of up to ~1 Mbit is the second budget the code must reproduce.

## Key references
Yin, J., et al. (2017). *Science*, 356, 1140. Lu, C.-Y., et al. (2022). Micius quantum experiments in space. *Rev. Mod. Phys.*, 94, 035001. Li, Y., et al. (2025). *Nature*, 640, 47. https://doi.org/10.1038/s41586-025-08739-z Bourgoin et al. (2013). *New J. Phys.*, 15, 023006.

## In this repo
Phase 3 `link_budget.py` must-pass test; flagship [F2](../../experiments/flagship/F2_earth_to_satellite.md) S1.
