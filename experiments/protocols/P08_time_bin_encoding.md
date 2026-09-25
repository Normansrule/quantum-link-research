# P08 — Time-Bin Encoding and a Fibre Interferometer

**What it shows.** Polarization does not survive long fibres or a rotating satellite without active compensation; time-bin qubits (a photon in an early or late pulse, $|e\rangle$ and $|l\rangle$, and their superpositions) do, and they are the encoding of every fibre QKD network and of the NV–telecom entanglement demonstrations [brendel1999] [tchebotareva2019]. This protocol builds the unbalanced interferometers that create and analyse them.

**Uses.** The P03 source or a pulsed laser; two unbalanced Mach–Zehnder interferometers (fibre couplers, a 1–3 m path difference giving a 5–15 ns bin separation), fibre stretchers or heaters for phase locking, two detectors with ns timing, a time-tagger.

**Procedure.** (1) Build the encoder: a photon entering the first interferometer leaves in $(|e\rangle+e^{i\varphi_A}|l\rangle)/\sqrt2$. (2) Build the matched decoder; the three output time slots are early–early, the interfering middle slot, and late–late; interference appears only in the middle slot. (3) Stabilize the phase difference $\varphi_A-\varphi_B$ with a bright reference pulse and a slow feedback loop (a heater on one arm). (4) Record visibility versus phase; expect > 95 % with good matching. (5) Send the encoded photons through the 1 km spool from P07 and repeat: the visibility should be unchanged (time-bin robustness), while the polarization visibility of P07 drifts.

**Analyze.** Visibility $V$ in the middle slot vs phase; time-bin QBER $=(1-V)/2$; compare with the polarization drift measured in P07.

**Cost.** Couplers, fibre, a heater and driver, time-tagger already owned: $500–1 500 above P07; one month.

**Verifies.** The encoding assumption behind the F1 fibre stages and behind `learn/03/13`'s statement that a time-bin qubit's shape survives Doppler and redshift; the classical phase reference is the same mechanism twin-field QKD needs (learn 03/18).

**References.** Brendel, J., Gisin, N., Tittel, W., & Zbinden, H. (1999). Pulsed energy-time entangled twin-photon source for quantum communication. *Physical Review Letters*, 82, 2594. https://doi.org/10.1103/PhysRevLett.82.2594 Marcikic, I., et al. (2002). Time-bin entangled qubits for quantum communication created by femtosecond pulses. *Physical Review A*, 66, 062308. https://doi.org/10.1103/PhysRevA.66.062308
