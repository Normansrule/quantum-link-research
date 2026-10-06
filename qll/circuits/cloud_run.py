"""Run circuits on a cloud quantum processor, a noisy local copy of one, or the ideal simulator, and get counts back
in one format. Every cloud experiment in the repository (P11 and the Phase 4 milestones) goes through here, so a
rehearsal on a fake device and a real run differ only in the backend passed in.

Counts are dictionaries from bitstrings to counts, in Qiskit's order: the highest-numbered classical bit first.
"""
from __future__ import annotations


def get_backend(name: str):
    """"fake_<device>" gives a noisy local copy of an IBM device (no account needed); any other name is a real device
    reached through the account saved with QiskitRuntimeService.save_account."""
    if name.startswith("fake_"):
        import qiskit_ibm_runtime.fake_provider as fp
        return getattr(fp, "Fake" + name[5:].capitalize())()
    from qiskit_ibm_runtime import QiskitRuntimeService
    return QiskitRuntimeService().backend(name)


def supports_feedforward(backend) -> bool:
    """True if the backend executes classically controlled gates (mid-circuit measurement and feed-forward)."""
    target = getattr(backend, "target", None)
    return target is not None and "if_else" in target.operation_names


def coupling_distance(backend, a: int, b: int) -> int | None:
    """Number of couplers on the shortest path between two physical qubits, or None for a simulator."""
    cmap = getattr(backend, "coupling_map", None)
    if cmap is None:
        return None
    return int(cmap.distance(a, b))


def run_aer(circuits, shots: int, seed: int = 0, noise_model=None, method: str = "automatic") -> list[dict[str, int]]:
    """Ideal or noisy local simulation, one seed per circuit. With a noise model and mid-circuit measurement, Aer
    (0.17) distributes noise over shots in a way that can shift a rate by about 2e-3 at tens of thousands of shots
    (checked against an exact density-matrix calculation in tests/test_cloud_frontier.py); compare noisy rates
    with that tolerance."""
    from qiskit_aer import AerSimulator

    sim = AerSimulator(noise_model=noise_model, method=method)
    return [sim.run(c, shots=shots, seed_simulator=seed + i).result().get_counts() for i, c in enumerate(circuits)]


def run_backend(backend, circuits, shots: int, layout: list[int] | None = None, seed: int = 0) -> list[dict[str, int]]:
    """Transpile for the backend (optionally pinning the logical qubits to `layout`) and run with Qiskit Runtime's
    Sampler; one counts dictionary per circuit."""
    from qiskit import transpile
    try:                                             # the client-side Sampler (qiskit-ibm-runtime 0.50 and later)
        from qiskit_ibm_runtime.executor_sampler import Sampler
    except ImportError:                              # older releases
        from qiskit_ibm_runtime import SamplerV2 as Sampler

    isa = transpile(list(circuits), backend=backend, initial_layout=layout, optimization_level=1, seed_transpiler=seed)
    result = Sampler(mode=backend).run(isa, shots=shots).result()
    out = []
    for pub in result:
        counts: dict[str, int] = {}
        for s in pub.join_data().get_bitstrings():
            counts[s] = counts.get(s, 0) + 1
        out.append(counts)
    return out
