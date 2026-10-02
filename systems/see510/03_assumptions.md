# 03 Assumptions

Every simulated result holds only under these assumptions. (0.45 replaced the ideal-source-only and HMAC-only versions of A-01 and A-07.) Each has an identifier so a test case, a limitation, or a hardware measurement can refer to it. "Replace with" says what a hardware measurement would supply.

| ID | Assumption | Consequence | Replace with |
|---|---|---|---|
| A-01 | By default an ideal single-photon source; a weak-coherent laser with or without decoy intensities is available (`source_model`) | with the default, no multi-photon pulses; with a laser, photon-number splitting is modelled and the decoy-state or worst-case bound sets the key | measured mean photon numbers and intensity ratios (Tier 3) |
| A-02 | Fiber loss is exponential in length, α dB/km, plus fixed inserted loss | attenuation alone is modelled; dispersion, polarization drift, and backscatter are not | measured loss of the spool or attenuator |
| A-03 | Polarization drift and optical imperfections are a fixed misalignment error e_mis | errors are independent and identically distributed per pulse | measured error rate with no adversary |
| A-04 | Background clicks (dark counts plus cross-talk) are independent per gate and give a random bit | no afterpulsing, dead time, or time-correlated noise | measured dark-count rate per gate |
| A-05 | Detectors have one efficiency and are identical | no efficiency mismatch, so no time-shift or detector-blinding attacks | characterized detector pair |
| A-06 | The adversary performs intercept-and-resend in a random basis, or photon-number splitting on a laser source, on a chosen fraction of pulses, at Site A's output | intercept-resend does not change the detection rate; collective, coherent, and side-channel attacks are not modelled | — (a model choice) |
| A-07 | The classical channel is authenticated with Wegman–Carter tags over each site's view of the whole transcript, checked before any key is accepted; pads come from a pool of pre-shared key refilled from each session's output (HMAC-SHA256 remains as an option) | information-theoretically secure authentication; the pads are simulated by a hash of the seed, so the simulation's pads are not secret | real pre-shared key exchanged in person at setup |
| A-08 | The classical channel has no latency or loss in the laboratory | session time is dominated by the quantum block | measured network timing |
| A-09 | Random numbers come from a seeded PCG64 generator | reproducible, but not a source of cryptographic randomness | a quantum random number generator or a NIST SP 800-90A generator [nist2015sp800-90a] |
| A-10 | The secret key length uses the Shor–Preskill formula on the single-photon detections, with a Hoeffding margin on the error rate and Chernoff margins on the decoy counts [shor2000] [hoeffding1963] [chernoff1952] | a finite-size flavoured estimate, not a composable finite-key proof | a composable finite-key analysis [scarani2009] |
| A-11 | Sifting is symmetric (each basis with probability 1/2) | half of the detections are discarded | biased basis choice [lo2005] |
| A-12 | Sites, stores, and applications are trusted and uncompromised | the key at rest and in use is not attacked | key-management hardening (09) |
| A-13 | One session is one block of N pulses at a fixed pulse rate | rates are per block; no pipelining or drift between blocks | long-run measurements |
| A-14 | Co-propagating classical light adds background only through a constant cross-talk click probability | Raman scattering's spectral and length dependence is not modelled | measured background with a classical channel in the same fiber |
| A-15 | The photon-number-splitting adversary has perfect equipment: a lossless line, an ideal memory, and knowledge of the mean photon number, the channel, and Site B's efficiency | the attack is the strongest of its kind; weaker real attacks only help the sites | — (a model choice) |

**What the assumptions do.** They make the model checkable: under A-01 to A-06, detection probability, error rate, and the effect of interception have closed forms (05), and the simulation is validated against them (06). **What they leave out** is listed in 09, with what each would take to remove.
