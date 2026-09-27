"""Animated SVG artwork for the README, generated from docs/site_data.json and docs/status.json so every number in
the pictures is the tested code's output. GitHub renders SVG images with SMIL animation, so these move in the README.

    python scripts/make_readme_art.py        # writes docs/figures/readme_{stats,timescales,stack,marquee,equations}.svg

Design patterns (re-implemented, nothing copied; see CREDITS.md): number-ticker tiles and bento grid (Magic UI
NumberTicker/BentoGrid), animated beams between nodes (Magic UI AnimatedBeam), an infinite marquee (Magic UI
Marquee), and a "show the real internal numbers" chart (llm-viz, transformer-explainer)."""
from __future__ import annotations

import json
import math
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "figures"
FONT = "Inter,Segoe UI,Helvetica,Arial,sans-serif"
MONO = "JetBrains Mono,Menlo,Consolas,monospace"
COL = {"warm": "#ff8a4c", "green": "#45e0a0", "blue": "#5ea8ff", "violet": "#a78bfa", "cyan": "#5ef2e0", "mars": "#ff6b4a"}

DEFS = f'''<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#060a16"/><stop offset="1" stop-color="#0b1224"/></linearGradient>
  <radialGradient id="aur" cx="0.15" cy="0" r="0.9"><stop offset="0" stop-color="#5ea8ff" stop-opacity=".16"/><stop offset="1" stop-color="#5ea8ff" stop-opacity="0"/></radialGradient>
  <linearGradient id="shine" x1="0" y1="0" x2="1" y2="1" gradientUnits="objectBoundingBox">
    <stop offset="0" stop-color="#5ea8ff" stop-opacity=".0"/><stop offset=".45" stop-color="#5ef2e0" stop-opacity=".9"/>
    <stop offset=".55" stop-color="#a78bfa" stop-opacity=".9"/><stop offset="1" stop-color="#ff8a4c" stop-opacity="0"/>
    <animateTransform attributeName="gradientTransform" type="rotate" from="0 .5 .5" to="360 .5 .5" dur="6s" repeatCount="indefinite"/>
  </linearGradient>
  <filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
</defs>'''


def frame(w: int, h: int, body: str, title: str) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{escape(title)}">'
            f'<title>{escape(title)}</title>{DEFS}<rect width="{w}" height="{h}" rx="22" fill="url(#bg)"/>'
            f'<rect width="{w}" height="{h}" rx="22" fill="url(#aur)"/>{body}</svg>')


def fmt(v: float, dec: int) -> str:
    return f"{v:,.{dec}f}"


def ticker(x: float, y: float, value: float, dec: int, unit: str, color: str, begin: float, frames: int = 16,
           dt: float = 0.07) -> str:
    """A number that counts up from 0 to `value` (ease-out cubic) with its unit riding behind it: one <text> per frame,
    toggled by <set>. The final frame is visible by default, so a renderer without SMIL shows the real value."""
    out = []
    for k in range(frames + 1):
        v = value * (1 - (1 - k / frames) ** 3)
        t_on, t_off = begin + k * dt, begin + (k + 1) * dt
        if k == frames:          # final value: shown unless an animation is running and has not reached it yet
            vis, sets = "visible", f'<set attributeName="visibility" to="hidden" begin="0s" end="{t_on:.2f}s"/>'
        else:
            vis = "hidden"
            sets = f'<set attributeName="visibility" to="visible" begin="{0 if k == 0 else t_on:.2f}s" end="{t_off:.2f}s"/>'
        out.append(f'<text x="{x}" y="{y}" visibility="{vis}" font-family="{FONT}" font-weight="800" font-size="40" fill="{color}">'
                   f'{fmt(v, dec)}<tspan dx="8" font-size="17" font-weight="600" fill="#93a1b8">{escape(unit)}</tspan>{sets}</text>')
    return "".join(out)


def appear(begin: float, dur: float = 0.5, rise: float = 14) -> str:
    """Fade-and-rise entrance that starts at t=0 (holding the hidden state until `begin`), so the static default is the
    finished picture and GitHub's animated render still staggers the tiles."""
    total = begin + dur
    f = begin / total
    return (f'<animate attributeName="opacity" values="0;0;1" keyTimes="0;{f:.3f};1" dur="{total:.2f}s" fill="freeze"/>'
            f'<animateTransform attributeName="transform" type="translate" values="0 {rise};0 {rise};0 0" keyTimes="0;{f:.3f};1" '
            f'dur="{total:.2f}s" fill="freeze"/>')


def stats(site: dict, status: dict) -> str:
    h = site["headline"]
    tiles = [
        (h["round_trip_max_min"], 1, "min", "round trip a memory must survive at Mars' farthest", "warm"),
        (h["one_way_max_min"], 1, "min", f"one-way light time to Mars (closest {h['one_way_min_min']:.1f} min)", "warm"),
        (h["mars_capable_memories"], 0, f"of {h['n_memories']}", "demonstrated memories that outlast that round trip", "green"),
        (h["micius_two_link_loss_db_30deg"], 1, "dB", "Micius two-downlink loss, reproduced at 30°", "blue"),
        (h["bb84_threshold_pct"], 2, "%", "BB84 error threshold", "violet"),
        (h["chain_crossover_km_1s_memory"], 0, "km", "where a repeater with 1 s memories beats fiber", "blue"),
        (h["dejmps_pairs"], 0, "pairs", f"DEJMPS purification 0.80→0.99 (BBPSSW {h['bbpssw_pairs']:,.0f})", "green"),
        (status.get("tests", 0), 0, "tests", f"{status.get('requirements_verified', 0)}/{status.get('requirements', 0)} requirements verified by test", "cyan"),
    ]
    W, H, cols, pad, gap = 1280, 404, 4, 28, 18
    tw, th = (W - 2 * pad - (cols - 1) * gap) / cols, 150
    body = [f'<text x="{pad}" y="46" font-family="{FONT}" font-size="15" font-weight="700" letter-spacing="2.5" fill="{COL["cyan"]}">THE CATCH, IN NUMBERS</text>',
            f'<text x="{W - pad}" y="46" text-anchor="end" font-family="{MONO}" font-size="13" fill="#5b6780">computed by the tested code · v{escape(str(status.get("version", "")))}</text>']
    for i, (val, dec, unit, label, c) in enumerate(tiles):
        x, y = pad + (i % cols) * (tw + gap), 70 + (i // cols) * (th + gap)
        d = 0.15 + 0.12 * i
        body.append(f'<g>{appear(d)}'
                    f'<rect x="{x:.1f}" y="{y}" width="{tw:.1f}" height="{th}" rx="16" fill="#111a2e" fill-opacity=".85"/>'
                    f'<rect x="{x:.1f}" y="{y}" width="{tw:.1f}" height="{th}" rx="16" fill="none" stroke="url(#shine)" stroke-width="1.6"/>'
                    f'<rect x="{x:.1f}" y="{y}" width="{tw:.1f}" height="{th}" rx="16" fill="none" stroke="rgba(148,170,210,.14)"/>')
        body.append(ticker(round(x + 22, 1), y + 62, val, dec, unit, COL[c], d + 0.2))
        words, lines, cur = label.split(), [], ""
        for w_ in words:
            if len(cur) + len(w_) + 1 > 31:
                lines.append(cur); cur = w_
            else:
                cur = (cur + " " + w_).strip()
        lines.append(cur)
        for j, ln in enumerate(lines[:3]):
            body.append(f'<text x="{x + 22:.1f}" y="{y + 94 + 19 * j}" font-family="{FONT}" font-size="14.5" fill="#93a1b8">{escape(ln)}</text>')
        body.append("</g>")
    return frame(W, H, "".join(body), "Headline results computed by the tested code")


def timescales(site: dict) -> str:
    """Log-time chart: how long each demonstrated memory keeps a teleportation above 2/3 versus each round trip."""
    W, H = 1280, 470
    x0, x1, t0, t1 = 330, 1250, -4.0, 5.7            # log10 seconds: 100 us to ~2 days
    X = lambda s: x0 + (x1 - x0) * (math.log10(s) - t0) / (t1 - t0)
    mems = sorted(site["memories"], key=lambda m: m["crossover_s"])
    rts = site["baselines_round_trip_s"]
    top, row = 92, 42
    ybot = top + row * len(mems) + 8
    body = [f'<text x="40" y="46" font-family="{FONT}" font-size="15" font-weight="700" letter-spacing="2.5" fill="{COL["cyan"]}">THE THESIS QUESTION, ANSWERED</text>',
            f'<text x="40" y="74" font-family="{FONT}" font-size="21" font-weight="700" fill="#e8eef8">How long each memory keeps teleportation above 2/3, against each round trip</text>']
    for e in range(-4, 6):
        body.append(f'<line x1="{X(10**e):.1f}" y1="{top - 6}" x2="{X(10**e):.1f}" y2="{ybot}" stroke="rgba(148,170,210,.10)"/>')
    labels = {-3: "1 ms", 0: "1 s", 1: "10 s", 2: "100 s", 3: "1000 s", 4: "2.8 h", 5: "28 h", -4: "100 µs", -2: "10 ms", -1: "0.1 s"}
    for e, lab in labels.items():
        body.append(f'<text x="{X(10**e):.1f}" y="{ybot + 22}" text-anchor="middle" font-family="{MONO}" font-size="12" fill="#5b6780">{lab}</text>')
    mars_max = rts["Mars max"]
    for i, m in enumerate(mems):
        y = top + i * row
        wbar = X(m["crossover_s"]) - x0
        ok = m["crossover_s"] >= mars_max
        c = COL["green"] if ok else "#3d5a80"
        d = 0.3 + 0.18 * i
        body.append(f'<text x="{x0 - 14}" y="{y + 20}" text-anchor="end" font-family="{FONT}" font-size="14" fill="#c9d4e6">{escape(m["name"])}</text>'
                    f'<text x="{x0 - 14}" y="{y + 35}" text-anchor="end" font-family="{MONO}" font-size="11" fill="#5b6780">retrieval {100 * m["efficiency"]:.1f} %</text>')
        f = d / (d + 1.1)
        body.append(f'<rect x="{x0}" y="{y + 8}" width="{wbar:.1f}" height="22" rx="6" fill="{c}" fill-opacity="{0.9 if ok else 0.55}">'
                    f'<animate attributeName="width" values="0;0;{wbar:.1f}" keyTimes="0;{f:.3f};1" dur="{d + 1.1:.2f}s" fill="freeze" '
                    f'calcMode="spline" keySplines="0 0 1 1;.2 .8 .2 1"/></rect>')
        if ok:
            g = (d + 1.1) / (d + 1.5)
            inside = x0 + wbar + 140 > W - 20                  # no room to the right: write it on the bar's end
            tx, anchor, fc = (x0 + wbar - 12, "end", "#06241a") if inside else (x0 + wbar + 10, "start", COL["green"])
            body.append(f'<text x="{tx:.1f}" y="{y + 25}" text-anchor="{anchor}" font-family="{FONT}" font-size="15" font-weight="800" fill="{fc}">'
                        f'✓ reaches Mars<animate attributeName="opacity" values="0;0;1" keyTimes="0;{g:.3f};1" dur="{d + 1.5:.2f}s" fill="freeze"/></text>')
    for name, s in rts.items():
        xx = X(s)
        body.append(f'<line x1="{xx:.1f}" y1="{top - 6}" x2="{xx:.1f}" y2="{ybot}" stroke="{COL["warm"]}" stroke-width="1.6" stroke-dasharray="5 5" opacity=".85">'
                    f'<animate attributeName="stroke-dashoffset" from="0" to="-20" dur="1s" repeatCount="indefinite"/></line>')
    # round-trip labels, staggered to avoid overlap
    for k, (name, s) in enumerate(rts.items()):
        xx = X(s)
        yl = ybot + 44 + (k % 2) * 18
        body.append(f'<text x="{xx:.1f}" y="{yl}" text-anchor="middle" font-family="{FONT}" font-size="12.5" font-weight="600" fill="{COL["warm"]}">{escape(name)}</text>')
    body.append(f'<text x="40" y="{H - 18}" font-family="{FONT}" font-size="12.5" fill="#5b6780">Bars: how long a Bell pair of fidelity 0.95 stored in each demonstrated memory keeps teleportation above 2/3 (green: longer than Mars\' farthest round trip). '
                f'Orange lines: classical round trips.</text>')
    return frame(W, H, "".join(body), "Memory useful time versus classical round trip, computed by qll.network.memory_decoherence")


STACK = [("constants", "n̄(ω,T)"), ("channels", "η, τ = d/c"), ("circuits", "F, S"), ("QKD", "r ≤ PLOB"),
         ("network", "memories"), ("space", "ephemeris"), ("messenger", "fail closed")]


def stack() -> str:
    W, H = 1280, 300
    xs = [120 + i * (W - 240) / (len(STACK) - 1) for i in range(len(STACK))]
    pos = [(x, 118 if i % 2 == 0 else 200) for i, x in enumerate(xs)]
    body = [f'<text x="40" y="46" font-family="{FONT}" font-size="15" font-weight="700" letter-spacing="2.5" fill="{COL["cyan"]}">HOW THE CODE FITS TOGETHER</text>',
            f'<text x="{W - 40}" y="46" text-anchor="end" font-family="{MONO}" font-size="13" fill="#5b6780">every node is a tested package · beams are the imports</text>']
    for i in range(len(pos) - 1):
        (x1, y1), (x2, y2) = pos[i], pos[i + 1]
        mx = (x1 + x2) / 2
        d = f"M{x1:.0f},{y1} C{mx:.0f},{y1} {mx:.0f},{y2} {x2:.0f},{y2}"
        body.append(f'<path d="{d}" fill="none" stroke="rgba(148,170,210,.18)" stroke-width="2"/>')
        body.append(f'<path d="{d}" fill="none" stroke="{COL["cyan"]}" stroke-width="3" stroke-linecap="round" stroke-dasharray="46 400" opacity=".9">'
                    f'<animate attributeName="stroke-dashoffset" from="446" to="0" dur="2.4s" begin="{0.35 * i:.2f}s" repeatCount="indefinite"/></path>')
        body.append(f'<circle r="4.5" fill="#e8fffb" filter="url(#glow)"><animateMotion dur="2.4s" begin="{0.35 * i:.2f}s" repeatCount="indefinite" path="{d}"/></circle>')
    for (x, y), (name, eq) in zip(pos, STACK):
        body.append(f'<rect x="{x - 72:.0f}" y="{y - 32}" width="144" height="64" rx="15" fill="#111a2e" stroke="rgba(148,170,210,.3)"/>'
                    f'<rect x="{x - 72:.0f}" y="{y - 32}" width="144" height="64" rx="15" fill="none" stroke="url(#shine)" stroke-width="1.2" opacity=".7"/>'
                    f'<text x="{x:.0f}" y="{y - 4}" text-anchor="middle" font-family="{FONT}" font-size="16" font-weight="700" fill="#e8eef8">{escape(name)}</text>'
                    f'<text x="{x:.0f}" y="{y + 17}" text-anchor="middle" font-family="{MONO}" font-size="13" fill="#93a1b8">{escape(eq)}</text>')
    body.append(f'<text x="{W / 2}" y="{H - 24}" text-anchor="middle" font-family="{FONT}" font-size="13" fill="#5b6780">'
                f'qll/constants → channels → circuits → qkd → network → space → app, plus hardware, analysis, and viz</text>')
    return frame(W, H, "".join(body), "The qll package stack from constants to the fail-closed messenger")


# One pill per file in experiments/done/ (tests/test_site.py holds the two in step).
LANDMARKS = ["Stern–Gerlach 1922", "Grangier–Roger–Aspect 1986", "Bell test with SPDC photons", "Gruber NV ODMR 1997",
             "Rabi, Ramsey, Hahn echo", "Hong–Ou–Mandel 1987", "Bouwmeester teleportation 1997",
             "NV network, Bernien → Hermans", "Micius satellite 2017", "QEC below threshold 2025",
             "Aspect time-varying analyzers 1982", "Furusawa CV teleportation 1998", "Bhaskar memory-enhanced 2020",
             "Jinan-1 microsatellite 2025", "Bluvstein logical atoms 2024"]


def marquee() -> str:
    W, H = 1280, 120
    pills, x = [], 0.0
    for name in LANDMARKS:
        w = 26 + 8.1 * len(name)
        pills.append((x, w, name))
        x += w + 14
    total = x
    track = []
    for rep in (0, total):
        for px, w, name in pills:
            track.append(f'<rect x="{px + rep:.1f}" y="58" width="{w:.1f}" height="36" rx="18" fill="#111a2e" stroke="rgba(148,170,210,.22)"/>'
                         f'<text x="{px + rep + w / 2:.1f}" y="81" text-anchor="middle" font-family="{FONT}" font-size="14" fill="#c9d4e6">{escape(name)}</text>')
    fade = ('<linearGradient id="fade" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".08" stop-color="#fff"/>'
            '<stop offset=".92" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
            f'<mask id="m"><rect width="{W}" height="{H}" fill="url(#fade)"/></mask>')
    body = (f'<defs>{fade}</defs>'
            f'<text x="40" y="38" font-family="{FONT}" font-size="15" font-weight="700" letter-spacing="2.5" fill="{COL["cyan"]}">{len(LANDMARKS)} LANDMARK EXPERIMENTS, EACH WITH A CHEAP RECREATION</text>'
            f'<g mask="url(#m)"><g>{"".join(track)}'
            f'<animateTransform attributeName="transform" type="translate" from="0 0" to="{-total:.1f} 0" dur="{total / 45:.1f}s" repeatCount="indefinite"/></g></g>')
    return frame(W, H, body, "Landmark experiments recreated in the repository")


EQUATIONS = [
    (r"$\bar{n}(\omega,T)=\dfrac{1}{e^{\hbar\omega/k_BT}-1}$", "Heat decides where each part of the link can live",
     "qll/circuits/noise/thermal.py", "warm"),
    (r"$\eta_{\mathrm{geo}}=1-\exp\!\left(-\dfrac{2r_{\mathrm{rx}}^2}{w(L)^2}\right),\quad w(L)=w_0\sqrt{1+(L/z_R)^2}$",
     "Photons are lost as 1/L² in space", "qll/channels/free_space_diffraction.py", "blue"),
    (r"$\tau=\dfrac{d(t)}{c}$", "The two classical bits of every teleportation arrive minutes later",
     "qll/channels/light_time_delay.py", "mars"),
    (r"$f(t)=\frac{1}{4}+\left(f_0-\frac{1}{4}\right)e^{-t/T_{\mathrm{mem}}},\quad \bar{F}=\dfrac{2f+1}{3}>\dfrac{2}{3}$",
     "So the memory must outlive the round trip 2d/c", "qll/network/memory_decoherence.py", "green"),
    (r"$K\leq-\log_2(1-\eta)$", "No repeaterless protocol beats this (the PLOB bound)", "qll/qkd/plob_bound.py", "violet"),
]


def equations() -> str:
    """The argument in five equations as one dark card, typeset by matplotlib's mathtext (glyphs become paths, so the
    SVG needs no fonts and GitHub shows it exactly as rendered here)."""
    import io

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch

    plt.rcParams.update({"mathtext.fontset": "cm", "svg.hashsalt": "qll-readme", "font.family": "DejaVu Sans"})
    W, H = 12.8, 6.9
    fig = plt.figure(figsize=(W, H), dpi=100, facecolor="#070b17")
    ax = fig.add_axes((0, 0, 1, 1)); ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis("off")
    ax.add_patch(FancyBboxPatch((0.02, 0.02), W - 0.04, H - 0.04, boxstyle="round,pad=0,rounding_size=0.22",
                                fc="#0b1224", ec="#1d2a44", lw=1.2))
    ax.text(0.4, H - 0.45, "THE ARGUMENT IN FIVE EQUATIONS", color=COL["cyan"], fontsize=12, fontweight="bold")
    ax.text(W - 0.4, H - 0.45, "each line is a tested module", color="#5b6780", fontsize=10, ha="right", family="monospace")
    row, top = 1.2, H - 0.85
    for i, (tex, why, mod, c) in enumerate(EQUATIONS):
        y = top - (i + 1) * row + 0.1
        ax.add_patch(FancyBboxPatch((0.4, y), W - 0.8, row - 0.18, boxstyle="round,pad=0,rounding_size=0.14",
                                    fc="#111a2e", ec="#22304d", lw=1))
        ax.add_patch(FancyBboxPatch((0.4, y), 0.07, row - 0.18, boxstyle="round,pad=0,rounding_size=0.03", fc=COL[c], ec="none"))
        ax.text(0.75, y + (row - 0.18) / 2, f"{i + 1}", color=COL[c], fontsize=20, fontweight="bold", va="center")
        ax.text(1.2, y + (row - 0.18) / 2, tex, color="#e8eef8", fontsize=19, va="center")
        ax.text(W - 0.65, y + (row - 0.18) / 2 + 0.16, why, color="#c9d4e6", fontsize=11.5, ha="right", va="center")
        ax.text(W - 0.65, y + (row - 0.18) / 2 - 0.2, mod, color="#5b6780", fontsize=9.5, ha="right", va="center",
                family="monospace")
    buf = io.StringIO()
    fig.savefig(buf, format="svg", metadata={"Date": None, "Creator": None}, facecolor=fig.get_facecolor())
    plt.close(fig)
    svg = buf.getvalue()
    return svg[svg.index("<svg"):]


def main() -> None:
    site = json.loads((ROOT / "docs" / "site_data.json").read_text(encoding="utf-8"))
    status = json.loads((ROOT / "docs" / "status.json").read_text(encoding="utf-8")) if (ROOT / "docs" / "status.json").exists() else {}
    for name, svg in (("readme_stats", stats(site, status)), ("readme_timescales", timescales(site)),
                      ("readme_stack", stack()), ("readme_marquee", marquee()), ("readme_equations", equations())):
        (OUT / f"{name}.svg").write_text(svg, encoding="utf-8")
        print(f"wrote docs/figures/{name}.svg")


if __name__ == "__main__":
    main()
