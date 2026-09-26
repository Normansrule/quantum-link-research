"""Animated SVG banner for the README (SMIL animations play in GitHub's image renderer).
Numbers are read from docs/site_data.json so the banner cannot disagree with the code."""
from __future__ import annotations

import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    d = json.loads((ROOT / "docs" / "site_data.json").read_text())["headline"]
    rnd = random.Random(7)
    W, H = 1280, 420
    stars = "".join(
        f'<circle cx="{rnd.uniform(0, W):.0f}" cy="{rnd.uniform(0, H):.0f}" r="{rnd.choice([0.6, 0.8, 1.1, 1.4])}" fill="#dfe8ff" opacity="{rnd.uniform(0.2, 0.9):.2f}">'
        + (f'<animate attributeName="opacity" values="0.2;0.9;0.2" dur="{rnd.uniform(2, 6):.1f}s" repeatCount="indefinite"/>' if rnd.random() < 0.3 else "")
        + "</circle>"
        for _ in range(180)
    )
    ex, ey, mx, my, rx, ry = 190, 300, 1090, 300, 640, 178
    arcA = f"M{rx},{ry} Q{(rx + ex) / 2 - 40},{ry - 10} {ex},{ey}"
    arcB = f"M{rx},{ry} Q{(rx + mx) / 2 + 40},{ry - 10} {mx},{my}"
    photons = "".join(
        f'<circle r="3.2" fill="#5ef2e0" filter="url(#glow)"><animateMotion dur="3.2s" begin="{k * 0.4:.1f}s" repeatCount="indefinite" path="{p}"/></circle>'
        for k in range(8) for p in (arcA, arcB)
    )
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Quantum Link Research: entangled photons from a relay to Earth and Mars, classical bits at the speed of light">
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#060a16"/><stop offset="1" stop-color="#0b1224"/></linearGradient>
  <radialGradient id="aur1" cx="0.2" cy="0.1" r="0.6"><stop offset="0" stop-color="#5ea8ff" stop-opacity=".35"/><stop offset="1" stop-color="#5ea8ff" stop-opacity="0"/></radialGradient>
  <radialGradient id="aur2" cx="0.85" cy="0.2" r="0.5"><stop offset="0" stop-color="#a78bfa" stop-opacity=".28"/><stop offset="1" stop-color="#a78bfa" stop-opacity="0"/></radialGradient>
  <radialGradient id="earth" cx=".35" cy=".35" r=".7"><stop offset="0" stop-color="#9cc7ff"/><stop offset="1" stop-color="#1b4fb0"/></radialGradient>
  <radialGradient id="mars" cx=".35" cy=".35" r=".7"><stop offset="0" stop-color="#ffb08a"/><stop offset="1" stop-color="#b8402a"/></radialGradient>
  <linearGradient id="title" x1="0" x2="1"><stop offset="0" stop-color="#5ea8ff"/><stop offset=".4" stop-color="#5ef2e0"/><stop offset=".75" stop-color="#a78bfa"/><stop offset="1" stop-color="#ff8a4c"/>
    <animate attributeName="x1" values="0;-1;0" dur="10s" repeatCount="indefinite"/><animate attributeName="x2" values="1;0;1" dur="10s" repeatCount="indefinite"/></linearGradient>
  <filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
</defs>
<rect width="{W}" height="{H}" fill="url(#bg)"/><rect width="{W}" height="{H}" fill="url(#aur1)"/><rect width="{W}" height="{H}" fill="url(#aur2)"/>
{stars}
<path d="{arcA}" fill="none" stroke="#45e0a0" stroke-opacity=".35" stroke-dasharray="4 6"/>
<path d="{arcB}" fill="none" stroke="#45e0a0" stroke-opacity=".35" stroke-dasharray="4 6"/>
<line x1="{ex}" y1="{ey}" x2="{mx}" y2="{my}" stroke="#ff8a4c" stroke-opacity=".55" stroke-width="2" stroke-dasharray="8 7"><animate attributeName="stroke-dashoffset" from="0" to="-60" dur="2s" repeatCount="indefinite"/></line>
{photons}
<circle r="7" fill="#ffb070" filter="url(#glow)"><animateMotion dur="7s" repeatCount="indefinite" path="M{ex},{ey} L{mx},{my}"/></circle>
<circle cx="{ex}" cy="{ey}" r="46" fill="url(#earth)" filter="url(#glow)"/>
<circle cx="{mx}" cy="{my}" r="34" fill="url(#mars)" filter="url(#glow)"/>
<rect x="{rx - 14}" y="{ry - 14}" width="28" height="28" rx="7" fill="#45e0a0" filter="url(#glow)"><animateTransform attributeName="transform" type="rotate" from="0 {rx} {ry}" to="360 {rx} {ry}" dur="24s" repeatCount="indefinite"/></rect>
<text x="{ex}" y="{ey + 74}" text-anchor="middle" font-family="Inter,Segoe UI,Helvetica,Arial,sans-serif" font-size="16" fill="#93a1b8">Earth</text>
<text x="{mx}" y="{my + 62}" text-anchor="middle" font-family="Inter,Segoe UI,Helvetica,Arial,sans-serif" font-size="16" fill="#93a1b8">Mars</text>
<text x="{rx}" y="{ry - 26}" text-anchor="middle" font-family="Inter,Segoe UI,Helvetica,Arial,sans-serif" font-size="14" fill="#45e0a0">relay: entangled-pair source + memory</text>
<text x="{W / 2}" y="{ey + 44}" text-anchor="middle" font-family="JetBrains Mono,Menlo,monospace" font-size="15" fill="#ff8a4c">two classical bits · {d["one_way_min_min"]:.1f}–{d["one_way_max_min"]:.1f} min one way</text>
<text x="{W / 2}" y="70" text-anchor="middle" font-family="Inter,Segoe UI,Helvetica,Arial,sans-serif" font-weight="800" font-size="52" fill="url(#title)">Quantum Link Research</text>
<text x="{W / 2}" y="104" text-anchor="middle" font-family="Inter,Segoe UI,Helvetica,Arial,sans-serif" font-size="19" fill="#c9d4e6">from a diamond on a bench to a message to Mars — tested physics, simulations, and experiments</text>
<text x="{W / 2}" y="{H - 24}" text-anchor="middle" font-family="JetBrains Mono,Menlo,monospace" font-size="14" fill="#5b6780">F = (2f+1)/3  ·  f(t) = 1/4 + (f0 − 1/4)e^(−t/T)  ·  K ≤ −log2(1−η)  ·  τ = d/c  ·  {d["mars_capable_memories"]} of {d["n_memories"]} memories survive the {d["round_trip_max_min"]:.1f}-min round trip</text>
</svg>'''
    (ROOT / "docs" / "figures" / "hero_banner.svg").write_text(svg)
    print("wrote docs/figures/hero_banner.svg")


if __name__ == "__main__":
    main()
