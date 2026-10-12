"""The outdoor lab's builds (docs/lab/outdoor/): Phase 3 of the mission, from a roof-to-roof link with the Phase 1
hardware to a ground station tracking a satellite. Distances are not to scale in 3D (two buildings 300 m apart, or a
satellite 500 km up, would not fit on a screen); the twin and the terminal use the true distances. Bills of materials
follow the mission's three-point costs for M3.2 to M3.5 (qll/systems/program_plan.py), which the tests check.
"""
from __future__ import annotations

from dataclasses import replace

from qll.systems.lab_scenes import Beam, Part, Slider, Tier

ROOF = 6.0                                    # roof height in the scene (metres)
XA, XB = -9.0, 9.0                            # the two roofs, drawn 18 m apart whatever the true distance


def _roofs(receiver_label: str) -> tuple[list[Part], list[Beam]]:
    P = [Part("ground", "ground", "Campus", (0.0, 0.0, 0.0), "", size=(60.0, 30.0)),
         Part("bldgA", "building", "Building A (sender)", (XA, 0.0, 0.0), "Any roof with a clear line of sight; ask facilities first (risk MR-R8).", size=(8.0, ROOF, 8.0)),
         Part("bldgB", "building", "Building B (receiver)", (XB, 0.0, 0.0), "The receiving roof.", size=(8.0, ROOF, 8.0)),
         Part("tableA", "table", "Roof bench A", (XA + 1.5, ROOF, 0.0), "", None, 1, size=(1.6, 0.8)),
         Part("tableB", "table", "Roof bench B", (XB - 1.5, ROOF, 0.0), "", None, 1, size=(1.6, 0.8)),
         Part("srcBox", "box", "The P10 source, boxed", (XA + 1.2, ROOF + 0.9, 0.0), "The four-diode source, combiners, filters, and FPGA from P10, in a weatherproof box.", None, 1, size=(0.6, 0.3, 0.4)),
         Part("txScope", "telescope", "Sending telescope (beam expander)", (XA + 2.6, ROOF, 0.0), "Widens the beam to a waist of about 1 cm so it spreads less over the path.", 0, 1, rot=0, param="tx_waist_m", size=(0.06, 0.35)),
         Part("rxScope", "telescope", "Receiving telescope, filter, field stop", (XB - 2.6, ROOF, 0.0), "Collects the beam; a 3 nm filter and a field stop keep out most of the sky.", 1, 1, rot=180, param="rx_aperture_m", size=(0.1, 0.5)),
         Part("rxBox", "box", receiver_label, (XB - 1.2, ROOF + 0.9, 0.0), "The P10 analyzer and detectors in a light-tight box behind the telescope.", 1, 1, size=(0.6, 0.3, 0.4)),
         Part("laptopA", "laptop", "Laptop A", (XA + 1.0, ROOF + 0.88, 0.25), "Site A's half of the protocol.", None, 1),
         Part("laptopB", "laptop", "Laptop B", (XB - 1.0, ROOF + 0.88, 0.25), "Site B's half.", None, 1),
         Part("gpsA", "coaxend", "GPS-disciplined clock A", (XA + 1.6, ROOF + 0.82, -0.3), "One pulse per second from GPS keeps the two roofs' clocks within nanoseconds.", 4, 2),
         Part("gpsB", "coaxend", "GPS-disciplined clock B", (XB - 1.6, ROOF + 0.82, -0.3), "", 4, 2),
         Part("note", "note", "distance not to scale: see the terminal", (0.0, ROOF + 4.0, 0.0), "", size=())]
    beams = [Beam("violet", ((XA + 2.9, ROOF + 0.9, 0.0), (XB - 2.9, ROOF + 0.9, 0.0)), "weak pulses across the roofs", 1, main=True),
             Beam("classical", ((XA + 1.0, ROOF + 0.85, 0.25), (XA + 1.0, ROOF + 3.2, -2.5), (XB - 1.0, ROOF + 3.2, -2.5), (XB - 1.0, ROOF + 0.85, 0.25)), "classical channel (fiber or radio)", 2)]
    return P, beams


OUT_SLIDERS = (Slider("distance_m", "Distance between roofs", 20, 5000, 10, 300, "m", True), Slider("tx_waist_m", "Sending beam waist", 0.002, 0.05, 0.001, 0.01, "m"),
               Slider("rx_aperture_m", "Receiving telescope diameter", 0.02, 0.3, 0.005, 0.05, "m"), Slider("pointing_urad", "Pointing jitter", 0, 100, 1, 10, "µrad"),
               Slider("air_db_per_km", "Air extinction at 405 nm", 0.2, 5, 0.1, 1.0, "dB/km"), Slider("coupling_loss_db", "Receiver coupling loss", 0, 8, 0.1, 3.0, "dB"),
               Slider("sky_radiance", "Sky brightness (W m⁻² sr⁻¹ nm⁻¹)", 1e-9, 0.2, 1e-9, 1e-6, "", True), Slider("filter_nm", "Filter width", 0.5, 10, 0.5, 3.0, "nm"),
               Slider("fov_mrad", "Field of view", 0.1, 5, 0.1, 1.0, "mrad"))
OUT_STAGES = (("Roofs and line of sight", "Permission, a clear path, benches, telescopes."), ("Classical channel and clocks", "Fiber or radio between buildings; GPS time."))


def rooftop() -> Tier:
    P, beams = _roofs("P10 receiver (silicon photomultipliers)")
    return Tier("rooftop", "Rooftop link with the Phase 1 hardware (P04)", "starter", ("P04", "P10"), ("M3.2",), "outdoor", "$100–800",
                "The P10 source and receiver carried onto two roofs with small telescopes. The twin says what to expect before you climb the stairs: "
                "loss you can measure, a background that is fine at night and overwhelming by day, and dark counts that keep the SiPMs from making a key outdoors.",
                "experiments/protocols/P04_rooftop_free_space_link.md",
                (("Two 50 mm lenses or 2x beam expanders", "the sending and receiving optics", 40, 150), ("Receiving telescope (50-100 mm), 3 nm filter at 405 nm, field stop", "collecting and filtering", 60, 400),
                 ("Two tripods with fine-adjust heads", "pointing", 0, 150), ("Sunshade baffle and a weatherproof receiver box", "daylight tests", 0, 50),
                 ("GPS-disciplined 1 PPS clock pair, or a cable across the roof", "timing", 0, 50)),
                OUT_STAGES, tuple(P), tuple(beams), OUT_SLIDERS,
                {"simulate": "python -c \"from qll.link import outdoor_link as O; print(O.predict(O.OutdoorParts(distance_m=300)))\"",
                 "real": "python -m qll.link.run ingest roof_a.csv --bob roof_b.csv --config roof_measured.json"},
                rooms=False, claim="Measures loss and background against the twin; a key needs better detectors (next tier).")


def building() -> Tier:
    P, beams = _roofs("Avalanche-diode receiver (four used modules)")
    remap = {"txScope": 1, "rxScope": 1, "rxBox": 0}
    P = [replace(q, bom=remap.get(q.id)) for q in P]
    return Tier("building", "Building to building at night (0.5–2 km)", "main", ("P04", "T3"), ("M3.3",), "outdoor", "$300–2,000",
                "The same link between two buildings up to two kilometres apart, with used single-photon avalanche diode modules instead of SiPMs and a 100 mm "
                "telescope. At night the twin accepts a key out to about two kilometres; by day the sky ends it, which is why daylight links use 1550 nm and very "
                "narrow filters.",
                "experiments/protocols/P04_rooftop_free_space_link.md",
                (("Used single-photon avalanche diode modules, four (or borrowed)", "detection", 200, 1200), ("100 mm telescope and a sturdier mount", "collecting and pointing", 80, 500),
                 ("Fiber or radio link for the classical channel between buildings", "classical channel", 20, 300)),
                OUT_STAGES, tuple(P), tuple(beams), OUT_SLIDERS,
                {"simulate": "python -c \"from qll.link import outdoor_link as O; print(O.predict(O.OutdoorParts(distance_m=1000, receiver=O.RECEIVERS['spad'])))\"",
                 "real": "python -m qll.link.run ingest bldg_a.csv --bob bldg_b.csv --config bldg_measured.json"},
                rooms=False, claim="The model accepts a key outdoors at night (a model output, not a measured or security-reviewed key); turbulence fades the signal around the mean it predicts.")


PASS_SLIDERS = (Slider("t", "Time from overhead", -200, 200, 1, -60, "s"), Slider("min_elevation_deg", "Lowest usable elevation", 5, 40, 1, 15, "°"),
                Slider("y0", "Background clicks per pulse", 1e-8, 1e-2, 1e-8, 1e-6, "", True), Slider("mu", "Signal mean photon number", 0.1, 1.0, 0.01, 0.5),
                Slider("e_det", "Downlink misalignment", 0, 0.05, 0.001, 0.01))


def _station(sat_label: str) -> tuple[list[Part], list[Beam]]:
    P = [Part("ground", "ground", "Ground station site", (0.0, 0.0, 0.0), "", size=(60.0, 40.0)),
         Part("dome", "dome", "Optical ground station", (0.0, 0.0, 0.0), "A roll-off roof or dome around a tracking telescope.", None, 1, size=(2.6,)),
         Part("scope", "telescope", "Tracking telescope (goto mount)", (0.0, 1.4, 0.0), "Follows the satellite across the sky to within its field of view; a fast mirror would hold it to microradians.", 0, 1, rot=0, size=(0.3, 1.4)),
         Part("desk", "table", "Control desk", (4.5, 0.0, 2.5), "", None, 2, size=(1.4, 0.7)),
         Part("tagger", "timetagger", "GPS clock and time tagger", (4.2, 0.88, 2.5), "Timestamps every detection against GPS time, within 10 ns of a second clock (MR-3.4).", 1, 2),
         Part("dets", "spad", "Detectors and filters (810/850 nm)", (4.9, 0.94, 2.4), "Single-photon detectors behind a narrow filter, fed from the telescope by fiber.", 2, 2),
         Part("laptop", "laptop", "Station laptop", (4.6, 0.88, 2.75), "Schedules passes from public orbit data (M3.1) and runs the protocol.", None, 2),
         Part("sat", "satellite", sat_label, (-12.0, 12.0, -3.0), "The source in orbit, sending weak pulses or entangled photons down.", None, 3),
         Part("note", "note", "orbit not to scale: see the terminal", (0.0, 16.0, -3.0), "", size=())]
    return P, [Beam("usb", ((4.9, 0.95, 2.4), (2.0, 0.5, 1.6), (0.0, 2.3, 0.0)), "fiber from the telescope", 2)]


def ground_station() -> Tier:
    P, beams = _station("Micius-class satellite (500 km)")
    return Tier("station", "Ground station and a satellite pass (Micius class)", "upgrade", ("D09", "E03", "E14"), ("M3.4", "M3.1"), "pass", "$1,000–8,000",
                "A tracking telescope with GPS timing follows a satellite for the six minutes it is above 15 degrees. The twin traces elevation, range, and loss "
                "second by second with the link budget that reproduces Micius's published losses, and adds up the key one pass could give.",
                "systems/program/01_phases_and_milestones.md",
                (("Used tracking mount and a 200-300 mm telescope", "tracking", 600, 4000), ("GPS-disciplined clock and time tagger", "timing", 300, 2500),
                 ("Single-photon detectors and filters at 810/850 nm", "detection", 100, 1500)),
                (("Station", "Dome or roll-off roof, telescope, mount."), ("Timing and detectors", "GPS clock, tagger, filtered detectors."), ("The pass", "A partner's satellite overhead.")),
                tuple(P), tuple(beams), PASS_SLIDERS,
                {"simulate": "python -c \"from qll.link import satellite_pass as S; s = S.pass_summary(S.PRESETS['micius']); print(s['duration_s'], s['min_loss_db'], s['max_loss_db'], s['key_bits'])\""},
                rooms=False, claim="Losses follow the validated link budget; the key is an asymptotic upper estimate for one pass.")


def microsatellite() -> Tier:
    P, beams = _station("Microsatellite (Jinan-1 class, 23 kg)")
    P = [replace(q, bom=0 if q.id == "sat" else None) for q in P]
    return Tier("microsat", "A microsatellite partner (Jinan-1 class)", "device", ("D14", "D09"), ("M3.5", "M3.6"), "pass", "partner time; a CubeSat only with outside funding",
                "Jinan-1 showed a 23 kg satellite and a portable 28 cm receiver can make keys. With a partner's pass (M3.5) the same station works; flying a source "
                "(M3.6) waits for outside funding.",
                "systems/program/07_startup_path.md", (("Proposal and partner coordination", "M3.5", 0, 1000),),
                (("Station", "As before."), ("Timing and detectors", "As before."), ("The pass", "A partner's microsatellite.")),
                tuple(P), tuple(beams), PASS_SLIDERS,
                {"simulate": "python -c \"from qll.link import satellite_pass as S; print(S.pass_summary(S.PRESETS['jinan1'])['key_bits'])\""},
                rooms=False, claim="A partner pass first; nothing is flown out of pocket.")


def outdoor_tiers() -> list[Tier]:
    return [rooftop(), building(), ground_station(), microsatellite()]
