"""INV-5: every repeaterless protocol rate is bounded by the PLOB capacity; twin-field is not repeaterless in
the relevant sense (it uses a midpoint) and may exceed it."""
from __future__ import annotations

from qll.qkd.plob_bound import plob_bits_per_use


def assert_below_plob(rate_per_use: float, eta: float, name: str = "protocol") -> None:
    bound = plob_bits_per_use(min(eta, 1 - 1e-15))
    if rate_per_use > bound * (1 + 1e-9):
        raise AssertionError(f"{name}: rate {rate_per_use:.3e} exceeds the PLOB bound {bound:.3e} at eta={eta:.3e}")
