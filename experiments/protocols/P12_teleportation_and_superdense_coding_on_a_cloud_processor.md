# P12 — Teleportation and Superdense Coding on a Cloud Processor

**What it shows.** What shared entanglement does deliver, each time with the control that shows what it cannot do alone. Teleportation moves an unknown qubit using one Bell pair and two classical bits [bennett1993]: with the bits fed forward, the average fidelity exceeds the classical limit of 2/3 [massar1995]; without them it is exactly 1/2. Superdense coding sends two classical bits by transmitting one qubit of a shared pair [bennett1992]; if the qubit is not sent, the receiver guesses the two bits a quarter of the time. Cost: $0 on a free cloud plan. These are mission milestones M4.1 and M4.2 ([`systems/program/`](../../systems/program/README.md)), and the teleportation run is a control for paper 1 (P11).

**The twin.**
- [`qll/circuits/teleport_cloud.py`](../../qll/circuits/teleport_cloud.py) gives the three teleportation modes (feed-forward, deferred correction, no bits) on the six cardinal states. They form a 2-design, so their mean fidelity is the average over all inputs [dankert2009]. The module also has the closed form for a depolarized pair, $F = (1 + (1-p)^2)/2$.
- [`qll/circuits/superdense_cloud.py`](../../qll/circuits/superdense_cloud.py) gives superdense coding and its keep-the-qubit control.
- [`qll/circuits/cloud_run.py`](../../qll/circuits/cloud_run.py) runs the circuits on the ideal simulator, a noisy copy of a device, or the device itself.
- [`tests/test_cloud_frontier.py`](../../tests/test_cloud_frontier.py) checks each against exact results.

## Stage 0 — Simulate (one evening)
```bash
python -m pytest tests/test_cloud_frontier.py
python experiments/bench/frontier/run_frontier.py teleport --backend aer
python experiments/bench/frontier/run_frontier.py teleport --backend aer --noise 0.1      # F = (1 + 0.9^2)/2 = 0.905
python experiments/bench/frontier/run_frontier.py superdense --backend aer
```
**Pass.**
- Teleportation: fidelity 1 with the bits and with deferred correction, 0.5 without the bits, and about 0.905 with the 0.1 noise.
- Superdense coding: success 1 and two bits per use when the qubit is sent; 0.25 and zero bits when it is kept.

## Stage 1 — Rehearse on a noisy device copy (one evening)
`teleport --backend fake_torino --layout 0 1 2` and `superdense --backend fake_torino --layout 0 1`; choose three connected qubits in a line for teleportation. The rehearsal in [`../bench/frontier/rehearsal/`](../bench/frontier/rehearsal/) gave:
- teleportation: 0.835 with feed-forward, 0.951 deferred, 0.505 without the bits;
- superdense coding: 0.79 success (1.1 bits per use) when the qubit is sent, 0.25 when it is kept.

**Pass.** Feed-forward fidelity above 2/3 and no-bits fidelity consistent with 1/2.

## Stage 2 — Run on hardware (within the monthly allowance)
Use the same commands with a real device name. If the device has no feed-forward, the runner skips that mode and records why; the deferred mode still shows the fidelity, but it carries no classical channel. Note the transpiled depth: the gap between feed-forward and deferred fidelity is the price of a mid-circuit measurement and its classical latency on that device.

## Analyze
`python experiments/bench/frontier/run_frontier.py analyze results/*.json` reprints every verdict from the stored counts. Report per-state fidelities, the pooled average with its 99 % Clopper–Pearson interval, and the superdense confusion matrix.

## If it does not work
- **Fidelity near 1/2 even with feed-forward:** the classical bits are mapped to the wrong corrections. Check the order: X controlled by Alice's second bit, then Z by her first.
- **Superdense coding below 0.5 on hardware:** readout error dominates; compare with the device's reported readout error for those two qubits.

**Verifies.** Mission requirements MR-4.1 and MR-4.2.

**References.** Bennett, C. H., et al. (1993). *Physical Review Letters, 70*, 1895. https://doi.org/10.1103/PhysRevLett.70.1895 · Bennett, C. H., & Wiesner, S. J. (1992). *Physical Review Letters, 69*, 2881. https://doi.org/10.1103/PhysRevLett.69.2881 · Massar, S., & Popescu, S. (1995). *Physical Review Letters, 74*, 1259. https://doi.org/10.1103/PhysRevLett.74.1259 · Dankert, C., Cleve, R., Emerson, J., & Livine, E. (2009). *Physical Review A, 80*, 012304. https://doi.org/10.1103/PhysRevA.80.012304
