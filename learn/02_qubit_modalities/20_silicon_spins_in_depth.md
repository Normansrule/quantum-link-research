# Silicon Spins in Depth

## Valley physics
Silicon's conduction band has six equivalent minima (valleys); confinement to a (001) interface leaves two low-lying valleys split by 50–300 µeV depending on interface roughness and electric field. A small valley splitting puts a valley state near the spin excited state, opening relaxation hot spots and spoiling the two-level approximation; controlling it is the central materials problem of silicon quantum dots [zwanenburg2013] [burkard2023].

## Isotopic purification and coherence
Natural silicon is 4.7 % ²⁹Si, whose nuclear spins dephase an electron in microseconds; isotopically purified ²⁸Si (800 ppm or 50 ppm ²⁹Si) extends T₂* to hundreds of microseconds and Hahn-echo T₂ to milliseconds [veldhorst2014]. The same purification is why silicon appears with the longest coherence among semiconductor qubits in the modality table.

## Control and readout
Single-qubit gates by electron-spin resonance (a microwave antenna) or electric-dipole spin resonance (a micromagnet gradient plus gate voltage modulation, faster and local); two-qubit gates by exchange, tuned by a barrier gate, with fidelities above 99 % [xue2022] [noiri2022]. Readout by spin-to-charge conversion: Elzerman (energy-selective tunnelling to a reservoir) or Pauli spin blockade (singlet–triplet), sensed by a charge sensor or by gate-based radio-frequency reflectometry, which needs no sensor dot and scales to arrays [vigneau2023].

## Hot operation
Because the qubits are electron spins in a few-nanometre dot, they tolerate 1–4 K operation with only modest coherence loss [petit2020] [yang2020hot]; that is the temperature at which cryogenic CMOS control can live next to the qubits, which is the platform's scaling argument.

## Key papers
- Zwanenburg, F. A., et al. (2013). Silicon quantum electronics. *Reviews of Modern Physics*, 85, 961. https://doi.org/10.1103/RevModPhys.85.961
- Veldhorst, M., et al. (2014). An addressable quantum dot qubit with fault-tolerant control-fidelity. *Nature Nanotechnology*, 9, 981. https://doi.org/10.1038/nnano.2014.216
- Noiri, A., et al. (2022). Fast universal quantum gate above the fault-tolerance threshold in silicon. *Nature*, 601, 338. https://doi.org/10.1038/s41586-021-04182-y
- Petit, L., et al. (2020). Universal quantum logic in hot silicon qubits. *Nature*, 580, 355. https://doi.org/10.1038/s41586-020-2170-7
- Vigneau, F., et al. (2023). Probing quantum devices with radio-frequency reflectometry. *Applied Physics Reviews*, 10, 021305. https://doi.org/10.1063/5.0088229

## In this repo
`learn/02/02`; the modality table; no optical interface, so silicon appears in this thesis as a processor candidate, not a node.
