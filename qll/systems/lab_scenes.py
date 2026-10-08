"""The real-world builds behind the lab pages (docs/lab/): for each experiment, a ladder of tiers from a starter you can
build this month to the real-world option, each with every part placed where it would stand in the rooms, the bill of
materials it comes from, the build stages of its protocol, the sliders that feed its twin, and the commands that run
the same twin and the real bench from a terminal.

Units are metres; y is up. The two-room layout puts room A's table at x = -5 and room B's at x = +5, so the beam
crosses 10 m, the `path_m` of qll/link/two_room.TwoRoomParts. Costs live on bill-of-materials rows copied from the
protocol each tier cites (tests/test_lab_scenes.py checks that the rows add up to the protocol's stated total);
parts point at the row that pays for them. `scripts/build_lab.py` writes everything to docs/lab/scenes.json.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field, replace

TABLE_Y = 0.80                       # bench-top height


@dataclass(frozen=True)
class Part:
    id: str
    kind: str                        # drawing primitive in docs/js/lab3d.js
    label: str
    pos: tuple[float, float, float]
    note: str                        # what it does and how it is built
    bom: int | None = None           # row of the tier's bill of materials that pays for it (None: owned or shared)
    stage: int = 0                   # build stage of the protocol that adds it
    rot: float = 0.0                 # yaw in degrees
    param: str = ""                  # the slider this part visualizes
    size: tuple[float, ...] = ()


@dataclass(frozen=True)
class Beam:
    kind: str                        # violet, red, nir, pair, pump, classical, sync, usb, cloud
    points: tuple[tuple[float, float, float], ...]
    label: str = ""
    stage: int = 0


@dataclass(frozen=True)
class Slider:
    key: str
    label: str
    lo: float
    hi: float
    step: float
    value: float
    unit: str = ""
    log: bool = False


@dataclass(frozen=True)
class Tier:
    id: str
    title: str
    rung: str                        # starter, main, upgrade, entangled, cloud, device
    experiments: tuple[str, ...]     # catalog ids (qll/systems/experiment_catalog.py)
    milestones: tuple[str, ...]
    twin: str                        # the twin function the page runs
    cost: str
    summary: str
    procedure: str                   # repository path of the step-by-step procedure
    bom: tuple[tuple[str, str, float, float], ...]
    stages: tuple[tuple[str, str], ...]
    parts: tuple[Part, ...]
    beams: tuple[Beam, ...]
    sliders: tuple[Slider, ...]
    commands: dict = field(default_factory=dict)
    rooms: bool = True
    claim: str = ""


def _t(x, z, dy=0.08):
    return (x, TABLE_Y + dy, z)


def _rooms_and_tables(a_label="Room A (Alice)", b_label="Room B (Bob)", hallway=True, stage=0):
    parts = [Part("roomA", "room", a_label, (-5.0, 0.0, 0.0), "A lab or office; blackout the window and keep the door open on the beam line.", size=(6.0, 5.0)),
             Part("roomB", "room", b_label, (5.0, 0.0, 0.0), "The receiving room, 10 m along the beam from room A's source.", size=(6.0, 5.0)),
             Part("tableA", "table", "Bench A", (-5.0, 0.0, 0.0), "Any sturdy desk; bolt or tape the mounts down.", size=(1.8, 1.0)),
             Part("tableB", "table", "Bench B", (5.0, 0.0, 0.0), "Any sturdy desk, at least 1.3 m deep for the two analyzer arms.", size=(1.8, 1.3))]
    if hallway:
        parts.append(Part("hall", "hallway", "Hallway", (0.0, 0.0, 0.0), "Free-space path between the two open doors; keep the beam below eye level.", size=(4.0, 2.2)))
    return parts


# ------------------------------------------------------------------------------------------------- Tier 1 starter
TIER1_BOM = (("Arduino Uno or Nano (or clone)", "controller", 10, 25), ("Hobby servos, SG90 class, x4", "turn the polarizers", 8, 16),
             ("Laser modules, 650 nm, class 2, x2", "Site A and the intercept station", 4, 10), ("Linear polarizer film sheet", "four disks", 8, 15),
             ("Photodiodes, BPW34 class, x2, with load resistors", "Site B and the station", 3, 8), ("5 V supply, breadboard, wires", "power", 10, 20),
             ("3D-printed mounts, dark box or black card", "mechanics", 5, 15))


def tier1() -> Tier:
    z = 0.0
    parts = _rooms_and_tables(hallway=False)[::2] + [
        Part("laser", "laser", "650 nm laser module", _t(-5.75, z), "Class 2 pointer module switched by a MOSFET from the Arduino.", 2, 2, rot=0, param="i0"),
        Part("servoA", "servo", "Servo + polarizer (Alice)", _t(-5.45, z), "Sets 0, 90, 45, or 135 degrees: the bit and basis of each pulse.", 1, 2),
        Part("polA", "polarizer", "Polarizer disk (Alice)", _t(-5.45, z, 0.14), "Film disk on the servo horn.", 3, 2),
        Part("servoE", "servo", "Intercept station analyzer", _t(-5.05, z), "Optional: a third servo and photodiode read the pulse in a random basis.", 1, 4, param="eve_fraction"),
        Part("pdE", "photodiode", "Station photodiode", _t(-4.95, z), "The intercept station's detector.", 4, 4, param="eve_fraction"),
        Part("laserE", "laser", "Station resend laser", _t(-4.85, z - 0.12), "Re-sends what the station measured through its own polarizer.", 2, 4, rot=0, param="eve_fraction"),
        Part("servoB", "servo", "Servo + analyzer (Bob)", _t(-4.6, z), "Analyzer at 0 (Z) or 45 (X) degrees.", 1, 2),
        Part("polB", "polarizer", "Analyzer disk (Bob)", _t(-4.6, z, 0.14), "Film disk on the servo horn; its leakage is one over the extinction ratio.", 3, 2, param="leakage"),
        Part("pdB", "photodiode", "BPW34 photodiode (Bob)", _t(-4.4, z), "Reads the light as ADC counts; bright is bit 0, dark is bit 1.", 4, 2, param="noise"),
        Part("darkbox", "box", "Dark box", _t(-4.5, z, 0.12), "Black card around the receiver: room light is this tier's dark count.", 6, 3, param="ambient", size=(0.5, 0.3, 0.4)),
        Part("arduino", "arduino", "Arduino", _t(-5.2, 0.32), "Runs experiments/bench/see510_tier1/see510_tier1.ino; one serial line per pulse.", 0, 2),
        Part("breadboard", "supply", "5 V supply and breadboard", _t(-5.55, 0.32), "Servos draw more than USB gives; join the grounds.", 5, 2),
        Part("laptopA", "laptop", "Laptop", _t(-4.5, 0.3), "python -m qll.link.bench_tier1 --port COM5 --out tier1.csv", None, 1),
    ]
    beams = (Beam("red", (_t(-5.75, z, 0.14), _t(-4.4, z, 0.14)), "650 nm, bright", 2), Beam("usb", (_t(-5.2, 0.32, 0.01), _t(-4.5, 0.3, 0.01)), "USB serial", 2))
    return Tier("tier1", "Starter: the bright-light analogue", "starter", ("T1",), ("M1.3",), "tier1", "$40–120",
                "BB84's whole processing chain on light you can see: bits, bases, sifting, error rates, and an intercept station, on one desk.",
                "systems/see510/10_real_world_experiments.md", TIER1_BOM,
                (("Simulate", "Run the twin with your measured readings."), ("Build the link", "Laser, two servo polarizers, photodiode, Arduino."),
                 ("Calibrate", "Aligned and crossed readings set the thresholds."), ("Intercept", "Add the station and watch the error rate climb toward 25 %.")),
                tuple(parts), beams,
                (Slider("i0", "Aligned reading I₀", 100, 1000, 10, 800, "counts"), Slider("leakage", "Polarizer leakage ε", 0.001, 0.2, 0.001, 0.01),
                 Slider("ambient", "Room light", 0, 300, 5, 20, "counts"), Slider("noise", "Reading noise σ", 0, 300, 1, 8, "counts"),
                 Slider("eve_fraction", "Intercepted fraction", 0, 1, 0.05, 0)),
                {"simulate": "python -m qll.link.bench_tier1 --out tier1.csv",
                 "real": "python -m qll.link.bench_tier1 --port /dev/ttyACM0 --out tier1.csv && python -m qll.link.run ingest tier1.csv --config systems/see510/hardware/tier1.json"},
                rooms=False, claim="A demonstration of the processing chain; bright light can be tapped, so no security claim.")


# ---------------------------------------------------------------------------------------- P10: the two-room link
P10_BOM = (("Two fiber media converters and a 10–30 m duplex patch cord", "classical channel (M1.1)", 40, 150),
           ("Four 405 nm laser diodes (5 mW class) with a nanosecond pulse driver", "the four BB84 states", 40, 120),
           ("Film polarizers, a half-wave retarder, neutral-density filters (OD 1–4)", "encoding and attenuation", 50, 120),
           ("Four non-polarizing beamsplitters and two polarizing beamsplitters", "combining and analysis", 100, 250),
           ("Four onsemi MicroFC-30035 SiPMs, breakouts, a 30 V boost module, four fast comparators", "detection", 230, 350),
           ("Two small FPGA boards", "timing", 30, 80),
           ("A coaxial cable or second fiber for the pulse clock", "synchronization", 10, 30),
           ("3D-printed mounts, black tubes, lens pairs, black card, felt", "mechanics", 30, 80))
P10_STAGES = (("Simulate first", "Predict the bench and write a synthetic run ($0)."),
              ("Classical channel", "Laptops, media converters, fiber through the door (M1.1)."),
              ("Bright analogue across rooms", "Tier 1 down the hallway (M1.3)."),
              ("Single-photon receiver", "SiPMs, comparators, dark box; measure dark counts (M1.4)."),
              ("Source", "Four diodes, polarizers, combiners, filters to μ = 0.5 (M1.5)."),
              ("Receiver optics", "Passive basis choice, PBS arms, waveplate at 22.5°."),
              ("Sessions", "Clock over coax, gated counting, logs, twin check (M1.6)."),
              ("Eavesdropper", "Optional intercept-resend station in the hallway."))


def two_room_parts(channel: str = "free_space") -> tuple[list[Part], list[Beam]]:
    """Room A: H and V meet on one cube, D and A on another, and the third cube joins the pairs onto the line z = 0
    (each cube takes one beam through its face and one at 90 degrees, so no mirrors are needed). Room B: the passive
    basis cube, then a polarizing cube and two SiPMs per arm, the X arm behind the half-wave plate."""
    y = 0.14
    P = [*_rooms_and_tables(),
         Part("laptopA", "laptop", "Laptop A", _t(-4.5, 0.3), "Runs Site A's half of the protocol; static address on the link subnet.", None, 1),
         Part("laptopB", "laptop", "Laptop B", _t(5.45, 0.45), "Runs Site B's half.", None, 1),
         Part("mcA", "mediaconv", "Media converter A", _t(-4.25, -0.35), "Ethernet to fiber; the authenticated classical channel (qll/link/net_transport.py).", 0, 2),
         Part("mcB", "mediaconv", "Media converter B", _t(4.3, 0.5), "Fiber back to Ethernet in room B.", 0, 2),
         # receiver electronics (stage 4)
         Part("darkbox", "box", "Light-tight receiver box", _t(4.7, -0.12, 0.1), "Felt and black card around the receiver: every leak is a dark count.", 7, 4, param="sipm_dark_hz", size=(1.3, 0.28, 1.15)),
         Part("boost", "supply", "30 V boost module", _t(5.7, 0.05), "Biases the SiPMs at breakdown plus 2.5 V (about 27 V).", 4, 4),
         Part("fpgaB", "fpga", "FPGA B (gate and count)", _t(5.6, -0.45), "Opens a 5 ns gate per clock pulse and logs which detector fired.", 5, 4, param="gate_s"),
         Part("sipmZ0", "sipm", "SiPM Z0 (H)", _t(5.15, 0.0), "MicroFC-30035: 31 % efficient at 420 nm, 300 kHz dark at 21 °C.", 4, 4, param="sipm_pde"),
         Part("sipmZ1", "sipm", "SiPM Z1 (V)", _t(4.8, 0.3), "Second detector of the Z arm.", 4, 4, param="sipm_pde", rot=90),
         Part("sipmX0", "sipm", "SiPM X0 (D)", _t(4.35, -0.6), "First detector of the X arm.", 4, 4, param="sipm_pde", rot=90),
         Part("sipmX1", "sipm", "SiPM X1 (A)", _t(4.7, -0.4), "Second detector of the X arm.", 4, 4, param="sipm_pde"),
         # source (stage 5)
         Part("diodeH", "laser", "405 nm diode (H)", _t(-5.78, 0.0), "Fired at random, one per 1 µs slot, at the signal or decoy current, or not at all (vacuum).", 1, 5, rot=0, param="mu"),
         Part("diodeV", "laser", "405 nm diode (V)", _t(-5.4, -0.26), "Enters the H+V cube from the side.", 1, 5, rot=90, param="mu"),
         Part("diodeD", "laser", "405 nm diode (D)", _t(-5.45, 0.25), "Enters the D+A cube through its face.", 1, 5, rot=0, param="mu"),
         Part("diodeA", "laser", "405 nm diode (A)", _t(-5.05, 0.42), "Enters the D+A cube from the side.", 1, 5, rot=-90, param="mu"),
         Part("polH", "polarizer", "Film polarizer at 0°", _t(-5.6, 0.0), "Fixed polarizer in front of its diode.", 2, 5, param="polarizer_extinction"),
         Part("polV", "polarizer", "Film polarizer at 90°", _t(-5.4, -0.13), "Fixed polarizer in front of its diode.", 2, 5, param="polarizer_extinction", rot=90),
         Part("polD", "polarizer", "Film polarizer at 45°", _t(-5.25, 0.25), "Fixed polarizer in front of its diode.", 2, 5, param="polarizer_extinction"),
         Part("polA", "polarizer", "Film polarizer at 135°", _t(-5.05, 0.33), "Fixed polarizer in front of its diode.", 2, 5, param="polarizer_extinction", rot=90),
         Part("bsHV", "bs", "Combiner H+V", _t(-5.4, 0.0), "50/50 cube: H through the face, V from the side.", 3, 5, rot=45),
         Part("bsDA", "bs", "Combiner D+A", _t(-5.05, 0.25), "50/50 cube: D through the face, A from the side; the pair leaves toward the third cube.", 3, 5, rot=45),
         Part("bsAll", "bs", "Combiner, all four", _t(-5.05, 0.0), "Joins the two pairs onto one beam line.", 3, 5, rot=45),
         Part("pinhole", "iris", "Pinhole spatial filter", _t(-4.85, 0.0), "Makes the four diodes' beams look alike (side channel MR-R2).", 7, 5),
         Part("nd", "nd", "Neutral-density filters", _t(-4.68, 0.0), "Attenuate each pulse to a mean of 0.5 photons (signal) or 0.1 (decoy).", 2, 5, param="mu"),
         Part("fpgaA", "fpga", "FPGA A (pulse and clock)", _t(-5.65, -0.33), "Chooses state and intensity per slot, drives the diodes, sends the clock.", 5, 5),
         # receiver optics (stage 6)
         Part("tubes", "tube", "Black tubes", _t(3.95, 0.0), "Shield the beam line from room light.", 7, 6),
         Part("lensB", "lens", "Collection lens", _t(4.18, 0.0), "Focuses the beam into the analyzer.", 7, 6),
         Part("bsB", "bs", "Basis beamsplitter", _t(4.35, 0.0), "Passive, random basis choice: half the photons go to Z, half to X.", 3, 6, rot=45),
         Part("pbsZ", "pbs", "PBS, Z arm", _t(4.8, 0.0), "Sends H to one SiPM and V to the other.", 3, 6, rot=45),
         Part("hwp", "hwp", "Half-wave plate at 22.5°", _t(4.35, -0.2), "Turns the diagonal basis into the rectilinear one for the X arm.", 2, 6, param="waveplate_error", rot=90),
         Part("pbsX", "pbs", "PBS, X arm", _t(4.35, -0.4), "Sends D to one SiPM and A to the other.", 3, 6, rot=45),
         # synchronization (stage 7)
         Part("coax", "coaxend", "Clock coax", _t(-5.65, -0.42, -0.05), "Room A's FPGA sends one clock edge per slot; timing is public.", 6, 7),
         # eavesdropper (stage 8)
         Part("eveTable", "table", "Eavesdropper's cart", (0.0, 0.0, 0.0), "Optional: an intercept-resend station halfway down the hallway.", None, 8, size=(0.7, 0.5)),
         Part("eveBS", "pbs", "Eve's analyzer", _t(-0.15, 0.0), "Measures each pulse in a random basis...", 3, 8, rot=45, param="eve_fraction"),
         Part("eveDet", "sipm", "Eve's detector", _t(-0.15, 0.18), "...with her own detector...", 4, 8, param="eve_fraction", rot=90),
         Part("eveLaser", "laser", "Eve's resend diodes", _t(0.15, 0.0), "...and re-sends what she saw: about 25 % errors where she guessed the basis wrong.", 1, 8, rot=0, param="eve_fraction"),
         ]
    beams = [Beam("classical", ((-4.25, TABLE_Y + 0.03, -0.35), (-4.25, 2.4, -0.35), (4.3, 2.4, 0.5), (4.3, TABLE_Y + 0.03, 0.5)), "duplex fiber: authenticated classical channel", 2),
             Beam("sync", ((-5.65, TABLE_Y + 0.02, -0.42), (-5.65, 2.3, -0.42), (5.6, 2.3, -0.45), (5.6, TABLE_Y + 0.02, -0.45)), "clock coax: one edge per slot", 7),
             Beam("violet", (_t(-5.78, 0.0, y), _t(-5.4, 0.0, y)), "", 5), Beam("violet", (_t(-5.4, -0.26, y), _t(-5.4, 0.0, y)), "", 5),
             Beam("violet", (_t(-5.45, 0.25, y), _t(-5.05, 0.25, y)), "", 5), Beam("violet", (_t(-5.05, 0.42, y), _t(-5.05, 0.25, y)), "", 5),
             Beam("violet", (_t(-5.4, 0.0, y), _t(-5.05, 0.0, y)), "", 5), Beam("violet", (_t(-5.05, 0.25, y), _t(-5.05, 0.0, y)), "", 5),
             Beam("violet", (_t(-5.05, 0.0, y), _t(-0.15, 0.0, y), _t(4.18, 0.0, y), _t(4.35, 0.0, y), _t(4.8, 0.0, y), _t(5.15, 0.0, y)), "weak pulses, 0.5 photons", 5),
             Beam("violet", (_t(4.8, 0.0, y), _t(4.8, 0.3, y)), "", 6),
             Beam("violet", (_t(4.35, 0.0, y), _t(4.35, -0.2, y), _t(4.35, -0.4, y), _t(4.35, -0.6, y)), "", 6),
             Beam("violet", (_t(4.35, -0.4, y), _t(4.7, -0.4, y)), "", 6)]
    if channel == "fiber":
        beams.append(Beam("violet", (_t(-4.6, 0.0, y), (-4.6, 0.2, 1.4), (4.0, 0.2, 1.4), _t(4.18, 0.0, y)), "405 nm single-mode fiber (rejected by the twin)", 5))
    return P, beams


def two_room() -> Tier:
    parts, beams = two_room_parts()
    return Tier("two_room", "The two-room single-photon link", "main", ("P10", "T3"), ("M1.1", "M1.3", "M1.4", "M1.5", "M1.6"), "two_room",
                "$530–1,180 (likely about $600)",
                "Weak 405 nm pulses at 0.5 photons, four polarization states, decoy pulses, four SiPMs, FPGA gating, free space across a hallway; "
                "a fiber classical channel carries the authenticated protocol. The twin predicts the clicks, errors, and key before you buy a part.",
                "experiments/protocols/P10_two_room_single_photon_link.md", P10_BOM, P10_STAGES, tuple(parts), tuple(beams),
                (Slider("mu", "Signal mean photon number μ", 0.05, 1.0, 0.01, 0.5), Slider("mu_decoy", "Decoy μ", 0.01, 0.4, 0.01, 0.1),
                 Slider("free_space_loss_db", "Path loss (clipping, windows)", 0, 12, 0.1, 2.0, "dB"),
                 Slider("receiver_loss_db", "Receiver loss", 0, 6, 0.1, 1.5, "dB"),
                 Slider("sipm_pde", "SiPM detection efficiency", 0.05, 0.6, 0.01, 0.31),
                 Slider("sipm_dark_hz", "SiPM dark rate", 10e3, 2e6, 10e3, 300e3, "Hz", True),
                 Slider("gate_s", "Gate width", 1e-9, 20e-9, 0.5e-9, 5e-9, "s"),
                 Slider("sipm_afterpulse", "Afterpulse probability", 0, 0.05, 0.001, 0.002),
                 Slider("polarizer_extinction", "Polarizer extinction ratio", 20, 2000, 10, 500, "", True),
                 Slider("waveplate_error", "Waveplate error", 0, 0.05, 0.001, 0.01),
                 Slider("rep_rate_hz", "Pulse rate", 1e5, 5e6, 1e5, 1e6, "Hz"),
                 Slider("n_pulses", "Pulses per session", 1e6, 5e7, 1e6, 1e7, "", True),
                 Slider("eve_fraction", "Intercepted fraction (stage 8)", 0, 1, 0.05, 0.0)),
                {"simulate": "python -c \"from qll.link import two_room as T; print(T.predict())\"",
                 "synthetic": "python -c \"from qll.link import two_room as T; from qll.link.hardware_log import simulate_quantum, write_site_logs; "
                              "write_site_logs(simulate_quantum(T.config()), 'room_a.csv', 'room_b.csv')\"",
                 "real": "python -m qll.link.run ingest room_a.csv --bob room_b.csv --config two_room_measured.json"},
                claim="Laboratory-grade: single-photon-level states between rooms and a decoy-state key; source side channels and detector attacks are not addressed.")


# ------------------------------------------------------------------------------------------- Tier 3: the upgrade
TIER3_BOM = (("Laser diodes near 850 nm with nanosecond drivers, or one diode and a liquid-crystal rotator", "source", 100, 600),
             ("Polarizers, beamsplitters, half-wave plate, mounts", "encoding and analysis", 300, 1000),
             ("ND filters, an attenuator, and a power meter with a calibrated sensor", "mean photon number", 200, 800),
             ("Single-photon avalanche diode modules (used), 2–4", "detection", 1000, 6000),
             ("FPGA board for pulses and time tagging, or a used time tagger", "timing", 100, 2000),
             ("780HP fiber spools and paddles", "the channel", 100, 400))


def tier3() -> Tier:
    parts, beams = two_room_parts()
    up = []
    for p in parts:
        if p.id.startswith("eve") or p.id in ("pinhole", "boost"):
            continue
        if p.kind == "sipm":
            p = Part(p.id, "spad", p.label.replace("SiPM", "SPAD module"), p.pos, "Used silicon single-photon avalanche diode module: about 50 % at 850 nm, a few hundred dark counts per second.", 3, p.stage, p.rot, "detector_efficiency")
        elif p.kind == "laser":
            p = Part(p.id, "laser", p.label.replace("405", "850"), p.pos, "850 nm diode, invisible: align with a card viewer and keep the beam enclosed.", 0, p.stage, p.rot, "mu_signal")
        elif p.id == "nd":
            p = Part("atten", "nd", "Attenuator + power meter", p.pos, "Set and verify μ with a calibrated sensor.", 2, 4, param="mu_signal")
        elif p.kind in ("bs", "pbs", "hwp", "polarizer"):
            p = Part(p.id, p.kind, p.label, p.pos, p.note, 1, p.stage, p.rot, p.param)
        elif p.kind == "fpga":
            p = Part(p.id, "fpga", p.label.replace("FPGA", "FPGA / time tagger"), p.pos, p.note, 4, p.stage, p.rot, p.param)
        elif p.bom is not None:
            p = Part(p.id, p.kind, p.label, p.pos, p.note, None, p.stage, p.rot, p.param, p.size)
        up.append(p)
    remap = {"sipm_dark_hz": "dark_count_prob", "gate_s": "dark_count_prob", "mu": "mu_signal", "sipm_pde": "detector_efficiency",
             "polarizer_extinction": "misalignment_error", "waveplate_error": "misalignment_error"}
    up = [replace(p, param=remap.get(p.param, p.param)) for p in up]
    up += [Part("spool", "spool", "780HP fiber spool", (0.0, 0.25, 1.2), "The channel: 0–5 km of fiber at 3.5 dB/km near 850 nm.", 5, 5, param="distance_km"),
           Part("paddles", "paddles", "Polarization paddles", _t(3.6, 0.35), "Undo the fiber's polarization rotation.", 5, 6)]
    bm = [b for b in beams if not (b.kind == "violet" and b.label == "weak pulses, 0.5 photons")]
    bm = [Beam("nir" if b.kind == "violet" else b.kind, b.points, b.label, b.stage) for b in bm]
    y = 0.14
    bm.append(Beam("nir", (_t(-5.05, 0.0, y), _t(-4.6, 0.0, y), (-4.4, 0.4, 1.2), (0.0, 0.4, 1.2), (3.4, 0.4, 1.2), _t(3.6, 0.35, y), _t(4.18, 0.0, y),
                           _t(4.35, 0.0, y), _t(4.8, 0.0, y), _t(5.15, 0.0, y)), "850 nm weak pulses through fiber", 5))
    return Tier("tier3", "Upgrade: avalanche-diode detectors and fiber", "upgrade", ("T3", "P07"), ("M1.6",), "tier3", "$2,000–8,000 planning (itemized rows span $1,800–10,800)",
                "The same protocol with used single-photon avalanche diode modules at 850 nm and a fiber spool: far fewer dark counts, so the key survives kilometres of fiber.",
                "systems/see510/10_real_world_experiments.md", TIER3_BOM, P10_STAGES[:7], tuple(up), tuple(bm),
                (Slider("distance_km", "Fiber length", 0, 15, 0.1, 0.0, "km"), Slider("attenuation_db_per_km", "Fiber loss", 2, 5, 0.1, 3.5, "dB/km"),
                 Slider("mu_signal", "Signal μ", 0.05, 1, 0.01, 0.5), Slider("mu_decoy", "Decoy μ", 0.01, 0.4, 0.01, 0.1),
                 Slider("detector_efficiency", "Detector efficiency", 0.1, 0.7, 0.01, 0.5), Slider("dark_count_prob", "Dark count per gate", 1e-8, 1e-3, 1e-8, 1e-6, "", True),
                 Slider("misalignment_error", "Misalignment", 0, 0.08, 0.001, 0.02), Slider("receiver_loss_db", "Receiver loss", 0, 8, 0.1, 3.0, "dB")),
                {"simulate": "python -m qll.link.run session --config systems/see510/hardware/tier3.json",
                 "real": "python -m qll.link.run ingest room_a.csv --bob room_b.csv --config systems/see510/hardware/tier3.json"},
                claim="Laboratory-grade against photon-number splitting; detector attacks not addressed.")


# ----------------------------------------------------------------------------------------- Tier 4: entanglement
TIER4_BOM = (("Pump laser near 405 nm", "source", 500, 5000), ("Down-conversion crystals (two crossed BBO, or PPKTP in a Sagnac loop)", "pairs", 1000, 5000),
             ("Single-photon detectors, four", "detection", 4000, 20000), ("Time tagger", "coincidences", 3000, 15000),
             ("Optics and mounts, fiber couplers, fibers", "analysis", 2000, 8000))


def tier4() -> Tier:
    y = 0.14
    P = [*_rooms_and_tables(),
         Part("laptopA", "laptop", "Laptop A", _t(-5.3, 0.3), "Site A's half of the protocol.", None, 1),
         Part("laptopB", "laptop", "Laptop B", _t(5.45, 0.45), "Site B's half.", None, 1),
         Part("mcA", "mediaconv", "Media converter A", _t(-4.25, -0.35), "Authenticated classical channel, as in Phase 1.", None, 1),
         Part("mcB", "mediaconv", "Media converter B", _t(4.3, 0.5), "Fiber back to Ethernet in room B.", None, 1),
         Part("pump", "pump", "405 nm pump laser (class 3B, enclosed)", _t(-5.7, -0.25), "Pumps the crystals; register it with your laser safety officer.", 0, 2),
         Part("bbo", "crystal", "Crossed BBO crystals", _t(-5.25, -0.25), "Spontaneous parametric down-conversion: pairs at 810 nm in |Φ⁺⟩.", 1, 2, param="visibility"),
         Part("hwpPump", "hwp", "Pump half-wave plate", _t(-5.45, -0.25), "Sets the pump polarization at 45° so both crystals fire equally.", 4, 2),
         Part("cplA", "lens", "Fiber coupler, photon A", _t(-5.0, -0.1), "Collects one photon of each pair.", 4, 2),
         Part("cplB", "lens", "Fiber coupler, photon B", _t(-5.0, -0.4), "Collects the partner photon for room B.", 4, 2),
         Part("anaA_hwp", "hwp", "Analyzer A: waveplate", _t(-4.75, 0.15), "Chooses Z or X for room A.", 4, 3),
         Part("anaA_pbs", "pbs", "Analyzer A: PBS", _t(-4.55, 0.15), "Splits by polarization.", 4, 3, rot=45),
         Part("detA0", "spad", "Detector A0", _t(-4.3, 0.15), "Single-photon avalanche diode.", 2, 3, param="detector_efficiency"),
         Part("detA1", "spad", "Detector A1", _t(-4.55, 0.42), "", 2, 3, param="detector_efficiency", rot=90),
         Part("spool", "spool", "Fiber to room B", (0.0, 0.25, 1.2), "Photon B travels through fiber; add spools to stretch the link.", 4, 2, param="distance_km"),
         Part("anaB_hwp", "hwp", "Analyzer B: waveplate", _t(4.3, 0.0), "Chooses Z or X for room B.", 4, 3),
         Part("anaB_pbs", "pbs", "Analyzer B: PBS", _t(4.6, 0.0), "Splits by polarization.", 4, 3, rot=45),
         Part("detB0", "spad", "Detector B0", _t(4.95, 0.0), "", 2, 3, param="detector_efficiency"),
         Part("detB1", "spad", "Detector B1", _t(4.6, 0.32), "", 2, 3, param="detector_efficiency", rot=90),
         Part("tagA", "timetagger", "Time tagger A", _t(-5.75, 0.3), "Timestamps every detection against a shared clock.", 3, 4),
         Part("tagB", "timetagger", "Time tagger B", _t(5.5, -0.3), "Coincidences within a few nanoseconds; accidentals are the background.", 3, 4, param="dark_count_prob"),
         Part("coax", "coaxend", "Clock / GPS reference", _t(-5.75, 0.42, -0.05), "Shared clock for the two taggers.", None, 4)]
    beams = (Beam("pump", (_t(-5.7, -0.25, y), _t(-5.25, -0.25, y)), "405 nm pump", 2),
             Beam("pair", (_t(-5.25, -0.25, y), _t(-5.0, -0.1, y), _t(-4.75, 0.15, y), _t(-4.55, 0.15, y), _t(-4.3, 0.15, y)), "photon A", 2),
             Beam("pair", (_t(-4.55, 0.15, y), _t(-4.55, 0.42, y)), "", 3),
             Beam("pair", (_t(-5.25, -0.25, y), _t(-5.0, -0.4, y), (-4.6, 0.3, 1.2), (0.0, 0.3, 1.2), (3.6, 0.3, 1.2), _t(4.3, 0.0, y), _t(4.6, 0.0, y), _t(4.95, 0.0, y)), "photon B through fiber", 2),
             Beam("pair", (_t(4.6, 0.0, y), _t(4.6, 0.32, y)), "", 3),
             Beam("classical", ((-4.25, TABLE_Y + 0.03, -0.35), (-4.25, 2.4, -0.35), (4.3, 2.4, 0.5), (4.3, TABLE_Y + 0.03, 0.5)), "classical channel", 1),
             Beam("sync", ((-5.75, TABLE_Y + 0.05, 0.3), (-5.75, 2.3, 0.3), (5.5, 2.3, -0.3), (5.5, TABLE_Y + 0.05, -0.3)), "shared clock", 4))
    return Tier("tier4", "Entangled photons between the rooms (BBM92)", "entangled", ("T4", "P03", "D03"), ("M2.1", "M2.2", "M2.3", "M2.4"), "tier4",
                "$15,000–60,000 planning (itemized $10,500–53,000), or a borrowed teaching kit",
                "A down-conversion source shares polarization-entangled pairs between the rooms. A Bell test certifies the source; matched-basis outcomes make the key. "
                "Phase 2 borrows the source (risk MR-R3), and the same rig runs the photonic collapse code (M2.4).",
                "systems/see510/10_real_world_experiments.md", TIER4_BOM,
                (("Simulate", "Predict with tier4.json."), ("Borrow or build the source", "Pump, crystals, couplers (P03)."),
                 ("Analyzers", "Waveplate, PBS, two detectors per room."), ("Timing and sessions", "Taggers, Bell test, then keys.")),
                tuple(P), beams,
                (Slider("visibility", "Pair visibility V", 0.7, 1.0, 0.005, 0.94), Slider("distance_km", "Fiber to room B", 0, 10, 0.1, 1.0, "km"),
                 Slider("detector_efficiency", "Collection × detection (B)", 0.05, 0.6, 0.01, 0.25), Slider("dark_count_prob", "Accidentals per window", 1e-7, 1e-3, 1e-7, 1e-5, "", True),
                 Slider("pulse_rate_hz", "Detected pairs at A", 5e3, 5e5, 5e3, 5e4, "Hz", True), Slider("session_s", "Session length", 5, 300, 5, 40, "s")),
                {"simulate": "python -m qll.link.run session --config systems/see510/hardware/tier4.json",
                 "real": "python -m qll.link.run ingest room_a.csv --bob room_b.csv --config systems/see510/hardware/tier4.json"},
                claim="Laboratory-grade, not device-independent; the Bell value certifies the source.")


# ------------------------------------------------------------------------------------------- circuits experiments
def _cloud_parts(device: str = "ibm") -> list[Part]:
    if device == "majorana":
        return [Part("fridge", "fridge", "Dilution refrigerator (partner lab)", (0.0, 0.0, 0.0), "Millikelvin stage for a topological device; outside funding or a partner only (M4.6).", None, 3),
                Part("device", "nanowire", "Two tetrons: six Majorana zero modes", (0.0, 0.78, 0.0), "Superconductor-semiconductor wires; parity read by quantum-dot interferometry [plugge2017] [karzig2017].", None, 3),
                Part("laptop", "laptop", "Your laptop", (2.2, TABLE_Y + 0.08, 0.0), "Runs the emulation and the error budget.", None, 1),
                Part("table", "table", "Desk", (2.2, 0.0, 0.0), "", None, 1, size=(1.2, 0.7))]
    return [Part("table", "table", "Desk", (2.2, 0.0, 0.0), "", None, 1, size=(1.2, 0.7)),
            Part("laptop", "laptop", "Your laptop", (2.2, TABLE_Y + 0.08, 0.0), "Builds the circuits; runs the simulator; submits jobs.", None, 1),
            Part("cloud", "cloud", "Internet and the provider's queue", (0.0, 2.2, 0.0), "Jobs travel as circuits; results come back as counts.", None, 2),
            Part("fridge", "fridge", "Cloud processor (dilution refrigerator)", (-2.0, 0.0, 0.0), "A superconducting processor near 10 mK: free time on the open plan [ibm2026openplan].", None, 3),
            Part("chip", "chip", "Qubit chip", (-2.0, 0.78, 0.0), "Pick neighbouring qubits for the circuit, and far ones for the crosstalk control.", None, 3)]


def _cloud_beams(device="ibm") -> tuple[Beam, ...]:
    if device == "majorana":
        return (Beam("usb", ((2.2, TABLE_Y + 0.1, 0.0), (0.0, 1.6, 0.0)), "control and readout", 3),)
    return (Beam("cloud", ((2.2, TABLE_Y + 0.2, 0.0), (0.0, 2.2, 0.0)), "jobs out, counts back", 2), Beam("cloud", ((0.0, 2.2, 0.0), (-2.0, 1.9, 0.0)), "", 2))


CLOUD_BOM = (("Laptop and internet", "owned", 0, 0), ("Simulator and fake devices (Qiskit Aer)", "rehearsal", 0, 0), ("Open-plan processor time, about 10 minutes a month", "cloud runs", 0, 0))
CLOUD_STAGES = (("In the browser", "Exact density matrices, this page."), ("Rehearse", "Aer with a noise model, and a fake device."), ("Run on hardware", "The free open plan; record calibration and layout."))


def circuit_tiers() -> list[Tier]:
    common = dict(rooms=False, bom=CLOUD_BOM, stages=CLOUD_STAGES)
    return [
        Tier("collapse", "Can collapse carry a message? (P11)", "cloud", ("P11", "E17", "E16"), ("M1.2",), "collapse", "$0",
             "Alice encodes a bit in what she does to her half of entangled pairs; Bob, never told, tries to read it from his half. The exact density matrix shows why he cannot, and the leak control shows the analysis would notice a real channel.",
             "experiments/protocols/P11_collapse_code_on_a_cloud_processor.md", parts=tuple(_cloud_parts()), beams=_cloud_beams(),
             sliders=(Slider("visibility", "Pair visibility V", 0.5, 1.0, 0.01, 0.97), Slider("leak", "Injected leak (control)", 0, 0.3, 0.005, 0.0)),
             commands={"simulate": "python experiments/bench/E17_collapse_code/run_collapse_code.py run --backend aer --scheme basis",
                       "real": "python experiments/bench/E17_collapse_code/run_collapse_code.py run --backend ibm_torino --scheme basis --shots 20000"},
             claim="A measured upper bound on information per use; never a faster-than-light channel.", **common),
        Tier("teleport", "Teleportation and superdense coding (P12)", "cloud", ("P12", "D07"), ("M4.1", "M4.2"), "teleport", "$0",
             "Teleport the six cardinal states with two classical bits, then without them; send two bits on one qubit, then keep the qubit. Fidelity above 2/3 needs the bits.",
             "experiments/protocols/P12_teleportation_and_superdense_coding_on_a_cloud_processor.md", parts=tuple(_cloud_parts()), beams=_cloud_beams(),
             sliders=(Slider("p2", "Two-qubit gate error p₂", 0, 0.2, 0.002, 0.02),),
             commands={"simulate": "python experiments/bench/frontier/run_frontier.py teleport --backend aer",
                       "real": "python experiments/bench/frontier/run_frontier.py teleport --backend ibm_torino"},
             claim="State transfer needs the two classical bits; nothing outruns them.", **common),
        Tier("majorana", "Majorana parity teleportation (P13)", "device", ("P13", "E18"), ("M4.6",), "majorana", "$0 emulated; a partner lab for devices",
             "Measurement-only teleportation of Crogman, Dang, and Erenso (2025): two parity measurements and two classical bits give fidelity 1; one bit gives at most 2/3. The error budget maps device knobs to fidelity.",
             "experiments/protocols/P13_majorana_teleportation_on_a_cloud_processor.md", parts=tuple(_cloud_parts("majorana")), beams=_cloud_beams("majorana"),
             sliders=(Slider("snr0", "Readout signal-to-noise μ₀/σ", 0.5, 8, 0.1, 4), Slider("gap", "Gap over thermal energy Δ/kT", 0.5, 20, 0.5, 5),
                      Slider("poison", "Poisoning per readout Γτ", 0, 0.1, 0.001, 0.01), Slider("l", "Separation L/ξ", 0.5, 8, 0.1, 3)),
             commands={"simulate": "python experiments/bench/frontier/run_frontier.py majorana --backend aer",
                       "real": "python experiments/bench/frontier/run_frontier.py majorana --backend ibm_torino"},
             claim="An emulation on qubits; a topological device needs a partner (T16).", **common),
    ]


def link_tiers() -> list[Tier]:
    return [tier1(), two_room(), tier3(), tier4()]


def bom_total(t: Tier) -> tuple[float, float]:
    return sum(r[2] for r in t.bom), sum(r[3] for r in t.bom)


def export() -> dict:
    def tier(t: Tier) -> dict:
        d = asdict(t)
        d["bom_total"] = bom_total(t)
        return d
    return {"link": [tier(t) for t in link_tiers()], "circuits": [tier(t) for t in circuit_tiers()]}
