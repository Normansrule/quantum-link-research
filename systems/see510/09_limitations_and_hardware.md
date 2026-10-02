# 09 Limitations, and the transition to hardware

## What the simulation does not show
- **Not a measurement.** Every number comes from a model under the assumptions of 03. Where a result is reported, the evidence says "simulated".
- **Not unconditional security.** The model's adversaries are two textbook attacks (A-06): intercept-and-resend, and photon-number splitting on a laser source, which the decoy-state analysis exposes. Collective and coherent attacks, detector blinding and time-shift attacks, Trojan-horse probing, and side channels are outside the model. Their defenses (measurement-device independence, detector monitoring, isolators) are known, but none is modelled here.
- **Authentication pads are simulated** (A-07). The Wegman–Carter scheme is information-theoretically secure, but the simulation derives its pre-shared pads from the seed; a deployment must exchange real pre-shared key at setup and keep the pool topped up from accepted sessions (a session that nets less than 381 bits drains it).
- **No identification or removal of an adversary.** An elevated error rate is evidence of interception or of noise, and the model shows the two are indistinguishable by error rate and detection rate alone (TC-5). The system rejects or shortens affected key; it does not find, attribute, or stop anyone, and it does not prevent denial of service: an adversary who cuts the fiber or raises the error rate stops the key.
- **A finite-size estimate, not a proof** (A-10). The Hoeffding margin is conservative but is not a composable finite-key bound.
- **Simplified optics.** Attenuation only (A-02); one misalignment number for all optical errors (A-03); no afterpulsing or dead time (A-04); identical detectors (A-05); constant background from co-propagating light (A-14), so SN-14 is only partly assessed.
- **Keys at rest.** Stored keys are plain bytes in a simulated store (A-12).

## Moving to hardware: the same code, measured parameters
The simulation was built so that hardware replaces blocks, not the design (01). The path is staged and reuses the repository's bench protocols.

| Step | Hardware | Replaces | Measured parameter, into `LinkConfig` | Hazard and control (SN-10) |
|---|---|---|---|---|
| H1 | Characterize detectors: dark counts, efficiency | A-04, A-05 | `dark_count_prob`, `detector_efficiency` | detector bias voltage: enclosure, current limit |
| H2 | Characterize the channel: patch cords, a fiber spool (1–25 km), and a variable optical attenuator | A-02 | `attenuation_db_per_km`, `extra_loss_db`, `receiver_loss_db` | none significant; bend radius and clean connectors |
| H3 | Polarization or time-bin encoding at Site A; analysis at Site B; error rate with no adversary | A-03 | `misalignment_error` | laser: eye-safe class 1 at 1550 nm after attenuation; never view a fiber end |
| H4 | Weak-coherent source with an attenuator; decoy intensities | A-01 | `source_model = weak_coherent_decoy`, `mu_signal`, `mu_decoy`, `p_signal`, `p_decoy`; log `alice_intensity` | as H3 |
| H5 | Random bases from a quantum random number generator | A-09 | — | none |
| H6 | Log raw detections with timestamps in the format of `qll/link/hardware_log.py`; `python -m qll.link.run ingest` runs them through `protocol_bb84.py` in place of `site_a.py`, `quantum_channel.py`, `site_b.py` (implemented and tested: a simulated log reproduces the simulated session exactly) | the quantum blocks | the measured session itself | none |
| H7 | Intercept-resend station on the link (protocol P07 step 6) | A-06 | `eve_fraction` | as H3 |
| H8 | Classical channel over a network socket, carrying the same Wegman–Carter transcript tags; real pre-shared pads | A-07, A-08 | `auth_pool_bits` | none |
| H9 | Key store as a service with the same three calls; application on two computers | A-12 | — | key handling: no test keys reused for real data; only non-sensitive test data |

Document [10](10_real_world_experiments.md) turns these steps into a ladder of five setups with parts, costs, procedures, and pass criteria, from a $40 tabletop analogue to a deployed link. For each step the simulation already states what the measurement should show, so a hardware result either confirms the model or identifies the assumption that failed. The detailed bench is protocol P07 (BB84 over a fiber spool, `experiments/protocols/P07_bb84_over_a_fiber_spool.md`), whose costs and parts are in `experiments/bench/`.

## Equipment definition (SN-11)
| Component class | Parameters that matter (configuration field) | Simulation default | What the default implies |
|---|---|---|---|
| Single-photon detectors, 1550 nm (InGaAs) | efficiency (`detector_efficiency`), dark-count probability per gate (`dark_count_prob`), gate rate (`pulse_rate_hz`) | 0.20; 10⁻⁶; 1 MHz | at these values the 11 % threshold is reached near 230 km, but a 10⁶-pulse block stops yielding key between 75 and 100 km |
| Fiber and connectors | loss per km, inserted loss | 0.2 dB/km; 0 dB | each 3 dB halves the detections |
| Receiver optics | internal loss | 1 dB | |
| Source | type, mean photon numbers, intensity ratios (`source_model`, `mu_signal`, `mu_decoy`, `p_signal`, `p_decoy`) | ideal single photon; decoy model 0.5 / 0.1 / vacuum at 80 / 15 / 5 % | without decoys a laser yields no guaranteed key beyond a few dB; with decoys key to about 50 km in 10⁷-pulse sessions |
| Random number generator | certification | seeded simulation generator | must be replaced (SN-09) |
| Classical network | latency, authentication | none; Wegman–Carter | 381 bits of pre-shared key per session, replaced from its output |

## Standards (SN-09)
AES-256-GCM for the application [nist2007sp800-38d]; HMAC-SHA256 for the classical-channel abstraction [nist2008fips198]; a DRBG per NIST SP 800-90A or a quantum generator for random numbers [nist2015sp800-90a]; key delivery after ETSI GS QKD 014 [etsi2019qkd014]. The simulation uses the primitives; it is not a certified implementation.
