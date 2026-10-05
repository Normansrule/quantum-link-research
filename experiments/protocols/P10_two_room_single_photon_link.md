# P10 — The Two-Room Link: Quantum States From One Room to Another for Under $1,000

**What it shows.** Polarization qubits, carried by laser pulses so faint that most hold no photon and few hold more than one, sent from one room to another and turned into a shared secret key by the same protocol code the simulation uses. A fiber Ethernet link between the rooms carries the classical channel. A digital twin predicts every reading from your parts before you build. This is mission Phase 1 ([`systems/program/`](../../systems/program/README.md), milestones M1.1 and M1.3–M1.7), the low-budget version of Tier 3 of the [SEE 510 ladder](../../systems/see510/10_real_world_experiments.md), and stage S2 of flagship [F1](../flagship/F1_earth_to_earth.md).

**What it does not show.** Entanglement: the states are prepared in room A and measured in room B (prepare and measure). Entanglement between the rooms is Phase 2 (P03 source, borrowed). Security against an adversary who attacks the detectors or the four-diode source's side channels: the key is laboratory-grade, and the paper says so.

**The twin.** [`qll/link/two_room.py`](../../qll/link/two_room.py) turns your parts into a `LinkConfig`: mean photon number from pulse energy and filters, dark counts per gate from the SiPM datasheet, afterpulses as background, and polarizer extinction as misalignment. `predict` gives the click rate and error rate; `check_against_twin` compares a measured session with that prediction, line by line, PASS or CHECK. The preset [`systems/see510/hardware/two_room.json`](../../systems/see510/hardware/two_room.json) is generated from the default parts. With them the twin predicts, across a hallway:

| Quantity | Prediction |
|---|---|
| Click probability per pulse | 0.0585 (58,500 clicks per second at 1 MHz) |
| Error rate | 3.7 % |
| Ten-second session | accepted, about 12,800 net key bits after authentication |
| The same through 6 dB of fiber coupling at 405 nm | rejected: dark counts win (start in free space) |
| Without decoy pulses | rejected: no single-photon key can be guaranteed |

The numbers regenerate in [`systems/program/05_feasibility.md`](../../systems/program/05_feasibility.md).

## Safety
- **Laser.** A bare 405 nm diode of a few milliwatts is Class 3R: never look into the beam or a reflection, remove watches and rings, keep the beam below eye level, and wear 405 nm laser goggles during alignment (before the filters go in). After the neutral-density filters the beam holds under a photon per pulse and is harmless, but alignment always happens before the filters.
- **Violet light is hard to see** and its scatter is easy to underestimate; block every stray beam with matte black card.
- **SiPM bias** is about 27–30 V from a small boost module: low current, but keep it off while you rewire.
- **Two rooms.** Tape cables down across the doorway; put a sign on the door while the laser is on.

## Parts (planning prices, October 2026; verify before buying)
| Item | For | Planning cost |
|---|---|---|
| Two fiber media converters and a 10–30 m duplex patch cord through the door or a cable pass | classical channel (M1.1) | $40–150 |
| Two laptops, an Ethernet cable each | the sites | owned |
| Four 405 nm laser diodes (5 mW class) with a nanosecond pulse driver | the four BB84 states, one diode per state, fired at random per pulse | $40–120 |
| Film polarizers, a half-wave retarder, neutral-density filters (optical density 1–4) | encoding and attenuation | $50–120 |
| Three non-polarizing beamsplitters (two to combine the diodes, one at room B) and two polarizing beamsplitters | combining and analysis | $100–250 |
| Four onsemi MicroFC-30035 SiPMs ($48.61 each at Newark, October 2026) [onsemi2022microfc], breakout boards, a 30 V boost module, four fast comparators | detection | $230–350 |
| Two small FPGA boards (one per room) for pulse generation, gating, and counting | timing | $30–80 |
| A coaxial cable or second fiber for the pulse clock between the rooms | synchronization (public) | $10–30 |
| 3D-printed mounts, black tubes, lens pairs, black card, felt | mechanics | $30–80 |
| **Total** | | **about $530–1,180; likely about $600** |

The [Tier 1 bench](../../systems/see510/10_real_world_experiments.md) ($40–120) is a prerequisite and shares the laptops, the classical channel, and the logging code.

---

## Stage 0 — Simulate first (one evening, $0)
1. `python -c "from qll.link import two_room as T; print(T.predict())"` prints what the default bench should show. Change a field (`T.TwoRoomParts(sipm_dark_hz=500e3)`) to see what each part does.
2. Write a synthetic run as the two rooms will: `python -c "from qll.link import two_room as T; from qll.link.hardware_log import simulate_quantum, write_site_logs; write_site_logs(simulate_quantum(T.config()), 'room_a.csv', 'room_b.csv')"`.
3. Process it: `python -m qll.link.run ingest room_a.csv --bob room_b.csv --config systems/see510/hardware/two_room.json`.

**Pass.** The session is accepted, and you can say why the fiber variant and the no-decoy variant are not.

## Stage 1 — The classical channel through fiber (one afternoon; M1.1)
**Build.** Connect each laptop to a media converter, and the converters through the duplex patch cord between the rooms. Give the laptops static addresses on one subnet.
**Measure.** `python -m qll.link.net_transport newkey link.key` in room A; carry `link.key` to room B on a USB stick. Room B: `python -m qll.link.net_transport serve --key link.key`. Room A: `python -m qll.link.net_transport probe --host <B's address> --key link.key -n 10000 --path-m 15`.
**Pass.** 10,000 frames, no authentication failure, 99th-percentile round trip under 5 ms. The light's own round trip over 15 m is 0.1 µs; everything else is the computers.

## Stage 2 — The bright-light analogue across the rooms (one weekend; M1.3)
Run [Tier 1](../../systems/see510/10_real_world_experiments.md) with the transmitter in room A and the receiver in room B, aimed down the hallway through both doors. Log with `bench_tier1`, ingest with the Tier 1 preset. **Pass:** honest error rate near 0 %, intercept-and-resend near 25 %.

## Stage 3 — The single-photon receiver (two weekends; M1.4)
**Build.** Solder each SiPM to its breakout, bias it at breakdown plus 2.5 V (the datasheet's 24.7 V breakdown is typical; find yours), and feed its output through a fast comparator set at half a photoelectron to an FPGA input. Close everything in a light-tight box.
**Measure.** With the box dark, count for 10 s at bias steps of 0.5 V from breakdown to breakdown plus 5 V; record the temperature. Then give a dim LED a fixed current and record the count rate at the same steps. Then look for afterpulses: the fraction of counts that arrive within 1 µs of another.
**Simulate.** Put your dark rate, relative efficiency, and afterpulse fraction into `TwoRoomParts` and rerun `predict`.
**Pass.** Dark rate inside the datasheet's 300–860 kHz at 2.5 V overvoltage and about 21 °C; afterpulsing below 1 %. If the dark rate is higher, the box leaks light: tape every seam and try again in a dark room.

## Stage 4 — The source and its mean photon number (two weekends; M1.5)
**Build.** Four diodes, each behind a film polarizer at 0°, 90°, 45°, or 135°, combined by two beamsplitters into one beam. The FPGA fires one diode per 1 µs slot, chosen at random, at one of two drive currents (signal or decoy), or none (vacuum), and logs the choice. Seed its generator from a quantum random source if you have one (E06).
**Measure.** With no filters, measure the average power $P$ of each diode at each current with a photodiode; the pulse energy is $E = P/f$. Choose the filters with `T.attenuation_for(0.5, E, 405e-9)` and install them.
**Pass.** With the filters in, the ratio of SiPM count rates for signal and decoy pulses equals the ratio of mean photon numbers (0.5 : 0.1) within 10 %.

## Stage 5 — Receiver optics and alignment (one weekend)
Assemble room B's analyzer: a 50/50 beamsplitter chooses the basis passively; each arm has a polarizing beamsplitter and two SiPMs, and the diagonal arm has the half-wave retarder at 22.5° in front. Align with the filters out and the laser at a safe, dim setting, then confirm each diode lights its own detector: the leakage into the wrong detector is one over the extinction ratio. Write that number into `polarizer_extinction`.

## Stage 6 — Sessions between the rooms (two weekends; M1.6)
**Synchronize.** Room A's FPGA sends a clock pulse per slot over the coaxial cable; room B's FPGA counts them and opens a 5 ns gate at a fixed delay after each one, found by scanning the delay for the peak count rate. Timing is public: an adversary learns nothing from it.
**Log.** Room A writes `pulse, alice_bit, alice_basis, alice_intensity` for every slot; room B writes `pulse, bob_basis, bob_bit` for every slot with a click (the arm gives the basis, the detector the bit). When two detectors click in one slot, room B picks one of them at random; the standard practice that keeps the single-detector analysis valid.
**Process.** Copy room B's file to room A (or the reverse) and run `python -m qll.link.run ingest room_a.csv --bob room_b.csv --config two_room_measured.json`, with your measured parts written into the configuration by `T.write_preset(parts, Path("two_room_measured.json"))`. Then compare with the twin:

```python
from qll.link import two_room as T
from qll.link.hardware_log import run_from_site_logs
r = run_from_site_logs("room_a.csv", "room_b.csv", T.config(parts))
for row in T.check_against_twin(r.metrics, parts)["rows"]: print(row)
```

**Pass.** Every line PASS, and the session accepted. Copying a log between the rooms is a laboratory convenience that reveals Room A's raw bits on the copy; the protocol itself exchanges only what the authenticated classical channel carries, and a deployment runs each site's half on its own computer.

## Stage 7 — An eavesdropper in the hallway (optional, one weekend)
Put a third analyzer and four diodes halfway down the hallway: measure each pulse in a random basis and resend what you saw. **Pass:** the error rate rises toward 25 % of the intercepted fraction, the session is rejected above 11 %, and the decoy statistics flag the change.

## If it does not work
- **No clicks above dark counts:** the gate delay is off; scan it in 1 ns steps.
- **Error rate high in one basis only:** the half-wave retarder is not at 22.5°, or the 405 nm retarder is not a half wave at your diode's wavelength; measure and correct.
- **Decoy alert on an honest run:** the filters or the diode are not linear at the two currents; measure each intensity class's click rate separately.
- **Click rate drifts:** the diode heats; let it settle for 10 minutes, or pulse it at a lower duty cycle.

**Verifies.** Milestones M1.3–M1.6; SN-02, SN-06, SN-07, SN-11 of the SEE 510 case study with data; the claim that the simulation and the bench agree within stated tolerances.

**References.** Bennett, C. H., Bessette, F., Brassard, G., Salvail, L., & Smolin, J. (1992). Experimental quantum cryptography. *Journal of Cryptology*, 5, 3–28. https://doi.org/10.1007/BF00191318 · Ma, X., Qi, B., Zhao, Y., & Lo, H.-K. (2005). Practical decoy state for quantum key distribution. *Physical Review A*, 72, 012326. https://doi.org/10.1103/PhysRevA.72.012326 · Gisin, N., Ribordy, G., Tittel, W., & Zbinden, H. (2002). Quantum cryptography. *Reviews of Modern Physics*, 74, 145–195. https://doi.org/10.1103/RevModPhys.74.145 · onsemi. (2022). *C-Series SiPM sensors* [Data sheet].
