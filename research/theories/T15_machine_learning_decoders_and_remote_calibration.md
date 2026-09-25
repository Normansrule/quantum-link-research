# T15 — Machine-Learning Decoders and Calibration Under Latency

**Claim.** Neural-network and other learned decoders now match or beat matching decoders on real surface-code data [bausch2024], and learned calibration routines keep processors tuned with less human intervention; both matter for a node that cannot be adjusted interactively from Earth because every command takes 3–22 minutes.

**Mechanism.** A decoder trained on the device's own syndrome statistics captures correlated and leakage errors that a graph decoder ignores; a calibration agent adjusts pulse parameters from measured fidelities. At Mars the constraint is autonomy: the node must decode, recalibrate, and decide locally, with Earth receiving summaries.

**Why it matters for a Mars link.** Every interactive protocol in this repository has a latency cost line; local autonomy removes rounds. A memory node that decodes its own syndromes and a link that calibrates its own pointing and timing are the difference between a link that works during conjunction recovery and one that waits 45 minutes per adjustment.

**What would change the design.** Compute at the node (radiation-tolerant, modest), a training pipeline that runs on synthetic data before flight, and a policy for when the node may act without Earth's confirmation, which is a systems-engineering decision recorded in the CONOPS.

**Evidence and status.** Decoders: demonstrated on published surface-code data [bausch2024]. Autonomous calibration: demonstrated in laboratories [kelly2018]. Space: deep-space probes already run autonomous fault protection; the quantum-specific version does not exist. TRL 3.

**Cheap version.** Train a small classifier on Stim syndromes from S04's repetition code and compare with the majority-vote decoder; then add a light-time delay to the "consult Earth" branch of a scheduler and measure the throughput loss.

**References.** Bausch, J., et al. (2024). Learning high-accuracy error decoding for quantum processors. *Nature*, 635, 834. https://doi.org/10.1038/s41586-024-08148-8 Kelly, J., et al. (2018). Physical qubit calibration on a directed acyclic graph. arXiv:1803.03226 Varsamopoulos, S., Criger, B., & Bertels, K. (2018). Decoding small surface codes with feedforward neural networks. *Quantum Science and Technology*, 3, 015004. https://doi.org/10.1088/2058-9565/aa955a
