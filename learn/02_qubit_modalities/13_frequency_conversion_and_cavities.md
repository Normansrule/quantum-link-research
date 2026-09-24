# Frequency Conversion and Nanophotonic Cavities

Two devices decide whether a solid-state emitter can join a telecom network: a converter that moves its photon to 1550 nm, and a cavity that makes it emit into the right mode in the first place.

## Quantum frequency conversion
Difference-frequency generation in periodically poled lithium niobate (PPLN): $1/\lambda_t=1/\lambda_s-1/\lambda_p$, with NV 637 nm + 1064 nm pump → 1588 nm [dreau2018]. Internal efficiency $\eta=\sin^2(\sqrt{\eta_{\rm nor}P}\,L)$ reaches 100 % at $P_{\max}=\pi^2/(4\eta_{\rm nor}L^2)$, about 150 mW for a 4 cm waveguide of $\eta_{\rm nor}\approx1$ W⁻¹cm⁻². The pump generates noise photons (Raman, spontaneous down-conversion) linearly in $P$, so the signal-to-noise ratio falls monotonically with pump power and the operating point is a trade between converted rate and the QBER floor, computed by `Converter.qber_floor` with the same background law as the link budget. External efficiencies of 30–60 % are typical after coupling and filtering [vanleent2020]; entanglement between an NV and a telecom photon through such a converter was shown in 2019 [tchebotareva2019].

## Purcell enhancement
An emitter in a cavity of quality factor $Q$ and mode volume $V$ radiates faster by $F_P=\frac{3}{4\pi^2}\left(\frac{\lambda}{n}\right)^3\frac{Q}{V}$ [purcell1946]. Diamond nanophotonic cavities with $Q\sim10^4$ and $V\sim(\lambda/n)^3$ give $F_P\sim700$, which turns the 3 % zero-phonon fraction of a silicon-vacancy center into a cooperativity above 10: most photons now leave coherently into one mode [bhaskar2020] [knaut2024]. This is the single largest lever on the herald rate in `qll/hardware/nv_node.py` (`purcell_factor`, `cooperativity`), and why the cavity node in S07 out-rates the bare emitter thirtyfold.

## Key papers
- Zaske, S., et al. (2012). Visible-to-telecom quantum frequency conversion of light from a single quantum emitter. *Physical Review Letters*, 109, 147404. https://doi.org/10.1103/PhysRevLett.109.147404
- Dréau, A., Tchebotareva, A., El Mahdaoui, A., Bonato, C., & Hanson, R. (2018). Quantum frequency conversion of single photons from a nitrogen-vacancy center in diamond to telecommunication wavelengths. *Physical Review Applied*, 9, 064031. https://doi.org/10.1103/PhysRevApplied.9.064031
- Tchebotareva, A., et al. (2019). Entanglement between a diamond spin qubit and a photonic time-bin qubit at telecom wavelength. *Physical Review Letters*, 123, 063601. https://doi.org/10.1103/PhysRevLett.123.063601
- van Leent, T., et al. (2020). Long-distance distribution of atom-photon entanglement at telecom wavelength. *Physical Review Letters*, 124, 010510. https://doi.org/10.1103/PhysRevLett.124.010510
- Purcell, E. M. (1946). Spontaneous emission probabilities at radio frequencies. *Physical Review*, 69, 681.
- Bhaskar, M. K., et al. (2020). Experimental demonstration of memory-enhanced quantum communication. *Nature*, 580, 60. https://doi.org/10.1038/s41586-020-2103-5

## In this repo
`qll/channels/frequency_conversion.py`, `qll/hardware/nv_node.py`; E7 and S07 (why converting the *microwave* photon is a different and harder problem than converting the *optical* one).
