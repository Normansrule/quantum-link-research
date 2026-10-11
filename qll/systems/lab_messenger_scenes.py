"""The messenger lab's builds (docs/lab/messenger/): the application on top of every link. Each tier reuses its link's
scene from the other labs, with the hardware already paid for there, and adds nothing but software; the twin
(qll/link/keyed_messaging.py) takes the link's daily key from that link's own twin.
"""
from __future__ import annotations

from dataclasses import replace

from qll.systems.lab_frontier_scenes import _earth_mars
from qll.systems.lab_outdoor_scenes import _roofs, _station
from qll.systems.lab_scenes import Beam, Part, Slider, Tier, two_room_parts

STAGES = (("The link", "Its own lab builds it; here it only makes key."), ("Key bank", "Accepted key is stored at both ends."),
          ("Messenger", "Each message spends key by its policy."), ("Fail closed", "An empty bank refuses; no weaker fallback."))
BOM = (("Messenger software and the key store (this repository)", "the application", 0, 0),)
COMMON = (Slider("messages_per_day", "Messages a day", 1, 1e6, 1, 500, "", True), Slider("msg_bytes", "Message size", 16, 1e7, 1, 200, "bytes", True),
          Slider("rekey_every", "Messages per session key (AES, hybrid)", 1, 1e4, 1, 100, "", True))


def _software_only(parts, beams) -> tuple[tuple[Part, ...], tuple[Beam, ...]]:
    n = len(STAGES)
    return (tuple(replace(p, bom=None, stage=min(p.stage, n), param="") for p in parts),
            tuple(replace(b, stage=min(b.stage, n)) for b in beams))


def _tier(id_, title, rung, experiments, milestones, summary, procedure, scene, sliders, rooms, claim) -> Tier:
    parts, beams = _software_only(*scene)
    return Tier(id_, title, rung, experiments, milestones, "messenger", "$0 above the link", summary, procedure, BOM, STAGES, parts, beams, sliders,
                {"simulate": "python -m qll.link.keyed_messaging --messages 500 --bytes 200", "real": "python -m qll.link.run demo"}, rooms=rooms, claim=claim)


def messenger_tiers() -> list[Tier]:
    P15 = "experiments/protocols/P15_messages_keyed_by_the_link.md"
    return [
        _tier("rooms", "Messages between the rooms (P10's key)", "main", ("P15", "P10"), ("M1.6",),
              "The two-room link runs around the clock and makes far more key than text needs: a one-time pad is affordable, and the bank never runs dry.",
              P15, two_room_parts(), COMMON, True, "Test messages only; keys at rest are ordinary memory, not a hardware security module."),
        _tier("buildings", "Messages between buildings (key made at night)", "upgrade", ("P15", "P04"), ("M3.3",),
              "Key arrives only at night and is spent by day, so the bank must carry a day's messages; daylight makes none.",
              P15, _roofs("Avalanche-diode receiver"), COMMON, False, "The bank bridges day and night; a cloudy night makes no key."),
        _tier("satellite", "Messages keyed by a satellite pass", "upgrade", ("P15", "D09"), ("M3.4",),
              "One pass a night delivers a burst of key; a one-time pad still covers a couple of thousand short messages a day, and AES millions.",
              P15, _station("Micius-class satellite (500 km)"), COMMON, False, "The pass key is an asymptotic upper estimate."),
        _tier("mars", "Messages to Mars (key carried on the lander)", "device", ("P15", "E01", "F3"), ("M4.3",),
              "No quantum link reaches Mars yet, so the first secure messenger carries its key: a terabyte of one-time pad loaded before launch outlasts the mission, and every message still takes the light time.",
              P15, _earth_mars(), COMMON + (Slider("preloaded_bits", "Key loaded before launch", 1e6, 8e13, 1, 8e12, "bits", True),
                                            Slider("distance_m", "Earth–Mars distance", 5.5e10, 4.1e11, 1, 4.0092e11, "m", True)),
              False, "Key carried, not distributed; a courier-keyed pad is as secure as the courier."),
    ]
