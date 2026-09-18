# F1 — Scalable communication between two computers on Earth

## The question
Can two independent computers in one city share heralded entanglement at a useful rate and use it to teleport qubits and grow keys, with every classical message routed at light speed and every number traceable?

## Physics (all in `learn/`)
- Heralded entanglement by a midpoint Bell measurement on photons from two nodes ([03/02](../../learn/03_quantum_communication/02_teleportation_and_swapping.md)); success per attempt $p\approx\frac12(\eta_{\rm node}\eta_{\rm fiber})^2$ for two-photon schemes.
- Fiber loss $10^{-\alpha L/10}$; at 637 nm (NV) $\alpha\approx8$ dB/km, so frequency conversion to 1550 nm is mandatory beyond a few km ([03/05](../../learn/03_quantum_communication/05_transduction.md), [02/03](../../learn/02_qubit_modalities/03_diamond_nv_and_group_iv.md)).
- Herald round trip $2L/(c/n)$: 0.25 ms for 25 km; the memory must hold that long, which every NV/SiV node does easily.
- Phase stabilization of the two arms is required for single-photon schemes; two-photon schemes trade rate for robustness.

## Stages
| Stage | What | Pass | Cost / time | Files |
|---|---|---|---|---|
| S1 simulate | Aer + Stim model of two nodes, midpoint BSM, `ClassicalMessage` heralds; rate and fidelity vs L | rate and $F$ reproduce Stolk 2024 within 3× | software, 2 weeks | Phase 2 circuits, Phase 4 `repeater_chain.py` |
| S2 bench | P03: SPDC source, HOM, CHSH; then split the two arms onto a 1 km fiber spool each | $S>2.2$ after the spool; HOM visibility > 85 % | $5–15k, one semester | [P03](../protocols/P03_spdc_bell_test.md) |
| S3 campus | two labs, deployed campus fiber (1–3 km), GPS-disciplined clocks, midpoint at a third location | herald rate > 1 Hz; $S>2.2$; teleportation $F>0.7$ | detectors + timing, one semester | new protocol P05 (NEXT_100 #66–68) |
| S4 metro | partner lab across the city; frequency conversion if solid-state emitters are used | match published metro results | collaboration | [done/08](../done/08_nv_remote_entanglement_and_network.md) |

## What "scalable" means here
Rate per node pair must not collapse as nodes are added: multiplexing (time-bin, frequency), a link-layer protocol ([T01](../../research/theories/T01_quantum_internet_stack.md)), and a routing rule ([T08](../../research/theories/T08_entanglement_routing_and_qos.md)) are part of the deliverable, tested in SeQUeNCe with 3, 5, and 10 nodes.

## Requirements verified
REQ-CIR-001..003, REQ-PHY-002, REQ-NET-001 (metro scale), plus a new REQ-F1-001: "two nodes deliver heralded pairs at > 1 Hz over ≥ 1 km deployed fiber with $S>2.2$."

## Key references
Stolk et al. (2024) *Sci. Adv.* 10, eadp6442 · Knaut et al. (2024) *Nature* 629, 573 · Pompili et al. (2021) *Science* 372, 259 · Dahlberg et al. (2019) *SIGCOMM* · Dehlinger & Mitchell (2002) *Am. J. Phys.* 70, 903.
