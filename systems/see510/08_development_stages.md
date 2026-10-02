# 08 Development stages

The handoff's sixteen tasks, in the order they were done. For each: what is modelled, why, the needs it serves, the assumptions it adds, and what its result does and does not prove. Status: done means implemented, tested, and in the evidence.

| # | Stage | What is modelled, and why | Needs | Assumptions | Proves | Does not prove | Status |
|---|---|---|---|---|---|---|---|
| 1 | Architecture | blocks with one responsibility each, so a protocol or a measurement can replace one block (01) | SN-13, SN-15 | — | the CONOPS steps each have an owner | that hardware divides the same way | done |
| 2 | Protocol | BB84 with an ideal source: the most checkable start (02) | SN-02, SN-05, SN-08 | A-01 | closed forms exist for every metric | that BB84 is the best deployed choice | done |
| 3 | Assumptions | fourteen, each with what would replace it (03) | SN-07 | A-01–A-14 | the scope of every claim is explicit | — | done |
| 4 | Inputs | one configuration; ranges enforced; run identifier (04) | SN-07, SN-11 | — | no run has an unrecorded parameter | that defaults match a specific device | done |
| 5 | Outputs | every required metric, three diagnostics, and the future list (04) | SN-04, SN-07 | — | each handoff metric is computed | — | done |
| 6 | Models | channel, detection, error rate, estimate, reconciliation, key length (05) | SN-06 | A-02–A-05, A-10 | expected values for validation | that the equations describe hardware | done |
| 7 | Test cases | validation V1–V12 and scenarios TC-1–TC-7 (06) | SN-07 | — | each claim has a test | — | done |
| 8 | Traceability | SN-01–SN-15 to module, test, and evidence (07) | all | — | every need is addressed or its gap stated | — | done |
| 9 | Structure | `qll/link/` one module per block; documents and evidence here (README) | SN-01, SN-08 | — | one developer can navigate it | — | done |
| 10 | Simplest two-site session | Site A prepares, Site B measures, sifting, keys compared, no loss or noise | SN-02 | A-01, A-09 | matching keys emerge from the protocol alone (V1) | anything about loss or attack | done |
| 11 | Validation | simulated statistics against closed forms (V2–V5), components against exact results (V9–V11) | SN-07 | — | the code computes what the models say | that the models are right about hardware | done |
| 12 | Distance and loss | fiber attenuation, inserted attenuators, block-size sensitivity (TC-2, TC-4) | SN-06 | A-02, A-13 | key falls with loss; the finite block, not the error rate, ends the key first | real fiber impairments beyond attenuation | done |
| 13 | Adversary | intercept-and-resend on a chosen fraction; classical tampering (TC-3, TC-5) | SN-03 | A-06, A-07 | interception raises the error rate by f/4; alert and abort follow; amplification removes more than she knew; noise looks the same | security against collective, coherent, or side-channel attacks; that an adversary can be identified, located, or removed | done |
| 14 | Logging and plots | evidence folders, CSV tables, ten plots, generated report (evidence/) | SN-04, SN-07 | — | every number is reproducible from its configuration and seed (V6, V12) | — | done |
| 15 | External demonstration | key stores with an ETSI GS QKD 014-style interface; AES-256-GCM application; fail closed (TC-7) | SN-09, SN-12, SN-15 | A-12 | only accepted key is used; messages decrypt; empty store refuses | protection of keys at rest and in use | done |
| 16 | Limitations and hardware | what is left out, and the path to a bench (09) | SN-10, SN-11, SN-14 | — | the transition is planned against measurable parameters | that it will succeed | done |

| 17 | Real-world ladder | five tiers from a bright-light analogue to a deployed link; experiment logs processed by the same protocol code; Tier 1 twin, Arduino sketch, and serial driver (10) | SN-01, SN-08, SN-10, SN-11, SN-14 | tier presets in `hardware/` | the path from simulation to hardware is executable, and a log reproduces the simulated session exactly | that any tier has been built yet | designed; Tier 1 ready to build |

| 18 | Information-theoretic authentication | Wegman–Carter tags over each site's transcript, checked before acceptance; a key pool refilled from each session; net key (05, TC-9) | SN-05, SN-09 | A-07 | authentication no longer rests on a computational assumption; a session must out-earn its 381-bit cost | that the simulation's pads are secret (they are derived from the seed) | done |
| 19 | Laser sources, decoys, and photon-number splitting | weak-coherent source, decoy-state bounds, worst-case analysis without decoys, a perfectly equipped splitting adversary, and an alert (05, TC-8) | SN-03 | A-01, A-15 | why decoys are needed: without them the attack is invisible and a naive key is hers; with them it is exposed and excluded | security against attacks beyond A-06 and A-15 | done |

**Next stages (not done).** A composable finite-key length (removes A-10); a live monitoring dashboard (extends SN-04); feeding hardware logs from protocol P07 into the same protocol code (09).
