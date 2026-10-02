# SEE 510 case study: Scalable Two-Node Fiber-Optic Quantum Communication Link

**System of Interest.** A laboratory-scale link between Site A and Site B that establishes shared secret keys, transmits quantum states, identifies evidence of interception before affected key material is used, monitors itself, records reproducible evidence, and hands accepted keys to an external secure-communication application. This folder is the simulation phase: a credible model of that system built before, and alongside, the hardware. It is flagship F1 of this repository at laboratory scale.

**What the simulation is, and is not.** It is a transparent Monte Carlo model of BB84 with an ideal single-photon source, a lossy fiber, imperfect detectors, a textbook intercept-and-resend adversary, a real error-correction protocol (Cascade), privacy amplification, and an authenticated classical channel. Every result comes from a recorded configuration and seed and is checked against closed-form expectations. It is **not** a measurement of hardware, **not** a proof of unconditional real-world security, and it does **not** identify, locate, or remove an adversary.

## Documents
| # | Document | Handoff task |
|---|---|---|
| 01 | [Simulation architecture](01_architecture.md) | 1, 9 |
| 02 | [Protocol selection](02_protocol_selection.md) | 2 |
| 03 | [Assumptions](03_assumptions.md) | 3 |
| 04 | [Inputs and outputs](04_inputs_and_outputs.md) | 4, 5 |
| 05 | [Mathematical models](05_models.md) | 6 |
| 06 | [Test cases and validation](06_test_cases.md) | 7, 11 |
| 07 | [Traceability: SN-01 to SN-15](07_traceability.md) ([`traceability.csv`](traceability.csv)) | 8 |
| 08 | [Development stages](08_development_stages.md): what each stage models, why, which need, what it proves and does not | 10–15 |
| 09 | [Limitations and the transition to hardware](09_limitations_and_hardware.md) | 16 |
| 10 | [**Real-world experiments**](10_real_world_experiments.md): a ladder from a $40 tabletop analogue to a deployed link, each tier predicted, logged, and processed by the same code | after 16 |
| — | [**Evidence**](evidence/README.md): validation table, six scenarios, plots, per-run summaries | 11–14 |

## Run it
Python 3.10 or later with NumPy, matplotlib, and `cryptography` (all open source). From the repository root:

```bash
python -m qll.link.run session                                   # one baseline session, with its summary and events
python -m qll.link.run session --set distance_km=25 eve_fraction=0.1 --out runs/   # any input, logged to a folder
python -m qll.link.run validate                                  # the controlled cases against the closed-form models
python -m qll.link.run scenarios                                 # scenarios 1-6 and the demo; rewrites evidence/ (~25 s)
python -m qll.link.run demo                                      # deliver accepted keys to the demonstration application
python -m qll.link.bench_tier1 --out tier1.csv                   # Tier 1 bench (add --port COM5 for the real Arduino)
python -m qll.link.run ingest tier1.csv --config systems/see510/hardware/tier1.json   # process an experiment's log
python -m pytest tests/test_two_site_link.py                     # 26 fast tests (the full scenario run is marked slow)
```

## Folder and file structure
```
qll/link/                     the simulation (one module per logical block of the architecture)
  config.py                   every input, its range, and the run identifier
  models.py                   closed-form expectations used for validation and plots
  site_a.py  site_b.py        preparation; measurement and detection
  quantum_channel.py          fiber loss, with the adversary at its input
  adversary.py                intercept-and-resend on a chosen fraction of pulses
  classical_channel.py        authenticated public channel with a transcript
  codec.py                    compact encoding of bit arrays in messages
  reconciliation.py           Cascade error correction and hash verification
  protocol_bb84.py            one session, CONOPS steps 1-10, and the accept/reject decision
  monitor.py                  metrics, status, events, the per-run summary
  logger.py                   evidence folders and CSV tables
  key_store.py                key delivery (ETSI GS QKD 014-style get_key / get_key_with_ids)
  demo_app.py                 the external secure-communication demonstration (AES-256-GCM)
  scenarios.py                scenarios 1-6, the demonstration, and the validation checks
  hardware_log.py             experiment logs in, the same protocol out (run_from_log)
  bench_tier1.py              Tier 1 bench: its software twin, the Arduino serial driver, and the runner
  plots.py  run.py            evidence plots; the command-line runner
tests/test_two_site_link.py   tests with known answers for every module
systems/see510/               these documents, traceability.csv, evidence/, and hardware/ (tier presets)
experiments/bench/see510_tier1/  the Tier 1 Arduino sketch
```
