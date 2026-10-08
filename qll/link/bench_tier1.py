"""Tier 1 of the real-world ladder: polarization BB84 with a laser pointer, polarizer film on hobby servos, and a
photodiode, driven by an Arduino. Bright light, so a classical analogue: it shows the protocol, not its security.

Physics
-------
Site A sets the transmitted polarization to theta_A = 0, 90 deg (Z basis, bits 0 and 1) or 45, 135 deg (X basis);
Site B's analyzer sits at 0 deg (Z) or 45 deg (X). Malus's law gives the light through the analyzer,
    I = I0 [eps + (1 - 2 eps) cos^2(theta_A - theta_B)] + I_amb + noise,
with eps the polarizers' leakage (one over the extinction ratio) [hecht2017]. Site B reads bit 0 above an upper
threshold, bit 1 below a lower one; between them (half intensity, which is what a mismatched basis gives) the reading
is ambiguous and Site B flips its own coin. That coin is where the analogue departs from quantum mechanics: a single
photon at a mismatched analyzer passes or not at random, whereas bright light simply splits. An intercept-resend
station does the same with its own analyzer, then re-sends its result with its own laser and polarizer; in matched
bases it causes errors on a quarter of the pulses, as the quantum adversary does, but a classical eavesdropper could
instead tap a fraction of the bright beam and learn everything without disturbing it. Tier 1 therefore demonstrates
sifting, error estimation, Cascade, amplification, and key delivery on real hardware, and makes no security claim.

`MalusBench` is the twin used for the dry run and the tests; `SerialBench` talks to the sketch in
experiments/bench/see510_tier1/see510_tier1.ino over USB. Both answer the same `pulse` call, so `run` drives either.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from qll.link.adversary import AdversaryRecord
from qll.link.hardware_log import write_log
from qll.link.protocol_bb84 import QuantumRecord
from qll.link.site_a import PreparedStates
from qll.link.site_b import Detections

ANGLE = {(0, 0): 0, (0, 1): 90, (1, 0): 45, (1, 1): 135}       # (basis, bit) -> polarizer angle in degrees
ANALYZER = {0: 0, 1: 45}                                         # basis -> analyzer angle for bit 0


@dataclass
class MalusBench:
    """A software twin of the Tier 1 bench, in ADC counts (0-1023)."""
    i0: float = 800.0                 # through-polarizer intensity at the photodiode, aligned
    leakage: float = 0.01             # one over the polarizers' extinction ratio
    ambient: float = 20.0             # room light reaching the photodiode
    noise: float = 8.0                # reading-to-reading noise (standard deviation)
    seed: int = 0
    rng: np.random.Generator = field(init=False)

    def __post_init__(self):
        self.rng = np.random.default_rng(self.seed)

    def _read(self, pol_deg: float, analyzer_deg: float) -> float:
        c2 = math.cos(math.radians(pol_deg - analyzer_deg)) ** 2
        return self.i0 * (self.leakage + (1 - 2 * self.leakage) * c2) + self.ambient + self.noise * self.rng.standard_normal()

    def pulse(self, alice_deg: float, bob_deg: float, eve=None) -> tuple[float, None]:
        """Fire one pulse at alice_deg through Site B's analyzer at bob_deg; return Site B's reading."""
        return self._read(alice_deg, bob_deg), None

    def eve_read(self, alice_deg: float, eve_deg: float) -> float:
        return self._read(alice_deg, eve_deg)


class SerialBench:
    """The Arduino bench over USB serial (needs `pip install pyserial`). Protocol, one line each way:
        host -> board   P <alice_deg> <bob_deg>\n          fire a pulse, read Site B
                        E <alice_deg> <eve_deg>\n          fire Site A's laser into the intercept station, read it
                        R <eve_out_deg> <bob_deg>\n        fire the station's laser into Site B, read Site B
        board -> host   V <adc>\n"""

    def __init__(self, port: str, baud: int = 115200, timeout_s: float = 5.0):
        import serial                                       # optional dependency, imported only for real hardware
        self.ser = serial.Serial(port, baud, timeout=timeout_s)
        self.ser.readline()                                 # the sketch prints a banner on reset

    def _ask(self, line: str) -> float:
        self.ser.write((line + "\n").encode())
        reply = self.ser.readline().decode().strip()
        if not reply.startswith("V "):
            raise IOError(f"unexpected reply from the bench: {reply!r}")
        return float(reply[2:])

    def pulse(self, alice_deg: float, bob_deg: float, eve=None):
        return self._ask(f"P {alice_deg:g} {bob_deg:g}"), None

    def eve_read(self, alice_deg: float, eve_deg: float) -> float:
        return self._ask(f"E {alice_deg:g} {eve_deg:g}")

    def resend(self, eve_out_deg: float, bob_deg: float) -> float:
        return self._ask(f"R {eve_out_deg:g} {bob_deg:g}")


@dataclass(frozen=True)
class Thresholds:
    high: float
    low: float

    def decide(self, reading: float, rng: np.random.Generator) -> int:
        """0 above high, 1 below low, a coin flip in between (the analogue's stand-in for quantum randomness)."""
        if reading >= self.high:
            return 0
        if reading <= self.low:
            return 1
        return int(rng.integers(2))


def calibrate(bench, repeats: int = 5) -> Thresholds:
    """Measure aligned (0 deg on 0 deg) and crossed (90 deg on 0 deg) readings; thresholds at 75 % and 25 % of the span."""
    bright = float(np.mean([bench.pulse(0, 0)[0] for _ in range(repeats)]))
    dark = float(np.mean([bench.pulse(90, 0)[0] for _ in range(repeats)]))
    span = bright - dark
    if span <= 0:
        raise ValueError("calibration failed: the aligned reading is not brighter than the crossed one")
    return Thresholds(dark + 0.75 * span, dark + 0.25 * span)


def mean_reading(bench, pol_deg: float, analyzer_deg: float) -> float:
    """The noise-free Malus reading I0 [eps + (1 - 2 eps) cos^2] + I_amb."""
    c2 = math.cos(math.radians(pol_deg - analyzer_deg)) ** 2
    return bench.i0 * (bench.leakage + (1 - 2 * bench.leakage) * c2) + bench.ambient


def ideal_thresholds(bench) -> Thresholds:
    """What `calibrate` converges to with many repeats: 75 % and 25 % of the noise-free span."""
    bright, dark = mean_reading(bench, 0, 0), mean_reading(bench, 90, 0)
    return Thresholds(dark + 0.75 * (bright - dark), dark + 0.25 * (bright - dark))


def p_decide_zero(mean: float, noise: float, th: Thresholds) -> float:
    """P(decision 0) for a Gaussian reading of the given mean: above `high`, plus half of the ambiguous band."""
    if noise <= 0:
        return 1.0 if mean >= th.high else 0.0 if mean <= th.low else 0.5
    cdf = lambda v: 0.5 * (1 + math.erf((v - mean) / (noise * math.sqrt(2))))
    above = 1 - cdf(th.high)
    return above + 0.5 * (cdf(th.high) - cdf(th.low))


def expected_error(bench, th: Thresholds | None = None, eve_fraction: float = 0.0) -> float:
    """Expected error rate on the sifted pulses (matched bases) of `run`, in closed form. Without the station a sent 0
    is misread with probability e0 = 1 - P(0 | bright) and a sent 1 with e1 = P(0 | dark), so e = (e0 + e1)/2. An
    intercepted pulse is read by the station in its own basis. In the right one, a sent 0 reaches Site B wrong with
    (1 - e0) e0 + e0 (1 - e1) and a sent 1 with (1 - e1) e1 + e1 (1 - e0); their mean is
        e_R = e0 + e1 - (e0^2 + e1^2)/2 - e0 e1        (= 2 e (1 - e) when e0 = e1 = e).
    In the wrong one Site B's analyzer sits at 45 degrees to the resent polarization, its decision no longer depends on
    Alice's bit, and its error is exactly 1/2 on average over her bits [bennett1984]. Hence
        Q = (1 - f) e + f (e_R / 2 + 1/4)."""
    th = th or ideal_thresholds(bench)
    e0 = 1 - p_decide_zero(mean_reading(bench, 0, 0), bench.noise, th)
    e1 = p_decide_zero(mean_reading(bench, 90, 0), bench.noise, th)
    e_r = e0 + e1 - (e0 ** 2 + e1 ** 2) / 2 - e0 * e1
    return (1 - eve_fraction) * (e0 + e1) / 2 + eve_fraction * (e_r / 2 + 0.25)


def run(bench, n: int, seed: int, eve_fraction: float = 0.0, thresholds: Thresholds | None = None) -> QuantumRecord:
    """Drive n pulses with random bits and bases (seeded here; a real Site A should use a certified random source),
    optionally through an intercept-resend station on a fraction of them, and return the quantum record."""
    if isinstance(bench, SerialBench) and 0 < eve_fraction < 1:
        raise ValueError("on the Tier 1 bench the intercept station sits in the beam for a whole run: use 0 or 1")
    rng = np.random.default_rng(seed)
    th = thresholds or calibrate(bench)
    a_bits, a_bases, b_bases = (rng.integers(0, 2, n).astype(np.int8) for _ in range(3))
    touched = rng.random(n) < eve_fraction
    e_bases = rng.integers(0, 2, n).astype(np.int8)
    e_bits = np.zeros(n, dtype=np.int8)
    b_bits = np.zeros(n, dtype=np.int8)
    for i in range(n):
        alice = ANGLE[(int(a_bases[i]), int(a_bits[i]))]
        bob = ANALYZER[int(b_bases[i])]
        if touched[i]:
            e_bits[i] = th.decide(bench.eve_read(alice, ANALYZER[int(e_bases[i])]), rng)
            out = ANGLE[(int(e_bases[i]), int(e_bits[i]))]
            reading = bench.resend(out, bob) if isinstance(bench, SerialBench) else bench.pulse(out, bob)[0]
        else:
            reading = bench.pulse(alice, bob)[0]
        b_bits[i] = th.decide(reading, rng)
    states = PreparedStates(a_bits, a_bases)
    det = Detections(np.ones(n, bool), np.ones(n, bool), b_bits, b_bases)
    adv = AdversaryRecord(eve_fraction, touched, e_bases, e_bits, a_bases) if eve_fraction > 0 else None
    return QuantumRecord(states, det, adv)


def main(argv: list[str] | None = None) -> None:
    import argparse
    ap = argparse.ArgumentParser(description="Tier 1 bench: drive the Arduino (or its twin) and write an experiment log.")
    ap.add_argument("--port", help="serial port of the Arduino, e.g. /dev/ttyACM0 or COM5; omit for the dry run")
    ap.add_argument("--pulses", type=int, default=4000)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--eve", type=float, default=0.0, help="fraction of pulses through the intercept station")
    ap.add_argument("--out", required=True, help="CSV log to write")
    a = ap.parse_args(argv)
    bench = SerialBench(a.port) if a.port else MalusBench(seed=a.seed)
    th = calibrate(bench)
    print(f"calibrated thresholds: bit 0 above {th.high:.0f}, bit 1 below {th.low:.0f} (ADC counts)")
    write_log(Path(a.out), run(bench, a.pulses, a.seed, a.eve, th))
    print(f"wrote {a.pulses} pulses to {a.out}; process it with: python -m qll.link.run ingest {a.out} "
          "--config systems/see510/hardware/tier1.json")


if __name__ == "__main__":
    main()
