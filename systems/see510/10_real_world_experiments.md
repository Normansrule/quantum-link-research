# 10 Real-world experiments: from a tabletop analogue to a deployed link

The simulation (tasks 1–16) said what a two-site link should do. This ladder builds it, one rung at a time, from a setup that costs less than a textbook to one that needs a partner institution. Every rung follows the same pattern:
1. **Predict.** Run `python -m qll.link.run session --config systems/see510/hardware/tierN.json` with your parts' values.
2. **Build and measure.**
3. **Log.** Record the session in the experiment-log format of `qll/link/hardware_log.py`.
4. **Process.** Run `python -m qll.link.run ingest LOG.csv --config systems/see510/hardware/tierN.json`, so sifting, estimation, Cascade, verification, amplification, and key delivery run through exactly the code the simulation uses.
5. **Compare** the processed result with the prediction.

A disagreement points at the assumption that failed (03).

| Tier | Setup | Planning cost | Time | What is real | Security meaning | Needs it advances |
|---|---|---|---|---|---|---|
| 0 | Simulation only (done) | $0 | done | nothing physical | none (a model) | all, in simulation |
| 1 | Bright-light polarization analogue: laser pointer, polarizer film on servos, photodiode, Arduino | $40–120 | 2–3 weekends | bases, sifting, errors from optics, interception disturbance, the whole processing chain on measured data | none: bright light can be tapped | SN-01, SN-02 (analogue), SN-04, SN-07, SN-08 |
| 2 | Fiber channel characterization: telecom transceivers, power meter, attenuator, spool, wavelength multiplexer | $80–350 | 2–4 weekends | the channel's loss, connector loss, polarization drift, and cross-talk from classical traffic | none (no quantum states) | SN-06, SN-11, SN-14 |
| 3 | Decoy-state BB84 at the single-photon level: pulsed laser near 850 nm at three intensities, four-state encoder, single-photon detectors, timing | $2,000–8,000 | one semester | single-photon detection, real dark counts, real error rates, decoy-state bounds, real key from a real channel | laboratory-grade against photon-number splitting; detector attacks not addressed | SN-02, SN-03, SN-06, SN-07, SN-11 |
| 4 | Entanglement-based BBM92: down-conversion pair source, analyzers at both sites, time tagger | $15,000–60,000 (or a lent teaching kit) | one semester to a year | entangled pairs, a Bell test, key measured on arrival | laboratory-grade, not device-independent | SN-02, SN-03, SN-05, SN-07 |
| 5 | Commercial or testbed link over deployed fiber | $100,000+ or a partnership | months | a production system and real infrastructure | as certified by the vendor | SN-12, SN-13, SN-14, SN-15 |

Prices are planning ranges for new hobby parts or used laboratory equipment; check current listings. Named commercial products are examples of a class, not endorsements.

---

## Tier 1 — The bright-light polarization analogue

**Goal.** Run the complete BB84 processing chain on data measured with your own hands, and watch an intercept station raise the error rate, for less than a hundred dollars.

**How it maps to the link.**
- **Site A** is a laser module behind a polarizer disk on a servo. It sets 0° or 90° in the rectilinear basis, and 45° or 135° in the diagonal basis.
- **Site B** is a second polarizer (the analyzer) on a servo, at 0° or 45°, in front of a photodiode.
- **Reading the bit:** bright means bit 0, dark means bit 1, and a half-bright reading is ambiguous, so Site B flips its own coin. That reading is what a mismatched basis gives.
- **The intercept station** is a third analyzer with its own photodiode, plus a fourth polarizer with its own laser that re-sends what it measured.
- **The controller** is an Arduino, driven by `python -m qll.link.bench_tier1` over USB.

**Parts.**

| Part | Qty | Planning price | Notes |
|---|---|---|---|
| Arduino Uno or Nano (or clone) | 1 | $10–25 | runs `experiments/bench/see510_tier1/see510_tier1.ino` |
| Hobby servos, SG90 class | 4 | $8–16 | two for the sites, two for the intercept station |
| Laser modules, 650 nm, class 2 (≤ 1 mW) | 2 | $4–10 | Site A and the station; switched by a logic-level MOSFET or the module's enable pin |
| Linear polarizer film sheet | 1 | $8–15 | cut four disks; mount on the servo horns |
| Photodiodes, BPW34 class, with 100 kΩ–1 MΩ load resistors | 2 | $3–8 | Site B and the station |
| 5 V supply for the servos, breadboard, wires | — | $10–20 | join the grounds |
| 3D-printed mounts, a dark box or black card enclosure | — | $5–15 | room light is the "dark count" here |
| **Total** | | **$40–120** | |

A commercial version of the same idea, with half-wave plates and polarizing beamsplitters, is sold as a teaching kit (for example Thorlabs' quantum cryptography analogy kit); expect a price in the thousands of dollars.

**Build and measure, step by step.**
1. **Predict:** `python -m qll.link.run session --config systems/see510/hardware/tier1.json`. Note the expected error rate (about 1 %) and key length.
2. **Dry run with the twin:** `python -m qll.link.bench_tier1 --out data/see510/tier1_dry.csv`, then `python -m qll.link.run ingest data/see510/tier1_dry.csv --config systems/see510/hardware/tier1.json`. The twin models Malus's law, polarizer leakage, room light, and reading noise [hecht2017].
3. **Wire and flash** the Arduino as described in the sketch header. Mount the polarizer disks on the servo horns, align the laser through both disks onto the photodiode, and close the box.
4. **Check Malus's law:** with Site A at 0°, step Site B's analyzer from 0° to 180°. The reading should follow cos² of the angle. The ratio of the crossed reading to the aligned one is the leakage, so a good film gives under 2 %.
5. **Run with no interception:** `python -m qll.link.bench_tier1 --port /dev/ttyACM0 --pulses 4000 --out data/see510/tier1_run1.csv` (or `COM5` on Windows). That is about 30–60 minutes at 0.3–0.6 s per pulse.
6. **Process:** `python -m qll.link.run ingest data/see510/tier1_run1.csv --config systems/see510/hardware/tier1.json --out data/see510/sessions`.
7. **Intercept:** put the intercept station in the beam and run again with `--eve 1`. Process with `--set eve_fraction=1`.

**Pass.**
- With no interception, the error rate is under 5 %, the keys match after Cascade, and the session is accepted.
- With the station in line, the error rate is 25 % ± 5 % and the session is rejected.
- Both agree with the prediction within statistical error.

**What it proves.**
- The protocol code runs unchanged on measured data.
- Optics set the error floor.
- An intercept-and-resend station disturbs exactly as the theory says.

**What it does not prove.** Any security at all. Bright light splits instead of choosing, so Site B's coin stands in for quantum randomness, and an eavesdropper could tap part of the beam without being seen. The documents and the summary must say "classical analogue" every time.

**Safety (SN-10).**
- Use class 2 lasers only, and never look into the beam.
- Keep beams below eye level and terminate them on the photodiode.
- Power the servos separately from the Arduino's 5 V pin.

---

## Tier 2 — The fiber channel, characterized

**Goal.** Replace the simulation's fiber assumptions (A-02, A-03, A-14) with numbers measured on the fiber your link would use, including what happens when classical data shares it.

**Parts.**

| Part | Qty | Planning price | Notes |
|---|---|---|---|
| Fiber media converters with SFP slots, and 1310 nm and 1550 nm SFP transceivers | 2 + 2 | $40–120 | cheap, stable light sources at telecom wavelengths; they also carry real Ethernet |
| Handheld optical power meter, 1310/1550 nm calibrated | 1 | $20–60 | read in dBm |
| Visual fault locator (650 nm) | 1 | $10–20 | finds breaks and bad connectors |
| Single-mode patch cords and adapters (SC or LC, to match the transceivers) | 6–10 | $30–60 | |
| Inline variable optical attenuator | 1 | $20–80 | the "distance" of scenario 4 |
| Fiber spool, SMF-28 class, 1–5 km (surplus) | 1 | $50–250 | or a 100–500 m drop-cable reel to start |
| Coarse wavelength-division multiplexer pair (1310/1550) | 1 pair | $20–60 | puts classical traffic and a test wavelength in one fiber |
| Fiber cleaning kit | 1 | $10–20 | dirty connectors are the first source of loss |
| 3D-printed polarization paddles; inline polarizer or polarizing beamsplitter (optional) | — | $0–150 | polarization drift |
| **Total** | | **$80–350** (with optional parts) | |

**Measure, step by step.**
1. **Connector and insertion loss:** compare the power through a short reference cord with the power through each added connector pair, and the attenuator at each setting. The result goes into `extra_loss_db`.
2. **Fiber attenuation:** compare the power through the spool with a short cord at 1310 and 1550 nm. Divide by the spool length to get `attenuation_db_per_km`; expect about 0.35 and 0.2 dB/km.
3. **Polarization drift** (optional parts): pass light through an inline polarizer, the spool, and a second polarizer, and log the power every 10 seconds for an hour while someone walks past. The fraction in the wrong port, averaged over a session, is the starting value of `misalignment_error`. Paddles bring it back down.
4. **Coexistence (SN-14):**
   - Run Ethernet at 1310 nm through the multiplexer and spool.
   - Measure the power that leaks into the 1550 nm port with the 1550 nm source off. It is often below a hobby meter's floor (about −50 to −70 dBm), and then the floor is an upper bound.
   - Convert it to photons per detection window to bound a cross-talk background.
   - Set `crosstalk_click_prob` and run scenario 2 again.
   - Raman scattering from strong classical light reaches single-photon levels even when a power meter reads nothing, so only Tier 3 detectors can measure it.
5. **Two rooms:** run patch cords between two rooms on your own cable only. Never connect to a building's live fiber.
6. **Merge and predict:** copy the numbers into `systems/see510/hardware/tier2_channel.json` and merge them into `tier3.json` or `tier4.json`. Then run `session` to see what the measured channel predicts.

**Pass.**
- Every channel field in the configuration has a measured value with an uncertainty.
- The prediction is rerun with those values.

**What it proves.** The real loss and drift of your fiber, and how much classical traffic in the same fiber would cost a quantum signal. **What it does not prove.** Anything about single photons, since this is classical power metrology.

**Safety (SN-10).**
- Transceivers emit invisible infrared light. Never look into a fiber end or a transceiver port, and use the power meter or a viewer card.
- Fiber shards are sharp. Dispose of them in a marked container.

---

## Tier 3 — Weak-coherent BB84 at the single-photon level

**Goal.** A real prepare-and-measure key from single-photon detections, through a real attenuator or fiber, processed by the same code. This is protocol P07 (`experiments/protocols/P07_bb84_over_a_fiber_spool.md`) seen from the case study.

**Setup.**
- **Site A** is a pulsed laser near 850 nm, either one diode with a fast polarization switch or four diodes behind polarizers at 0°, 45°, 90°, and 135°, combined with beamsplitters. A field-programmable gate array (FPGA) chooses one per time slot from a random source. The pulse is attenuated to a mean photon number of about 0.1–0.5, verified with a calibrated power meter.
- **The channel** is a variable attenuator, free space across a room, or 780HP fiber with paddles.
- **Site B** makes a passive basis choice with a 50/50 beamsplitter, then a polarizing beamsplitter in each arm, the diagonal arm behind a half-wave plate, and four silicon single-photon detectors. The cheaper version uses an active basis switch and two detectors.
- **Timing:** an FPGA or a time tagger timestamps every detection against a shared clock.

**Parts.**

| Part | Planning price | Notes |
|---|---|---|
| Laser diodes near 850 nm with drivers capable of nanosecond pulses, or one diode and a liquid-crystal polarization rotator | $100–600 | an invisible beam: see safety |
| Polarizers, beamsplitters, half-wave plate, mounts | $300–1,000 | |
| ND filters and an inline or free-space attenuator; power meter with a calibrated sensor | $200–800 | to set and verify the mean photon number |
| Single-photon detectors: silicon single-photon avalanche diode modules (used), or silicon photomultipliers with comparators (cheaper, noisier) | $1,000–6,000 for 2–4 | the dominant cost; used modules are common |
| FPGA board for pulse generation and time tagging, or a used time tagger | $100–2,000 | |
| 780HP fiber spools and paddles (fiber version) | $100–400 | |
| **Total** | **$2,000–8,000** | |

**Measure, step by step.**
1. **Predict** with `tier3.json`, after merging in the Tier 2 values and your detectors' datasheet efficiency and dark-count rate. Convert the dark-count rate to a probability per detection window.
2. **Characterize the detectors:** dark counts with the input blocked, and efficiency against the calibrated power meter. Update `detector_efficiency` and `dark_count_prob`.
3. **Set the intensities:** measure the average power at Site A's output for each intensity, divide by the photon energy and the pulse rate, and set the attenuations for a signal mean photon number of 0.5 and a decoy of 0.1, with vacuum slots (laser off). Put the measured values in `mu_signal` and `mu_decoy`, and the proportions you programmed (for example 80 % signal, 15 % decoy) in `p_signal` and `p_decoy`.
4. **Run and log:**
   - Run sessions of 10⁶ slots.
   - Log one row per slot with Site A's bit, basis, and intensity class (`alice_intensity`: 0 signal, 1 decoy, 2 vacuum) and Site B's basis, click, and bit, matching the hardware_log format.
   - A detection with both outputs firing goes in as a random bit; record how many there were.
5. **Process:** `python -m qll.link.run ingest LOG.csv --config systems/see510/hardware/tier3.json`.
6. **Sweep the attenuator** from 0 to 20 dB (scenario 4 on hardware) and plot the detection probability and error rate against the twin's curves.
7. **Intercept:** an intercept-and-resend station (P07 step 6) on the link should raise the error rate by a quarter of the intercepted fraction.

**Pass.**
- Detection probability within 20 % of the prediction at every attenuator setting.
- Error rate under 5 % with no interception.
- The interception error within statistical error of e + f/4.
- Keys verified and accepted.

**What it proves.** Real single-photon detection statistics and a real key, with every processing step checked against the model, and the decoy-state bound on the single-photon detections [ma2005] computed from your own gains. **What it does not prove.** Security against detector blinding and similar attacks on the detectors. Running without decoys (one intensity) is a useful comparison: the worst-case analysis then guarantees no key beyond a few dB of loss, as scenario 8 shows.

**Safety (SN-10).** Laser diodes near 850 nm, before attenuation, can be class 3B and are invisible.
- Enclose the beam path.
- Use an infrared viewer card.
- Wear laser safety eyewear rated for the wavelength.
- Follow your institution's laser safety program.
- Detector modules need their specified bias and must be shielded from room light when powered.

---

## Tier 4 — Entanglement-based BBM92

**Goal.** Key from entangled photon pairs measured on arrival at both sites: the protocol behind the repository's Earth–Mars result, with a Bell test that certifies the source.

**Setup.**
- **Source:** a spontaneous parametric down-conversion source pumped near 405 nm, making polarization-entangled pairs near 810 nm (two crossed BBO crystals, or a periodically poled crystal in a Sagnac loop). This is protocol P03, `experiments/protocols/P03_spdc_bell_test.md`.
- **Fiber:** each photon is fiber-coupled to its site.
- **Analyzers:** at each site, a half-wave plate and a polarizing beamsplitter, with two silicon single-photon detectors.
- **Timing:** a time tagger finds coincidences within a few nanoseconds.
- **Commercial option:** teaching kits that package the source and analyzers exist (for example qutools' quED), sold on quote.

**Planning cost.** $15,000–60,000: the pump laser ($500–5,000), the crystals ($1,000–5,000), detectors ($4,000–20,000 for four), a time tagger ($3,000–15,000), and optics and mounts ($2,000–8,000). Many universities lend these for a semester project.

**Measure, step by step.**
1. **Predict** with `tier4.json`: each Site A detection is a slot, Site B's efficiency is collection times detection, accidental coincidences are the background, and the visibility V sets `misalignment_error = (1 - V)/2`.
2. **Check the source:** measure the Clauser–Horne–Shimony–Holt (CHSH) value S. It should be above 2, about 2.6–2.7 for a good source. Measure the visibility in both bases.
3. **Log coincidences:**
   - Each Site A detection is a row.
   - Site A's measured bit and basis go in the alice columns, and Site B's basis, detection, and bit in the bob columns.
   - Process with `ingest`. The post-processing is identical to BB84's [bennett1992bbm92].
4. **Add fiber** (spools between the source and Site B) and repeat, as scenario 2 on hardware.

**Pass.**
- S > 2 by at least five standard deviations.
- Error rate within statistical error of the prediction from the measured visibility.
- Keys verified and accepted at each spool length.

**What it proves.** A key built from entanglement, with the source certified by a Bell violation, and the same code from simulation to hardware. **What it does not prove.** Device-independent security, which needs a loophole-free Bell test and a different analysis, or anything about deployed fiber at distance.

**Safety (SN-10).** The 405 nm pump is usually class 3B: enclose it, use rated eyewear, and register the setup with your laser safety officer.

---

## Tier 5 — A commercial or testbed link over deployed fiber

**Goal.** The production end of the roadmap, outside the initial scope set by the handoff (no metropolitan infrastructure), recorded so that the design path is clear.

**Options.**
- **Commercial systems.** A pair of commercial QKD units (for example from ID Quantique or Toshiba) over campus dark fiber or leased fiber. These systems typically expose a key-management interface following ETSI GS QKD 014 [etsi2019qkd014]: the same three calls as `qll/link/key_store.py`. The demonstration application then runs against a real key-management service without change, which is what SN-12 and SN-15 ask.
- **A regional testbed.** Join a university or regional quantum network testbed as a user, which gives access to deployed fiber, timing, and trusted nodes without buying them.

**Planning cost.** $100,000 and up for a commercial pair; a partnership instead of a purchase for a testbed.

**What it proves.** Interoperability of the external interface with a real key-management service, and coexistence with real infrastructure. **What it does not prove.** Anything the vendor's certification does not cover.

---

## Which rung to climb first
For SEE 510's laboratory scope, Tier 1 and Tier 2 together cost under $500, take about a month of weekends, and exercise every block of the architecture with measured data:
- **Tier 1** supplies the sites, the processing chain, the monitor, the logs, and the key delivery.
- **Tier 2** supplies the channel.

Tier 3 is the first rung where the photons are real single photons, and the first that needs an institution's help with detectors and laser safety. The simulation stays the reference throughout: each rung's prediction is written before its measurement, and each rung's log runs through the same code.
