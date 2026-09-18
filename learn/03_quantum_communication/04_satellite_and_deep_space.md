# Satellite and deep-space quantum links

## Definitions
- **Why space**: diffraction loss is $\propto1/L^2$ versus exponential in fiber; a 1200 km satellite link loses ~65–80 dB where fiber would lose ~240 dB.
- **Link budget**: $\eta=\eta_{\rm src}\eta_{\rm geo}\eta_{\rm atm}\eta_{\rm point}\eta_{\rm opt}\eta_{\rm det}$, with background counts from sky radiance (`qll/channels/thermal_background.py`) setting the QBER floor.
- **Acquisition, pointing, and tracking (APT)**: beacon lasers, coarse gimbals (~100 µrad), fine steering mirrors (~1 µrad).
- **Trusted-node vs untrusted-node**: Micius 2017–2018 relayed keys as a trusted node; the 2020 entanglement-based QKD needed no trust in the satellite.
- **Deep space**: NASA's Deep Space Quantum Link (DSQL) concept for lunar-distance and beyond quantum optical experiments; the Deep Space Optical Communications (DSOC) demonstration on Psyche (2023–2024) showed classical optical links at hundreds of Mbit/s from > 30 million km, which anchors the *classical* half of the Earth–Mars CONOPS. **TODO: add DSOC citation.**

## Equations
$$\theta=\frac{\lambda}{\pi w_0},\qquad \eta_{\rm geo}=1-e^{-2r_{\rm rx}^2/w(L)^2}\approx\frac{2r_{\rm rx}^2}{(\theta L)^2},\qquad \eta_{\rm point}=\frac{w^2}{w^2+4\sigma_p^2L^2},\qquad Q_{\rm bg}\approx\frac{N\tau}{2(R\eta+N\tau)}$$
At Mars opposition with $w_0=0.15$ m, $\lambda=810$ nm, $D_{\rm rx}=1$ m: spot radius ~100 km, $\eta_{\rm geo}\sim10^{-11}$; with a 10 m receiver and 1550 nm, still $\sim10^{-9}$. Pair sources at 10⁷–10⁸ pairs/s give at best ~1 detected pair per minute to hour: the link is possible in principle and starved in practice, which is why relays and memories are the only route.

## Visual
![loss](../../docs/figures/link_loss_explorer.svg)

## Landmarks
Micius: entanglement over 1200 km (2017), teleportation uplink 1400 km (2017), satellite-to-ground QKD (2017), intercontinental relay (2018), entanglement-based QKD without trust (2020). Jinan-1 microsatellite: real-time QKD with 100 kg portable ground stations, 12,900 km China–South Africa relay (2025). Europe: Eagle-1 (EuroQCI) planned 2026. Canada: QEYSSat.

## Key papers
- Bourgoin, J.-P., et al. (2013). A comprehensive design and performance analysis of low Earth orbit satellite quantum communication. *New J. Phys.*, 15, 023006.
- Yin, J., et al. (2017). *Science*, 356, 1140. Ren, J.-G., et al. (2017). *Nature*, 549, 70. Liao, S.-K., et al. (2017). *Nature*, 549, 43. Liao, S.-K., et al. (2018). *Physical Review Letters*, 120, 030501.
- Yin, J., et al. (2020). Entanglement-based secure quantum cryptography over 1,120 kilometres. *Nature*, 582, 501. https://doi.org/10.1038/s41586-020-2401-y
- Bedington, R., Arrazola, J. M., & Ling, A. (2017). *npj Quantum Inf.*, 3, 30. https://doi.org/10.1038/s41534-017-0031-5
- Sidhu, J. S., et al. (2021). Advances in space quantum communications. *IET Quantum Commun.*, 2, 182. https://doi.org/10.1049/qtc2.12015
- Khatri, S., et al. (2021). Spooky action at a global distance: analysis of space-based entanglement distribution for the quantum internet. *npj Quantum Inf.*, 7, 4.
- Li, Y., et al. (2025). Microsatellite-based real-time quantum key distribution. *Nature*, 640, 47. https://doi.org/10.1038/s41586-025-08739-z
- Mohageg, M., et al. (2022). The deep space quantum link. *EPJ Quantum Technol.*, 9, 25. https://doi.org/10.1140/epjqt/s40507-022-00143-0 ; (2025) update https://doi.org/10.1140/epjqt/s40507-025-00370-1
- Gündoğan, M., et al. (2024). Time-delayed single satellite quantum repeater node for global quantum communications. *Optica Quantum*, 2, 140.

## In this repo
Done: `fiber_loss.py`, `free_space_diffraction.py`, `deep_space_geometry.py`, `thermal_background.py`. Phase 3: `atmosphere.py`, `pointing_jitter.py`, `link_budget.py`. Phase 5: `qll/space/`.

## Exercises
1. Reproduce the Micius 1200 km loss (65–80 dB) from the formulas with plausible $w_0$, $D_{\rm rx}$, $\sigma_p$.
2. Find the receiver diameter at which the Earth–Mars pair rate reaches one per second for a $10^8$ pairs/s source at opposition. Comment on whether that telescope exists.
