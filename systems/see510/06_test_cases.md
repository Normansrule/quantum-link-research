# 06 Test cases and validation

Two kinds of evidence, kept apart. **Validation** compares the simulation with cases whose answers are known in closed form; it shows the model computes what it claims. **Scenarios** use the validated model to answer the handoff's questions; they show what the modelled system would do. Neither is a hardware measurement. Results: [`evidence/README.md`](evidence/README.md). Tests: `tests/test_two_site_link.py`.

## Validation (controlled cases; `python -m qll.link.run validate`)
| ID | Case | Expected | Pass criterion | Test |
|---|---|---|---|---|
| V1 | no misalignment, no dark counts, 0 km | error rate exactly 0; keys identical; accepted | exact | `test_ideal_session_gives_identical_keys_and_the_accounted_length` |
| V2 | detection probability at 0, 25, 75 km | $p_{\mathrm{det}}$ of 05 | within 4 binomial standard deviations | `test_every_validation_check_passes` |
| V3 | sifting fraction at the same distances | 1/2 | within 4 standard deviations | same |
| V4 | error rate over all sifted bits | $Q$ of 05 | within 4 standard deviations | same |
| V5 | full intercept-resend | $Q \approx 25\,\%$; rejected | within 4 standard deviations; reason `qber` | same, and `test_decisions` |
| V6 | same configuration and seed twice | identical metrics, keys, run identifier; another seed differs | exact | `test_reproducibility` |
| V7 | one classical message altered | rejected; reason `auth` | exact | `test_decisions` |
| V8 | key delivery | only accepted sessions deposit keys; AES-256-GCM round trips succeed; empty store refuses | exact | `test_demo_application_uses_only_accepted_key_and_fails_closed` |
| V9 | Cascade on keys with 1, 3, 8 % errors | every error corrected; leak between $n\,h(Q)$ and $1.6\,n\,h(Q)$ | exact, bounded | `test_cascade_removes_every_error_close_to_the_shannon_limit` |
| V10 | verification with one differing bit | mismatch detected | exact | `test_verification_catches_a_single_differing_bit` |
| V11 | fast Toeplitz hash | equals the explicit matrix product | exact | `test_fast_toeplitz_equals_the_matrix_product` |
| V12 | committed evidence | a fresh run reproduces the baseline rows of `evidence/sessions/1_baseline.csv` | exact | `test_committed_evidence_is_reproduced_by_a_fresh_run` |

## Scenarios (`python -m qll.link.run scenarios`)
| ID | Scenario | Configuration | What is measured | Expected behavior (model) | Needs |
|---|---|---|---|---|---|
| TC-1 | Baseline | 0 km, no adversary, three seeds | detections, sifted bits, error rate, decision, final key | accepted; error rate near 1 %; about 45,000 key bits per 10⁶ pulses | SN-02, SN-07 |
| TC-2 | Increasing distance | 0–125 km, three seeds; 10⁷-pulse blocks at 50–125 km | detection probability, error rate, final key, acceptance | key falls with loss; error rate flat; the 10⁶-pulse block runs out of detections between 75 and 100 km; longer blocks reach further | SN-06 |
| TC-3 | Interception | 0, 5, 10, 25, 50, 100 % intercepted, three seeds; one tampered classical message | error rate, alert, decision, bits the adversary knew against bits removed | error rate rises by f/4; alert from about 10 %; rejected above about 40 %; accepted keys lose more bits to amplification than the adversary knew; tampering rejected | SN-03, SN-05 |
| TC-4 | High loss | inserted loss 0–40 dB at 0 km | final key, decision | key until about 15 dB per 10⁶ pulses; rejected (too few detections) beyond | SN-06 |
| TC-5 | Random channel error | misalignment 0–15 %, and an adversary tuned to the same expected error rate | error rate, detection rate, decision | the two are indistinguishable by these indicators; both rejected above the threshold | SN-03, SN-07 |
| TC-6 | Reproducibility | same configuration and seed twice, and a second seed | every metric and the keys | identical; the second seed differs | SN-07 |
| TC-7 | Demonstration | accepted and rejected sessions feeding the key stores and the application | keys delivered, round trips, refusal | keys only from the accepted session; messages decrypt; refusal when empty | SN-12, SN-15 |

**What this proves.** The simulation's statistics match their closed forms (V1–V5), its decisions follow the rules (V5, V7, V8), it is exactly reproducible (V6, V12), and its components work individually (V9–V11). Under the model, the scenarios then show how loss, block size, noise, and interception change the key. **What it does not prove.** That hardware behaves this way, that the security argument holds against attacks outside A-06, or that the finite-key estimate is composably secure.
