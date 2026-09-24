# AFC Memories and Rare-Earth Crystals

## Definitions
- **Inhomogeneous broadening**: each rare-earth ion in a crystal sits in a slightly different environment, so the ensemble absorbs over GHz while each ion's line is kHz wide. Spectral hole burning carves this into a structure.
- **Atomic frequency comb (AFC)**: absorption shaped into teeth of spacing $\Delta$ and finesse $F=\Delta/\gamma$; an absorbed photon rephases and re-emits after $1/\Delta$ [afzelius2009].
- **Spin-wave storage**: a control pulse transfers the optical excitation to a spin state and back, making the release on-demand and extending the storage from the echo time to the spin coherence time.
- **ZEFOZ**: zero first-order Zeeman points in the magnetic-field space where the spin transition frequency is stationary, suppressing sensitivity to field noise; with dynamical decoupling this gave 6 h in Eu:YSO [zhong2015] and 13.1 h in 2025 [wang2025memory].

## Efficiency
Forward recall: $\eta=(d/F)^2e^{-d/F}e^{-7/F^2}e^{-d_0}$, at most 54 % at $d/F=2$; backward recall or a cavity lifts the ceiling to 100 %. Demonstrated on-demand efficiencies at long storage times are far lower: the same crystal that holds coherence for hours retrieves a few percent, which is the trade the memory table in `qll/network/memory_decoherence.py` carries and the reason the Mars-capable memories in the capability matrix all sit at < 5 %.

## Multiplexing
An AFC stores ~$F/2$ temporal modes at once, and the comb can be repeated at many frequencies: 26 spectral modes with feed-forward frequency shifting were demonstrated in 2014 [sinclair2014]. This is where the multiplexing factor of S08 (≈ 2 × 10³ for Mars with 1 m → 10 m optics) would come from; 10³ is within reach of temporal × spectral multiplexing, 10⁶ is not yet.

## Why rare earths
4f electrons are shielded by outer shells, so optical transitions are narrow (kHz) and nuclear spins are quiet; the price is weak oscillator strength (long crystals or cavities), cryogenic operation (2–4 K, ~1 K for the best coherence), and slow gates. The platform is a memory, not a processor: the heterogeneous node design of E8 pairs it with a color center or ion for logic.

## Key papers
- Afzelius, M., Simon, C., de Riedmatten, H., & Gisin, N. (2009). Multimode quantum memory based on atomic frequency combs. *Physical Review A*, 79, 052329. https://doi.org/10.1103/PhysRevA.79.052329
- Afzelius, M., & Simon, C. (2010). Impedance-matched cavity quantum memory. *Physical Review A*, 82, 022310. https://doi.org/10.1103/PhysRevA.82.022310
- Sinclair, N., et al. (2014). *Physical Review Letters*, 113, 053603. https://doi.org/10.1103/PhysRevLett.113.053603
- Zhong, M., et al. (2015). Optically addressable nuclear spins in a solid with a six-hour coherence time. *Nature*, 517, 177. https://doi.org/10.1038/nature14025
- Lago-Rivera, D., Grandi, S., Rakonjac, J. V., Seri, A., & de Riedmatten, H. (2021). Telecom-heralded entanglement between multimode solid-state quantum memories. *Nature*, 594, 37. https://doi.org/10.1038/s41586-021-03481-8

## In this repo
`qll/network/afc_memory.py` (efficiency laws, mode count, `AfcMemory`); memory table; S08; E8.
