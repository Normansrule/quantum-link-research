"""Linear optics through Perceval: Hong-Ou-Mandel and the linear-optics Bell-state measurement.

Physics
-------
Perceval evolves Fock states through unitary linear-optical circuits exactly [heurtel2023perceval]. Two
identical photons on a 50:50 beam splitter never exit in different ports (|1,1> -> (|2,0> - |0,2>)/sqrt2)
[hong1987]; photons tagged as distinguishable exit separately half the time. A polarization Bell-state
analyser made of one beam splitter and two polarizing beam splitters identifies |Psi+> and |Psi-> and
confuses |Phi+> with |Phi->, so its success probability is 1/2 [calsamiglia2001]. Both facts are computed
here from the circuit, and the tests compare them with qll.hardware.beam_splitter and
qll.circuits.bell_measurement.
"""
from __future__ import annotations


def hom_output_probabilities(indistinguishability: float = 1.0) -> dict[str, float]:
    """Output distribution of |1,1> on a 50:50 beam splitter for a source of given indistinguishability V;
    keys are Fock strings like '|2,0>'."""
    import perceval as pcvl

    circuit = pcvl.Circuit(2) // pcvl.BS()
    proc = pcvl.Processor("SLOS", circuit, noise=pcvl.NoiseModel(indistinguishability=indistinguishability))
    proc.min_detected_photons_filter(2)
    proc.with_input(pcvl.BasicState([1, 1]))
    res = pcvl.algorithm.Sampler(proc).probs()["results"]
    out: dict[str, float] = {}
    for k, v in res.items():
        key = "|" + ",".join(str(n) for n in [k[0], k[1]]) + ">"
        out[key] = out.get(key, 0.0) + float(v)
    return out


def hom_coincidence_probability(indistinguishability: float = 1.0) -> float:
    return hom_output_probabilities(indistinguishability).get("|1,1>", 0.0)


def bell_state_analyser_success() -> float:
    """Polarization Bell analyser (dual-rail, 4 modes: H1 V1 H2 V2): a 50:50 BS on the spatial modes then
    PBS readout. |Psi+> and |Psi-> give unique click patterns; |Phi+-> give identical ones -> success 1/2."""
    import numpy as np
    import perceval as pcvl
    from perceval.components import BS

    # modes 0,1 = (H_A, H_B); modes 2,3 = (V_A, V_B). A polarization-independent 50:50 BS acts on each pair.
    c = pcvl.Circuit(4)
    c.add(0, BS()); c.add(2, BS())
    proc = pcvl.Processor("SLOS", c)
    proc.min_detected_photons_filter(2)
    # Bell states in dual-rail Fock encoding: |H>=|1,0>, |V>=|0,1> per photon
    def sv(pairs):
        s = pcvl.StateVector()
        for amp, occ in pairs:
            s += pcvl.StateVector(pcvl.BasicState(occ)) * float(amp)
        return s
    r = 1 / np.sqrt(2)
    bell = {   # |H_A H_B> = [1,1,0,0], |V_A V_B> = [0,0,1,1], |H_A V_B> = [1,0,0,1], |V_A H_B> = [0,1,1,0]
        "phi+": sv([(r, [1, 1, 0, 0]), (r, [0, 0, 1, 1])]),
        "phi-": sv([(r, [1, 1, 0, 0]), (-r, [0, 0, 1, 1])]),
        "psi+": sv([(r, [1, 0, 0, 1]), (r, [0, 1, 1, 0])]),
        "psi-": sv([(r, [1, 0, 0, 1]), (-r, [0, 1, 1, 0])]),
    }
    patterns = {}
    for name, st in bell.items():
        proc.with_input(st)
        res = pcvl.algorithm.Sampler(proc).probs()["results"]
        patterns[name] = {str(k): round(float(v), 6) for k, v in res.items() if v > 1e-9}
    # a Bell state is identified if its click patterns overlap with no other state's patterns
    identifiable = 0
    for name, pat in patterns.items():
        others = set().union(*(set(p) for n, p in patterns.items() if n != name))
        if not (set(pat) & others):
            identifiable += 1
    return identifiable / 4
