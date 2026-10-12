# E1 — Teleportation with the classical channel delayed to a planetary light-time

**Gap.** Every teleportation experiment to date closes the classical channel within microseconds to milliseconds. No one has completed teleportation where the two bits arrive 3–22 minutes after the Bell measurement, which is the operating regime of an Earth–Mars link.

**Physics being tested.** The no-signaling theorem says the delay changes nothing about Bob's state until the bits arrive; the memory-decoherence model says the fidelity when they arrive is $F=(2f(t)+1)/3$ with $f(t)$ the stored singlet fraction. The experiment measures $F$ versus classical delay and finds where it crosses $2/3$.

**Cheapest version (Tier 1, SPDC bench).** Do not delay the qubit, delay the *record*: run the CHSH/teleportation bench, log Alice's Bell-measurement outcomes with timestamps, and release them to Bob's analysis only after a software delay equal to the Mars light-time (`qll/channels/light_time_delay.py` `DelayQueue`). Show that the conditional correlations are identical for any delay: a direct classroom demonstration that the two bits, and nothing else, carry the state. Cost: zero above the Bell bench.

**Research version.** Store one half of an entangled pair in a Eu:YSO or NV-¹³C memory for the full light-time, transfer the two bits over a link throttled to the Deep Space Network round-trip time, apply the correction, and measure $F(t)$. Rare-earth crystals and trapped ions are the memories whose lifetimes already allow the 45-minute worst case.

**Cloud-processor version (free, milestone M4.3).** Delay the qubit itself, for microseconds instead of minutes. Teleport the six cardinal states on a free cloud processor with a delay instruction on Bob's qubit between Alice's measurement and the feed-forward corrections, and sweep the delay from zero to about twice T₂ ([`qll/circuits/teleport_delay_cloud.py`](../../qll/circuits/teleport_delay_cloud.py)). The idle qubit relaxes and dephases, so the average fidelity follows $F(t) = \tfrac12 + k\,(2e^{-t/T_2} + e^{-t/T_1})/6$, where $k$ is measured at zero delay and absorbs the gate and readout errors (Krantz et al., 2019; Nielsen, 2002). The run passes when the points follow that curve with the device's calibrated T₁ and T₂, cross 2/3 where it says, and the no-bits control stays at 1/2.

```
python experiments/bench/frontier/run_frontier.py delay --backend aer
python experiments/bench/frontier/run_frontier.py delay --backend fake_torino --layout 0 1 2 --delays 0 60 120 180
python experiments/bench/frontier/run_frontier.py delay --backend ibm_torino --layout 0 1 2
```

On a local copy of a 133-qubit device (Bob's qubit has T₁ = 170 µs and T₂ = 152 µs), the rehearsal gives 0.831, 0.732, 0.662, and 0.608 at 0, 60, 120, and 180 µs, against the model's 0.831, 0.727, 0.655, and 0.606. The no-bits control gives 0.498. The fidelity falls through 2/3 near 110 µs, about 33 km of light travel. A Mars link needs a memory about ten million times longer, which is the point of the research version.

**Digital twin.** [`qll/network/teleport_across.py`](../../qll/network/teleport_across.py) times every step with the light time. Pairs wait in both memories for a banking time $t_b$, and Bob's half waits $t_b + t_c$ more until the bits arrive. The Werner parameter decays as $w_0 e^{-(2t_b + t_c)/T_{\rm mem}}$, and the fidelity is $(2f+1)/3$ (Horodecki et al., 1999). A link of light time $t_c$ therefore needs $T_{\rm mem} > t_c/\ln(4f_0 - 1)$, which is 1.24 s for the Moon and 21.6 min for Mars at its farthest when $f_0 = 0.95$. The [frontier lab](https://normansrule.github.io/quantum-link-research/lab/frontier/) draws each case as a spacetime diagram and shows which memory coherence time, as reported, survives which distance; the photon storage efficiencies it uses are assumptions, not demonstrated at these storage times.

**Verifies.** REQ-CAP-001 (memory time vs light delay), REQ-PHY-002 (2 bits), and adds REQ-CAP-002 ("teleportation completes after a light-time-delayed classical channel").

**Failure modes to expect.** Timestamp synchronization between Alice and Bob (GPS-disciplined clocks); memory efficiency at long storage times (rare-earth AFC efficiency falls below 1% at hours); the temptation to read the qubit early, which the `NotYetArrived` guard makes impossible in software and which the protocol must forbid in hardware.

**Key references.** Bennett, C. H., et al. (1993). *Physical Review Letters*, 70, 1895. Horodecki, M., Horodecki, P., & Horodecki, R. (1999). *Physical Review A*, 60, 1888. Krantz, P., et al. (2019). *Applied Physics Reviews*, 6, 021318. Nielsen, M. A. (2002). *Physics Letters A*, 303, 249. Hermans, S. L. N., et al. (2022). *Nature*, 605, 663. Wang, F., et al. (2025). *PRX Quantum*, 6, 010302. Peres, A., & Terno, D. R. (2004). *Rev. Mod. Phys.*, 76, 93.
