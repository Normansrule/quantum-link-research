# Gate reviews

One record per gate: the date, the evidence examined, each pass criterion with its result, the decision, and the actions. A gate is passed only when every criterion has evidence in the repository; "almost" means the gate is not passed and the phase continues.

| Gate | Like NASA's | Record |
|---|---|---|
| G0 | mission concept review | [G0_concept_review.md](G0_concept_review.md) |
| G1 | system requirements review, plus a preliminary design review for Phase 2 | written when Phase 1 ends |
| G2 | critical design review for the outdoor and satellite segments | written when Phase 2 ends |
| G3 | flight-readiness decision | written when Phase 3's ground segment is ready |

Template:

```
# G<n> <name> — <date>
Evidence examined: <links>
| Criterion | Evidence | Result (pass / not yet) |
Decision: proceed / hold / stop.  Actions: <owner, due>.
Spending unlocked: <amount and items>.
```
