# P03 — Two-crystal SPDC source, Hong–Ou–Mandel, CHSH, and BB84

## Safety
A 405 nm pump at 50–100 mW is class 3B: goggles rated OD 5+ at 405 nm, enclosed beam path, interlock, beam blocks, no reflective jewelry. Single-photon detectors are damaged by room light while biased: cover the bench and use a dark enclosure.

## Parts ([`../bench/hardware_guide.md`](../bench/hardware_guide.md) §2.3)
405 nm laser diode (single-frequency preferred; a broadband multimode diode works with a compensator) · two crossed type-I BBO crystals cut for 405→810 nm · half-wave plate for the pump (45° polarization) · quartz compensator · 810 nm bandpass filters (10 nm, then 3 nm for HOM) · two half-wave plates and two polarizers (or polarizing beam splitters + four detectors) in precision rotation mounts · fiber couplers or free-space irises · two to four single-photon detectors (Excelitas SPCM-AQRH or Hamamatsu C13001) · coincidence counter (PSoC/FPGA design or commercial) · translation stage with 1 µm resolution for HOM · optical breadboard, posts, beam blocks.

## Build and align
1. Mount the pump, expand to ~1 mm, set polarization to 45° with the HWP.
2. Place the crystal pair; find the 810 nm cone (about 3° half-angle) with a CCD camera or by scanning a detector; mark the two diametrically opposite points.
3. Couple both arms into fibers; maximize singles, then coincidences with a 5–10 ns window. Target 1–5 k coincidences/s per 100 k singles.
4. Insert the compensator and adjust for maximal visibility in the diagonal basis (the two-crystal source needs its phase balanced).

## Measure
5. **Polarization correlations**: record coincidences vs analyzer angles; visibility in H/V and in the ±45° basis both > 90%.
6. **CHSH**: settings 0°, 45° (Alice), 22.5°, 67.5° (Bob); 16 coincidence counts; compute $E(a,b)=\frac{N_{++}+N_{--}-N_{+-}-N_{-+}}{N_{\rm total}}$ and $S$. Accidental coincidences $N_{\rm acc}=S_1S_2\tau_w$ must be subtracted or, better, kept small.
7. **HOM**: send both photons to one 50:50 beam splitter; scan the delay stage in 5 µm steps over ±200 µm; record coincidences; fit the dip.
8. **BB84**: Alice's HWP chooses random bases and bits (from the QRNG board for proposal E6); Bob's chooses random bases; sift and compute QBER.

## Analyze
$S$ with statistical error $\sqrt{\sum 1/N}$-style propagation; infer the singlet fraction from $S=2\sqrt2(4f-1)/3$ (`qll/circuits/chsh.py`); HOM visibility → indistinguishability; BB84 QBER → `qll.qkd.key_rate.bb84_rate_per_sifted_bit`.

## Expected numbers
$S=2.3$–$2.7$ at > 5σ in a few minutes; HOM visibility 85–95% with 3 nm filters; QBER 2–5%.

## If it does not work
Low visibility in the diagonal basis only: compensator wrong (temporal walk-off between the two crystals). Low overall coincidences: fiber coupling or a wrong cone angle. $S>2\sqrt2$: accidentals subtraction is wrong or the coincidence window is too wide.

## References
Dehlinger & Mitchell (2002) *Am. J. Phys.* 70, 903 and 898 · Kwiat et al. (1999) *PRA* 60, R773 · Hong, Ou, Mandel (1987) *PRL* 59, 2044 · Beck, M., *Modern Undergraduate Quantum Mechanics Experiments* (Reed College, online).
