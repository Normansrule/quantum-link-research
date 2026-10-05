"""Experiment logs: the bridge from a real two-site setup to the same protocol code the simulation uses.

Format
------
One CSV row per pulse (or per time slot of a photon-counting experiment), with each site's private record in its
own columns:
    pulse, alice_bit, alice_basis, bob_basis, bob_click, bob_bit[, alice_intensity][, eve_touched, eve_basis, eve_bit]
Bases are 0 (rectilinear, Z) and 1 (diagonal, X). `alice_intensity` (0 signal, 1 decoy, 2 vacuum) is required for a
decoy-state experiment and absent otherwise. `bob_click` is 1 if Site B registered a detection in that slot; for
a bright-light analogue (systems/see510/10_real_world_experiments.md, Tier 1) every slot clicks. The optional Eve
columns are written only when an intercept-resend station is present, and are used only for simulation-only
diagnostics, never by the protocol. The log merges both sites' records for convenience; the protocol still lets
nothing cross between the sites except through the authenticated classical channel, so a real two-computer
deployment would split this file into one file per site with the same columns.

`run_from_log` replaces steps 3-4 of a session (preparation, transmission, detection) with the log and runs sifting,
estimation, Cascade, verification, amplification, and key delivery unchanged. `simulate_log` writes the simulation's
own record in this format: it is both the template for an experiment's logger and the test that the bridge is exact.
"""
from __future__ import annotations

import csv
from dataclasses import replace
from pathlib import Path

import numpy as np

from qll.link.adversary import AdversaryRecord
from qll.link.config import LinkConfig
from qll.link.protocol_bb84 import QuantumRecord, SessionResult, run_session, simulate_quantum
from qll.link.site_a import PreparedStates
from qll.link.site_b import Detections

COLUMNS = ["pulse", "alice_bit", "alice_basis", "bob_basis", "bob_click", "bob_bit"]
EVE_COLUMNS = ["eve_touched", "eve_basis", "eve_bit"]


def write_log(path: Path, rec: QuantumRecord) -> Path:
    s, d, e = rec.states, rec.det, rec.adversary
    cols = COLUMNS + (["alice_intensity"] if s.intensity is not None else []) + (EVE_COLUMNS if e is not None else [])
    arrays = [np.arange(len(s.bits)), s.bits, s.bases, d.bases, d.detected.astype(np.int8), np.where(d.detected, d.bits, 0)]
    if s.intensity is not None:
        arrays.append(s.intensity)
    if e is not None:
        arrays += [e.touched.astype(np.int8), e.bases, e.results]
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(cols)
        w.writerows(np.column_stack(arrays).tolist())
    return Path(path)


def read_log(path: Path) -> QuantumRecord:
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.reader(fh)
        header = next(reader)
        missing = [c for c in COLUMNS if c not in header]
        if missing:
            raise ValueError(f"log is missing columns {missing}")
        rows = np.array([[int(float(v)) for v in r] for r in reader if r], dtype=np.int64)
    if rows.size == 0:
        raise ValueError("log has no rows")
    col = {name: rows[:, i] for i, name in enumerate(header)}
    for name in ("alice_bit", "alice_basis", "bob_basis", "bob_click", "bob_bit"):
        if not np.isin(col[name], (0, 1)).all():
            raise ValueError(f"column {name} must hold only 0 and 1")
    intensity = None
    if "alice_intensity" in col:
        if not np.isin(col["alice_intensity"], (0, 1, 2)).all():
            raise ValueError("column alice_intensity must hold 0 (signal), 1 (decoy), or 2 (vacuum)")
        intensity = col["alice_intensity"].astype(np.int8)
    # a photon count is not observable in an experiment; its presence only marks a weak-coherent record
    photons = np.ones(len(col["alice_bit"]), dtype=np.int64) if intensity is not None else None
    states = PreparedStates(col["alice_bit"].astype(np.int8), col["alice_basis"].astype(np.int8), photons, intensity)
    click = col["bob_click"].astype(bool)
    det = Detections(click, click, col["bob_bit"].astype(np.int8), col["bob_basis"].astype(np.int8))
    adv = None
    if all(c in col for c in EVE_COLUMNS):
        touched = col["eve_touched"].astype(bool)
        adv = AdversaryRecord(float(touched.mean()), touched, col["eve_basis"].astype(np.int8), col["eve_bit"].astype(np.int8), states.bases)
    return QuantumRecord(states, det, adv)


def simulate_log(c: LinkConfig, path: Path) -> Path:
    """Write the simulated quantum record of configuration c as an experiment log."""
    return write_log(path, simulate_quantum(c))


def run_from_log(path: Path, c: LinkConfig, managers=None) -> SessionResult:
    """Process an experiment log with configuration c (thresholds, security parameters, pulse rate, and the operator's
    description of the channel); the number of pulses comes from the log."""
    rec = read_log(path)
    c = replace(c, n_pulses=len(rec.states.bits))
    return run_session(c, managers, record=rec)


# ------------------------------------------------------------------------------------- one log per site (two rooms)
ALICE_SITE = ["pulse", "alice_bit", "alice_basis"]
BOB_SITE = ["pulse", "bob_basis", "bob_bit"]


def write_site_logs(rec: QuantumRecord, alice_path: Path, bob_path: Path) -> tuple[Path, Path]:
    """Write what each site records on its own computer: Site A every pulse it prepared (and its intensity class),
    Site B only the pulses on which a detector clicked, with its basis and bit. This is the format of a real two-room
    run; the files never need to be merged by hand."""
    s, d = rec.states, rec.det
    a_cols = ALICE_SITE + (["alice_intensity"] if s.intensity is not None else [])
    a = [np.arange(len(s.bits)), s.bits, s.bases] + ([s.intensity] if s.intensity is not None else [])
    idx = np.flatnonzero(d.detected)
    for path, cols, arrays in ((alice_path, a_cols, a), (bob_path, BOB_SITE, [idx, d.bases[idx], d.bits[idx]])):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        np.savetxt(path, np.column_stack(arrays).astype(np.int64), fmt="%d", delimiter=",", header=",".join(cols), comments="")
    return Path(alice_path), Path(bob_path)


def _load(path: Path, required: list[str]) -> dict[str, np.ndarray]:
    with open(path, encoding="utf-8") as fh:
        header = fh.readline().strip().split(",")
    missing = [c for c in required if c not in header]
    if missing:
        raise ValueError(f"{Path(path).name} is missing columns {missing}")
    rows = np.loadtxt(path, delimiter=",", skiprows=1, dtype=np.int64, ndmin=2)
    return {name: rows[:, i] for i, name in enumerate(header)} if rows.size else {name: np.zeros(0, np.int64) for name in header}


def read_site_logs(alice_path: Path, bob_path: Path) -> QuantumRecord:
    """Join the two sites' logs on the pulse index into the record the protocol processes."""
    a, b = _load(alice_path, ALICE_SITE), _load(bob_path, BOB_SITE)
    n = len(a["pulse"])
    if n == 0 or not np.array_equal(a["pulse"], np.arange(n)):
        raise ValueError("Site A's log must list every pulse once, in order, from 0")
    idx = b["pulse"]
    if len(idx) and (idx.min() < 0 or idx.max() >= n or np.any(np.diff(idx) <= 0)):
        raise ValueError("Site B's pulse indices must be increasing and within Site A's log")
    for name, col in (("alice_bit", a["alice_bit"]), ("alice_basis", a["alice_basis"]), ("bob_basis", b["bob_basis"]), ("bob_bit", b["bob_bit"])):
        if not np.isin(col, (0, 1)).all():
            raise ValueError(f"column {name} must hold only 0 and 1")
    intensity = a["alice_intensity"].astype(np.int8) if "alice_intensity" in a else None
    photons = np.ones(n, dtype=np.int64) if intensity is not None else None
    states = PreparedStates(a["alice_bit"].astype(np.int8), a["alice_basis"].astype(np.int8), photons, intensity)
    click = np.zeros(n, bool); click[idx] = True
    bases = np.zeros(n, np.int8); bases[idx] = b["bob_basis"]
    bits = np.zeros(n, np.int8); bits[idx] = b["bob_bit"]
    return QuantumRecord(states, Detections(click, click, bits, bases), None)


def run_from_site_logs(alice_path: Path, bob_path: Path, c: LinkConfig, managers=None) -> SessionResult:
    rec = read_site_logs(alice_path, bob_path)
    return run_session(replace(c, n_pulses=len(rec.states.bits)), managers, record=rec)
