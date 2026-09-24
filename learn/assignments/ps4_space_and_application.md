# Problem Set 4 — Space Segment and Application

Read `learn/03_quantum_communication/04`, `07`, `08`, `13`. Check with `python -m pytest tests/test_assignments.py -k ps4`.

1. **Light time.** One-way light time at the Earth–Mars range of 1.8 au, in minutes. *(`ps4_lt_18au_min`)*
2. **Conjunction.** How many solar conjunctions occur in 10 years? *(`ps4_conjunctions_10y`, to the nearest integer using the synodic period)*
3. **Doppler.** Fractional Doppler shift for a range rate of 12 km/s, and the shift in GHz of a 193.4 THz carrier. *(`ps4_doppler_frac`, `ps4_doppler_ghz`)*
4. **Classical link.** Holevo capacity in bits per mode at a mean photon number of 10⁻⁴. *(`ps4_holevo_1e4`)*
5. **Buffer.** Key buffer (bytes) needed to send one 32-byte-keyed message every 30 s through a Mars-maximum round trip with zero key rate. *(`ps4_buffer_bytes`)*
6. *(written)* Explain why an L4/L5 relay keeps availability through conjunction but does not fix the yield collapse near it.
7. *(written)* The messenger refuses to send when the key buffer is empty. Argue for or against a fallback to ML-KEM-only keys, in terms of the security model each provides.
