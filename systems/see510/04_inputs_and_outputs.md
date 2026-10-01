# 04 Inputs and outputs

## Configurable inputs (`qll/link/config.py`, `LinkConfig`)
Every input is a field of one frozen configuration; a run is fully described by it, and its SHA-256 hash is the run identifier. A test checks that every field below exists in the code and that the code has no field missing here.

| Input | Unit | Default | Valid range | Why this default | Needs |
|---|---|---|---|---|---|
| `scenario` | — | baseline | text | label for logs | SN-07 |
| `seed` | — | 2026 | integer | reproducibility | SN-07 |
| `n_pulses` | pulses | 1,000,000 | ≥ 1 | one second at 1 MHz; the finite block size | SN-06 |
| `pulse_rate_hz` | Hz | 1 × 10⁶ | ≥ 0 | typical laboratory source; converts bits per session into bits per second | SN-06 |
| `distance_km` | km | 0 | ≥ 0 | laboratory sites | SN-06 |
| `attenuation_db_per_km` | dB/km | 0.2 | ≥ 0 | standard single-mode fiber near 1550 nm | SN-06, SN-11 |
| `extra_loss_db` | dB | 0 | ≥ 0 | connectors, or a deliberately inserted attenuator | SN-06 |
| `receiver_loss_db` | dB | 1.0 | ≥ 0 | Site B's internal optics | SN-11 |
| `detector_efficiency` | — | 0.20 | [0, 1] | InGaAs single-photon avalanche diode | SN-11 |
| `dark_count_prob` | per gate | 1 × 10⁻⁶ | [0, 1] | gated InGaAs detector | SN-11 |
| `crosstalk_click_prob` | per gate | 0 | [0, 1] | background from co-propagating classical light (A-14) | SN-14 |
| `misalignment_error` | — | 0.01 | [0, 0.5] | well-aligned polarization optics | SN-06 |
| `source_model` | — | single_photon | single_photon | A-01; anything else is refused | SN-07 |
| `eve_fraction` | — | 0 | [0, 1] | fraction of pulses intercepted and resent | SN-03 |
| `sample_fraction` | — | 0.1 | [0, 1] | share of sifted bits disclosed to estimate the error rate | SN-03 |
| `min_sample_bits` | bits | 200 | ≥ 0 | smallest useful estimate | SN-03 |
| `qber_threshold` | — | 0.11 | [0, 1] | the BB84 limit where 1 − 2h(Q) reaches zero [shor2000] | SN-03 |
| `qber_alert` | — | 0.03 | [0, 1] | about three times the baseline error; operator warning | SN-04 |
| `min_key_block_bits` | bits | 1000 | ≥ 0 | smallest block worth reconciling | SN-07 |
| `eps_pe` | — | 1 × 10⁻¹⁰ | (0, 1) | confidence of the error-rate upper bound | SN-07 |
| `eps_pa` | — | 1 × 10⁻¹⁰ | (0, 1) | privacy-amplification security parameter | SN-05 |
| `ec_passes` | — | 4 | ≥ 0 | standard Cascade [brassard1994] | SN-07 |
| `verify_tag_bits` | bits | 64 | ≥ 1 | collision probability 2⁻⁶⁴ | SN-03 |
| `tamper_classical` | — | false | true/false | an attacker alters one classical message | SN-03 |
| `key_size_bits` | bits | 256 | multiple of 8 | AES-256 keys for the application | SN-09, SN-12 |

## Measured outputs (`qll/link/monitor.py`, `SessionMetrics`)
**Implemented in every session.**

| Output | Meaning | Required by the handoff |
|---|---|---|
| `run_id`, `scenario`, `seed`, `timestamp_utc`, `execution_time_s` | identity and provenance | yes |
| `distance_km`, `channel_loss_db`, `channel_transmittance` | the simulated channel | yes |
| `adversary`, `eve_touched` | adversary state and what it did | yes |
| `states_sent`, `states_detected`, `detection_probability` | transmission | yes |
| `sifted_bits`, `sample_bits`, `sample_errors` | sifting and the error estimate | yes |
| `qber_estimate`, `qber_upper_bound`, `alert` | the security indicator the operator sees | yes |
| `key_block_bits`, `ec_leaked_bits`, `ec_corrected_bits`, `verified` | reconciliation | future in the handoff, implemented |
| `accepted`, `reject_reason` | the key-validity decision | yes |
| `final_key_bits`, `secret_key_rate_bps`, `keys_delivered_256` | usable key | yes (secret key rate is a handoff "future" metric, implemented) |
| `pa_removed_bits` | privacy-amplification reduction | future in the handoff, implemented |
| `classical_messages`, `classical_bytes` | classical overhead | future in the handoff, implemented |
| `events` | the monitor's time-ordered log | yes |

**Simulation-only diagnostics** (an operator could never see these; they exist to validate the model): `qber_true` (error rate over all sifted bits), `residual_errors_before_verify`, `eve_known_key_bits` (key bits the adversary measured in the right basis).

**Not implemented (future metrics).** Session latency including classical round trips; availability over days; decoy-state yields and multi-photon bounds; composable finite-key length; afterpulsing and dead-time losses; detector-efficiency mismatch; error-correction efficiency against a production decoder (Cascade's measured efficiency, 1.1–1.4, is reported instead).

## Per-run summary
Every session prints and logs this block (`summary.txt`):
```
Simulation Run ID:       9ce7440fb81b
Scenario:                1_baseline
Protocol:                BB84 (ideal single-photon source, prepare and measure)
Distance:                0 km
Loss:                    0.00 dB (transmittance 1)
States Sent:             1,000,000
States Detected:         158,319 (p = 1.583e-01)
Sifted Key Bits:         79,373
Errors:                  90 of 7938 sampled bits
QBER:                    1.13 % estimated (upper bound 4.94 %)
Adversary:               none
Key Accepted:            yes
Final Usable Key Length: 44,396 bits (44,396.0 bit/s at the pulse rate)
Random Seed:             11
Execution Time:          0.248 s
```
This is the first baseline session; its folder, with the configuration and event log, is in [`evidence/example_run/`](evidence/example_run/).
