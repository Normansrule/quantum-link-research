# Photonic teleportation (Bouwmeester et al. 1997)

**Original.** A polarization qubit was teleported using an SPDC Bell pair and a linear-optics Bell measurement identifying $\lvert\Psi^-\rangle$ (25% of cases); fidelity ~0.80 in the post-selected events.

**Physics.** `03_quantum_communication/02`; the two classical bits here are the "which detectors clicked" record; the linear-optics BSM identifies at most two of four Bell states.

**Simple recreation.** Hardware: a three-photon experiment needs two pair sources (or one pulsed source and a heralded input), four detectors, and femtosecond timing; a semester project at the graduate level, not a $5k bench. Software: Qiskit Aer teleportation circuit with a linear-optics BSM modeled as 50% success (Phase 2 `bell_measurement.py`), then Perceval for the actual photonic circuit.

**What went wrong historically.** The 1997 result was criticized as "post-selected" (the output photon existed only when the BSM succeeded, and vacuum events were discarded); unconditional teleportation came with Furusawa (1998, CV) and later matter qubits.

**Repo hook.** `qll/circuits/teleportation.py` with `BellMeasurement(kind="linear_optics")`; REQ-CIR-001, REQ-CIR-002.

- Bouwmeester, D., et al. (1997). *Nature*, 390, 575. https://doi.org/10.1038/37539
- Braunstein, S. L., & Kimble, H. J. (1998). A posteriori teleportation. *Nature*, 394, 840. (The post-selection critique.)
