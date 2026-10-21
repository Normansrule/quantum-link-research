"""Animated SVG banner for the README (SMIL animations play in GitHub's image renderer), drawn in the site's Light cone
style: a small spacetime diagram with time running down and light at 45 degrees, on the dark "instrument screen"
ground so it reads the same on GitHub's light and dark themes. Numbers are read from docs/site_data.json so the banner
cannot disagree with the code. Without SMIL the finished diagram is shown."""
from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FONT = "Geist,Inter,Segoe UI,Helvetica,Arial,sans-serif"
MONO = "Geist Mono,Menlo,Consolas,monospace"
BG, INK, MUTED, FAINT, LINE, CONE = "#111317", "#e9ebef", "#a4aab5", "#8a919d", "#2a2e36", "#8593ff"


def main() -> None:
    d = json.loads((ROOT / "docs" / "site_data.json").read_text(encoding="utf-8"))["headline"]
    W, H = 1280, 420
    xE, top, D, trips = 900, 92, 88, 3               # Earth's worldline, the emission event, one light time in px
    xM = xE + D
    pts = [(xE, top)] + [((xM if k % 2 else xE), top + k * D) for k in range(1, trips + 1)]
    path = "M" + " L".join(f"{x},{y}" for x, y in pts)
    length = math.sqrt(2) * D * trips
    t = 7.0                                          # seconds per pass; light moves linearly, then the picture holds
    events = [(1, "Banked key", "readable after one trip"), (3, "Key made on demand", "needs a round trip first")]
    ev = "".join(
        f'<circle cx="{xM}" cy="{top + n * D}" r="5.5" fill="{CONE}"/>'
        f'<text x="{xM + 18}" y="{top + n * D - 2}" font-family="{FONT}" font-size="16" font-weight="600" fill="{INK}">{title}</text>'
        f'<text x="{xM + 18}" y="{top + n * D + 18}" font-family="{FONT}" font-size="13.5" fill="{CONE}">{n} trip{"s" if n > 1 else ""} · '
        f'{n * d["one_way_min_min"]:.1f}–{n * d["one_way_max_min"]:.1f} min</text>'
        f'<text x="{xM + 18}" y="{top + n * D + 36}" font-family="{FONT}" font-size="13.5" fill="{FAINT}">{sub}</text>'
        for n, title, sub in events)
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Quantum Link Research: talk to anywhere, as fast as light allows. A spacetime diagram of a message from Earth to Mars, with light at 45 degrees reaching Mars after one trip for a banked key and three trips for a key made on demand">
<rect width="{W}" height="{H}" rx="18" fill="{BG}"/>
<g font-family="{FONT}">
  <path d="M64 68 l14 -22 l14 22" fill="none" stroke="{CONE}" stroke-width="3" stroke-linejoin="round"/>
  <text x="104" y="68" font-size="22" font-weight="600" fill="{INK}">Quantum Link Research</text>
  <text x="64" y="168" font-size="52" font-weight="650" letter-spacing="-1.5" fill="{INK}">Talk to anywhere,</text>
  <text x="64" y="228" font-size="52" font-weight="650" letter-spacing="-1.5" fill="{MUTED}">as fast as light allows.</text>
  <text x="64" y="284" font-size="18" fill="{MUTED}">Tested physics, interactive labs, and a staged two-room experiment toward</text>
  <text x="64" y="310" font-size="18" fill="{MUTED}">secure communication at the light-time floor, wherever the two ends are.</text>
</g>
<text x="64" y="{H - 34}" font-family="{MONO}" font-size="13" fill="{FAINT}">τ = d/c  ·  F = (2f+1)/3  ·  K ≤ −log₂(1−η)  ·  {d["mars_capable_memories"]} of {d["n_memories"]} memories outlast the {d["round_trip_max_min"]:.1f}-min Mars round trip</text>
<g font-family="{FONT}">
  <text x="{xE}" y="{top - 30}" text-anchor="middle" font-size="15" font-weight="600" fill="{INK}">Earth</text>
  <text x="{xM}" y="{top - 30}" text-anchor="middle" font-size="15" font-weight="600" fill="{INK}">Mars</text>
  <text x="{xE - 14}" y="{top + 4}" text-anchor="end" font-family="{MONO}" font-size="12" fill="{FAINT}">time ↓</text>
</g>
<line x1="{xE}" y1="{top - 14}" x2="{xE}" y2="{top + trips * D + 14}" stroke="{LINE}" stroke-width="1.5"/>
<line x1="{xM}" y1="{top - 14}" x2="{xM}" y2="{top + trips * D + 14}" stroke="{LINE}" stroke-width="1.5"/>
<polygon points="{xE},{top} {xM},{top + D} {xE},{top + D}" fill="{CONE}" fill-opacity=".10"/>
<path d="{path}" fill="none" stroke="{CONE}" stroke-opacity=".25" stroke-width="1.5" stroke-dasharray="4 5"/>
<path d="{path}" fill="none" stroke="{CONE}" stroke-width="2.2" stroke-dasharray="{length:.1f} {length:.1f}" stroke-dashoffset="0">
  <animate attributeName="stroke-dashoffset" values="{length:.1f};0;0" keyTimes="0;.72;1" dur="{t}s" calcMode="linear" repeatCount="indefinite"/>
</path>
<circle cx="{xE}" cy="{top}" r="5.5" fill="{CONE}"/>
{ev}
</svg>'''
    (ROOT / "docs" / "figures" / "hero_banner.svg").write_text(svg, encoding="utf-8")
    print("wrote docs/figures/hero_banner.svg")


if __name__ == "__main__":
    main()
