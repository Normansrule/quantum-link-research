# Risk register

Likelihood and impact on a 1–5 scale; status as of this version, with the evidence in the repository.

| ID | Risk | L | I | Mitigation | Status |
|---|---|---|---|---|---|
| R-1 | Memory coherence falls short of the 6–45 min round trip | 4 | 5 | Trade TS-3; store-and-forward relay; purification (learn 03/20) | Open. Only the trapped ion clears the maximum round trip usefully, margin < 1.5×; crystals clear it with retrieval ≤ 1 % |
| R-2 | Thermal load of cryogenic memories in space | 3 | 4 | Flown-cooler comparison (REQ-SPC-003); room-temperature ion traps | Mitigated for ions (300 K); open for rare-earth crystals |
| R-3 | Diffraction loss at astronomical distance | 5 | 5 | Architecture TS-1 (one crossing), apertures TS-4, multiplexing (S08) | Mitigated in the budget: 87 dB paid once; REQ-CAP-003 met with margin ~9 at maximum range |
| R-4 | Simulator drift between pinned libraries | 2 | 3 | Pinned versions, analytic tests of every adapter | Mitigated |
| R-5 | An unverified citation reaches the code | 3 | 3 | Every [key] checked against the bibliography by tests; entries marked confident or verified | Mitigated; 21 entries hand-verified, the rest marked |
| R-6 | Over-claiming feasibility | 3 | 5 | Report fidelity with every rate (REQ-NET-002); closed forms checked by sampling (REQ-NET-003); "rate is not enough" (learn 03/19) | Mitigated; the 393 km headline now carries its 0.58 fidelity |
| R-7 | Pointing at 100 nrad from a planetary distance | 4 | 4 | Budget sensitivity (docs/budget); deep-space optical terminal heritage | Open |
| R-8 | Key cannot be distilled near maximum range (Werner error rate above 11 %) | 4 | 3 | Store key made near closest approach; purify; better memories | Open (learn 03/21) |
