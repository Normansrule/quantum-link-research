# T09 — Continuous-variable QKD and its satellite variant

**The idea.** Encode key in the quadratures of coherent states (Gaussian modulation), detect with homodyne or heterodyne receivers made from telecom components, and post-process with reverse reconciliation. No single-photon detectors; high rates at short range; security proofs against collective and (with care) general attacks. Satellite CV-QKD would reuse coherent-optical terminals of the DSOC class.

**Equations.** Secret key rate (reverse reconciliation, collective attacks) $K=\beta I_{AB}-\chi_{BE}$ with reconciliation efficiency $\beta\approx0.95$; transmittance $T$ and excess noise $\xi$ set $\chi_{BE}$; the PLOB bound still applies; CV-QKD is competitive below ~100 km of fiber and is more sensitive to excess noise from turbulence in free space.

**Status.** Metropolitan fiber deployments; free-space demos of hundreds of metres to tens of km; satellite feasibility studies and a 2024–2025 downlink demonstration reported (**TODO: verify**).

**What it would change.** If the Earth–Mars terminals are DSOC-class coherent terminals, CV protocols are the natural fit for the *key* function, while single-photon/entanglement functions remain for teleportation; a hybrid CV/DV architecture is a trade for E8.

**Key papers.** Grosshans, F., & Grangier, P. (2002). Continuous variable quantum cryptography using coherent states. *PRL*, 88, 057902. https://doi.org/10.1103/PhysRevLett.88.057902 Weedbrook, C., et al. (2012). Gaussian quantum information. *Rev. Mod. Phys.*, 84, 621. https://doi.org/10.1103/RevModPhys.84.621 Diamanti, E., & Leverrier, A. (2015). Distributing secret keys with quantum continuous variables. *Entropy*, 17, 6072. Pirandola, S., et al. (2020). *Adv. Opt. Photon.*, 12, 1012. Dequal, D., et al. (2021). Feasibility of satellite-to-ground continuous-variable quantum key distribution. *npj Quantum Inf.*, 7, 3.

**Repo hook.** Phase 3 stretch: `qll/qkd/cv_qkd.py` with the Gaussian-modulation rate formula and a turbulence-induced excess-noise model.
