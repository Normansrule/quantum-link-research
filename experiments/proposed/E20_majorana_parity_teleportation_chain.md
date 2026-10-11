# E20 — Scaling Majorana parity teleportation: from one hop to a chain

**Gap.** Crogman, Dang, and Erenso (2025) teleport one qubit across one pair of Majorana-encoded qubits [crogman2025], and [E18](E18_majorana_parity_teleportation_emulated.md) emulates that single hop. A network or a topological processor moves a state across many such hops. Neither the paper nor the emulations so far say how the fidelity falls with the number of hops, or what that demands of the device. E20 answers both: it emulates the protocol along a chain of *N* hops on a free cloud processor, measures the loss per hop, and turns a target chain length into a requirement on parity-readout quality.

**Physics.** A chain of *N* hops holds the input on mode 0 and *N* shared pairs on modes (1, 2), …, (2*N* − 1, 2*N*). Hop *h* measures the two parities of the holder mode *k* = 2*h* and its neighbour. Under the Jordan–Wigner transformation, $i\gamma_{2k+2}\gamma_{2k+3} = -X_kX_{k+1}$ and $i\gamma_{2k+1}\gamma_{2k+4} = Y_kY_{k+1}$ at every position, because the strings of adjacent modes cancel. So each hop is the same local Bell measurement as the single hop of P13, and its two parity bits drive the corrections on the next pair.

If one hop shrinks the teleported Bloch vector by *s*, the chain's average fidelity is

$$F_N = \tfrac12\,(1 + k\,s^N),$$

where *k* absorbs the one-time costs of preparation and final readout (*k* = 1 when they are perfect). The chain beats every classical strategy (2/3; Massar & Popescu, 1995) only while $k s^N > 1/3$. On a processor with two-qubit error *p*₂, each hop gives $s = (1-p_2)^2$, so a 1 % gate error allows 54 hops. On Majorana hardware, the paper's error budget (its Equations 18–20) gives each hop's fidelity, and $s = 2F_{\rm hop} - 1$ treats that bound conservatively (Nielsen, 2002). Without the bits Bob holds a coin flip at every length: each hop's two classical bits are what move the state (Bennett et al., 1993).

**Cheapest version ($0, milestone M4.8).** Run the chain for *N* = 1, 2, 3, … hops on 2*N* + 1 qubits in a line, with the no-bits control at the longest length, and fit *s* and *k*:

```
python experiments/bench/frontier/run_frontier.py chain --backend aer --hops 1 2 3
python experiments/bench/frontier/run_frontier.py chain --backend fake_torino --layout 0 1 2 3 4 5 6 --hops 1 2 3 --shots 8000
python experiments/bench/frontier/run_frontier.py chain --backend ibm_torino --layout <a line of 2N+1 qubits> --hops 1 2 3 4 5 6
```

On a local copy of a 133-qubit device, the rehearsal gave 0.837, 0.797, and 0.796 for one, two, and three hops, and 0.505 with no bits ([`../bench/frontier/rehearsal/`](../bench/frontier/rehearsal/)). The fit gives *s* ≈ 0.94 and *k* ≈ 0.70: about 11 hops above 2/3. The flat step from two hops to three shows that the qubits added for each hop differ in quality. The hardware run should therefore use a longer line, repeat each length, and record each qubit's calibration.

**What the device needs.** Take the gap Δ/*kT* = 5, poisoning 0.001 per readout window, and *L*/ξ = 6. The smallest readout signal-to-noise ratio μ₀/σ for each chain length and target fidelity is ([`qll/circuits/majorana_chain.py`](../../qll/circuits/majorana_chain.py) `required_snr`):

| Hops | Above 2/3 (beats classical) | Above 0.9 | Above 0.99 |
|---|---|---|---|
| 1 | 0.92 | 1.66 | 2.65 |
| 4 | 1.56 | 2.25 | 3.21 |
| 16 | 2.17 | 2.79 | not reachable |
| 64 | 2.71 | 3.42 | not reachable |
| 128 | 2.98 | not reachable | not reachable |

The "not reachable" entries are the scaling result. At 0.001 poisoning per readout, no readout quality keeps a 16-hop chain above 0.99, because poisoning alone caps each hop. A long Majorana chain therefore needs quasiparticle poisoning cut by an order of magnitude more than it needs better readout. That is a concrete question to bring to the device groups.

**Research version (with the CSUDH authors and a device partner).**
- Encode each logical qubit in a tetron at fixed parity, and emulate the parity readout as a weak, noisy measurement with the paper's misclassification model.
- Fit *s* per hop on hardware, and invert it through the error budget to the device knobs.
- Set the result against the devices of the paper's Table 2, then against measured poisoning times as partners report them.

**Failure modes to expect.**
- Qiskit prints classical bit 2*N* first (Bob's check). The analysis reads that character.
- Devices without feed-forward cannot run the chain mode. Deferring the corrections works, but it carries no classical bits.
- Qubit quality varies along the line, so one long fit can hide a single bad pair. Fit with and without each hop's qubits.

**Repo hook.**
- Model and circuits: [`qll/circuits/majorana_chain.py`](../../qll/circuits/majorana_chain.py).
- Tests: [`tests/test_majorana_chain.py`](../../tests/test_majorana_chain.py). They check the local parities on the fermionic operators at every position for 3, 5, and 7 modes, the scaling law in Qiskit Aer, no signalling at every length, and the readout requirement.
- Runner: `run_frontier.py chain`.
- Builds on [P13](../protocols/P13_majorana_teleportation_on_a_cloud_processor.md) and [E18](E18_majorana_parity_teleportation_emulated.md).
- Mission milestone M4.8 and requirement MR-4.8.

**Key references.** Crogman, H. T., Dang, T., & Erenso, D. (2025). *Quantum Reports, 7*, 42. https://doi.org/10.3390/quantum7030042 · Huang, H.-L., et al. (2021). *Physical Review Letters, 126*, 090502. https://doi.org/10.1103/PhysRevLett.126.090502 · Massar, S., & Popescu, S. (1995). *Physical Review Letters, 74*, 1259. · Nielsen, M. A. (2002). *Physics Letters A, 303*, 249. · Bennett, C. H., et al. (1993). *Physical Review Letters, 70*, 1895.
