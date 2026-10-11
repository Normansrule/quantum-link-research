"""The frontier lab's builds (docs/lab/frontier/): Phase 4 of the mission, teleportation across a distance. Four
tiers climb from a free cloud-processor run, where the classical channel is a delay on Bob's qubit (E01, M4.3),
through a three-node network with a swapping node (M4.4) and photonic teleportation between the rooms (M4.5), to
the research version of E01, Earth to Mars with entanglement banked in memories. Distances are not to scale in 3D;
the twins (qll/circuits/teleport_delay_cloud.py, qll/network/teleport_across.py) and the terminal use true ones.
Bills of materials follow the mission's three-point costs for M4.4 and M4.5 (qll/systems/program_plan.py), which the
tests check.
"""
from __future__ import annotations

from qll.systems.lab_scenes import CLOUD_BOM, CLOUD_STAGES, TABLE_Y, Beam, Part, Slider, Tier, _cloud_beams, _cloud_parts, _rooms_and_tables, _t

DELAY_SLIDERS = (Slider("t_us", "Delay before the bits arrive", 0, 600, 1, 60, "µs"), Slider("T1_us", "Qubit relaxation time T₁", 20, 500, 5, 200, "µs"),
                 Slider("T2_us", "Qubit dephasing time T₂", 10, 400, 5, 150, "µs"), Slider("p2", "Two-qubit gate error p₂", 0, 0.1, 0.001, 0.01))
LINK_SLIDERS = (Slider("distance_m", "Distance", 1, 5e11, 1, 10, "m", True), Slider("f0", "Pair fidelity when made f₀", 0.55, 1.0, 0.005, 0.95),
                Slider("T_mem_s", "Memory lifetime", 1e-6, 1e5, 1e-6, 1.0, "s", True), Slider("bank_s", "Time in the bank before use", 0, 3600, 1, 0, "s"),
                Slider("eta_mem", "Memory retrieval efficiency", 0.001, 1.0, 0.001, 0.9), Slider("p_bsm", "Bell-measurement success", 0.25, 1.0, 0.25, 0.5))
SWAP_SLIDERS = (Slider("distance_m", "Distance A to B", 10, 5e5, 10, 20000, "m", True), Slider("f0", "Each segment's pair f₀", 0.55, 1.0, 0.005, 0.95),
                Slider("T_mem_s", "Memory lifetime", 1e-4, 1e3, 1e-4, 1.0, "s", True), Slider("alpha_db_per_km", "Fiber loss", 0.15, 0.5, 0.01, 0.2, "dB/km"),
                Slider("p_swap", "Bell-measurement success at the node", 0.25, 1.0, 0.25, 0.5))


def delay() -> Tier:
    P = [*_cloud_parts(), Part("note", "note", "the delay stands in for distance", (0.0, 2.9, 0.0), "", size=(0.16,))]
    return Tier("delay", "Teleport with the bits delayed, on a cloud processor (E01)", "cloud", ("E01", "P12"), ("M4.3",), "delay", "$0",
                "Teleportation on a free cloud processor with Bob's qubit made to wait before the two bits arrive, as it would while they cross a distance. "
                "The fidelity falls as the qubit relaxes and dephases, and crosses the classical 2/3 after about T₂; without the bits it is 1/2 at every delay.",
                "experiments/proposed/E01_delayed_classical_channel_teleportation.md", CLOUD_BOM, CLOUD_STAGES, tuple(P), _cloud_beams(), DELAY_SLIDERS,
                {"simulate": "python experiments/bench/frontier/run_frontier.py delay --backend aer",
                 "real": "python experiments/bench/frontier/run_frontier.py delay --backend ibm_torino"},
                rooms=False, claim="Fidelity against delay on a real qubit; the delay is time, not distance, so it tests the memory model, not a link.")


NX = (-6.0, 0.0, 6.0)                                   # benches A, C, B


def _three_nodes() -> tuple[list[Part], list[Beam]]:
    a, c, b = NX
    P = [Part("ground", "ground", "Three labs (not to scale)", (0.0, 0.0, 0.0), "", size=(30.0, 14.0)),
         Part("tableA", "table", "Node A (Alice)", (a, 0.0, 0.0), "", None, 1, size=(1.6, 0.8)),
         Part("tableC", "table", "Node C (the swapping node)", (c, 0.0, 0.0), "", 0, 1, size=(1.8, 0.9)),
         Part("tableB", "table", "Node B (Bob)", (b, 0.0, 0.0), "", None, 1, size=(1.6, 0.8)),
         Part("memA", "box", "Memory A", (a + 0.3, TABLE_Y + 0.1, 0.0), "Holds Alice's half of the A–C pair until the node announces the swap.", None, 1, param="T_mem_s", size=(0.4, 0.2, 0.3)),
         Part("memB", "box", "Memory B", (b - 0.3, TABLE_Y + 0.1, 0.0), "Holds Bob's half of the C–B pair.", None, 1, param="T_mem_s", size=(0.4, 0.2, 0.3)),
         Part("srcAC", "crystal", "Pair source for A–C", _t(c - 0.5, -0.2), "Sends one photon of each pair toward A and keeps the other at C.", None, 1, param="f0"),
         Part("srcCB", "crystal", "Pair source for C–B", _t(c + 0.5, -0.2), "The same toward B.", None, 1, param="f0"),
         Part("bsm", "bs", "Bell-state measurement at C", _t(c, 0.2), "Joins the two pairs into one between A and B; its two-bit result goes to both ends.", 2, 2, param="p_swap"),
         Part("detC0", "spad", "Node detector 1", _t(c + 0.3, 0.45), "", 2, 2, rot=90),
         Part("detC1", "spad", "Node detector 2", _t(c - 0.3, 0.45), "", 2, 2, rot=90),
         Part("spoolAC", "spool", "Fiber, A to C", (a / 2, 0.25, 1.0), "Each segment is half the distance; its loss sets how often a pair arrives.", 1, 1, param="alpha_db_per_km"),
         Part("spoolCB", "spool", "Fiber, C to B", (b / 2, 0.25, 1.0), "", 1, 1, param="alpha_db_per_km"),
         Part("laptopA", "laptop", "Laptop A", (a - 0.4, TABLE_Y + 0.08, 0.2), "Runs Alice's side.", None, 3),
         Part("laptopB", "laptop", "Laptop B", (b + 0.4, TABLE_Y + 0.08, 0.2), "Runs Bob's side.", None, 3),
         Part("tagC", "timetagger", "Time tagger at the node", _t(c, -0.35), "Heralds which attempts succeeded on each segment.", 2, 2),
         Part("note", "note", "the node learns nothing about the key", (0.0, 3.3, -0.8), "", size=(0.24,))]
    y = TABLE_Y + 0.14
    beams = [Beam("pair", ((c - 0.5, y, -0.2), (a / 2, 0.3, 1.0), (a + 0.3, y, 0.0)), "photon to A", 1, main=True),
             Beam("pair", ((c + 0.5, y, -0.2), (b / 2, 0.3, 1.0), (b - 0.3, y, 0.0)), "photon to B", 1),
             Beam("pair", ((c - 0.5, y, -0.2), (c, y, 0.2)), "", 2), Beam("pair", ((c + 0.5, y, -0.2), (c, y, 0.2)), "", 2),
             Beam("classical", ((c, TABLE_Y + 0.05, 0.2), (c, 2.6, 0.2), (a, 2.6, 0.2), (a - 0.4, TABLE_Y + 0.1, 0.2)), "swap result to A", 2),
             Beam("classical", ((c, 2.6, 0.2), (b, 2.6, 0.2), (b + 0.4, TABLE_Y + 0.1, 0.2)), "swap result to B", 2),
             Beam("classical", ((a - 0.4, TABLE_Y + 0.1, 0.2), (a - 0.4, 3.0, -0.6), (b + 0.4, 3.0, -0.6), (b + 0.4, TABLE_Y + 0.1, 0.2)), "teleportation bits, A to B", 3)]
    return P, beams


def network() -> Tier:
    P, beams = _three_nodes()
    return Tier("network", "Three nodes: a swapping node between two labs (M4.4)", "main", ("D08", "D13"), ("M4.4",), "swap", "$0 in the twin; up to $2,000 with a third room",
                "Two pairs, A–C and C–B, become one A–B pair when the node in the middle makes a Bell measurement and tells both ends the result. The node "
                "learns nothing about a key made from the pair, unlike a trusted relay, and with memories the two halves wait for each other, which beats "
                "sending one photon all the way once the distance is long enough.",
                "experiments/done/08_nv_remote_entanglement_and_network.md",
                (("Third room's bench and fiber patch cords", "node C", 0, 300), ("Two fiber spools for the segments", "segments", 0, 700),
                 ("Bell-state analyzer and tagger channels at the node (borrowed with the Phase 2 source)", "the swap", 0, 1000)),
                (("Two pairs", "A source per segment, memories at the ends."), ("The swap", "Bell measurement and its announcement."), ("Teleport", "Alice to Bob over the new pair.")),
                tuple(P), tuple(beams), SWAP_SLIDERS,
                {"simulate": "python -c \"from qll.network import teleport_across as X; print(X.swap(X.Swap(distance_m=20000)))\""},
                rooms=False, claim="Keys between every pair in the twin; with hardware, the swap is the borrowed Phase 2 source twice over.")


def _photonic_rooms() -> tuple[list[Part], list[Beam]]:
    y = 0.14
    P = [*_rooms_and_tables("Room A (Alice)", "Room B (Bob)"),
         Part("input", "laser", "Input photon (heralded single photon)", _t(-5.7, 0.25), "The qubit Alice teleports: a heralded photon in the polarization she chooses.", 0, 1),
         Part("pump", "pump", "Pair source pump (405 nm)", _t(-5.7, -0.3), "Pumps the down-conversion crystals that make the shared pair (the Phase 2 source).", None, 1),
         Part("bbo", "crystal", "Entangled-pair crystals", _t(-5.3, -0.3), "One photon of the pair goes to Alice's Bell measurement, the other to room B.", None, 1, param="f0"),
         Part("bs", "bs", "Bell-state analyzer: beam splitter", _t(-4.8, 0.0), "Two-photon interference picks out Bell states; linear optics succeeds half the time.", 1, 2, param="p_bsm"),
         Part("bsmD0", "spad", "Analyzer detector 1", _t(-4.4, 0.0), "", 1, 2),
         Part("bsmD1", "spad", "Analyzer detector 2", _t(-4.8, 0.35), "", 1, 2, rot=90),
         Part("delay", "spool", "Fiber delay line (Bob's memory)", (0.0, 0.25, 1.2), "Holds Bob's photon until Alice's result arrives: 5 µs per kilometre of fiber.", 3, 2, param="T_mem_s"),
         Part("pockels", "box", "Pockels cell (fast correction)", _t(4.2, 0.0), "Applies Bob's correction in nanoseconds, driven by Alice's two bits.", 2, 3, size=(0.25, 0.12, 0.12)),
         Part("anaB_hwp", "hwp", "Bob's analyzer: waveplate", _t(4.55, 0.0), "Checks the teleported polarization.", None, 3),
         Part("anaB_pbs", "pbs", "Bob's analyzer: PBS", _t(4.8, 0.0), "", None, 3, rot=45),
         Part("detB0", "spad", "Bob's detector 1", _t(5.1, 0.0), "", None, 3),
         Part("detB1", "spad", "Bob's detector 2", _t(4.8, 0.3), "", None, 3, rot=90),
         Part("ffA", "mediaconv", "Feed-forward link A", _t(-4.3, 0.4), "Carries Alice's two bits to room B: a cable or fiber, at most light speed.", 3, 3),
         Part("ffB", "mediaconv", "Feed-forward link B", _t(4.2, 0.45), "Drives the Pockels cell.", 3, 3)]
    beams = (Beam("pump", (_t(-5.7, -0.3, y), _t(-5.3, -0.3, y)), "pump", 1),
             Beam("pair", (_t(-5.3, -0.3, y), _t(-4.8, 0.0, y)), "pair photon to Alice", 1),
             Beam("red", (_t(-5.7, 0.25, y), _t(-4.8, 0.0, y), _t(-4.4, 0.0, y)), "input photon", 1),
             Beam("pair", (_t(-4.8, 0.0, y), _t(-4.8, 0.35, y)), "", 2),
             Beam("pair", (_t(-5.3, -0.3, y), (-4.6, 0.3, 1.2), (0.0, 0.3, 1.2), (3.6, 0.3, 1.2), _t(4.2, 0.0, y), _t(4.55, 0.0, y), _t(4.8, 0.0, y), _t(5.1, 0.0, y)), "Bob's photon through the delay line", 2, main=True),
             Beam("pair", (_t(4.8, 0.0, y), _t(4.8, 0.3, y)), "", 3),
             Beam("classical", ((-4.3, TABLE_Y + 0.03, 0.4), (-4.3, 2.4, 0.4), (4.2, 2.4, 0.45), (4.2, TABLE_Y + 0.03, 0.45)), "Alice's two bits", 3))
    return P, list(beams)


def rooms() -> Tier:
    P, beams = _photonic_rooms()
    return Tier("rooms", "Photonic teleportation between the rooms (M4.5)", "upgrade", ("D06", "D07"), ("M4.5",), "link", "$2,000–30,000 (outside funding)",
                "The 1997 experiment across the hallway: an input photon and one photon of a pair meet at a beam splitter in room A, and the two-bit "
                "result races Bob's photon, held in a fiber delay line, to a fast Pockels cell in room B. The fiber is the memory; the distance is the "
                "rooms; the twin says how long a delay line keeps the fidelity above 2/3.",
                "experiments/done/07_teleportation_photonic.md",
                (("Heralded single-photon source for the input (or a second pair source)", "the input qubit", 1000, 10000),
                 ("Bell-state analyzer: beam splitter, two detectors, coincidence logic", "Alice's measurement", 500, 8000),
                 ("Pockels cell and fast driver", "Bob's correction", 300, 8000), ("Fiber delay line and feed-forward cable", "Bob's memory", 200, 4000)),
                (("Sources", "Input photon and the shared pair."), ("Alice's measurement", "Beam splitter and two detectors."), ("Bob's correction", "Feed-forward and Pockels cell."),
                 ("Memory", "A longer delay line, then a real memory.")),
                tuple(P), tuple(beams), LINK_SLIDERS,
                {"simulate": "python -c \"from qll.network import teleport_across as X; print(X.link(X.Link(distance_m=10, T_mem_s=1e-3, eta_mem=0.9)))\""},
                claim="Fidelity above 2/3 with the Bell measurement and the bits; one Bell state in two, as linear optics allows.")


def _earth_mars() -> tuple[list[Part], list[Beam]]:
    P = [Part("earth", "planet", "Earth", (-9.0, 3.0, 0.0), "Ground station with a memory that holds Alice's half of each pair.", None, 1, size=(2.4, 0x2f6fd6)),
         Part("mars", "planet", "Mars", (9.0, 3.0, 0.0), "A lander or orbiter with a memory holding Bob's half.", None, 1, size=(1.3, 0xc1440e)),
         Part("relay", "satellite", "Pair source in deep space", (0.0, 7.5, -2.0), "Sends one photon of each pair to each planet ahead of time; pairs are banked, not made on demand.", None, 1),
         Part("memE", "box", "Earth memory (rare-earth or ion)", (-6.3, 3.0, 0.0), "Holds Alice's halves; a 171Yb+ ion holds for an hour, a Eu:YSO crystal for hours.", 0, 2, param="T_mem_s", size=(0.6, 0.4, 0.5)),
         Part("memM", "box", "Mars memory", (7.4, 3.0, 0.0), "Holds Bob's halves until Alice's bits arrive, 3 to 22 minutes later.", 0, 2, param="T_mem_s", size=(0.6, 0.4, 0.5)),
         Part("note", "note", "nothing outruns the light-time: the two bits set the pace", (0.0, 10.5, -2.0), "", size=())]
    beams = [Beam("pair", ((0.0, 7.2, -2.0), (-6.3, 3.3, 0.0)), "pair photon to Earth", 1),
             Beam("pair", ((0.0, 7.2, -2.0), (7.4, 3.3, 0.0)), "pair photon to Mars", 1),
             Beam("classical", ((-6.3, 3.0, 0.0), (-3.0, 1.2, 1.5), (3.0, 1.2, 1.5), (7.4, 3.0, 0.0)), "Alice's two bits, at light speed", 3, main=True)]
    return P, beams


def mars() -> Tier:
    P, beams = _earth_mars()
    return Tier("mars", "Earth to Mars with banked entanglement (E01, research version)", "device", ("E01", "E02", "F3"), ("M4.3",), "link", "research; outside funding",
                "Pairs are sent ahead and banked in memories on both planets, so the message moment needs only Alice's Bell measurement and two bits that take "
                "3 to 22 minutes to arrive. Teleportation is then never faster than light, but it needs no photon to survive the trip at the moment of sending, "
                "and only memories that outlive the light-time keep the fidelity above 2/3.",
                "experiments/proposed/E01_delayed_classical_channel_teleportation.md",
                (("Partner memory laboratories and a deep-space optical link", "the research version", 0, 0),),
                (("Banked pairs", "A source sends ahead; memories hold."), ("Memories", "Ion or rare-earth storage at both ends."), ("Teleport", "Alice measures; two bits cross at light speed.")),
                tuple(P), tuple(beams), LINK_SLIDERS,
                {"simulate": "python -c \"from qll.network import teleport_across as X; print(X.for_scenario('Mars at its farthest', '171Yb+ hyperfine'))\""},
                rooms=False, claim="A design study: every number is the light-time and the memory model, and no claim outruns them.")


def frontier_tiers() -> list[Tier]:
    return [delay(), network(), rooms(), mars()]
