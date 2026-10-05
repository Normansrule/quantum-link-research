# E17 — Can the way a shared state collapses carry a message?

**Gap.** "Entanglement Morse code" is one of the most common ideas people bring to quantum communication: encode a message in how one half of an entangled pair is measured, and read it from how the other half collapses. The no-signalling theorem [ghirardi1980] says it carries nothing, and Bell experiments with fast-switched analyzers have long been consistent with that [aspect1982]. What is missing is a teaching-grade experiment that asks the question directly and reports what a null result means quantitatively: an upper bound on the information per use, with its confidence level, plus controls that show the analysis would have caught a real channel. On a shared-chip processor the same test doubles as a crosstalk detector.

**Physics.** For any instrument $\{K_k\}$ of Alice's, Bob's state is $\rho_B' = \mathrm{Tr}_A\,\rho_{AB}$, independent of her choice. For polarization pairs, $P(a,b) = [1 + (-1)^{a\oplus b} V\cos 2(\alpha-\beta)]/4$ and Bob's marginal is 1/2. Statistics: a likelihood-ratio test of independence [casella2002], Clopper–Pearson intervals on Bob's conditional outcome rates [clopper1934], and an upper bound on mutual information from its convexity in the channel [cover2006].

**Cheapest version ($0).** Protocol [P11](../protocols/P11_collapse_code_on_a_cloud_processor.md) on a cloud processor's free plan: three schemes, three qubit pairs at increasing distance, two controls (teleportation with and without its two classical bits; an injected physical leak), and the E16 crosstalk measurement on the same pairs.

**Research version.** The same test with entangled photons in two rooms (mission milestone M2.4), then with Alice's switching and Bob's detection spacelike separated, which needs nanosecond switching and detectors far enough apart for light not to cross between the switch and the detection (D11).

**Failure modes to expect.** Unbalanced or non-interleaved messages make drift look like signal; readout crosstalk on neighboring qubits produces a real, small, distance-dependent dependence that is not signalling; a reversed bit order makes Alice's outcome look like Bob's.

**Repo hook.** [`qll/circuits/collapse_signalling.py`](../../qll/circuits/collapse_signalling.py), [`tests/test_collapse_signalling.py`](../../tests/test_collapse_signalling.py), runner [`experiments/bench/E17_collapse_code/`](../bench/E17_collapse_code/run_collapse_code.py); mission milestones M1.2 and M2.4; first paper [`systems/program/08_first_paper.md`](../../systems/program/08_first_paper.md).

**Key references.** Ghirardi, G. C., Rimini, A., & Weber, T. (1980). *Lettere al Nuovo Cimento*, 27, 293. · Aspect, A., Dalibard, J., & Roger, G. (1982). *Physical Review Letters*, 49, 1804. https://doi.org/10.1103/PhysRevLett.49.1804 · Bennett, C. H., et al. (1993). *Physical Review Letters*, 70, 1895. https://doi.org/10.1103/PhysRevLett.70.1895
