# 09 From classical links to quantum channels

Phase 1 began with two channels between the rooms: a fiber that carries bits (the classical channel) and a hallway that carries photons. Until now the photons were used only to make key. This document is about the photons themselves: the **quantum channel**, which carries qubits. A qubit can be a polarization in superposition, or half of an entangled pair. This section sets out how the mission builds quantum channels, proves they are quantum, measures what they carry, and grows them from a hallway toward a network.

## What a quantum channel is, and what it is not

A quantum channel is the map that takes the state Alice sends to the state Bob receives. For one photon's polarization, it is fixed by sixteen numbers, the Pauli transfer matrix. Physically, the matrix says how the sphere of all polarizations is shrunk, rotated, and shifted on the way ([`qll/circuits/qubit_channel.py`](../../qll/circuits/qubit_channel.py)).

Three facts set the boundaries, and every plan below respects them:

1. **The photon is the message, at light speed or slower.** A quantum channel delivers what physically travels through it. Nothing reaches Bob faster than the photon, and collapse carries no message ([05](05_feasibility.md)).
2. **One qubit carries at most one classical bit, or two if the pair was shared beforehand** [holevo1973] [bennett1992]. A quantum channel is not a faster or bigger pipe for ordinary data. Its value is that it carries quantum states: for keys whose security rests on physics, for teleportation, and for linking quantum processors and sensors.
3. **Quantum channels need classical channels, and the reverse is not true.**
   - **Loss.** A lost photon is a *heralded erasure*: no detector clicks, and Bob knows it. Below 50 % transmission, a one-way link carries no qubits at all. Announcing over the classical channel which photons arrived recovers a rate proportional to the transmission [bennett1997erasure].
   - **Teleportation** needs two classical bits per qubit [bennett1993].
   - **Keys.** Key distribution needs public discussion.

   So the plan adds quantum channels to the classical ones; it does not replace them.

## Three ways to build a quantum channel

| Way | How it works | In this mission | What limits it |
|---|---|---|---|
| **Send the photon** | the qubit travels through air or fiber | the hallway (P10, P14), the rooftop (M3.2), the satellite downlink (Phase 3) | loss, which grows exponentially in fiber and with the square of distance in free space, and polarization drift |
| **Teleport it** | a shared entangled pair plus two classical bits per qubit | cloud processor now (M4.1, M4.7), photons between rooms later (M4.5) | the quality of the shared pairs, and the delay of the classical bits |
| **Chain it** | entanglement swapping through intermediate nodes (repeaters) | three-node network (M4.4), the repeater lab | memories that must outlast the classical round trip |

## How each channel is proved quantum and measured

1. **Certificate.** The entanglement fidelity satisfies $F_e \ge 1 - e_Z - e_X$ for every qubit channel. Any channel that could be replaced by a classical relay (measure, then resend) has $F_e \le 1/2$ [horodecki2003eb]. So the two error rates a BB84 link already measures certify that a channel is quantum, with a confidence level from the counts ([`qll/link/channel_tomography.py`](../../qll/link/channel_tomography.py)).
2. **Map.** Process tomography sends a third input direction, measures a third basis, and fits the Pauli transfer matrix [chuang1997].
3. **Capacities.** From the map, the code computes four rates:
   - the classical capacity [king2002];
   - the entanglement-assisted capacity [bennett2002];
   - the quantum capacity, as the hashing bound and the coherent information [bennett1996mixed] [devetak2005q], exact for amplitude damping [giovannetti2005];
   - the private capacity from the BB84 error rates [shor2000].

   The repeaterless bound [pirandola2017] caps what any protocol can do without repeaters.

The same three steps apply to the hallway, a rooftop, a fiber spool, a satellite pass, and teleportation. That is the framework: one data format, one estimator, one certificate.

## What the twin predicts for the two rooms

From the default P10 parts ([`qll/link/hallway_channel.py`](../../qll/link/hallway_channel.py)):

| Quantity | Value |
|---|---|
| Single photons that click | 13.8 % (the rest are heralded erasures) |
| Click-conditioned error rate, Z and X | 2.1 % |
| Entanglement fidelity of the clicked channel | 0.968 (the classical limit is 0.5) |
| Certified for single photons from decoys | at least 0.83 |
| One-way quantum capacity per photon sent | 0 |
| With heralding over the classical channel | 0.10 qubits per photon sent |
| Repeaterless bound | 0.215 per photon sent |

## The quantum-channel ladder

| Step | Milestone | Channel | Pass | Cost |
|---|---|---|---|---|
| 1 | **M1.8** (P14) | the hallway, single photons | certified quantum ($F_e$ bound above 1/2 at 99 %), mapped by tomography | about $20 |
| 2 | **M4.7** (P14, Part C) | teleportation on a cloud processor | certified quantum with the bits; entanglement breaking without them | $0 |
| 3 | **M2.2** | entangled pairs across the rooms through fiber | Bell violation, so the pair channel preserves entanglement | borrowed source |
| 4 | **M2.6** (E19) | superdense coding through the hallway | more than 1 bit per transmitted photon | about $600 |
| 5 | **M3.2–M3.3** | rooftop, then building to building | certificate and map outdoors at night | Phase 3 |
| 6 | **M4.5** | photonic teleportation between the rooms | teleportation channel certified quantum | outside funding |
| 7 | **M4.4** | three nodes, with swapping | end-to-end channel certified through the middle node | Phase 4 |

The lab's [channel page](https://normansrule.github.io/quantum-link-research/lab/channel/) shows each of these channels as a deformed Bloch sphere, with the certificate, the capacities, and a simulated tomography run whose log loads into the Python above.
