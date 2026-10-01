# 03 Assumptions

Every simulated result holds only under these assumptions. Each has an identifier so a test case, a limitation, or a hardware measurement can refer to it. "Replace with" says what a hardware measurement would supply.

| ID | Assumption | Consequence | Replace with |
|---|---|---|---|
| A-01 | Ideal single-photon source: exactly one photon per pulse | no multi-photon pulses, so no photon-number splitting [brassard2000] | decoy-state model with a measured mean photon number |
| A-02 | Fiber loss is exponential in length, α dB/km, plus fixed inserted loss | attenuation alone is modelled; dispersion, polarization drift, and backscatter are not | measured loss of the spool or attenuator |
| A-03 | Polarization drift and optical imperfections are a fixed misalignment error e_mis | errors are independent and identically distributed per pulse | measured error rate with no adversary |
| A-04 | Background clicks (dark counts plus cross-talk) are independent per gate and give a random bit | no afterpulsing, dead time, or time-correlated noise | measured dark-count rate per gate |
| A-05 | Detectors have one efficiency and are identical | no efficiency mismatch, so no time-shift or detector-blinding attacks | characterized detector pair |
| A-06 | The adversary performs intercept-and-resend in a random basis on a chosen fraction of pulses, at Site A's output, and resends single photons | she does not change the detection rate; collective, coherent, and side-channel attacks are not modelled | — (a model choice) |
| A-07 | The classical channel is authenticated with HMAC-SHA256 under a pre-shared key | authentication is computationally secure, not information-theoretically secure | Wegman–Carter authentication [wegman1981] |
| A-08 | The classical channel has no latency or loss in the laboratory | session time is dominated by the quantum block | measured network timing |
| A-09 | Random numbers come from a seeded PCG64 generator | reproducible, but not a source of cryptographic randomness | a quantum random number generator or a NIST SP 800-90A generator [nist2015sp800-90a] |
| A-10 | The secret key length uses the Shor–Preskill formula with a Hoeffding margin on the error rate [shor2000] [hoeffding1963] | a finite-size flavoured estimate, not a composable finite-key proof | a composable finite-key analysis [scarani2009] |
| A-11 | Sifting is symmetric (each basis with probability 1/2) | half of the detections are discarded | biased basis choice [lo2005] |
| A-12 | Sites, stores, and applications are trusted and uncompromised | the key at rest and in use is not attacked | key-management hardening (09) |
| A-13 | One session is one block of N pulses at a fixed pulse rate | rates are per block; no pipelining or drift between blocks | long-run measurements |
| A-14 | Co-propagating classical light adds background only through a constant cross-talk click probability | Raman scattering's spectral and length dependence is not modelled | measured background with a classical channel in the same fiber |

**What the assumptions do.** They make the model checkable: under A-01 to A-06, detection probability, error rate, and the effect of interception have closed forms (05), and the simulation is validated against them (06). **What they leave out** is listed in 09, with what each would take to remove.
