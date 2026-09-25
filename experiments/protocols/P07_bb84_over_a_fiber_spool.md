# P07 — BB84 Over a Fiber Spool With Quantum Random Bases

**What it shows.** A complete key from raw photons: heralded single photons from the P03 source, polarization encoding, a 1 km spool of single-mode fiber (or two, one per station), bases chosen by the QRNG board, and the full post-processing of `qll.qkd`. This is F1's stage S2 and the first end-to-end run of every layer of the repository on real photons.

**Uses.** P03 source (810 nm) or a weak-coherent 850/1550 nm laser with an attenuator (decoy-state version); a 1 km SM fiber spool (780HP for 810 nm); polarization controllers (fiber paddles) to undo the spool's birefringence; two electro-optic or waveplate basis selectors driven by the QRNG board; four detectors or two with a switch; time-tagger; GPS-disciplined or shared clock.

**Procedure.** (1) Characterize the spool: loss and polarization drift over an hour (expect 2–3 dB at 810 nm in 780HP; ~0.2 dB at 1550). (2) Align polarizations through the spool; measure the QBER floor with fixed bases (target < 3 %). (3) Run 10⁶ signals with QRNG-chosen bases; save `alice_bits, alice_bases, bob_bases, bob_bits, timestamps` as CSV. (4) Feed to `qll.qkd`: `sift`, estimate $Q$, `reconcile` (LDPC), `final_key_length`, `toeplitz_hash`. (5) Authenticate the classical exchange with a pre-shared key (Wegman–Carter tag). (6) Optional: run with 25 % of the signals intercepted and resent by a third station to watch $Q$ rise to 25 % and the key vanish.

**Analyze.** Report sifted bits, $Q$, secret fraction, final key length, and the classical time; compare with `run_bb84` at the measured $Q$ and loss. Log the QRNG health checks (`hardware.randomness.health_check`) alongside.

**Cost.** Spool ~$100–300, paddles ~$200, basis selectors $200–2 000 (waveplates on motorized mounts are cheapest); one semester as a project.

**Verifies.** REQ-QKD-001 with data; the pipeline of learn 03/10; the QRNG board's role (INV-7). Landmark: the first BB84 demonstration [bennett1992exp].

**References.** Bennett, C. H., Bessette, F., Brassard, G., Salvail, L., & Smolin, J. (1992). Experimental quantum cryptography. *Journal of Cryptology*, 5, 3. https://doi.org/10.1007/BF00191318 Dehlinger, D., & Mitchell, M. W. (2002). *American Journal of Physics*, 70, 903. https://doi.org/10.1119/1.1498860
