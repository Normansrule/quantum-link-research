"""Experiment logs: the bridge from a real two-site setup to the same protocol code the simulation uses.

Format
------
One CSV row per pulse (or per time slot of a photon-counting experiment), with each site's private record in its
own columns:
    pulse, alice_bit, alice_basis, bob_basis, bob_click, bob_bit[, eve_touched, eve_basis, eve_bit]
Bases are 0 (rectilinear, Z) and 1 (diagonal, X). `bob_click` is 1 if Site B registered a detection in that slot; for
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
    cols = COLUMNS + (EVE_COLUMNS if e is not None else [])
    arrays = [np.arange(len(s.bits)), s.bits, s.bases, d.bases, d.detected.astype(np.int8), np.where(d.detected, d.bits, 0)]
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
    states = PreparedStates(col["alice_bit"].astype(np.int8), col["alice_basis"].astype(np.int8))
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
