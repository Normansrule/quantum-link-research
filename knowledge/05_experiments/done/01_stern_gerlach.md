# Stern–Gerlach (1922): spin is quantized

**Original.** Stern and Gerlach sent a beam of silver atoms through an inhomogeneous magnetic field; the beam split into two spots, not a continuous smear, showing that the magnetic moment (spin) along the field axis takes only two values. It is the first qubit measurement in history.

**Physics.** Force $F_z=\mu_z\,\partial B_z/\partial z$ with $\mu_z=\pm g\mu_B/2$; the two outputs are the eigenstates of $S_z$. Sequential Stern–Gerlach devices along $z$, then $x$, then $z$ show that measuring $S_x$ erases the $S_z$ information: non-commuting observables, the content of `00_foundations/02`.

**Simple recreation.** A real beam apparatus needs vacuum and an oven; the standard classroom substitute is (a) the qubit version, an NV-center ODMR measurement in a bias field, which is literally "measure $S_z$ of a spin-1 with a magnetic field on" (`done/04`), and (b) a numerical simulation of sequential measurements with Qiskit: prepare $\lvert+\rangle$, measure $Z$, then $X$, then $Z$ and watch the statistics.

**What went wrong historically.** The split was first invisible because the silver deposit was too thin; sulfur from a cheap cigar reportedly tarnished it into visibility. The expected result (three spots for $l=1$ orbital angular momentum) was wrong; spin had not yet been proposed.

**Repo hook.** Sequential-measurement notebook target for Phase 2 `notebooks/01_circuits.ipynb`.

- Gerlach, W., & Stern, O. (1922). Der experimentelle Nachweis der Richtungsquantelung im Magnetfeld. *Zeitschrift für Physik*, 9, 349. https://doi.org/10.1007/BF01326983
- Friedrich, B., & Herschbach, D. (2003). Stern and Gerlach: how a bad cigar helped reorient atomic physics. *Physics Today*, 56(12), 53.
