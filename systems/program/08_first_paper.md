# 08 Papers: the first in detail, and the two after it

## Paper 1 (milestone M1.2): "Can the way a shared state collapses carry a message? A measured bound on a cloud quantum processor"

**Research question.** Can a sender encode information in how she measures or acts on her half of an entangled pair, such that a receiver who hears nothing else can read it from his own outcomes? If not, how small is the bound a modest experiment can set, and what does a shared-chip processor do to the answer?

**Hypotheses.**
- **H0 (quantum mechanics).** Bob's outcome distribution does not depend on Alice's choice; the information per use is 0 [ghirardi1980].
- **H1 (signalling).** Bob's outcome rate differs between Alice's two choices by some δ ≠ 0.
- **H2 (device).** On a shared chip, a small dependence appears for neighboring qubits, shrinks with distance, and tracks the measured crosstalk (E16): a physical disturbance through the chip, not signalling.

**Design.** Three encodings (measurement basis, measure or not, flip or not); three qubit pairs at increasing separation; balanced random messages, with the two message values interleaved in each job so drift affects both alike. Two controls: teleportation with and without its two classical bits (the analysis must read the message only with them), and an injected dissipative leak of 0.1 (the analysis must detect it). Shot budget from `uses_to_detect`: 74,390 uses per message value detect a 1 % bias at the 1 % level with 90 % power. Protocol P11; runner and analysis in the repository.

**Analysis plan (fixed before the data, and stated as such in the paper).**
1. For each run, a likelihood-ratio test of independence of Bob's outcome and Alice's bit [casella2002]; significance level 1 %, with a Bonferroni correction across the nine scheme-and-pair runs.
2. Clopper–Pearson intervals on Bob's conditional outcome rates [clopper1934]; the 99 % upper bound on the information per use is the largest mutual information over the corners of that box, which is valid because mutual information is convex in the channel [cover2006].
3. Regress any measured bias on the qubit pair's distance and on the E16 crosstalk for that pair.
4. Report every run, including those that show nothing.

**Expected result.** No dependence for distant pairs, with the information per use bounded near $10^{-4}$ bit at about $10^5$ uses per message value. A possible small dependence for neighbors, explained by crosstalk. A bound, not a "proof," and the paper says so.

**Threats to validity.**
- *Internal:* bit-order mistakes, unbalanced messages, and drift. The controls and interleaving address them.
- *Construct:* on one chip, "Alice" and "Bob" are not separated in space. That is why H2 exists, and why Phase 2 (M2.4) repeats the test with photons in two rooms.
- *External:* one vendor's device.

**Outline.**
1. Introduction: the idea and why people keep proposing it.
2. Theory: the one-line no-signalling proof, and what the correlations do give.
3. Method: encodings, circuits, controls, and shot budget.
4. Statistics: the test, the intervals, and the convexity bound.
5. Results: nine runs and two controls; the crosstalk regression.
6. Discussion: what a bound means; the two-room follow-up.
7. Reproducibility: code, data, and commands.

**Figures.**
1. The circuit for each scheme.
2. Bob's outcome rate for each message value, per run, with intervals.
3. The information bound against the number of uses, falling as $1/n$, with the data points.
4. Bias against qubit distance, overlaid with the E16 crosstalk.
5. The two controls: teleportation with and without the classical bits, and the injected leak.

**Where to send it (judge fit with your advisor).**
- A physics-education journal such as the *American Journal of Physics* or the *European Journal of Physics*: the experiment is a teaching-grade test of a common misconception, with open code.
- A student or poster track at an IEEE quantum-engineering conference.
- A preprint on arXiv (quant-ph) as soon as the draft is stable.

**Timeline.** Six weeks at ten hours a week: one week of simulation, one of rehearsal on a fake device, one hardware session (within the free allowance), two of analysis and writing, and one of revision with your advisor.

## Paper 2 (milestone M1.7): "A twin-validated single-photon link between two rooms for under $1,000"

Polarization BB84 with decoy pulses, four silicon photomultipliers, and FPGA timing between two rooms, with a fiber Ethernet classical channel. Every measured quantity is predicted beforehand by an open digital twin, and the paper reports measurement against prediction line by line (`check_against_twin`). Contributions: the bill of materials, the twin, the per-site data format, and an honest list of what the key does not protect against (the four-diode side channel and detector attacks). Venue: physics-education or instrumentation journals, or a conference workshop on quantum networking testbeds.

## Paper 3 (milestone M2.5): "Entanglement between two rooms on a student budget"

A Bell test above the classical bound between the rooms, an entanglement-based key from the same protocol code, and the collapse code repeated with photons in separate rooms (M2.4): Bob's file alone shows nothing, and the correlation appears when the files are compared. This closes the question paper 1 opened, with the separation that a chip cannot give.
