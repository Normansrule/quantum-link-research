# E3 — Relay-constellation scheduling validated on Jinan-1 pass data

**Gap.** Jinan-1 published per-pass key yields for 20 passes (Zenodo 10.5281/zenodo.14732295). No study feeds measured per-pass statistics into a scheduler for an Earth–Mars relay with solar-conjunction outages and the actual Earth–Mars range from an ephemeris.

**Cheapest version.** Software only: `qll/network/relay_constellation.py` with the Jinan-1 empirical distribution per pass, JPL Horizons ranges (`qll/space/ephemeris.py`), conjunction windows (Sun–Earth–Mars angle < 3°), and SeQUeNCe for the discrete-event timeline. Output: key or entanglement availability versus number of relays and their placement (Earth orbit, Sun–Earth L1/L2, Mars orbit).

**Verifies.** REQ-NET-001 (chain beats direct beyond crossover) at planetary scale; feeds trade study "relay placement".

**Failure modes.** Over-fitting to one satellite's statistics; ignoring pointing acquisition time per pass; assuming the relay memory outlives the inter-pass gap.

**Key references.** Li, Y., et al. (2025). *Nature*, 640, 47. Polnik, M., et al. (2020). Scheduling of space to ground quantum key distribution. *EPJ Quantum Technol.*, 7, 3. Khatri, S., et al. (2021). *npj Quantum Inf.*, 7, 4. Wu, X., et al. (2021). SeQUeNCe. *Quantum Sci. Technol.*, 6, 045027.
