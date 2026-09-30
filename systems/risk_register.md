# Risk register

Likelihood and impact on a 1–5 scale; status as of this version, with the evidence in the repository.

| ID | Risk | L | I | Mitigation | Status |
|---|---|---|---|---|---|
| R-1 | Memory coherence falls short of the 6–45 min round trip | 4 | 5 | Trade TS-3; store-and-forward relay; purification (learn 03/20) | Open. Only the trapped ion clears the maximum round trip usefully, margin < 1.5×; crystals clear it with retrieval ≤ 1 % |
| R-2 | Thermal load of cryogenic memories in space | 3 | 4 | Flown-cooler comparison (REQ-SPC-003); room-temperature ion traps | Mitigated for ions (300 K); open for rare-earth crystals |
| R-3 | Diffraction loss at astronomical distance | 5 | 5 | Architecture TS-1 (one crossing), apertures TS-4, multiplexing (S08) | Mitigated in the budget: 87 dB paid once; REQ-CAP-003 met with margin ~11 at maximum range |
| R-4 | Simulator drift between pinned libraries | 2 | 3 | Pinned versions, analytic tests of every adapter | Mitigated |
| R-5 | An unverified citation reaches the code | 3 | 3 | Every [key] checked against the bibliography by tests; entries marked confident or verified | Mitigated; 21 entries hand-verified, the rest marked |
| R-6 | Over-claiming feasibility | 3 | 5 | Report fidelity with every rate (REQ-NET-002); closed forms checked by sampling (REQ-NET-003); "rate is not enough" (learn 03/19) | Mitigated; the 393 km headline now carries its 0.58 fidelity |
| R-7 | Pointing at 100 nrad from a planetary distance | 4 | 4 | Budget sensitivity (docs/budget); deep-space optical terminal heritage | Open |
| R-8 | Key cannot be distilled near maximum range (Werner error rate above 11 %) | 1 | 3 | Measure on arrival (BBM92 needs no memory); bank key for conjunction (TS-7) | Closed in 0.41: the risk came from charging key for the memory wait; measured on arrival, key flows on every day with a link (error rate ≤ 5 %) |
| R-9 | Sunlit Earth swamps the heralds at the Mars receiver (background light) | 5 | 4 | Source in space off Earth's disk (TS-1); coronagraph-grade stray-light control, floor 1e-9 (TS-6, REQ-CAP-005); narrow filters | Mitigated in the budget: purity ≥ 0.96 every day with a link; floor not yet demonstrated at 1 mrad |
| R-10 | Banked key is compromised at rest while it waits up to a synodic period | 2 | 5 | Tamper-evident, zeroizing storage split between two holders; spend oldest key first; bank sized to need, not to maximum (TS-7) | Open: the bank is tens of megabytes, so the cost is its protection, not its size |
