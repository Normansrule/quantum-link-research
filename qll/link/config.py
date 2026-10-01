"""Every configurable input of the two-site link simulation, with units, defaults, valid ranges, and a run identifier.

Design
------
One frozen dataclass holds every input, so a run is fully described by its configuration and seed (SN-07). The
canonical JSON of the configuration hashes to a run identifier: two runs with the same identifier are the same
experiment. Defaults describe a laboratory-scale 1550 nm link with InGaAs single-photon detectors; each default is a
modelling assumption to be replaced by a measured value when hardware exists (systems/see510/03_assumptions.md).
"""
from __future__ import annotations

import hashlib
import json
import math
from dataclasses import asdict, dataclass, fields, replace

SOURCE_MODELS = ("single_photon",)          # weak coherent pulses with decoy states are future work


@dataclass(frozen=True)
class LinkConfig:
    scenario: str = "baseline"
    seed: int = 2026                        # all randomness in a session derives from this seed
    n_pulses: int = 1_000_000               # states Site A sends in one session (the block size): 1 s at 1 MHz
    pulse_rate_hz: float = 1e6              # converts per-session results into rates
    distance_km: float = 0.0
    attenuation_db_per_km: float = 0.2      # standard single-mode fiber near 1550 nm
    extra_loss_db: float = 0.0              # connectors, splices, or a deliberately inserted attenuator
    receiver_loss_db: float = 1.0           # Site B's internal optics
    detector_efficiency: float = 0.20
    dark_count_prob: float = 1e-6           # per detection gate, per detector pair
    crosstalk_click_prob: float = 0.0       # extra background per gate, e.g. from co-propagating classical light
    misalignment_error: float = 0.01        # probability that a correctly-based detection gives the wrong bit
    source_model: str = "single_photon"
    eve_fraction: float = 0.0               # fraction of pulses an intercept-resend adversary measures and resends
    sample_fraction: float = 0.1            # share of sifted bits disclosed to estimate the error rate
    min_sample_bits: int = 200
    qber_threshold: float = 0.11            # abort above this estimated error rate
    qber_alert: float = 0.03                # warn the operator above this (about three times the baseline error)
    min_key_block_bits: int = 1000          # abort if fewer sifted bits remain for the key
    eps_pe: float = 1e-10                   # confidence of the error-rate upper bound
    eps_pa: float = 1e-10                   # privacy-amplification security parameter
    ec_passes: int = 4                      # passes of parity reconciliation
    verify_tag_bits: int = 64               # hash compared to confirm the keys match
    tamper_classical: bool = False          # an active attacker alters one classical message
    key_size_bits: int = 256                # size of delivered keys (AES-256)

    def __post_init__(self):
        for f in fields(self):
            v = getattr(self, f.name)
            if isinstance(v, complex):
                raise TypeError(f"{f.name} must be real")
        problems = []
        if self.n_pulses < 1:
            problems.append("n_pulses must be at least 1")
        for name in ("distance_km", "attenuation_db_per_km", "extra_loss_db", "receiver_loss_db", "pulse_rate_hz"):
            if getattr(self, name) < 0 or not math.isfinite(getattr(self, name)):
                problems.append(f"{name} must be finite and non-negative")
        for name in ("detector_efficiency", "dark_count_prob", "crosstalk_click_prob", "misalignment_error",
                     "eve_fraction", "sample_fraction", "qber_threshold", "qber_alert"):
            if not 0.0 <= getattr(self, name) <= 1.0:
                problems.append(f"{name} must lie in [0, 1]")
        if self.misalignment_error > 0.5:
            problems.append("misalignment_error above 0.5 is not physical")
        if self.source_model not in SOURCE_MODELS:
            problems.append(f"source_model must be one of {SOURCE_MODELS} (weak coherent pulses are future work)")
        if not (0 < self.eps_pe < 1 and 0 < self.eps_pa < 1):
            problems.append("eps_pe and eps_pa must lie in (0, 1)")
        if self.key_size_bits % 8:
            problems.append("key_size_bits must be a multiple of 8")
        if problems:
            raise ValueError("; ".join(problems))

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True)

    @classmethod
    def from_dict(cls, d: dict) -> "LinkConfig":
        names = {f.name for f in fields(cls)}
        unknown = set(d) - names - {"_help"}
        if unknown:
            raise ValueError(f"unknown configuration fields: {sorted(unknown)}")
        return cls(**{k: v for k, v in d.items() if k in names})

    def run_id(self) -> str:
        """Deterministic identifier: the first 12 hex digits of SHA-256 over the canonical configuration."""
        return hashlib.sha256(self.to_json().encode()).hexdigest()[:12]

    def with_(self, **kw) -> "LinkConfig":
        return replace(self, **kw)
