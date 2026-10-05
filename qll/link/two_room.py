"""The two-room link: polarization BB84 with weak laser pulses at the single-photon level between two rooms, built
from hobby-priced parts, and the configuration that makes the simulation its digital twin.

Setup
-----
Room A: a 405 nm laser diode pulsed at `rep_rate_hz` by a microcontroller, attenuated by neutral-density filters to a
mean photon number mu per pulse, then a polarizer at 0, 90, 45, or 135 degrees (four fixed polarizers selected by
four laser diodes, or one diode and a servo-turned half-wave plate). Channel: free space across a hallway, or a
single-mode fiber patch cord through the wall. Room B: a 50/50 beamsplitter for a passive basis choice, a polarizing
beamsplitter in each arm (the diagonal arm behind a half-wave plate at 22.5 degrees), and four silicon
photomultipliers (SiPMs) read by fast comparators and a gated counter on a second microcontroller. A fiber Ethernet
link between the rooms carries the classical channel (qll/link/net_transport.py).

Twin
----
The parts become a LinkConfig through four relations:

    mu       = E_pulse / (h c / lambda) * 10^(-A_ND / 10)                         photons per pulse [bipm2019]
    p_dark   = 1 - exp(-R_dark tau)   per SiPM per gate (Poisson counts),          per basis pair 1 - (1 - p_dark)^2 [casella2002]
    p_after  = P_ap * p_click         afterpulses in the next gate, added as background (gates are far apart compared
                                      with the 82 ns recharge of the datasheet part [onsemi2022microfc])
    e_d      = 1 / (1 + ER) + e_wp    polarizer leakage (one over the extinction ratio [hecht2017]) plus waveplate error

and loss in dB adds along the path. The source is a weak-coherent laser with decoy states: the microcontroller drives
the diode at a signal and a decoy current, or leaves it off (vacuum), chosen at random per pulse; qll/link/decoy.py
bounds the single-photon detections. Without decoys the worst-case analysis finds no key even across a hallway,
because a 0.5-photon pulse is multi-photon 9 % of the time, more than the 7 % of pulses that click. The SiPM's optical crosstalk makes multi-cell pulses inside one sensor, not clicks
in another, so at a 0.5-photoelectron threshold it does not create errors and is not modelled. Everything here is
planning: replace each default with the value measured on your own parts (P10, step 3), and the twin then predicts
the run you will make.
"""
from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path

from qll.constants.physical import C_LIGHT, H_PLANCK
from qll.link import models
from qll.link.config import LinkConfig

PRESET = Path(__file__).resolve().parents[2] / "systems" / "see510" / "hardware" / "two_room.json"


@dataclass(frozen=True)
class TwoRoomParts:
    wavelength_m: float = 405e-9
    rep_rate_hz: float = 1e6                  # a microcontroller's programmable I/O can pulse and gate at this rate
    mu: float = 0.5                           # mean photons per signal pulse after the filters (mean_photon_number)
    mu_decoy: float = 0.1                     # decoy pulses: a lower drive current (or a second, dimmer diode)
    gate_s: float = 5e-9                      # detection window per pulse
    sipm_pde: float = 0.31                    # photon detection efficiency at 420 nm, 2.5 V overvoltage [onsemi2022microfc]
    sipm_dark_hz: float = 300e3               # dark-count rate of a 3 mm sensor at 21 C, typical [onsemi2022microfc]
    sipm_afterpulse: float = 0.002            # afterpulse probability [onsemi2022microfc]
    channel: str = "free_space"               # or "fiber"
    path_m: float = 10.0                      # room to room
    free_space_loss_db: float = 2.0           # beam clipping and windows over a hallway, measured with the power meter
    fiber_coupling_loss_db: float = 6.0       # two fiber collimators at 405 nm, measured
    fiber_db_per_km: float = 30.0             # single-mode fiber for the violet (planning; measure your patch cord)
    receiver_loss_db: float = 1.5             # beamsplitter, polarizing beamsplitters, waveplate, focusing lenses
    polarizer_extinction: float = 500.0       # film polarizers: a few hundred to one
    waveplate_error: float = 0.01             # plastic or zero-order waveplate misalignment, as an error probability
    n_pulses: int = 10_000_000                # ten seconds of pulses per session keeps the decoy margins small

    def path_loss_db(self) -> float:
        if self.channel == "fiber":
            return self.fiber_coupling_loss_db + self.fiber_db_per_km * self.path_m / 1000
        if self.channel == "free_space":
            return self.free_space_loss_db
        raise ValueError("channel must be 'free_space' or 'fiber'")


def mean_photon_number(pulse_energy_j: float, wavelength_m: float, attenuation_db: float) -> float:
    """Photons per pulse after the neutral-density filters."""
    return pulse_energy_j / (H_PLANCK * C_LIGHT / wavelength_m) * 10 ** (-attenuation_db / 10)


def attenuation_for(mu: float, pulse_energy_j: float, wavelength_m: float) -> float:
    """Neutral-density attenuation in dB that brings a pulse of the given energy to mean photon number mu."""
    return 10 * math.log10(pulse_energy_j / (H_PLANCK * C_LIGHT / wavelength_m) / mu)


def dark_prob_per_gate(dark_hz: float, gate_s: float, detectors: int = 2) -> float:
    p = 1.0 - math.exp(-dark_hz * gate_s)
    return 1.0 - (1.0 - p) ** detectors


def config(parts: TwoRoomParts = TwoRoomParts(), seed: int = 2027, scenario: str = "two_room") -> LinkConfig:
    """The digital twin: a LinkConfig built from the parts."""
    p_dark = dark_prob_per_gate(parts.sipm_dark_hz, parts.gate_s)
    base = LinkConfig(scenario=scenario, seed=seed, n_pulses=parts.n_pulses, pulse_rate_hz=parts.rep_rate_hz,
                      distance_km=0.0, extra_loss_db=parts.path_loss_db(), receiver_loss_db=parts.receiver_loss_db,
                      detector_efficiency=parts.sipm_pde, dark_count_prob=p_dark,
                      misalignment_error=1.0 / (1.0 + parts.polarizer_extinction) + parts.waveplate_error,
                      source_model="weak_coherent_decoy", mu_signal=parts.mu, mu_decoy=parts.mu_decoy)
    # afterpulses follow clicks; the click probability per gate is about mu T eta for a weak pulse
    p_click = parts.mu * models.signal_click_prob(base) + p_dark
    return base.with_(crosstalk_click_prob=parts.sipm_afterpulse * p_click)


def predict(parts: TwoRoomParts = TwoRoomParts()) -> dict:
    """What the bench should show before it is built, from the closed-form models: the click probability of a
    Poisson pulse of mean k, 1 - e^(-k T eta), plus background, averaged over the signal, decoy, and vacuum pulses in
    the proportions the twin sends; the error rate; sifted bits; and the misalignment the parts imply."""
    c = config(parts)
    t_eta = models.signal_click_prob(c.with_(source_model="single_photon"))
    pb, e_d = models.background_click_prob(c), models.signal_error(c)
    p_det = err = 0.0
    for share, k in ((c.p_signal, c.mu_signal), (c.p_decoy, c.mu_decoy), (1 - c.p_signal - c.p_decoy, 0.0)):
        p_sig = 1 - math.exp(-k * t_eta)
        p_det += share * (p_sig + (1 - p_sig) * pb)
        err += share * (p_sig * e_d + (1 - p_sig) * pb / 2)
    return {"path_loss_db": parts.path_loss_db(), "mu": parts.mu, "dark_prob_per_gate": c.dark_count_prob,
            "click_prob_per_pulse": p_det, "clicks_per_s": p_det * parts.rep_rate_hz, "expected_qber": err / p_det,
            "sifted_bits_per_s": 0.5 * p_det * parts.rep_rate_hz, "misalignment_error": c.misalignment_error}


def write_preset(parts: TwoRoomParts = TwoRoomParts(), path: Path = PRESET) -> Path:
    keep = ("scenario", "seed", "n_pulses", "pulse_rate_hz", "distance_km", "attenuation_db_per_km", "extra_loss_db",
            "receiver_loss_db", "detector_efficiency", "dark_count_prob", "crosstalk_click_prob", "misalignment_error",
            "source_model", "mu_signal", "mu_decoy", "p_signal", "p_decoy")
    d = {k: v for k, v in config(parts).to_dict().items() if k in keep}
    out = {"_help": "Two-room tier (P10): weak laser pulses at 405 nm, polarization BB84 across a hallway or through a "
                    "fiber patch cord, four silicon photomultipliers. Generated by qll.link.two_room.write_preset from "
                    "the parts in `_parts`; replace them with measured values and regenerate.",
           "_parts": asdict(parts), **d}
    path.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    return path


def check_against_twin(metrics, parts: TwoRoomParts = TwoRoomParts(), click_rel_tol: float = 0.15,
                       qber_abs_tol: float = 0.015) -> dict:
    """Compare a measured session (the metrics of run_from_site_logs) with the twin's prediction for the parts you
    measured. Each line passes when the measurement sits inside the stated tolerance, which covers both statistics
    and the systematic uncertainty of hand-measured parts; a CHECK points at the part to re-measure."""
    pred = predict(parts)
    rows = []
    click_dev = metrics.detection_probability / pred["click_prob_per_pulse"] - 1
    rows.append(("click probability per pulse", pred["click_prob_per_pulse"], metrics.detection_probability,
                 abs(click_dev) <= click_rel_tol, "loss, detector efficiency, or mean photon number"))
    rows.append(("error rate", pred["expected_qber"], metrics.qber_estimate,
                 abs(metrics.qber_estimate - pred["expected_qber"]) <= qber_abs_tol, "polarizer extinction, waveplate angle, or dark counts"))
    if metrics.source_model == "weak_coherent_decoy":
        rows.append(("decoy gain against an honest channel (sd)", 0.0, metrics.decoy_gain_deviation_sd,
                     abs(metrics.decoy_gain_deviation_sd) < 5, "the decoy drive level, or the filters' linearity"))
    return {"rows": [{"quantity": q, "predicted": p, "measured": m, "result": "PASS" if ok else "CHECK", "if CHECK": hint}
                     for q, p, m, ok, hint in rows],
            "all_pass": all(r[3] for r in rows)}
