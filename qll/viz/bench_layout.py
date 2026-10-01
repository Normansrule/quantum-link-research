"""The tabletop Mars-link bench (experiments/protocols/P09), seen from above, beside the Earth-Mars link it stands in
for. The lamp is the Sun, a matte white ball is Earth, a bare fiber tip is the Earth-end transmitter (on the lit face,
on the dark face, or beside the ball), and a fiber collimator is the Mars receiver. The table's numbers come from
qll/systems/bench_twin.py and qll/systems/mars_budget.py: on both, the receiver resolves the planet."""
from __future__ import annotations

import math

from dataclasses import replace

from qll.systems.bench_twin import BenchDesign, background_power_w, field_of_view_rad, purity, signal_power_w
from qll.systems.mars_budget import MarsLinkDesign, budget
from qll.viz._common import cli, finish


def main() -> None:
    args = cli(__doc__)
    import matplotlib.pyplot as plt
    from matplotlib.patches import Arc, Circle, FancyArrowPatch, FancyBboxPatch, Rectangle

    b, m = BenchDesign(), MarsLinkDesign()
    fig, (ax, tx) = plt.subplots(1, 2, figsize=(15, 6.2), gridspec_kw={"width_ratios": [1.55, 1]})
    fig.suptitle("P09 · the Mars link on a table: same laws, bench-sized numbers", fontsize=15, y=0.99)
    ax.set(xlim=(0, 1.55), ylim=(0, 1)); ax.axis("off"); ax.set_aspect("equal")

    def box(x, y, w, h, label, color, fs=8.5):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.008", fc=color, alpha=0.18, ec=color, lw=1.6))
        ax.text(x + w / 2, y + h / 2, label, ha="center", va="center", fontsize=fs)

    def arrow(x0, y0, x1, y1, color="0.35", style="-|>", ls="-"):
        ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle=style, mutation_scale=11, color=color, lw=1.3, ls=ls))

    # backdrop, ball, lamp on its arm
    ax.add_patch(Rectangle((0.05, 0.18), 0.012, 0.64, color="0.1")); ax.text(0.04, 0.84, "black backdrop\n(dark space)", fontsize=8, ha="left")
    bx, by, br = 0.30, 0.50, 0.06
    ax.add_patch(Circle((bx, by), br, fc="white", ec="0.3", lw=1.5))
    ax.add_patch(Arc((bx, by), 2 * br, 2 * br, theta1=-90, theta2=90, color="#f5b942", lw=5, alpha=0.7))
    ax.text(bx, by - br - 0.05, f"matte white ball\n(Earth), {b.ball_diameter_m * 1e3:.0f} mm", ha="center", va="top", fontsize=8.5)
    lx, ly = bx + 0.22 * math.cos(math.radians(35)), by + 0.22 * math.sin(math.radians(35))
    ax.add_patch(Circle((lx, ly), 0.03, fc="#ffd35a", ec="#c99700", lw=1.5)); ax.text(lx + 0.04, ly + 0.02, "lamp (the Sun)\non a turntable arm", fontsize=8.5)
    ax.add_patch(Arc((bx, by), 0.44, 0.44, theta1=0, theta2=35, color="#c99700", lw=1.2, ls="--"))
    ax.text(bx + 0.24, by + 0.05, "phase α", fontsize=8.5, color="#a07800")
    # transmitter positions
    for (x, y, lab, c) in ((bx + br, by, "day", "#d9534f"), (bx - br * 0.2, by - br * 0.98, "night", "#5b6780"), (bx + 0.02, by + 0.26, "space", "#2f9e6e")):
        ax.add_patch(Circle((x, y), 0.011, color=c, zorder=5)); ax.text(x + 0.018, y + 0.012, lab, fontsize=8.5, color=c, fontweight="bold")
    box(0.10, 0.03, 0.23, 0.08, "650 nm laser → ND wheel\n→ single-mode fiber (transmitter)", "#d9534f")
    arrow(0.22, 0.11, bx + br - 0.005, by - 0.01, "#d9534f", ls="--")
    # receiver
    rx = 1.18
    ax.add_patch(Rectangle((rx - 0.05, by - 0.018), 0.035, 0.036, color="#6f42c1", alpha=0.6)); ax.text(rx - 0.03, by + 0.05, "bandpass\nfilter", ha="center", fontsize=8)
    ax.add_patch(Rectangle((rx, by - 0.025), 0.08, 0.05, color="#4a6fa5")); ax.text(rx + 0.04, by - 0.07, "fiber collimator\non a rotation stage\n(the Mars receiver)", ha="center", va="top", fontsize=8.5)
    ax.add_patch(Arc((rx + 0.04, by), 0.2, 0.2, theta1=150, theta2=210, color="#4a6fa5", lw=1.2))
    box(rx + 0.12, by + 0.14, 0.2, 0.09, "SMF → photon counter\n(Tier 2)", "#4a6fa5")
    box(rx + 0.12, by - 0.24, 0.2, 0.09, "MMF → photodiode\n+ TIA (Tier 1)", "#4a6fa5")
    arrow(rx + 0.08, by + 0.01, rx + 0.12, by + 0.18, "#4a6fa5"); arrow(rx + 0.08, by - 0.01, rx + 0.12, by - 0.19, "#4a6fa5")
    arrow(bx + br + 0.03, by + 0.38, rx - 0.06, by + 0.38, "0.3", style="<|-|>")
    ax.text((bx + rx) / 2, by + 0.40, f"d = {b.distance_m:g} m", ha="center", fontsize=9)
    box(0.66, 0.03, 0.34, 0.1, "Stage 6: polarizer at the transmitter;\nPBS + two detectors at the receiver", "#6c757d", fs=8)
    box(1.1, 0.03, 0.4, 0.1, "controller: Arduino/RP2040 + laptop\n(ND steps, lamp, logging, key bank)", "#6c757d", fs=8)

    # the mapping table
    tx.axis("off")
    close = budget(m, 538.0)
    ground = budget(replace(m, architecture="earth_source"), 538.0)
    S = signal_power_w(b, "mmf")
    w_day, w_night = purity(S, background_power_w(b, "mmf", "day")), purity(S, background_power_w(b, "mmf", "night"))
    w_space = purity(S, background_power_w(b, "mmf", "space", offset_radii=5))
    earth_r = 6.371e6 / close.range_m
    mode_mars = m.wavelength_m / m.rx_diameter_mars_m
    rows = [
        ("", "Earth–Mars (closest approach)", "bench (multimode receiver)"),
        ("the Sun", "the Sun", "a lamp, turntable arm"),
        ("the planet", "Earth, albedo 0.3", f"white ball, albedo {b.albedo:g}"),
        ("planet angular radius", f"{earth_r * 1e6:.0f} µrad", f"{b.ball_diameter_m / 2 / b.distance_m * 1e3:.1f} mrad"),
        ("receiver field", f"λ/D = {mode_mars * 1e6:.2f} µrad", f"SMF {field_of_view_rad(b, 'smf') * 1e3:.2f}, MMF {field_of_view_rad(b, 'mmf') * 1e3:.1f} mrad"),
        ("resolved?", "yes, ~250×", f"yes, {b.ball_diameter_m / 2 / b.distance_m / field_of_view_rad(b, 'mmf'):.0f}–{b.ball_diameter_m / 2 / b.distance_m / field_of_view_rad(b, 'smf'):.0f}×"),
        ("ground source, day", f"daylight: purity {100 * ground.extra['purity_daylight']:.1f} %", f"tip on the lit face: {100 * w_day:.0f} %"),
        ("ground source, night", f"airglow: purity {100 * ground.purity:.1f} %", f"tip on the dark face: {100 * w_night:.1f} %"),
        ("space source", f"{m.tx_offset_m / 6.371e6:.0f} Earth radii off: {100 * close.purity:.2f} %", f"tip 5 radii off: {100 * w_space:.1f} %"),
        ("wavelength", f"{m.wavelength_m * 1e9:.0f} nm", f"{b.wavelength_m * 1e9:.0f} nm (silicon, class 2)"),
        ("filter per mode", f"{m.filter_hz / 1e6:.0f} MHz", f"{b.filter_nm:g} nm bandpass"),
        ("stray-light floor", f"{m.stray_light:g}", f"{b.stray_light:g} (to measure)"),
    ]
    tbl = tx.table(cellText=[list(r) for r in rows[1:]], colLabels=list(rows[0]), loc="center", cellLoc="left",
                   colWidths=[0.3, 0.36, 0.36])
    tbl.auto_set_font_size(False); tbl.set_fontsize(8.5); tbl.scale(1, 1.55)
    for (r, c), cell in tbl.get_celld().items():
        cell.set_edgecolor("0.8")
        if r == 0:
            cell.set_text_props(fontweight="bold"); cell.set_facecolor("#eef2f8")
    tx.set_title("what stands in for what", fontsize=11)
    finish(fig, args)


if __name__ == "__main__":
    main()
