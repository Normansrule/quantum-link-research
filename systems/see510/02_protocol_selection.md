# 02 Protocol selection

**Decision.** BB84, prepare-and-measure, with an ideal single-photon source, as the first protocol [bennett1984].

**Why it is needed.** The protocol decides what the sites do, what the adversary can do, and what an error rate means. The first one should be the best understood, so that every simulated number can be checked against a textbook result before anything novel is attempted (handoff rule: "use known protocols before developing novel ones").

| Criterion | BB84 (chosen) | BBM92 / E91 (entanglement) | Decoy-state BB84 | Continuous-variable QKD | MDI-QKD |
|---|---|---|---|---|---|
| Closed-form expectations to validate against | detection, error rate, intercept-resend 25 %, secret fraction 1 − 2h(Q) | similar, plus a Bell test for E91 | needs yields per intensity | needs excess-noise models | needs Bell-state measurement models |
| Hardware a single developer can reach | attenuated laser and two detectors (P07) | an entangled-photon source (P03, $3,000+) | as BB84 plus intensity modulation | homodyne detectors, a local oscillator | two sources, interference at a relay |
| Teaching value | the reference protocol | shows that no memory is needed for key | the practical fix for multi-photon pulses | a different physical picture | removes detector attacks |
| Security proofs in the literature | mature [shor2000] [scarani2009] | mature | mature [lo2005] | mature, more involved | mature |
| Implemented in this repository | `qll/link/` (this work) and `qll/qkd/bb84.py` | `qll/qkd/e91.py` | `qll/qkd/decoy_state.py` | `qll/qkd/cv_qkd.py` | `qll/qkd/mdi.py` |

**Why the ideal single-photon source.** It isolates the effects the handoff asks about (distance, loss, noise, interception) from the photon-number statistics of a laser. The consequence is stated in 03 and 09: a real weak-coherent source needs decoy states, or photon-number splitting attacks break the security claim [brassard2000]. Since 0.45 the same protocol also runs with a weak-coherent laser source, with or without decoy intensities (`source_model`), and the decoy-state analysis bounds the single-photon detections [ma2005]; scenario 8 shows why that matters.

**Supports** SN-02 (states are prepared and measured between the sites), SN-03, SN-05 (security rests on physics plus authentication, not on factoring), SN-08 (lowest-cost hardware path). **What this does not claim.** That BB84 is the best protocol for a deployed link; for that, decoy states and finite-key proofs are required (09).
