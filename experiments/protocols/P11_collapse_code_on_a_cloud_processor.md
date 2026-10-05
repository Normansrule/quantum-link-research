# P11 — The Collapse Code on a Cloud Processor

**What it shows.** Whether the way one half of an entangled pair collapses can carry a message to the other half, asked as a measurement rather than argued. Alice encodes each bit of a message in what she does to her qubit (measure in one basis or another, measure or not, flip or not); Bob, who never hears from her, tries to read the message from his own outcomes alone. The analysis tests for any dependence, bounds the information per use at 99 % confidence, and runs two controls that prove it would notice a real channel. Cost: $0, on the free plan of a cloud quantum processor (up to 10 minutes of runtime every 28 days in March 2026 [ibm2026openplan]). This is mission milestone M1.2 and the experiment behind the first paper ([`systems/program/08_first_paper.md`](../../systems/program/08_first_paper.md)).

**Expected result.** No dependence: quantum mechanics forbids it (the no-signalling theorem [ghirardi1980]), and the experiment turns that into a measured bound. On a shared chip, any dependence that does appear is crosstalk between neighboring qubits, a physical disturbance that travels through the chip, never through the collapse; running far-apart qubit pairs separates the two. That is the second result of the paper: an upper bound on the information per use, and a crosstalk map of the device.

**The twin.** [`qll/circuits/collapse_signalling.py`](../../qll/circuits/collapse_signalling.py) holds the exact physics (Bob's state after any instrument of Alice's), the Monte Carlo of the code, the analysis (likelihood-ratio test, Clopper–Pearson intervals, the convexity bound on mutual information), the sample-size formula, the Qiskit circuits, and the hardware runner. [`tests/test_collapse_signalling.py`](../../tests/test_collapse_signalling.py) checks every piece against exact results and checks that the analysis catches both controls.

## Safety
None physical. Keep your cloud token out of the repository (`QiskitRuntimeService.save_account` stores it in your home folder).

## Parts
A laptop with Python, `qiskit`, `qiskit-aer`, and `qiskit-ibm-runtime`; a free IBM Quantum account.

## Stage 0 — Simulate (one evening)
```bash
python -m pytest tests/test_collapse_signalling.py                        # the physics and the analysis, checked
python experiments/bench/E17_collapse_code/run_collapse_code.py run --backend aer --scheme basis --shots 20000
python experiments/bench/E17_collapse_code/run_collapse_code.py run --backend aer --scheme measure --leak 0.1 --shots 20000
python experiments/bench/E17_collapse_code/run_collapse_code.py analyze results/*.json
```
**Pass.** The ideal runs report "no signal" with an information bound near $10^{-4}$ bit per use; the leak control reports "SIGNAL" with a bias near −0.05. You now know the analysis can see a channel when one exists.

## Stage 1 — Rehearse on a noisy copy of a device (one evening)
`run --backend fake_torino --layout 0 1 --repeats 5`. The fake device has realistic gate and readout errors but no crosstalk model, so it should report no signal. **Pass:** no signal, and you can read the transpiled circuit.

## Stage 2 — Run on hardware (one session of your monthly allowance)
1. Choose three qubit pairs from the device's coupling map: one pair of neighbors, one pair two couplers apart, one pair on opposite sides of the chip. The Bell pair needs a two-qubit gate, so a far pair is joined by swaps; record the transpiled depth.
2. For each pair and each scheme (`basis`, `measure`, `flip`), run `--shots 4000 --repeats 5`. Circuits for message 0 and message 1 alternate inside one job, so slow drift affects both alike.
3. Run E16's conditional-Ramsey circuits on the same pairs the same day: they measure the static crosstalk that could leak into Bob's readout.

**Analyze.** `analyze results/*.json` prints, for each run, the bias $P(b{=}1|x{=}1) - P(b{=}1|x{=}0)$, the p-value, and the 99 % upper bound on the information per use. To detect a 1 % bias at the 1 % level with 90 % power takes 74,390 uses per message value (`uses_to_detect(0.01)`); plan the shot budget from that number.

**Pass.** Either no signal on every pair, with the bound reported, or a signal that shrinks with qubit distance and tracks the E16 crosstalk. Either is a result; a signal that does not shrink with distance means a bug in the analysis or the run, never physics, so check the controls again.

## Stage 3 — Photons in two rooms (Phase 2, milestone M2.4)
With the Phase 2 entangled source, put Alice's analyzer in room A and Bob's in room B. Alice switches her analyzer between 0° and 45° by the message bit, slot by slot; Bob keeps his at 0°. Log both, and analyze Bob's file alone with `analyze(x, b)`; then compare the two files and watch the correlation appear (the quantum eraser of P06 is the same lesson). **Pass:** no dependence in Bob's file alone; correlation near $V\cos 2(\alpha - \beta)$ when the files are compared.

## If it does not work
- **A signal on every pair, even far apart:** the message bits are not balanced or not interleaved, or the bitstring order is reversed (Qiskit prints classical bit 1 first; `counts_to_outcomes` expects that).
- **Jobs fail on the open plan:** reduce `--repeats`; check the current allowance.

**Verifies.** Milestone M1.2 and the physics invariant that no requirement of the mission depends on signalling through collapse (`tests/test_program_plan.py`).

**References.** Ghirardi, G. C., Rimini, A., & Weber, T. (1980). A general argument against superluminal transmission through the quantum mechanical measurement process. *Lettere al Nuovo Cimento*, 27, 293–298. · Aspect, A., Dalibard, J., & Roger, G. (1982). Experimental test of Bell's inequalities using time-varying analyzers. *Physical Review Letters*, 49, 1804–1807. https://doi.org/10.1103/PhysRevLett.49.1804 · Clopper, C. J., & Pearson, E. S. (1934). The use of confidence or fiducial limits illustrated in the case of the binomial. *Biometrika*, 26, 404–413. https://doi.org/10.1093/biomet/26.4.404
