# G0 Mission concept review — 2026-10-05

**Evidence examined.**
- The simulation library and its tests (continuous integration on every push).
- The SEE 510 two-site link ([`../../see510/`](../../see510/README.md)), including the operations day.
- The experiment catalog ([02](../02_research_foundation.md)).
- The feasibility numbers ([05](../05_feasibility.md)).
- The two-room twin ([`qll/link/two_room.py`](../../../qll/link/two_room.py)) and the collapse-code analysis ([`qll/circuits/collapse_signalling.py`](../../../qll/circuits/collapse_signalling.py)).

| Criterion | Evidence | Result |
|---|---|---|
| The simulation reproduces every analytic case it implements | the full test suite passes; validation V1–V15 of the two-site link | pass |
| The evidence regenerates from configurations and seeds | `python -m qll.link.run scenarios` and `operations` reproduce the committed numbers (slow tests) | pass |
| Mission needs and requirements are written and verifiable | [03](../03_requirements_and_verification.md); every milestone verifies a requirement (tested) | pass |
| Phase 1 is feasible on paper within its budget | the twin accepts a ten-second session across a hallway with the planned parts; Phase 1 likely cost $670, against a cap of $1,400 (MR-1.8) | pass |
| The physical limits are stated, and no requirement depends on signalling | MR-X.1; [05](../05_feasibility.md); `test_no_milestone_depends_on_signalling_through_collapse` | pass |

**Decision.** Proceed to Phase 1.

**Actions.**
- Start M1.1, M1.2, M3.1, and S1, which need no purchases beyond the classical-channel parts.
- Ask a physics teaching lab about lending an entangled-photon kit for Phase 2 (risk MR-R3), by Gate G1.
- Verify the citations still marked TODO (ghirardi1980 DOI, kelley1959 DOI) before paper 1.

**Spending unlocked.** Phase 1, up to $1,400 (requirement MR-1.8), released milestone by milestone as each twin check passes.
