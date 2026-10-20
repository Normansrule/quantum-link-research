# P16 — An Off-Grid Link You Can Measure: The LoRa Range Walk

**What it shows.** The off-grid mesh model ([`qll/link/mesh_messenger.py`](../../qll/link/mesh_messenger.py)) decides whether two radios can talk from a link budget: transmit power, antenna gains, free-space path loss, an *assumed* 20 dB of excess loss for terrain and buildings, and the receiver's sensitivity. Every number in that model is computed, not measured. This protocol measures the one number the model guesses. Two radio boards, a laptop, and a walk give you:

1. **The path-loss exponent *n*** where you live. The signal falls as $10\,n\log_{10} d$: *n* = 2 in free space, and about 2.7 to 4 near the ground among buildings and trees [rappaport2002].
2. **The excess loss** over free space, which you can plug straight into `Mesh(excess_loss_db=...)`.
3. **The packet delivery ratio at each distance**, with a 95 % interval, compared with the model's yes or no for that link.

It is the first step in the repository that can produce a **MEASURED HARDWARE** result. It is eye-safe: there is no laser, only a 0.1 W radio in the unlicensed 902–928 MHz band.

**Why this experiment and not optics.** A bright-light polarization analogue of BB84 (key distribution) already exists as SEE 510 Tier 1 ($40, [`systems/see510`](../../systems/see510/10_real_world_experiments.md)), and the single-photon link (P10) is blocked pending a laser-safety review. The radio walk adds something new: it tests a model the repository already uses for its "messages without the internet" goal, and its result changes a number in the code.

**Cost.** About $60 for the two boards, or about $90 with the options. Prices are from Rokland's store, checked on 2026-10-19.

| Part | Qty | Price | Notes |
|---|---|---|---|
| Heltec WiFi LoRa 32 (V3), US915, with plastic case | 2 | $29.97 each ($26.97 without the case) | SX1262 radio, up to 21 ± 1 dBm; comes with a small antenna |
| USB-C power bank | 1 | $0 to $15 | powers the sender; you probably own one |
| USB-C data cable | 1 | $0 to $8 | connects the receiver to the laptop |
| Laptop with Python 3.12 | 1 | — | runs the logger and the analysis |
| Optional: camera tripod or a 2 m pole | 1 | $0 to $20 | holds the sender at a fixed, recorded height |
| Optional: a third board | 1 | $29.97 | for stage 4, the relay |

**Time.** One evening to set up, and two hours for one walk (eight to ten stops of about ten minutes each).

**The twin.** [`qll/link/radio_survey.py`](../../qll/link/radio_survey.py) reads the walk, fits it, and compares it with the mesh model. [`scripts/lora_survey_logger.py`](../../scripts/lora_survey_logger.py) records each stop. [`tests/test_radio_survey.py`](../../tests/test_radio_survey.py) checks the fit against synthetic walks drawn from a known law, the strict ingest, and the packet parsing.

## Safety and the law

- The boards are unlicensed devices under 47 CFR 15.247 in the 902–928 MHz band [cfr47_15_247]. Set Meshtastic's region to **US** so the firmware keeps to the band and its power limit. Do not raise the power above what the firmware allows, and do not fit a high-gain antenna to push past the limit.
- On these unlicensed settings encryption is lawful. Do not move the experiment to amateur-radio settings with encryption on, because amateur stations may not obscure the meaning of their messages [cfr47_97_113].
- **Always attach the antenna before powering a board.** Transmitting without an antenna can damage the radio.
- Walk on public paths, watch the traffic rather than the laptop, and do not leave the sender unattended in a public place.

## The physics you are testing

The radio reports **RSSI** (received signal strength indicator), which is signal **plus** noise, and **SNR** (signal-to-noise ratio). Near the edge of coverage LoRa still decodes up to 20 dB *below* the noise, so RSSI stops falling there. The analysis recovers the signal alone [semtech2013sx1276]:

$$S = \mathrm{RSSI} + \mathrm{SNR} - 10\log_{10}\!\left(1 + 10^{\mathrm{SNR}/10}\right)$$

It fits the log-distance law with log-normal shadowing [rappaport2002]:

$$S(d) = S(100\ \mathrm{m}) - 10\,n\,\log_{10}(d / 100\ \mathrm{m}) + X_\sigma$$

The model's prediction is $S = P_{tx} + G_{tx} + G_{rx} - \mathrm{FSPL}(d) - L_{excess}$ [friis1946]. The receiver's sensitivity on Meshtastic's LONG_FAST preset (spreading factor 11, 250 kHz, coding rate 4/5 [meshtastic2026presets]) is −131.5 dBm with a 6 dB noise figure [semtech2015an1200_22].

## What the model predicts (SIMULATED)

On LONG_FAST at 20 dBm, with 2 dBi antennas held 1.5 m above the ground, the mesh model with its default 20 dB excess loss predicts:

| Distance | Model margin above sensitivity |
|---|---|
| 100 m | 64 dB |
| 1 km | 44 dB |
| 5 km | 30 dB |
| 10 km | 24 dB |

The model would call every link up to the **10.1 km radio horizon** good. A 16-byte packet takes 0.29 s on air. Experience with handheld LoRa near the ground in a city suggests one to three kilometers, not ten. The gap between those two numbers is what this walk measures. If the model is right, you will see it. If it is not, you will have the number that fixes it.

## Stage 1 — Set up the two boards (one evening)

1. Flash both boards with Meshtastic from the web flasher (flasher.meshtastic.org) in Chrome. Pair each one with the Meshtastic phone app.
2. On both boards, set the region to **US** and the modem preset to **LONG_FAST**. Write down the channel frequency the app shows (the default is 906.875 MHz).
3. On the **sender**, enable the Range Test module as sender with an interval of **30 s**, as the Meshtastic documentation suggests for LONG_FAST [meshtastic2026rangetest]. Write down its transmit power setting and its node id (it looks like `!a1b2c3d4`).
4. On the **receiver**, leave the Range Test module off. Plug it into the laptop.
5. Install the logger's one extra package: `pip install meshtastic`.
6. Test indoors with both boards on a table. Run the logger for two minutes (see Stage 2). It should print about four packets with RSSI near −40 dBm.

## Stage 2 — The walk (two hours)

1. Fix the sender at a recorded height: a tripod, a pole, or a windowsill. Note what is around it.
2. Pick a straight path with a clear view if you can, such as a long street, a park, a beach, or a levee path. Mark stops at about 50, 100, 200, 400, 800, 1200, 1600, 2000, 2400, and 3200 m, using a map app for the distances.
3. At each stop, hold the receiver at a recorded height and run:

```bash
python scripts/lora_survey_logger.py --out data/lora/walk1.csv --stop 0 --distance-m 50 --minutes 10 \
    --sender '!a1b2c3d4' --tx-dbm 20 --tx-height-m 1.5 --rx-height-m 1.5 --site "your path" --notes "clear sky"
```

Raise `--stop` by one and change `--distance-m` at each stop. Ten minutes at a 30 s interval is 20 packets. The logger keeps only direct Range Test packets from the sender (it drops copies another node relayed) and records each sequence gap as a lost packet. The first stop also writes `walk1.csv.run.json` with the radio settings and `"origin": "measured"`.

4. Keep walking past the first stop where packets stop arriving, so the log has at least one stop at or beyond the edge.

## Stage 3 — Analyze (ten minutes)

```bash
python -m qll.link.radio_survey report data/lora/walk1.csv
```

It prints the label (**MEASURED HARDWARE** only when the sidecar says `measured`), the SHA-256 (Secure Hash Algorithm 256) of the log, the fitted exponent *n* and spread σ, the excess loss over free space beside the model's 20 dB, the range at 10 dB margin from the fit, and a table per stop. Add `--json` for a machine-readable copy. To see the output before you own a radio, `python -m qll.link.radio_survey simulate demo.csv` writes a synthetic walk, which is labelled SIMULATED.

**Pass.** The report runs, the fit uses at least five stops, and every stop's delivery ratio has its interval. That is a valid measurement whatever the numbers turn out to be. The experiment does not "fail" when the model is wrong; it tells you how wrong.

**Feed it back.** Put the measured excess loss into the mesh model, re-run `mesh_messenger.mountain_scenario`, and record in `docs/SESSION_LOG.md` whether the ridge relay still makes the difference.

## Stage 4 (optional) — A wall, then a relay

- **Obstruction.** Repeat four stops with a building between the radios. The difference in excess loss is the building's loss, the `obstructed` entry of `Mesh`.
- **Relay.** Place a third board halfway, as a relay, where the end-to-end link failed in Stage 2. Send text messages from the phone app and note whether each one shows as delivered (an acknowledgment came back) or only as sent. The model's delivery states (`QUEUED`, `RELAYED`, `DELIVERED`, `UNREACHABLE`) predict which. Logging this automatically is FUTURE RESEARCH. For now, keep it in a lab notebook.

## If it does not work

- **No packets indoors.** Check that both boards are on the same region, preset, and channel, and that the sender's Range Test interval is not 0.
- **The logger finds no board.** Pass `--port` (on Windows something like `COM5`; in WSL, use `usbipd` to attach the device or run the logger from Windows Python).
- **Every stop receives everything.** The walk was not long enough. Go further, or lower the sender's power to shorten the range.
- **The exponent comes out below 2.** You are probably fitting only stops near the edge, where faint packets were lost. Faint packets that never arrive are missing from the fit, which biases *n* low near the edge. Include close stops.

## What this result is, and is not

The report is a **measurement of one radio link on one day along one path**. It is not a coverage map, a city-wide exponent, or a measurement of the mesh's delivery. Report the site, the date, the weather, the antenna heights, and what stood between the radios. The repository's labels apply: a walk you ran is MEASURED HARDWARE, a walk `simulate_survey` wrote is SIMULATED, and nothing in this protocol involves quantum states. The radio carries the classical messages that every quantum link still needs: teleportation costs two classical bits per qubit, and those bits travel no faster than light.

## Key references

- Friis, H. T. (1946). A note on a simple transmission formula. *Proceedings of the IRE* 34(5), 254–256.
- Rappaport, T. S. (2002). *Wireless Communications: Principles and Practice*, 2nd edition. Prentice Hall. The log-distance law with log-normal shadowing, and the radio horizon.
- Clopper, C. J., and Pearson, E. S. (1934). The use of confidence or fiducial limits illustrated in the case of the binomial. *Biometrika* 26(4), 404–413.
- Semtech Corporation (2013). SX1276/77/78/79 data sheet: packet RSSI, SNR, and time on air. Semtech Corporation (2015). AN1200.22, LoRa modulation basics: demodulator SNR limits.
- Meshtastic (2026). Radio settings (modem presets) and Range Test module documentation, meshtastic.org, read on 2026-10-19.
- U.S. Federal Communications Commission. 47 CFR 15.247 (unlicensed 902–928 MHz devices) and 47 CFR 97.113 (amateur prohibited transmissions).
