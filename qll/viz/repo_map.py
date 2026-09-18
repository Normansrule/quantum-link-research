"""The repository as a map: three doors (learn, experiments, research) around the tested code."""
from __future__ import annotations

from qll.viz._common import cli, finish

BOXES = [  # (x, y, w, h, title, lines, color)
    (0.02, 0.56, 0.30, 0.40, "learn/  ·  understand", ["00 foundations (15)", "01 computing core (8)", "02 qubit modalities (12)", "03 communication (5)", "glossary · misconceptions", "3 learning paths"], "#4c72b0"),
    (0.35, 0.56, 0.30, 0.40, "experiments/  ·  build", ["bench/ parts, budgets", "protocols/ P01–P04", "done/ 10 landmarks", "proposed/ E1–E10", "lessons/ what failed, what scaled"], "#55a868"),
    (0.68, 0.56, 0.30, 0.40, "research/  ·  frontier", ["cutting_edge/ timeline, problems", "theories/ T01–T10", "thesis/ DESIGN_PROCESS", "thesis/ BACKLOG: what next", "watchlist 2026"], "#c44e52"),
    (0.02, 0.06, 0.46, 0.42, "qll/  ·  tested physics code", ["constants → channels → circuits", "→ qkd → network → space → app", "viz/ 10 explorers", "178+ analytic tests", "invariants: no-signaling, no-cloning,", "2 bits/qubit, CPTP, PLOB, T required"], "#8172b2"),
    (0.52, 0.06, 0.46, 0.42, "docs/ + systems/  ·  engineering", ["physics_overview.md (all equations)", "physics_module_design.md (module cards)", "figures/ · apps/ (browser explorers)", "references.bib (+ additions, TODO flags)", "needs · requirements · risks · TRL", "traceability_matrix.csv (machine-checked)"], "#937860"),
]


def main() -> None:
    args = cli(__doc__)
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

    fig, ax = plt.subplots(figsize=(12, 7))
    ax.axis("off"); ax.set(xlim=(0, 1), ylim=(0, 1))
    for x, y, w, h, title, lines, c in BOXES:
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.01", fc=c, alpha=0.12, ec=c, lw=2))
        ax.text(x + 0.015, y + h - 0.045, title, fontsize=12, fontweight="bold", color=c)
        for i, ln in enumerate(lines):
            ax.text(x + 0.02, y + h - 0.10 - 0.05 * i, ln, fontsize=9)
    for (x0, y0, x1, y1, lab) in [(0.32, 0.76, 0.35, 0.76, "then build"), (0.65, 0.76, 0.68, 0.76, "then push the frontier"),
                                  (0.17, 0.56, 0.17, 0.48, "equations → code"), (0.50, 0.56, 0.75, 0.48, "proposals → requirements")]:
        ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="->", mutation_scale=16, lw=1.5, color="0.4"))
        ax.text((x0 + x1) / 2, (y0 + y1) / 2 + 0.015, lab, fontsize=8, ha="center", color="0.4")
    ax.text(0.5, 0.995, "quantum-link-research: three doors around one tested core", ha="center", va="top", fontsize=14)
    finish(fig, args)


if __name__ == "__main__":
    main()
