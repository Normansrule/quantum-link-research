# E13 — Frequency-multiplexed heralding on the SPDC bench

**Gap.** S08 computes that the Mars link needs a multiplexing factor of ~2 × 10³; a teaching bench demonstrates none.

**Question.** How many spectral channels can a broadband SPDC source plus fibre Bragg gratings (or a cheap wavelength-division multiplexer) separate on the P03 bench, and does the heralded rate scale linearly with the number of channels while HOM visibility per channel holds?

**Cheap version (bench).** Type-II or broadband type-I SPDC at 1550 nm (or 810 nm with a grating spectrometer); a 4- or 8-channel dense-WDM demultiplexer (~$300–1 000 used); detectors on two channels at a time; herald rate and HOM visibility per channel.

**Research version.** Spectral multiplexing into an AFC memory with feed-forward frequency shifting [sinclair2014].

**Verifies.** The linear-in-M assumption of S08 at M = 4–8.

**References.** Sinclair, N., et al. (2014). *Physical Review Letters*, 113, 053603. https://doi.org/10.1103/PhysRevLett.113.053603 Puigibert, M. G., et al. (2020). Entanglement and nonlocality between disparate solid-state quantum memories mediated by photons. *Physical Review Research*, 2, 013039. https://doi.org/10.1103/PhysRevResearch.2.013039
