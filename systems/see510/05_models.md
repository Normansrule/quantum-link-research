# 05 Mathematical models

Each equation is implemented once, in the file named, and each is checked against simulation in 06.

**Channel** (`qll/link/models.py`, `qll/channels/fiber_loss.py`). Loss and transmittance:
$$\mathrm{Loss_{dB}} = \alpha L + \mathrm{Loss_{extra}}, \qquad T_{\mathrm{ch}} = 10^{-\mathrm{Loss_{dB}}/10}.$$

**Detection** (`site_b.py`). A pulse gives a signal click with probability $\mu_s = T_{\mathrm{ch}}\,10^{-\mathrm{Loss_{rx}}/10}\,\eta_{\mathrm{det}}$; otherwise a background click (dark counts plus cross-talk) with probability $p_{\mathrm{bg}}$ and a random bit:
$$p_{\mathrm{det}} = \mu_s + (1-\mu_s)\,p_{\mathrm{bg}}.$$

**Sifting** [bennett1984]. Bases agree with probability 1/2, so $n_{\mathrm{sift}} \approx \tfrac12 N p_{\mathrm{det}}$.

**Error rate.** With misalignment $e_{\mathrm{mis}}$ and an intercept-resend adversary on a fraction $f_E$ of pulses, a signal detection is wrong with probability $e_s = q(1-e_{\mathrm{mis}}) + (1-q)e_{\mathrm{mis}}$, $q = f_E/4$ (she picks the wrong basis half the time, and then Site B's bit is wrong half the time) [bennett1984] [nielsen2010]. Background clicks are wrong half the time:
$$Q = \frac{\mu_s e_s + (1-\mu_s)\,p_{\mathrm{bg}}/2}{p_{\mathrm{det}}}.$$
For a full intercept-resend on a perfect channel, $Q = 25\,\%$.

**Error estimate** (`protocol_bb84.py`). A public random sample of $m$ sifted bits gives $\hat Q$; the upper bound used for privacy amplification is
$$Q_U = \hat Q + \sqrt{\ln(1/\varepsilon_{\mathrm{pe}})/(2m)}$$
[hoeffding1963]. The session is rejected if $\hat Q$ exceeds the threshold (11 %).

**Reconciliation** (`reconciliation.py`). Cascade [brassard1994] discloses $\mathrm{leak_{EC}}$ parity bits; any method must disclose at least $n\,h(Q)$ (the Slepian–Wolf limit), and Cascade with four passes discloses about 1.1 to 1.4 times that. Verification compares a 64-bit two-universal hash, so different keys pass with probability at most $2^{-64}$ [wegman1981].

**Secret key length** (`protocol_bb84.py`, `qll/qkd/privacy_amplification.py`). Toeplitz hashing of the $n$-bit reconciled block to
$$\ell = \left\lfloor n\,[1 - h(Q_U)] - \mathrm{leak_{EC}} - t - 2\log_2(1/\varepsilon_{\mathrm{pa}}) \right\rfloor$$
bits [renner2005] [shor2000], with $h$ the binary entropy and $t$ the verification tag. Asymptotically, with an ideal reconciliation, this tends to the Shor–Preskill rate $1 - 2h(Q)$ per sifted bit, positive below about 11 %.

**Key rate.** $R = \ell / (N / f_{\mathrm{pulse}})$ bits per second.

**Expected maximum distance.** The smallest $L$ at which the expected $Q$ reaches the threshold (`models.max_distance_km`); with the defaults about 230 km, where dark counts compete with the signal. A finite block ends the key much earlier, because too few detections remain (06, scenario 2).

**What the models prove.** That the simulation's averages are right: each simulated quantity matches its closed form within statistical error (06, V2–V5). **What they do not prove.** That the closed forms describe hardware; that is what the assumptions of 03 and the bench of 09 are for.
