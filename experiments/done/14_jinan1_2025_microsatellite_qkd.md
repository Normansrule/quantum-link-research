# Jinan-1 2025: microsatellite QKD with a portable ground station

**Original.** A 23 kg microsatellite in low Earth orbit carried a 625 MHz decoy-state BB84 source at 850 nm; a 280 mm portable ground station received it. Over a campaign of passes the link delivered up to about one megabit of secret key per pass, and keys established over separate passes with two stations (Jinan and Stellenbosch, 12 900 km apart) were combined to relay an encrypted image between them [li2025jinan]. This is the current state of the art for satellite QKD: a hundred times lighter than Micius and a ground station that fits in a van.

**Physics.** The same link budget as Micius (`learn/03/06`) with a brighter, faster source and finer pointing (~1 µrad), so more detected photons per pass; decoy states let a weak laser stand in for single photons (`qll/qkd/decoy_state.py`); per-pass yields vary widely with elevation, weather, and background, which is why the pass table (E3) is the input the constellation model needs.

**Simple recreation (Tier 2).** P04 (rooftop link) measures the loss and background laws; P07 (BB84 over a spool) runs the protocol end to end; `qll/channels/link_budget.JINAN1_2025` reproduces the budget once exact parameters are confirmed. The Zenodo pass table, when downloaded, feeds `qll.space.relay_constellation.load_pass_table`.

**What went wrong historically.** Nothing failed; the caution is that "megabit per pass" is a best pass, and the median over a campaign is what a network would live on — which is exactly why the constellation model bootstraps daily totals from the empirical distribution rather than the headline.

**Repo hook.** REQ-F2-001 (Jinan-1 half, pending exact figures); E3; the F2 flagship's stage S4 partner mission.

- Li, Y., et al. (2025). Microsatellite-based real-time quantum key distribution. *Nature*, 640, 47. https://doi.org/10.1038/s41586-025-08739-z
- Lu, C.-Y., et al. (2022). Micius quantum experiments in space. *Reviews of Modern Physics*, 94, 035001.
- Bedington, R., Arrazola, J. M., & Ling, A. (2017). Progress in satellite quantum key distribution. *npj Quantum Information*, 3, 30. https://doi.org/10.1038/s41534-017-0031-5
