"""Compare installed package versions with the pins in environment.yml and import the heavy libraries.

Exit 1 on any drift or import failure. Run inside the `qll` conda environment.
"""
from __future__ import annotations

import importlib
import importlib.metadata as md
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMPORT_NAMES = {
    "qiskit": "qiskit", "qiskit-aer": "qiskit_aer", "stim": "stim", "qutip": "qutip",
    "sequence": "sequence", "perceval-quandela": "perceval", "kyber-py": "kyber_py",
    "cryptography": "cryptography", "numpy": "numpy", "scipy": "scipy",
    "matplotlib": "matplotlib", "networkx": "networkx", "pytest": "pytest",
}


def parse_pins(path: Path) -> dict[str, str]:
    pins: dict[str, str] = {}
    for line in path.read_text().splitlines():
        m = re.match(r"\s*-\s*([A-Za-z0-9_.-]+)\s*(?:==|=)\s*([0-9][^\s]*)\s*$", line)
        if m and m.group(1) not in {"python", "pip"}:
            pins[m.group(1)] = m.group(2)
    return pins


def main() -> int:
    pins = parse_pins(ROOT / "environment.yml")
    ok = True
    for dist, want in pins.items():
        try:
            have = md.version(dist)
        except md.PackageNotFoundError:
            print(f"MISSING  {dist} (want {want})")
            ok = False
            continue
        flag = "ok     " if have == want else "DRIFT  "
        ok &= have == want
        print(f"{flag} {dist}: installed {have}, pinned {want}")
    for dist, mod in IMPORT_NAMES.items():
        try:
            importlib.import_module(mod)
            print(f"import  {mod}: ok")
        except Exception as exc:  # noqa: BLE001
            print(f"IMPORT FAILED {mod}: {exc}")
            ok = False
    py = sys.version_info
    if (py.major, py.minor) != (3, 12):
        print(f"DRIFT   python: {py.major}.{py.minor}, pinned 3.12")
        ok = False
    print("ENVIRONMENT OK" if ok else "ENVIRONMENT DRIFT")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
