# Cryogenics, vacuum, and the environment (why the thermal model is first-class)

## Temperatures and how to reach them
| Stage | Temperature | Technology | Cooling power | Flown in space? |
|---|---|---|---|---|
| Liquid nitrogen | 77 K | dewar | W–kW | yes |
| Pulse-tube / Gifford–McMahon | 4 K | closed-cycle cryocooler | ~1 W | yes (Planck, JWST-class coolers at 4–6 K) |
| ³He sorption / JT | 0.3–1 K | adsorption or Joule–Thomson | mW | yes (Planck 0.1 K stage via dilution, open-cycle) |
| Dilution refrigerator | 10–20 mK | ³He/⁴He mixing chamber | 10–100 µW at 20 mK | not for optical payloads |
| Adiabatic demagnetization (ADR) | 50–100 mK | paramagnetic salt pill | µW, cyclic | yes (Hitomi/XRISM, ~50 mK) |
| Laser cooling | µK–nK | Doppler, sideband, evaporative | — | yes (Cold Atom Lab on ISS) |

Each modality's temperature requirement (`02_qubit_modalities/README.md`) maps to a row, and the row decides whether a memory node can fly: 4 K (NV, Er/Eu:YSO, ions need no cryostat at all) is routine; 100 mK (SiV cavities, superconducting) is ADR territory with tiny cooling power; 10 mK is Earth-only today. That is risk R-2.

## Why temperature enters every level (the repo's thesis)
$\bar n=1/(e^{\hbar\omega/k_BT}-1)$: at 5 GHz you need $T\ll240$ mK for $\bar n\ll1$; at 200 THz room temperature is already "zero temperature". Beyond occupation, temperature sets phonon-induced $T_1$ (NV: $T_1$ falls from hours at 4 K to ms at 300 K by two-phonon Raman processes), thermal expansion (alignment drift in optics), blackbody radiation on Rydberg atoms, and the noise temperature of every amplifier.

## Vacuum
Ions and atoms need $10^{-11}$ mbar (UHV/XHV): collision-limited trap lifetimes of minutes to hours; cryopumping at 4 K improves it. Superconducting chips sit in vacuum inside the fridge for thermal isolation.

## Shielding and filtering
Magnetic shielding (mu-metal, superconducting cans) for flux-noise-sensitive qubits; infrared filters and "Eccosorb" absorbers stop stray photons that would raise the effective qubit temperature above the fridge temperature (the reason measured residual excitations exceed $\bar n$ predictions); vibration isolation for optical setups.

## Key references
- Pobell, F. (2007). *Matter and Methods at Low Temperatures* (3rd ed.). Springer.
- Krinner, S., et al. (2019). Engineering cryogenic setups for 100-qubit scale superconducting circuit systems. *EPJ Quantum Technol.*, 6, 2. https://doi.org/10.1140/epjqt/s40507-019-0072-0
- Jarmola, A., Acosta, V. M., Jensen, K., Chemerisov, S., & Budker, D. (2012). Temperature- and magnetic-field-dependent longitudinal spin relaxation in nitrogen-vacancy ensembles in diamond. *Physical Review Letters*, 108, 197601. https://doi.org/10.1103/PhysRevLett.108.197601
- Shirron, P. J. (2014). Applications of the magnetocaloric effect in single-stage, multi-stage and continuous adiabatic demagnetization refrigerators. *Cryogenics*, 62, 130.
- Aveline, D. C., et al. (2020). Observation of Bose–Einstein condensates in an Earth-orbiting research lab. *Nature*, 582, 193. https://doi.org/10.1038/s41586-020-2346-1

## In this repo
`qll/circuits/noise/thermal.py`; Phase 5 `qll/space/platform_thermal.py` will encode this table as data; proposal E2 measures the NV $T_1(T)$ curve on the bench.
