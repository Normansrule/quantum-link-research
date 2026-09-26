# E15 — Radiation screening of the bench's diamond, crystal, and detectors

**Gap.** Learn 02/14 states that diamond and nonlinear crystals are radiation hard and detectors are the weak point; no numbers exist for the specific parts this repository uses.

**Question.** After a total ionizing dose representative of a two-year Mars transit (order 10–50 krad(Si) behind modest shielding; TODO: confirm the dose model), do the ODMR contrast of the P01 microdiamond, the SPDC pair rate of the P03 crystal, and the dark count of a silicon SPAD change measurably?

**Cheap version (bench + facility).** Measure each part before and after exposure at a university gamma (⁶⁰Co) source; the P01 and P03 pipelines already produce the numbers to compare (`qll/analysis/odmr_fit.py`, coincidence rates).

**Research version.** Proton irradiation for displacement damage; in-situ annealing of SPADs as on Micius.

**Verifies.** A new requirement on radiation tolerance of the node's optical components.

**References.** Tan, Y. C., Chandrasekara, R., Cheng, C., & Ling, A. (2013). *Optics Express*, 21, 16946. https://doi.org/10.1364/OE.21.016946 Yang, M., et al. (2019). Spaceborne, low-noise, single-photon detection for satellite-based quantum communications. *Optics Express*, 27, 36114.
