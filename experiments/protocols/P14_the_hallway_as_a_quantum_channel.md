# P14 — The Hallway as a Quantum Channel: Certify It, Map It, and Measure What It Can Carry

**What it shows.** The two-room link of [P10](P10_two_room_single_photon_link.md) already sends qubits: the polarization of each photon. This protocol stops treating the hallway as a pipe for key bits. Instead, it measures the hallway as a *quantum channel*, which is the map that takes the qubit Alice sends to the qubit Bob receives. It produces three results:

1. **A certificate that the channel is quantum.** No classical relay that measures each photon and resends it (an entanglement-breaking channel) could produce the error rates you measure. The certificate comes from the BB84 counts you already have. For every qubit channel, the entanglement fidelity satisfies $F_e \ge 1 - e_Z - e_X$, and every entanglement-breaking channel has $F_e \le 1/2$ [horodecki2003eb].
2. **The channel itself.** Process tomography gives the channel's Pauli transfer matrix: how the Bloch sphere of input polarizations is shrunk, rotated, and shifted on its way to room B [chuang1997].
3. **What it can carry.** From the measured channel, it computes the classical capacity, the quantum capacity, the entanglement-assisted capacity, and the private (key) capacity. It also shows the most important fact about photon links: a lost photon is a *heralded erasure*. Below 50 % transmission a one-way link carries no qubits at all [bennett1997erasure]. Heralding the arrivals over the classical channel recovers a quantum rate proportional to the transmission. Quantum and classical channels work together; neither replaces the other.

**Extra cost.** About $10–30: two quarter-wave retarders cut from one plastic film sheet, and a 3D-printed flip mount. This is mission milestone M1.8, verifying requirement MR-1.9. Part C runs the same analysis on teleportation over a free cloud processor (milestone M4.7, $0).

**The twin.**
- [`qll/circuits/qubit_channel.py`](../../qll/circuits/qubit_channel.py): representations, figures of merit, the certificate, and capacities.
- [`qll/link/hallway_channel.py`](../../qll/link/hallway_channel.py): the P10 parts as a quantum channel.
- [`qll/link/channel_tomography.py`](../../qll/link/channel_tomography.py): estimator, certificate with confidence, and log format.
- [`qll/circuits/teleport_channel_cloud.py`](../../qll/circuits/teleport_channel_cloud.py): the teleportation channel.
- [`tests/test_quantum_channels.py`](../../tests/test_quantum_channels.py) covers all four:
  - the certificate is checked on 200 random channels;
  - every capacity is checked against its closed form;
  - the hallway twin is checked against the link twin;
  - the tomography estimator is checked on known channels;
  - teleportation is checked against Qiskit Aer.

The [channel lab](https://normansrule.github.io/quantum-link-research/lab/channel/) runs the same arithmetic in the browser.

## What the twin predicts for the default P10 parts

| Quantity | Value | Meaning |
|---|---|---|
| Single-photon click probability $\eta$ | 0.138 | 86 % of photons are lost, and Bob knows which (no click) |
| Error rate in Z and X, click-conditioned | 2.1 % | misalignment plus dark clicks |
| Entanglement fidelity $F_e$ | 0.968 | the classical limit is 0.5 |
| Single-photon $F_e$ certified from decoys, $1 - 2e_1$ | ≥ 0.83 | above 0.5: the single-photon channel is quantum |
| One-way quantum capacity per photon sent | 0 | erasure above 50 % kills one-way quantum communication |
| Quantum rate with heralding, $\eta\,[1 - H(p)]$ | 0.10 qubits per photon | the classical channel announces which photons arrived |
| Repeaterless bound $-\log_2(1-\eta)$ [pirandola2017] | 0.215 | no protocol over this loss can do better without repeaters |

## Part A — Certify the channel from BB84 data (no new parts)

1. Run a normal P10 session (stage 6).
2. Group Bob's clicks by Alice's state:
   - $e_Z$ is the average error rate over H and V measured in Z;
   - $e_X$ is the average over D and A measured in X.
3. Take one-sided Clopper–Pearson upper limits on each of the four per-state error rates at $\alpha/4$ [clopper1934]. The certificate is
   $$F_e \ge 1 - \tfrac{u_H + u_V}{2} - \tfrac{u_D + u_A}{2}$$
   at confidence $1-\alpha$.

```python
from qll.link import channel_tomography as CT
counts = CT.read_log("tomography.csv")          # input, basis, outcome per click
print(CT.certify(counts, alpha=0.01))
```

**Pass.** `fe_lower` is above 0.5 at 99 % confidence. Report $e_Z$, $e_X$, and the bound. With laser pulses, also report the decoy bound $F_e \ge 1 - 2e_1$, which certifies the single-photon part of the channel.

**What it rules out.** It rules out every measure-and-resend relay, including the eavesdropper of P10 stage 8 at full interception. Run that stage as the control: the certificate must fail.

## Part B — Map the channel (two quarter-wave plates)

The P10 source makes H, V, D, and A, and the receiver measures Z and X. Mapping the channel needs a third input direction and a third measurement basis:
- **A circular input.** For tomography sessions, put a quarter-wave plate with its fast axis horizontal (0°) behind the D diode's 45° polarizer. That diode then sends circular light; call it R if Bob's flipped-in arm sends it to its "+" detector (the handedness label is a convention, so fix it once and keep it).
- **A circular measurement.** Put a quarter-wave plate on a flip mount in front of the X arm's half-wave plate, fast axis horizontal (0°). It turns R and L into D and A, which the half-wave plate and polarizing cube already separate, so flipped in, the X arm measures Y. Check the setting with the R diode: the "+" SiPM should take nearly all of its clicks.

Run four ten-second sessions and log every click as `input, basis, outcome`:

| Session | Inputs | Bases measured |
|---|---|---|
| 1 | H, V, D, A | Z, X |
| 2 | H, V, D, A | Z, Y (flip in) |
| 3 | H, V, R, A | Z, X |
| 4 | H, V, R, A | Z, Y (flip in) |

```python
R = CT.estimate(counts)                         # Pauli transfer matrix, least squares
from qll.circuits import qubit_channel as Q
print(R, Q.entanglement_fidelity(R), Q.is_physical(R), Q.is_entanglement_breaking(R))
```

**Pass.** The estimate is physical within its error, its diagonal matches the twin, and the off-diagonal terms reveal any rotation. A rotation is polarization drift, which you can correct with the waveplates.

## Part C — Teleportation is a quantum channel too (cloud, $0)

```bash
python -c "from qll.circuits import teleport_channel_cloud as TC; from qll.circuits.cloud_run import run_aer; \
from qll.link import channel_tomography as CT; k, c = TC.circuits('feedforward'); \
n = TC.counts_to_tomography(k, run_aer(c, 20000)); print(CT.estimate(n), CT.certify(n))"
```

Then run on a device (see [P12](P12_teleportation_and_superdense_coding_on_a_cloud_processor.md) for the backend options) with modes `feedforward` and `no_bits`.

**Pass.**
- With the bits, the teleportation channel is certified quantum. Its diagonal is $(1-p_2)^2$ under the depolarizing model.
- Without the bits it is $I/2$ for every input: entanglement breaking, with $F_e = 1/4$.

The comparison is the point. Entanglement plus two classical bits per qubit *makes* a quantum channel, and the bits are an essential ingredient.

## If it does not work

- **$e_Y$ much larger than $e_Z$ and $e_X$.** The quarter-wave plate's axis is off, or the film's retardance is not a quarter wave at 405 nm (plastic film is specified at a design wavelength). Measure its retardance with crossed polarizers.
- **The estimate is unphysical by more than its statistics.** The source's states are not what the labels say. Measure each diode's polarization with a polarizer and a power meter first.
- **The certificate fails while the BB84 session passes.** You are near threshold. More counts shrink the Clopper–Pearson margins as $1/\sqrt{n}$.

**Verifies.** Mission requirements MR-1.9 (Parts A and B) and MR-4.7 (Part C).

**References.**
- Horodecki, M., Shor, P. W., & Ruskai, M. B. (2003). Entanglement breaking channels. *Reviews in Mathematical Physics, 15*, 629–641. https://doi.org/10.1142/S0129055X03001709
- Chuang, I. L., & Nielsen, M. A. (1997). Prescription for experimental determination of the dynamics of a quantum black box. *Journal of Modern Optics, 44*, 2455–2467. https://doi.org/10.1080/09500349708231894
- Bennett, C. H., DiVincenzo, D. P., & Smolin, J. A. (1997). Capacities of quantum erasure channels. *Physical Review Letters, 78*, 3217–3220. https://doi.org/10.1103/PhysRevLett.78.3217
- Pirandola, S., Laurenza, R., Ottaviani, C., & Banchi, L. (2017). Fundamental limits of repeaterless quantum communications. *Nature Communications, 8*, 15043. https://doi.org/10.1038/ncomms15043
