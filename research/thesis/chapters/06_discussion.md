# Chapter 6 — Discussion (draft)

## 6.1 What the numbers say

The thesis question has a quantitative answer. Against a Mars-maximum round trip of 44.6 minutes, three demonstrated memories keep a pair useful for teleportation: the hour-class trapped-ion qubit with less than 1.5× margin at 99 % retrieval efficiency, and two europium-doped crystals with wide margin at 1 % and 0.5 % efficiency. Diamond and ensemble memories, which carry the strongest network record, reach the Moon and no farther. Lifetime and efficiency therefore trade against each other across today's platforms, and the honest architecture is heterogeneous: crystals or ions to hold entanglement across the wait, color centers or photons to interface and process. That trade is proposal E8.

The rate problem is separate from the memory problem and is worse. Diffraction over an astronomical unit leaves about 10⁻⁹ of the photons even for a 10 m receiver, so a bright source delivers pairs per hour, not per second. Multiplexing by three to six orders of magnitude (E9) or relays at intermediate points, which do not exist between Earth and Mars, are the only remedies. Relays at Sun–Earth L4/L5 solve a different problem, conjunction blackouts, and the model shows they keep a path open through every one.

Two proposals settled in software sharpen the picture. Device-independent certification survives the light time provided the pair rate exceeds roughly one pair per second for a good device (E10), so the security model can be the strongest one available without a change of architecture. And the transducer question is settled for now: no verified device keeps entanglement above the classical threshold, so the node must speak optics natively (E7).

The classical half is not a bottleneck: a DSOC-class terminal delivers tens of megabits per second beyond 2 au, and the two bits per teleported qubit are negligible. Latency is the whole cost, and no throughput hides it; the messenger's three reported numbers make this explicit.

## 6.2 Where the models are weakest

Atmospheric optical depths are representative, not measured at a site; relay pass yields are shaped on one published campaign; the all-photonic repeater is a redundancy model; and the memory decay is single-parameter depolarization or dephasing rather than a platform-specific spectral-diffusion model. Each simplification is stated in its module and listed in the backlog. The largest gap is empirical: no bench data yet exist, and the two requirements that need them (memory coherence versus temperature, and the exact Jinan-1 budget) remain unverified.

## 6.3 Lessons from the field's failures and successes

The lessons files (`experiments/lessons/`) record claims that did not survive: the retracted quantized-Majorana-conductance result, contested "supremacy" gaps that classical algorithms closed, boson-sampling benchmarks that were spoofed, and commercial QKD systems that were secure in theory and hacked in practice. Four habits in this work follow from them: every number carries a source and a year; every claim in code has an analytic test; capacity bounds are asserted rather than assumed; and over-claiming feasibility is a live risk in the register. The platforms that scaled (transmons, atom arrays, microsatellite QKD) did so by removing one dominant noise source at a time, reusing an existing supply chain, and optimizing one agreed metric. The Earth–Mars link should be designed the same way: the dominant loss is diffraction, the supply chain is DSOC-class terminals and the Deep Space Network, and the metric is secret bits per day at a stated fidelity with latency reported alongside.

## 6.4 Open problems

Ten open problems are ranked in `research/cutting_edge/02_open_problems.md`. The three the thesis considers decisive are memory lifetime versus efficiency, entanglement rate at astronomical-unit loss, and classical-latency-aware protocol design, which no published repeater or purification scheduler addresses at a 20-minute round trip.
