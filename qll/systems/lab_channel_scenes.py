"""The quantum-channel lab's builds (docs/lab/channel/), ladder from a channel you can play with on a laptop to
superdense coding through the hallway. Each tier reuses a build from qll/systems/lab_scenes.py and adds what the
quantum-channel experiment needs: two quarter-wave plates for tomography (P14), a fiber spool with drift, a cloud
processor for teleportation's channel, and Alice's encoder and Bob's Bell measurement for E19.
"""
from __future__ import annotations

from dataclasses import replace

from qll.systems.lab_scenes import (CLOUD_STAGES, TABLE_Y, Beam, Part, Slider, Tier, _cloud_beams, _cloud_parts, _rooms_and_tables, _t,
                                    tier3, two_room_parts)

TWO_ROOM_ROW = ("The two-room P10 build (see the two-room lab)", "source, hallway, receiver, timing", 530, 1180)
QWP_ROW = ("Two quarter-wave retarders cut from one film sheet, and a printed flip mount", "a circular input and a circular measurement", 10, 30)
TOMO_STAGES = (("Certify from BB84 counts", "No new parts: e_Z and e_X bound the entanglement fidelity."),
               ("Add a circular input", "Quarter-wave plate behind the 45° polarizer: that diode sends R."),
               ("Add a circular measurement", "Flip a quarter-wave plate into the X arm: it measures Y."),
               ("Tomography sessions", "Four ten-second sessions, every click logged as input, basis, outcome."))


def zoo() -> Tier:
    parts = (Part("table", "table", "Desk", (2.2, 0.0, 0.0), "", None, 1, size=(1.2, 0.7)),
             Part("laptop", "laptop", "Your laptop", (2.2, TABLE_Y + 0.08, 0.0), "Every channel here is computed exactly, as in qll/circuits/qubit_channel.py.", 0, 1))
    return Tier("zoo", "Starter: build a channel from five noise processes", "starter", ("P14",), ("M1.8",), "zoo", "$0",
                "Stack depolarizing noise, dephasing, energy loss, a rotation, and a measure-and-resend relay, and watch what each does to the sphere "
                "of polarizations, whether the channel stays quantum, and what it can still carry.",
                "systems/program/09_quantum_channels.md", (("A laptop", "owned", 0, 0),), (("Pick the noise", "Sliders compose five channels in order."),),
                parts, (), (Slider("p_dep", "Depolarizing p", 0, 1, 0.01, 0.0), Slider("lam_deph", "Dephasing λ", 0, 1, 0.01, 0.0),
                            Slider("gamma", "Amplitude damping γ (energy loss)", 0, 1, 0.01, 0.0), Slider("theta", "Rotation angle (degrees)", 0, 180, 1, 0.0),
                            Slider("f_ir", "Measure-and-resend fraction", 0, 1, 0.01, 0.0)),
                {"simulate": "python -c \"from qll.circuits import qubit_channel as Q; R = Q.compose(Q.depolarizing_ptm(0.1), Q.rotation_ptm(0.3)); "
                             "print(Q.entanglement_fidelity(R), Q.is_entanglement_breaking(R), Q.hashing_bound(R))\""},
                rooms=False, claim="Exact channel arithmetic; no hardware.")


def hallway() -> Tier:
    parts, beams = two_room_parts()
    parts = [replace(p, bom=0 if p.bom is not None else None, stage=1 if p.stage else 0) for p in parts]
    beams = [replace(b, stage=1 if b.stage else 0) for b in beams]
    parts += [Part("qwpSource", "qwp", "Quarter-wave plate (makes R)", _t(-5.16, 0.25), "Behind the 45° polarizer of the D diode, fast axis horizontal: that diode now sends circular light.", 1, 2),
              Part("qwpFlip", "qwp", "Flip-in quarter-wave plate (measures Y)", _t(4.35, -0.11), "Fast axis horizontal, in front of the X arm's half-wave plate: flipped in, the X arm measures Y.", 1, 3, rot=90)]
    return Tier("hallway", "The hallway, certified and mapped as a quantum channel", "main", ("P14", "P10"), ("M1.8",), "hallway", "$10–30 on top of P10",
                "The P10 link, seen as a quantum channel: the BB84 error rates certify it is not a classical relay, two quarter-wave plates add the "
                "third direction for full tomography, and the measured map gives what the hallway can carry: bits, qubits, and secret key.",
                "experiments/protocols/P14_the_hallway_as_a_quantum_channel.md", (TWO_ROOM_ROW, QWP_ROW), TOMO_STAGES, tuple(parts), tuple(beams),
                (Slider("polarizer_extinction", "Polarizer extinction ratio", 20, 2000, 10, 500, "", True), Slider("waveplate_error", "Waveplate error", 0, 0.05, 0.001, 0.01),
                 Slider("sipm_dark_hz", "SiPM dark rate", 10e3, 2e6, 10e3, 300e3, "Hz", True), Slider("free_space_loss_db", "Path loss", 0, 12, 0.1, 2.0, "dB"),
                 Slider("sipm_pde", "SiPM detection efficiency", 0.05, 0.6, 0.01, 0.31), Slider("eve_fraction", "Measure-and-resend fraction (Eve)", 0, 1, 0.05, 0.0),
                 Slider("shots", "Clicks per tomography setting", 200, 50000, 100, 5000, "", True)),
                {"simulate": "python -c \"from qll.link.hallway_channel import hallway_channel; print(hallway_channel())\"",
                 "real": "python -c \"from qll.link import channel_tomography as CT; n = CT.read_log('tomography.csv'); print(CT.estimate(n), CT.certify(n))\""},
                claim="Certifies the click-conditioned channel and, with decoys, its single-photon part; it does not certify the devices themselves.")


def fiber() -> Tier:
    t = tier3()
    parts = [replace(p, bom=0 if p.bom is not None else None, stage=1 if p.stage else 0) for p in t.parts]
    parts = [replace(p, stage=2) if p.id in ("spool", "paddles") else p for p in parts]
    parts = [replace(p, param="theta") if p.id in ("spool", "paddles") else p for p in parts]
    return Tier("fiber", "Through a fiber spool: drift is a rotation", "upgrade", ("P14", "T3", "P07"), ("M1.8",), "fiber", "$100–400 for the spool and paddles",
                "In fiber, temperature and stress rotate the polarization slowly: the channel is a rotation of the sphere, which the error rates see as "
                "noise until the paddles turn it back. The map from tomography tells you exactly how to set them.",
                "experiments/protocols/P07_bb84_over_a_fiber_spool.md", (("Fiber spool, 780HP class, and polarization paddles", "the channel", 100, 400),),
                (("Rotate", "Drift tilts the sphere."), ("Measure", "Tomography finds the rotation."), ("Correct", "Paddles undo it.")),
                tuple(parts), tuple(replace(b, stage=1 if b.stage else 0) for b in t.beams),
                (Slider("theta", "Drift rotation (degrees)", 0, 180, 1, 25), Slider("tilt", "Drift axis tilt from vertical (degrees)", 0, 90, 1, 60),
                 Slider("p_dep", "Depolarization (mode mixing)", 0, 0.3, 0.005, 0.02), Slider("correction", "Paddle correction applied", 0, 1, 0.01, 0.0)),
                {"simulate": "python -c \"from qll.circuits import qubit_channel as Q; import math; R = Q.compose(Q.rotation_ptm(math.radians(25), (1, 0, 0.6)), Q.depolarizing_ptm(0.02)); print(Q.basis_errors(R))\""},
                claim="A model of drift: measure your spool's rotation and its rate of change before trusting a correction.")


def teleport_channel() -> Tier:
    return Tier("teleport", "Teleportation is a quantum channel (with its two bits)", "cloud", ("P14", "P12"), ("M4.7",), "teleport", "$0",
                "Entanglement plus two classical bits per qubit makes a quantum channel; without the bits it is completely depolarizing. Tomography on a "
                "free cloud processor measures it with the same estimator as the hallway.",
                "experiments/protocols/P14_the_hallway_as_a_quantum_channel.md", (("Laptop and the free open plan", "cloud runs", 0, 0),), CLOUD_STAGES,
                tuple(_cloud_parts()), _cloud_beams(), (Slider("p2", "Two-qubit gate error p₂", 0, 0.3, 0.002, 0.03),),
                {"simulate": "python -c \"from qll.circuits import teleport_channel_cloud as TC; from qll.circuits.cloud_run import run_aer; from qll.link import channel_tomography as CT; "
                             "k, c = TC.circuits('feedforward'); n = TC.counts_to_tomography(k, run_aer(c, 20000)); print(CT.estimate(n), CT.certify(n))\""},
                rooms=False, claim="The classical bits are part of the channel; nothing outruns them.")


SD_BOM = (("Borrowed entangled-photon kit: pump, crystals, couplers, four detectors, time tagger", "source and detection (Phase 2 loan)", 0, 0),
          ("Alice's half-wave and quarter-wave plates on rotation mounts", "the encoder", 60, 400),
          ("50/50 beamsplitter and two polarizing beamsplitters", "Bob's Bell measurement", 80, 400),
          ("Fiber to room A, collimators, and a fiber delay line", "matching the photons' arrival times", 60, 500),
          ("Mounts, irises, black tubes", "mechanics", 0, 200))


def superdense() -> Tier:
    y = 0.14
    P = [*_rooms_and_tables(),
         Part("laptopA", "laptop", "Laptop A (picks the message)", _t(-4.5, 0.3), "Chooses one of three messages per photon and sets the waveplates.", None, 1),
         Part("laptopB", "laptop", "Laptop B (reads it)", _t(5.45, 0.45), "Logs which detectors fired together.", None, 1),
         Part("pump", "pump", "405 nm pump (kit)", _t(5.75, -0.45), "Pumps the down-conversion crystals in room B.", 0, 1),
         Part("bbo", "crystal", "Entangled-pair crystals (kit)", _t(5.35, -0.45), "Pairs in |Φ⁺⟩.", 0, 1, param="visibility"),
         Part("cplA", "lens", "Coupler: photon to Alice", _t(5.1, -0.35), "One photon of each pair goes to room A through fiber.", 3, 1),
         Part("cplB", "lens", "Coupler: photon kept by Bob", _t(5.1, -0.55), "The partner waits in a fiber delay.", 3, 1),
         Part("delay", "spool", "Fiber delay line", (5.0, 0.25, -1.1), "Holds Bob's photon until Alice's arrives, within its coherence time.", 3, 2, param="v_hom"),
         Part("colA", "lens", "Fiber collimator (room A)", _t(-5.6, 0.0), "Alice's photon leaves the fiber.", 3, 2),
         Part("hwpA", "hwp", "Encoder: half-wave plate", _t(-5.3, 0.0), "Applies X or not.", 1, 2),
         Part("qwpA", "qwp", "Encoder: quarter-wave plate", _t(-5.05, 0.0), "With the half-wave plate, applies Z or not.", 1, 2),
         Part("launch", "lens", "Launch lens", _t(-4.75, 0.0), "Sends the encoded photon across the hallway.", 4, 2),
         Part("bsm", "bs", "Bell measurement: 50/50 beamsplitter", _t(4.35, 0.0), "Alice's and Bob's photons interfere here.", 2, 3, rot=45, param="v_hom"),
         Part("pbs1", "pbs", "Polarizing beamsplitter 1", _t(4.75, 0.0), "Resolves polarization in output 1.", 2, 3, rot=45),
         Part("pbs2", "pbs", "Polarizing beamsplitter 2", _t(4.35, 0.4), "Resolves polarization in output 2.", 2, 3, rot=45),
         Part("d1", "spad", "Detector 1H", _t(5.1, 0.0), "", 0, 3), Part("d2", "spad", "Detector 1V", _t(4.75, -0.3), "", 0, 3, rot=90),
         Part("d3", "spad", "Detector 2H", _t(4.35, 0.62), "", 0, 3, rot=90), Part("d4", "spad", "Detector 2V", _t(4.7, 0.4), "", 0, 3),
         Part("tag", "timetagger", "Time tagger (kit)", _t(5.6, 0.1), "Coincidences within a few nanoseconds.", 0, 3)]
    beams = (Beam("pump", (_t(5.75, -0.45, y), _t(5.35, -0.45, y)), "405 nm pump", 1),
             Beam("pair", (_t(5.35, -0.45, y), _t(5.1, -0.35, y), (4.9, 0.3, -1.6), (-4.0, 0.3, -1.6), (-5.6, 0.3, -0.6), _t(-5.6, 0.0, y)), "photon to Alice, by fiber", 2),
             Beam("pair", (_t(-5.6, 0.0, y), _t(-5.3, 0.0, y), _t(-5.05, 0.0, y), _t(-4.75, 0.0, y), _t(0.0, 0.0, y), _t(4.35, 0.0, y), _t(4.75, 0.0, y), _t(5.1, 0.0, y)),
                  "the encoded photon crosses the hallway: the message", 2, main=True),
             Beam("pair", (_t(5.35, -0.45, y), _t(5.1, -0.55, y), (5.0, 0.3, -1.1), (4.35, 0.3, -0.6), _t(4.35, -0.3, y), _t(4.35, 0.0, y), _t(4.35, 0.4, y), _t(4.35, 0.62, y)), "Bob's photon, delayed", 2),
             Beam("pair", (_t(4.75, 0.0, y), _t(4.75, -0.3, y)), "", 3), Beam("pair", (_t(4.35, 0.4, y), _t(4.7, 0.4, y)), "", 3))
    return Tier("superdense", "Superdense coding through the hallway (E19)", "entangled", ("E19", "T4"), ("M2.6",), "superdense", "$200–1,500 with a borrowed kit",
                "The photon that crosses the hallway is the message, and because its partner was shared beforehand it can carry log₂3 = 1.58 bits instead "
                "of the one bit any single photon carries alone. Pair visibility and two-photon interference decide whether the experiment beats one bit.",
                "experiments/proposed/E19_superdense_coding_through_the_hallway.md", SD_BOM,
                (("Share the pairs", "Source in room B; one photon to Alice by fiber."), ("Encode and send", "Alice's waveplates; the photon crosses the hallway."),
                 ("Bell measurement", "Interfere with Bob's delayed photon; three classes.")),
                tuple(P), beams, (Slider("visibility", "Pair visibility V", 0.5, 1, 0.005, 0.94), Slider("v_hom", "Two-photon interference visibility", 0.3, 1, 0.01, 0.9)),
                {"simulate": "python -c \"from qll.circuits import superdense_photonic as SP; print(SP.bits_per_photon(0.94, 0.9))\""},
                claim="Information per detected pair; exceeding one bit assumes fair sampling (losses independent of the message).")


def _keep_params(t: Tier) -> Tier:
    """Parts point only at sliders this tier has."""
    keys = {sl.key for sl in t.sliders}
    return replace(t, parts=tuple(replace(p, param=p.param if p.param in keys else "") for p in t.parts))


def channel_tiers() -> list[Tier]:
    return [_keep_params(t) for t in (zoo(), hallway(), fiber(), teleport_channel(), superdense())]
