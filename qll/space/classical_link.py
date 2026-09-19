"""The classical half of the Earth-Mars link: photon-starved optical telemetry.

Physics
-------
At low mean photon number per mode n the Holevo capacity of a pure-loss optical channel is
C = g(n) = (1+n) log2(1+n) - n log2 n bits per mode (the capacity of the lossy bosonic channel with
n = eta * n_source) [giovannetti2004] [giovannetti2014], which behaves as n log2(1/n) for n << 1. Direct
detection with pulse-position modulation (PPM) and ideal photon counting achieves a photon information
efficiency (PIE) of a few bits per detected photon, within ~1-3 dB of the Holevo limit at low n; DSOC on
Psyche demonstrated 267 Mb/s at 0.2 au and tens of Mb/s beyond 2 au with a 5 m receiver [biswas2024].
Received photon rate uses the same diffraction law as the quantum link: the classical link is the quantum
link with a bright source. Two teleportation bits are then negligible bandwidth; latency is the whole cost.
"""
from __future__ import annotations

import math

from qll.channels.free_space_diffraction import geometric_transmittance

H_PLANCK = 6.62607015e-34
C = 299792458.0


def holevo_capacity_bits_per_mode(n_mean: float) -> float:
    if n_mean <= 0:
        return 0.0
    return (1 + n_mean) * math.log2(1 + n_mean) - n_mean * math.log2(n_mean)


def received_photons_per_s(P_tx_W: float, lambda_m: float, w0_m: float, D_rx_m: float, L_m: float, eta_other: float = 0.3) -> float:
    E_ph = H_PLANCK * C / lambda_m
    return P_tx_W / E_ph * geometric_transmittance(L_m, lambda_m, w0_m, D_rx_m) * eta_other


def ppm_data_rate_bps(photons_per_s: float, pie_bits_per_photon: float = 2.0, max_rate_bps: float = 267e6) -> float:
    """Photon information efficiency of ~2 bits/photon is representative of DSOC-class PPM at low signal;
    the terminal's modulator/decoder caps the rate (DSOC: 267 Mb/s), which is why short-range rates saturate."""
    return min(max_rate_bps, photons_per_s * pie_bits_per_photon)


def holevo_limited_rate_bps(photons_per_s: float, mode_rate_hz: float) -> float:
    n = photons_per_s / mode_rate_hz
    return holevo_capacity_bits_per_mode(n) * mode_rate_hz


DSOC_PSYCHE = dict(P_tx_W=4.0, lambda_m=1550e-9, w0_m=0.07, D_rx_m=5.1)
"""DSOC flight terminal: 4 W, 22 cm aperture (effective waist ~7 cm), 1550 nm; Palomar 5.1 m receiver
[biswas2024] (TODO: verify exact terminal parameters)."""
