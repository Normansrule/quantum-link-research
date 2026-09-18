# T05 — Networks of entangled clocks, and relativity meets entanglement

**The idea.** (a) Entangling the atoms of clocks at different sites yields a network clock whose stability beats the sum of its parts (Heisenberg scaling in the number of clocks) and is secure against tampering. (b) At interplanetary baselines, gravitational redshift, Doppler shifts, and Shapiro delay affect photon frequencies and arrival times by parts in $10^{-8}$–$10^{-10}$, large enough that a quantum link *must* model them, and large enough to test predictions about entanglement in curved spacetime: this is the scientific program of the Deep Space Quantum Link.

**Equations.** Gravitational redshift $\Delta\nu/\nu=\Delta\Phi/c^2$ ($\approx7\times10^{-10}$ Earth surface to infinity); a photon's time-bin qubit acquires relative phases from path-dependent proper time; proposed tests look for deviations in HOM visibility or Bell correlations between Earth and orbit.

**Status.** Clock networks: proposal (Kómár et al. 2014), lab entanglement of clock qubits; DSQL: mission concept with lunar-gateway phase, updated 2025; Micius did an "entanglement and gravity" test with null result at the expected precision.

**What it would change.** Timing synchronization to nanoseconds across Earth–Mars becomes a relativistic problem the link solves as a by-product; the link becomes a physics instrument, which helps funding and TRL progression.

**Key papers.** Kómár, P., et al. (2014). A quantum network of clocks. *Nature Physics*, 10, 582. https://doi.org/10.1038/nphys3000 Rideout, D., et al. (2012). Fundamental quantum optics experiments conceivable with satellites. *Class. Quantum Grav.*, 29, 224011. Mohageg, M., et al. (2022). *EPJ Quantum Technol.*, 9, 25. https://doi.org/10.1140/epjqt/s40507-022-00143-0 Xu, P., et al. (2019). Satellite testing of a gravitationally induced quantum decoherence model. *Science*, 366, 132. Nichol, B. C., et al. (2022). An elementary quantum network of entangled optical atomic clocks. *Nature*, 609, 689.

**Repo hook.** Phase 5 `qll/space/ephemeris.py` should carry relativistic time corrections; `light_time_delay.py` gains a Shapiro-delay term.
