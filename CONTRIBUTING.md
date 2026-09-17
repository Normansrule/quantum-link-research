# Contributing

Six rules. Pull requests that break one are not merged.

1. **Physics must be correct.** No faster-than-light signaling (no-communication theorem), no cloning,
   and teleportation costs exactly 2 classical bits per qubit sent at or below c.
2. **Build on established libraries.** Qiskit Aer, Stim, QuTiP, SeQUeNCe, Perceval, kyber-py, cryptography.
   Never write a simulator from scratch.
3. **Every formula and default parameter carries a `[bibkey]`** in its docstring and an entry in
   `docs/references.bib`. Never invent a citation. DOI or arXiv ID only when certain; otherwise mark `TODO: verify`.
4. **Every module is validated against an analytic result in pytest** before merge.
5. **One physical idea per file.** If a docstring would need a second "Physics" section, split the file.
6. **Commit after each phase with all tests passing.** Target Windows 11 + conda + Python 3.12 and Ubuntu;
   pins live in `environment.yml`.

Writing style: US English, Oxford commas, warm and professional tone, APA citations in prose.
