# P13 — Majorana Parity Teleportation on a Cloud Processor

**What it shows.** The measurement-only teleportation of Crogman, Dang, and Erenso (2025) [crogman2025], emulated on qubits. Its parity measurements become Pauli measurements under the Jordan–Wigner transformation [huang2021]. Four runs show what the classical bits carry: with two parity bits the state arrives (average fidelity 1); one parity bit reaches at most the classical 2/3, and the correction as written gives 1/2; with no bits the result is 1/2. Cost: $0. This is mission milestone M4.6 and proposal E18. It emulates the protocol's logic; topological protection is a property of Majorana hardware and is not emulated.

**The twin.**
- [`qll/circuits/majorana_teleport.py`](../../qll/circuits/majorana_teleport.py): exact fermionic model with six Majorana operators.
- [`qll/circuits/majorana_cloud.py`](../../qll/circuits/majorana_cloud.py): the mapped circuits.
- [`tests/test_majorana_teleport.py`](../../tests/test_majorana_teleport.py): checks the operator mapping, the fidelities state by state against the fermionic model, and the paper's appendix theorems.

## Stage 0 — Simulate (one evening)
```bash
python -m pytest tests/test_majorana_teleport.py
python experiments/bench/frontier/run_frontier.py majorana --backend aer
```
**Pass.** Average fidelities 1, 0.667, 0.5, and 0.5 for the two-bit, one-bit, as-written, and no-bits modes. In the one-bit mode, the states $|\pm\rangle$ arrive perfectly and the other four at 1/2: one parity bit carries one Bloch component.

## Stage 1 — Rehearse on a noisy device copy
`run_frontier.py majorana --backend fake_torino --layout 0 1 2`, on three qubits in a line. The rehearsal in [`../bench/frontier/rehearsal/`](../bench/frontier/rehearsal/) gave 0.835 (two-bit), 0.641 (one-bit), 0.505 (as written), and 0.495 (no bits). Device noise lowers the two-bit result from 1 but leaves it well above 2/3, and the one-bit result stays below 2/3. **Pass:** two-bit above 2/3, no-bits consistent with 1/2.

## Stage 2 — Hardware
Use the same command with a real device name (within the free monthly allowance). Report each mode's average fidelity with its 99 % interval, and the per-state table.

## Analyze
`run_frontier.py analyze results/*.json`. Then set the two-bit fidelity against the error budget (`qll.hardware.majorana_error_budget.teleport_fidelity`). Ask which readout signal-to-noise and poisoning per readout would give the same fidelity on Majorana hardware; that turns the emulation into a device requirement.

## If it does not work
- **The one-bit mode gives 1/2 for $|\pm\rangle$:** the parity bit's sign convention is flipped; the correction belongs on $p = +1$ in this model.
- **The two-bit mode is near 1/2:** the corrections are swapped; X is controlled by the Z-parity bit and Z by the X-parity bit.

**Verifies.** Mission requirement MR-4.6 (added with this protocol).

**References.** Crogman, H. T., Dang, T., & Erenso, D. (2025). *Quantum Reports, 7*, 42. https://doi.org/10.3390/quantum7030042 · Huang, H.-L., et al. (2021). *Physical Review Letters, 126*, 090502. https://doi.org/10.1103/PhysRevLett.126.090502
