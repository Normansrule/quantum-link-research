# 10 · Anywhere at light speed: the goal, stated so it can be verified

**The goal.** Communication that is as close to instantaneous as physics allows, wherever the two ends are, and secure.

This document turns that sentence into quantities the project can compute, build toward, and eventually measure. The model is [`qll/space/latency_floor.py`](../../qll/space/latency_floor.py), tested in [`tests/test_latency_floor.py`](../../tests/test_latency_floor.py); the [latency page](https://normansrule.github.io/quantum-link-research/latency/) runs the same arithmetic in the browser.

## 1. What "almost instantaneous" can mean

No signal travels faster than light, and shared entanglement does not provide a way around that: whatever one end does to its half of a pair, the other end's statistics are unchanged until a classical message arrives (Eberhard & Ross, 1989; Ghirardi et al., 1980). The one-line proof is in [05](05_feasibility.md). The goal therefore has a precise form:

> Deliver each message in **one trip at the light-time floor** of its route, with **nothing waiting on top**, and with security that does not depend on the message's own handshake.

The floor between two places on Earth is the great-circle distance over c; the chord through the planet is the absolute floor. Between bodies it is the straight line. The worst case on Earth (antipodal points) is 66.8 ms along the surface; the Moon is about 1.28 s; Mars is 3.1 to 22.3 minutes.

## 2. The latency budget

Every delivered message decomposes into three factors, each of which the project can attack separately:

| Factor | Definition | Today's typical case | What closes it |
|---|---|---|---|
| Route stretch | route delay ÷ floor | terrestrial fiber: 1.47 × the route factor, about 2.2× | hollow-core fiber (about 1.5× on the same route); a low-orbit laser mesh (1.15–1.4× over intercontinental distances); free space between bodies (1.0×) |
| Handshake trips | one-way trips before the receiver can read | a new TCP + TLS 1.3 connection: 5 | key agreed in advance: 1 |
| Key latency | trips spent making fresh key | QKD on demand: 3 | **banked key**: QKD run earlier, stored, spent as one-time pad or AES key: 1 |

The low-orbit mesh overtakes terrestrial fiber beyond about 980 km of surface distance and hollow-core fiber beyond about 2,600 km (`leo_crossover_km`); below those distances the climb to orbit costs more than the vacuum speed saves.

## 3. Why banking is the core idea

The project's three tracks already contain the mechanism. Work that would otherwise wait inside the message's trip is moved to before the message exists:

- **Banked key.** The two-room link (P10) and the Mars messenger (P15) both distill key ahead of demand. With a bank, a secure message costs exactly one trip on any route. The key bank sizing (TS-7, learn 03/22) is what keeps that true through solar conjunction.
- **Banked entanglement.** Teleportation with pairs stored in memories sends only the two classical bits, again one trip (E01, the frontier lab). The limit is memory lifetime, not distance: a pair must outlive the light time, which is what the memory crossover ([03/16](../../learn/03_quantum_communication/README.md)) and the frontier lab quantify.
- **Fast routes.** Free-space links (Phase 3: roofs, buildings, a satellite pass) are the vacuum-speed routes the project can reach; hollow-core fiber and laser meshes are outside its budget but appear in the model so the gap is visible.

## 4. Verification ladder

| Step | Claim | Evidence | Status |
|---|---|---|---|
| L0 | The floor and every route are computed correctly | closed-form tests: no route beats d/c; the geometry of each route; JavaScript equals Python for every pair of places | tested |
| L1 | The authenticated classical channel between two rooms adds little above its light time | P10 Stage 1 round-trip measurement (99th percentile under 5 ms on a 15 m path whose light round trip is 0.1 µs) | planned |
| L2 | A banked key delivers a secure message in one trip between two independent ends | [`qll/link/banked_messenger.py`](../../qll/link/banked_messenger.py): two operating-system processes, each loading only its own bank file from an accepted session, over the session-bound transport with an emulated path delay; `tests/test_banked_messenger.py` measures about 1.0 trip for banked key and 3.0 for key made on demand, as the model counts | tested on one machine (emulated delay); between two computers, planned |
| L3 | A free-space path between buildings carries the classical channel at its light time | Phase 3 outdoor link with timestamped frames | planned |
| L4 | Teleportation from banked pairs costs only the classical bits | cloud-processor E01 rehearsal now; memories later | modelled; rehearsal only |

Nothing in this ladder claims faster-than-light communication, and nothing will: the target is the floor itself.

## Running L2 yourself

```bash
python -m qll.link.banked_messenger bank --out-a bank_a.json --out-b bank_b.json      # one accepted session, one file per site
python -m qll.link.net_transport newkey link.key                                       # the transport's pre-shared key
python -m qll.link.banked_messenger serve --bank bank_b.json --key link.key --port 7070 --delay-ms 35.4 &
python -m qll.link.banked_messenger send --bank bank_a.json --key link.key --port 7070 --delay-ms 35.4 -n 10
```

With the Los Angeles to London delay of the low-orbit route (35.4 ms), a typical run reads banked messages after about 36 ms (1.02 trips) and messages keyed on demand after about 108 ms (3.06 trips); the small excess is the two computers' processing. The bank is a demonstration key from a simulated session, and each key is recorded as spent on disk before it is used, so no key serves twice, even after a restart.

## References

Eberhard, P. H., & Ross, R. R. (1989). Quantum field theory cannot provide faster-than-light communication. *Foundations of Physics Letters, 2*, 127–149. https://doi.org/10.1007/BF00696109

Ghirardi, G. C., Rimini, A., & Weber, T. (1980). A general argument against superluminal transmission through the quantum mechanical measurement process. *Lettere al Nuovo Cimento, 27*, 293–298. https://doi.org/10.1007/BF02817189

Handley, M. (2018). Delay is not an option: Low latency routing in space. In *Proceedings of the 17th ACM Workshop on Hot Topics in Networks*. https://doi.org/10.1145/3286062.3286075

Poletti, F., Wheeler, N. V., Petrovich, M. N., Baddela, N., Numkam Fokoua, E., Hayes, J. R., Gray, D. R., Li, Z., Slavík, R., & Richardson, D. J. (2013). Towards high-capacity fibre-optic communications at the speed of light in vacuum. *Nature Photonics, 7*, 279–284. https://doi.org/10.1038/nphoton.2013.45

Rescorla, E. (2018). *The Transport Layer Security (TLS) protocol version 1.3* (RFC 8446). Internet Engineering Task Force. https://doi.org/10.17487/RFC8446
