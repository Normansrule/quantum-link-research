# Materials and fabrication: where qubits actually come from

| Platform | Substrate / host | Key process steps | Dominant material defect | Foundry status |
|---|---|---|---|---|
| Transmon | high-resistivity Si or sapphire; Al, Nb, Ta films | sputtering/evaporation, photolithography, Dolan-bridge or Manhattan shadow evaporation for junctions, controlled oxidation, airbridges, flip-chip bonding | two-level systems (TLS) in amorphous oxides at interfaces; junction $I_c$ spread (~few %) needs laser annealing | 300 mm pilot lines (IBM, Google in-house; imec, MIT-LL) |
| Si spin | ²⁸Si epilayer or Si/SiGe heterostructure; Al or poly-Si gates | CVD epitaxy, e-beam lithography, ALD dielectrics, multi-layer gate stacks | interface disorder, valley splitting variability, charge noise | 300 mm CMOS lines (Intel Tunnel Falls, imec, CEA-Leti) |
| Diamond NV/SiV | CVD single-crystal diamond, [N] < 5 ppb "electronic grade"; ¹²C enrichment | N or Si implantation, high-temperature anneal (800–1200 °C), plasma etching of nanopillars/cavities, solid-immersion lenses by FIB | strain, surface charge traps, spectral diffusion; implantation damage | Element Six (De Beers), Applied Diamond; small volumes |
| Rare-earth crystals | Y₂SiO₅, Y₂O₃, LiNbO₃ doped with Eu/Er/Pr | Czochralski growth, dopant control at ppm, waveguide fabrication in LiNbO₃ | inhomogeneous broadening, spectral diffusion from host nuclear spins | boutique crystal growers (Scientific Materials) |
| Ion traps | fused silica or sapphire; Au or Nb electrodes | microfabricated surface traps, laser-written 3-D traps, integrated waveguides for delivery | surface contamination → anomalous heating; laser-induced charging | Sandia, Honeywell/Quantinuum, IonQ in-house |
| Photonics | Si₃N₄, thin-film LiNbO₃, SOI; SNSPD (NbN, WSi) | CMOS-compatible waveguide fabs, heterogeneous integration of sources and detectors | propagation loss (dB/m), coupling loss, detector jitter | commercial foundries (GlobalFoundries with PsiQuantum, LioniX, Ligentec) |
| Neutral atoms | none (atoms in vacuum); optics and lasers are the "fab" | SLM/AOD arrays, high-NA objectives, vacuum cells | laser noise, atom loss | commercial optics; no wafer fab |

## Lessons the table teaches
- Every platform's *dominant* error is a materials or surface problem, not a physics-of-the-qubit problem: TLS, interface disorder, surface spins, trap heating, waveguide loss.
- The platforms that scaled fastest (transmons, Si spins, photonics) rode existing semiconductor fabs; diamond and rare-earth crystals lack that supply chain, which is a systems-engineering risk for a network memory and a reason to design for heterogeneous nodes.
- Isotopic purification (²⁸Si, ¹²C) is a recurring trick: remove the nuclear-spin bath and $T_2$ improves by orders of magnitude.

## Key references
- Oliver, W. D., & Welander, P. B. (2013). Materials in superconducting quantum bits. *MRS Bulletin*, 38, 816. https://doi.org/10.1557/mrs.2013.229
- Müller, C., Cole, J. H., & Lisenfeld, J. (2019). Towards understanding two-level-systems in amorphous solids: insights from quantum circuits. *Rep. Prog. Phys.*, 82, 124501. https://doi.org/10.1088/1361-6633/ab3a7e
- Zwerver, A. M. J., et al. (2022). Qubits made by advanced semiconductor manufacturing. *Nature Electronics*, 5, 184. https://doi.org/10.1038/s41928-022-00727-9
- Balasubramanian, G., et al. (2009). Ultralong spin coherence time in isotopically engineered diamond. *Nature Materials*, 8, 383. https://doi.org/10.1038/nmat2420
- Ruf, M., Wan, N. H., Choi, H., Englund, D., & Hanson, R. (2021). Quantum networks based on color centers in diamond. *J. Appl. Phys.*, 130, 070901. https://doi.org/10.1063/5.0056534
- Wang, J., Sciarrino, F., Laing, A., & Thompson, M. G. (2020). Integrated photonic quantum technologies. *Nature Photonics*, 14, 273. https://doi.org/10.1038/s41566-019-0532-1
- Hite, D. A., et al. (2012). 100-fold reduction of electric-field noise in an ion trap cleaned with in situ argon-ion-beam bombardment. *Physical Review Letters*, 109, 103001.
