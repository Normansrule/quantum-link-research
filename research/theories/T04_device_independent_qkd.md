# T04 — Device-independent and semi-device-independent QKD

**The idea.** Certify the key from a Bell violation alone, without modeling the devices: if $S>2$ with settings chosen freely and the outcomes are recorded promptly, then any eavesdropper's information is bounded by $S$, whatever the boxes contain. Semi-DI variants relax one assumption (trusted source dimension, trusted measurement) for higher rates.

**Equations.** $r_{\rm DI}\ge1-h_2\!\left(\frac{1+\sqrt{S^2/4-1}}{2}\right)-h_2(Q)$ (collective attacks, asymptotic); needs high detection efficiency ($>0.9$ system) to close the detection loophole without fair sampling, which is why the first demonstrations used ions or heralded links.

**Status.** Two demonstrations in 2022 (trapped ions over 2 m; photonic over 220 m and 400 m with heralding); rates of bits per hour to per second; no deployment. Finite-key security under general attacks proven (entropy accumulation theorem).

**What it would change.** Mars could verify its own hardware was not compromised in transit, using only the $S$ value; but settings and outcomes must be exchanged classically, so the protocol's finite-key analysis has to be redone for 20-minute round trips (proposal E10).

**Key papers.** Acín, A., et al. (2007). *PRL*, 98, 230501. Pironio, S., et al. (2009). *New J. Phys.*, 11, 045021. Arnon-Friedman, R., et al. (2018). Practical device-independent quantum cryptography via entropy accumulation. *Nat. Commun.*, 9, 459. Nadlinger, D. P., et al. (2022). Experimental quantum key distribution certified by Bell's theorem. *Nature*, 607, 682. Zhang, W., et al. (2022). A device-independent quantum key distribution system for distant users. *Nature*, 607, 687. Liu, W.-Z., et al. (2022). Toward a photonic demonstration of device-independent quantum key distribution. *PRL*, 129, 050502.

**Repo hook.** `qll/qkd/e91.py` DI rate function; E10.
