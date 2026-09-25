# Lessons 04 — Reproducibility Checklist for Quantum Experiments

What must be recorded for a measurement in this repository to count, drawn from the practices of the groups whose results have held up.

## Before the run
- [ ] Protocol file named (P01–P07), with the version of the repository (`git describe`).
- [ ] Every source and detector parameter written in the JSON sidecar (`data/README.md`): powers, wavelengths, dwell times, averages, temperatures, magnet geometry, filter set, coincidence window.
- [ ] Calibration data saved separately (dark counts with the source blocked; background with the sample removed; detector efficiency reference if available).
- [ ] Randomness source declared if settings are chosen (INV-7): QRNG board serial number and `health_check` output, or an explicit "pseudo-random, teaching mode".
- [ ] Analysis code committed *before* the data is taken where a pass/fail number is at stake (pre-registration in spirit).

## During the run
- [ ] Raw time tags or raw counts saved, not only processed values.
- [ ] Clock source recorded (GPS-disciplined, shared, or free-running) and drift bounded.
- [ ] Any parameter changed mid-run logged with a timestamp.

## After the run
- [ ] The report script's output (`odmr_report`, or the relaxation fits) committed with the data.
- [ ] Systematic uncertainty estimated, not only statistical: for CHSH, the accidental-coincidence subtraction and its effect on $S$; for ODMR, the fit's sensitivity to the baseline model.
- [ ] Comparison with the model stated as a number with a tolerance (e.g. "$D$ within one linewidth of 2.870 GHz − 74 kHz/K").
- [ ] Failure modes tried and recorded: what happens to $S$ when the coincidence window is widened; to the ODMR contrast when the microwave power is halved.
- [ ] Data, sidecar, code version, and report archived together; a DOI (Zenodo) for anything cited in the thesis.

## Why each line exists
The 2010 detector-blinding attacks succeeded because efficiency curves were never characterized under the attack; the retracted Majorana result fell to selective data presentation; several contested advantage claims omitted the classical baseline's improvement. Each checklist line above closes one of those doors at bench scale.

## Sources
- Baker, M. (2016). 1,500 scientists lift the lid on reproducibility. *Nature*, 533, 452. https://doi.org/10.1038/533452a
- Wilkinson, M. D., et al. (2016). The FAIR guiding principles for scientific data management and stewardship. *Scientific Data*, 3, 160018. https://doi.org/10.1038/sdata.2016.18
- Frolov, S. (2021). Quantum computing's reproducibility crisis: Majorana fermions. *Nature*, 592, 350. https://doi.org/10.1038/d41586-021-00954-8
