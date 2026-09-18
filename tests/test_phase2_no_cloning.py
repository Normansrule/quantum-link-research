"""No public function in qll.circuits returns two copies of an unknown input (REQ-PHY-003)."""
import importlib
import inspect
import pkgutil

import numpy as np
import pytest

import qll.circuits
from qll.circuits.fidelity import fidelity
from qll.circuits.no_cloning_guard import BUZEK_HILLERY_BOUND, clone_fidelities

pytestmark = pytest.mark.phase2


def test_naive_cloner_fails_on_superposition():
    fa, fb = clone_fidelities(np.array([1, 0]))
    assert fa == pytest.approx(1.0) and fb == pytest.approx(1.0)      # classical states copy fine
    fa, fb = clone_fidelities(np.array([1, 1]))
    assert fa == pytest.approx(0.5) and fb == pytest.approx(0.5)      # superpositions do not
    assert BUZEK_HILLERY_BOUND == 5 / 6


def _public_callables():
    for m in pkgutil.walk_packages(qll.circuits.__path__, "qll.circuits."):
        mod = importlib.import_module(m.name)
        for name, fn in inspect.getmembers(mod, inspect.isfunction):
            if not name.startswith("_") and fn.__module__ == mod.__name__:
                yield f"{mod.__name__}.{name}", fn


def _contains_two_copies(out, psi) -> bool:
    """True if ``out`` is a 4x4 state (or a pair of 2x2 states) equal to psi⊗psi within tolerance."""
    target = np.kron(psi, psi)
    cands = []
    if isinstance(out, np.ndarray) and out.shape == (4, 4):
        cands.append(out)
    if isinstance(out, tuple) and len(out) == 2 and all(isinstance(x, np.ndarray) and x.shape == (2, 2) for x in out):
        if fidelity(psi, out[0]) > 0.999 and fidelity(psi, out[1]) > 0.999:
            return True
    return any(fidelity(target, c) > 0.999 for c in cands)


def test_no_public_function_clones():
    rng = np.random.default_rng(0)
    psi = rng.normal(size=2) + 1j * rng.normal(size=2); psi /= np.linalg.norm(psi)
    checked = 0
    for name, fn in _public_callables():
        params = list(inspect.signature(fn).parameters.values())
        if not params:
            continue
        try:
            out = fn(psi)
        except Exception:
            continue
        checked += 1
        assert not _contains_two_copies(out, psi), f"{name} returned two copies of its input"
    assert checked >= 3
