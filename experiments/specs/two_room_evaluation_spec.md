# Two-Room Link Evaluation Specification

**Status:** Proposed; no measurements or approvals are implied. Every hardware row below is **Not measured** or **BLOCKED** until evidence is archived.
**Product scope:** A controlled educational and research prototype, not a production secure-communications appliance.
**Specification revision:** 0.1 (October 2026), adapted from the template supplied with the October 2026 independent audit.
**Software / firmware revisions:** Software: quantum-link-research 0.56.0; the exact commit is recorded in each run's events and in the release manifest. Firmware and gateware: **none exists** (see Section 3).
**Responsible experimenter / safety approval reference:** **BLOCKED**: no qualified safety review has been recorded.

The procedure this specification evaluates is [P10](../protocols/P10_two_room_single_photon_link.md). A model prediction and a measurement always occupy separate columns; a model output is never entered as a measurement.

## 1. Claims under test

Each claim is tested and reported on its own. They are never combined into a generic claim of secure quantum key distribution (QKD).

| Claim | Statement | Current status |
|---|---|---|
| A | The classical channel between the two rooms authenticates every frame to a fresh session and refuses tampered, replayed (within and across connections), reflected, truncated, and late frames. | Software tests pass on loopback (`tests/test_two_room.py`); **not measured** between the rooms. |
| B | A calibrated bright-light polarization analogue between the rooms reproduces the expected honest and intercept-and-resend error rates. This is an educational analogue, not secure QKD. | **BLOCKED** by the safety gate. |
| C | A characterized low-light receiver: dark-count rate versus temperature and overvoltage, afterpulsing corrected for accidentals, timing response, and gate acceptance, each with an uncertainty. | **BLOCKED** by the safety gate and the timing electronics. |
| D | Weak-pulse BB84 sessions between the rooms, processed by the repository's protocol code, agree with the planning model within stated tolerances. | **BLOCKED** by claims B and C and by the source characterization. |

Release of a claimed secure key needs additional, explicitly reviewed protocol and device evidence that is outside this specification.

| Field | Value for this project |
|---|---|
| Experiment identifier | The run identifier derived from the configuration (`LinkConfig` hash, `metrics.run_id`). |
| Execution identifier | A fresh UUID per acquisition (`execution_id` in the run's events), separate from the configuration. Key identifiers derive from both. |
| Data origin | One of: simulation; synthetic replay (logs labelled `synthetic` in a `.meta.json` sidecar); bright-light analogue; single-photon experiment. Only the last two can be measured evidence. |
| Quantum path | Free space, inside an enclosed path between the rooms. Length and loss: **Not measured**. |
| Classical path | Two fiber media converters and a 10–30 m duplex patch cord (Ethernet), separate from the quantum path; a coaxial cable or second fiber for the public slot clock. |
| Endpoint implementation | Today: shared-state simulation (both sites in one process), or offline analysis of both sites' logs on one computer. Independent endpoints for the full key-agreement protocol are **not implemented**. Two programs do run as separate processes with no shared state: the authenticated transport probe, and the banked-key messenger (`qll/link/banked_messenger.py`), which spends key banked from an accepted session. |
| Protocol profile | Decoy-state BB84 as implemented in `qll/link/protocol_bb84.py`; basis probabilities, sampling fraction, reconciliation (seeded permutations sent in the clear), verification hash, and key-length rule as recorded in each run's configuration. The finite-key length is a simplified estimate, not a composable proof. |
| Security exclusions | Trusted devices; no detector-control or blinding attacks; no source side channels (timing, spectral, spatial distinguishability between the four diodes); no physical access to either room; no implementation side channels in the computers; authentication in the simulation uses a seeded ledger, not secret material. |
| Success condition | Per claim, a numeric criterion with its uncertainty, stated before the run, plus the failure behavior required in Section 6. |

## 2. Safety gate

**Status: BLOCKED.** No hardware instruction in this repository is authorized by this specification or by P10.

Before any source is powered, record a qualified review (an institutional laser safety officer or an equivalent qualified reviewer) of:

| Item | Record | Status |
|---|---|---|
| Assembled source and driver, pulse behavior, and accessible emissions | Reviewer, date, reference, measured values | BLOCKED |
| Laser class of the assembled system | Determined, not assumed from a part description | BLOCKED |
| Alignment method (full power, filters out) | Approved procedure and controls | BLOCKED |
| Enclosure and termination of every beam, including the path between rooms | Drawing and inspection | BLOCKED |
| Eye protection, wavelength and optical density | Specified by the reviewer | BLOCKED |
| Electrical hazards (SiPM bias near 30 V, laser drivers) and mechanical hazards (cables across the doorway) | Listed with controls | BLOCKED |
| Stop conditions | Written and posted | BLOCKED |
| Instrument calibration and verified maximum operating envelope | Instrument, calibration date, limits | BLOCKED |

Nominal attenuation or a vendor label alone is not proof of safe accessible emissions. No exposed alignment beam is ever routed through an occupied or uncontrolled area. Optical safety and occupational safety are separate acceptance gates from optical security.

## 3. Hardware configuration

| Subsystem | Planned design (from P10) | Evidence required | Status |
|---|---|---|---|
| Source | Four 405 nm diodes behind fixed polarizers, combined by beamsplitters, one fired per 1 µs slot at signal, decoy, or vacuum intensity | Part numbers, driver, per-state and per-intensity pulse-energy distributions, wavelength, timing, spectral and spatial distinguishability, phase assumptions, drift | Not measured |
| Optics | Neutral-density filters, passive 50/50 basis choice, polarizing beamsplitters, half-wave retarder at 22.5° | Actual attenuation and coupling, extinction per detector, drift, geometry, alignment record | Not measured |
| Receiver | Four onsemi MicroFC-30035 SiPMs at about 2.5 V overvoltage, fast comparators at half a photoelectron | Bias, threshold, dark counts versus temperature and overvoltage, afterpulsing (accidentals subtracted), crosstalk, dead time, timing response, efficiency, uncertainties | Not measured |
| Timing electronics | Two small FPGA boards: slot clock, random state choice, laser triggers, 5 ns gate, counting | Exact board and part number, logic levels, interface schematic, clock architecture, reset, synchronization, counter overflow, metastability handling, pin constraints | **BLOCKED BY MISSING EVIDENCE**: planned, not implemented |
| Firmware / gateware | None exists | Source commit, tool versions, build options, image hash, programming steps, simulation testbench, board traces | **BLOCKED BY MISSING EVIDENCE** |
| Classical network | `qll/link/net_transport.py`: pre-shared key, mutual identities, session-bound handshake (HKDF), per-frame HMAC over session, direction, and sequence; a lab construction, not reviewed (mutual TLS is the recommended replacement) | Device identities, addressing, key provisioning record, timeout policy, measured round-trip times | Software tested on loopback; not measured between the rooms |
| Instruments | Photodiode power meter, oscilloscope or logic analyzer, thermometer | Model, serial or reference, calibration date, measurement limits | Not identified |

A planning bill of materials is not a tested implementation. The P10 budget (about $530–1,180, October 2026) excludes instruments and contingency; owned instruments, shared equipment, consumables, optics, electronics, and contingency are budgeted separately once chosen.

## 4. Acquisition and provenance

Each raw file retains site identity, run identifier, execution identifier, schema version, pulse identifiers, local settings, acquisition timestamps, and software and firmware identifiers.

Implemented in software (`qll/link/hardware_log.py`):
- exact integer parsing; fractional, non-numeric, and out-of-range values are rejected, not truncated;
- duplicate and unknown headers, short rows, and pulse-index gaps or reordering are rejected;
- the SHA-256 digest and the declared origin of every input file are recorded in the run's events before analysis;
- synthetic logs are labelled `synthetic` in a sidecar file when written, and selecting a hardware preset does not change that label.

Not yet implemented: firmware identifiers and acquisition timestamps in the log schema, and a check that both sites' files come from the same execution. Private endpoint material (either site's raw bits) is not exported into public artifacts; copying one site's log to the other computer is a laboratory convenience that reveals that site's raw bits on the copy.

## 5. Analysis and reporting

| Quantity | Model prediction | Measurement | Uncertainty / method | Source / raw artifact |
|---|---|---|---|---|
| Per-state source pulse energy | Set by the chosen μ = 0.5 (signal) and 0.1 (decoy) | Not measured | Power meter, per diode and intensity | None |
| Receiver dark-count rate | Datasheet 300–860 kHz at 2.5 V overvoltage, about 21 °C | Not measured | 10 s counts per bias step, temperature logged | None |
| Timing / gate acceptance | 5 ns gate | Not measured | Delay scan, instrument response | None |
| Optical loss / transfer | 2.0 dB path plus 1.5 dB receiver (assumed) | Not measured | Power ratio, per path | None |
| Detection and double-click rates | Click probability 0.0585 per pulse (model) | Not measured | Counts per emitted pulse | None |
| Basis-resolved error rates | 3.7 % (model) | Not measured | Per basis, binomial interval | None |
| Reconciliation leakage | Counted from the transcript (simulation) | Not measured | Exact transcript accounting | None |
| Verification outcome | Pass in simulation | Not measured | Exact profile | None |
| Authentication state | VERIFIED in simulation (seeded ledger) | Not measured | Verified immutable transcript | None |
| Accepted output material | About 12,000–13,000 bits per 10 s session (model only) | Not established | Simplified finite-key estimate; not a composable proof | None |

Rates per emitted pulse, per detected event, per sifted event, and per accepted output are reported separately. A passing goodness-of-fit check (`two_room.check_against_twin`) does not establish cryptographic security.

## 6. Adverse-condition matrix

Rows marked with a test are software checks against the actual code; they are not hardware measurements.

| Condition | Expected behavior | Software evidence | Hardware observation |
|---|---|---|---|
| Wrong pre-shared key | Handshake refused, no frames accepted | `tests/test_two_room.py` (wrong key) | Not measured |
| Replay within a session | Frame refused | `tests/test_two_room.py` (replay) | Not measured |
| Replay across sessions | Frame refused (fresh session key) | `tests/test_two_room.py` (cross-connection replay) | Not measured |
| Reflection of a frame to its sender | Refused (direction bound into the tag) | `tests/test_two_room.py` (reflection) | Not measured |
| Partial frames, disconnect, timeout | Link error, no partial acceptance | `tests/test_two_room.py` (timeouts and partial frames) | Not measured |
| Late transcript mutation | Refused after closure; key release requires the verified digest | `tests/test_key_lifecycle.py` | Not applicable |
| Exhausted authentication pool | Channel FAILED, stays failed, no key released | `tests/test_key_lifecycle.py` | Not applicable |
| Duplicate or reused key identity or material | Refused (tombstones, digests, unique executions) | `tests/test_key_lifecycle.py` | Not applicable |
| Negative, zero, or fractional counts | Refused without changing state | `tests/test_key_lifecycle.py`, `tests/test_two_room.py` | Not applicable |
| Invalid logs | Refused with the offending row | `tests/test_two_room.py` (strict log parsing) | Not measured |
| Source off | No key; session rejected | Simulation only | Not measured |
| Excess background | Error rate rises; session rejected above threshold | Simulation only | Not measured |
| Drift | Detected by per-class rates | Not implemented | Not measured |
| Missing clock, resets, counter overflow | Detected and logged by gateware | Not implemented (no gateware) | BLOCKED |

For each case the report records the expected refusal, the observed result, a trace, and whether any key or success status escaped. A generic printed PASS is insufficient evidence.

## 7. Release record

Each release archives the source and environment manifest, test results (JUnit), measured raw data, analysis commands, generated figures, known limitations, and approval references. The release is classified independently in each category:

| Category | Assessment for 0.56.0 |
|---|---|
| Educational simulation | See the release assessment in [`docs/audit/2026-10-11_findings.md`](../../docs/audit/2026-10-11_findings.md) |
| Independent network prototype | Not ready: only the transport probe runs between two computers |
| Optical experiment | Not ready: BLOCKED by the safety gate and the timing electronics |
| Finite-key implementation reviewed | Not reviewed |
| Production security qualified | No |

**Release decision for the optical experiment:** NOT ASSESSED. It changes only when the responsible reviewers have evidence for the stated claim. No value in this specification establishes a measured or secure implementation.

## References

American National Standards Institute. (2022). *American national standard for safe use of lasers* (ANSI Z136.1-2022). Laser Institute of America.

ETSI. (2019). *Quantum key distribution (QKD); Protocol and data format of REST-based key delivery API* (ETSI GS QKD 014 V1.1.1). European Telecommunications Standards Institute.

Krawczyk, H., & Eronen, P. (2010). *HMAC-based extract-and-expand key derivation function (HKDF)* (RFC 5869). Internet Engineering Task Force. https://doi.org/10.17487/RFC5869

Lim, C. C.-W., Curty, M., Walenta, N., Xu, F., & Zbinden, H. (2014). Concise security bounds for practical decoy-state quantum key distribution. *Physical Review A, 89*, 022307. https://doi.org/10.1103/PhysRevA.89.022307

Ma, X., Qi, B., Zhao, Y., & Lo, H.-K. (2005). Practical decoy state for quantum key distribution. *Physical Review A, 72*, 012326. https://doi.org/10.1103/PhysRevA.72.012326

Occupational Safety and Health Administration. (n.d.). *OSHA technical manual (OTM), Section III: Chapter 6. Laser hazards*. U.S. Department of Labor. https://www.osha.gov/otm/section-3-health-hazards/chapter-6

Tomamichel, M., Lim, C. C. W., Gisin, N., & Renner, R. (2012). Tight finite-key analysis for quantum cryptography. *Nature Communications, 3*, 634. https://doi.org/10.1038/ncomms1631
