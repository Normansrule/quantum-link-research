"""Assemble research/thesis/chapters/*.md plus the generated tables into research/thesis/THESIS_DRAFT.md.
Convert with pandoc if desired: pandoc THESIS_DRAFT.md -o thesis.docx --citeproc --bibliography docs/references.bib"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
T = ROOT / "research" / "thesis"

if __name__ == "__main__":
    parts = ["# Quantum Links from a Bench to Mars: a Systems-Engineering Study of Physics-Secured Communication at Planetary Distance", "",
             "Aleksander Norman · M.S. Systems Engineering, California State University, Dominguez Hills · draft assembled by `scripts/build_thesis.py`", ""]
    for ch in sorted((T / "chapters").glob("*.md")):
        parts += [ch.read_text(encoding="utf-8").rstrip(), "", "\\newpage", ""]
    parts += ["# Appendix A — Generated results tables", "", (T / "results" / "tables.md").read_text(encoding="utf-8").split("\n", 3)[3]]
    parts += ["", "\\newpage", "", "# Appendix B — Requirements and verification", "", (T / "VERIFICATION_PLAN.md").read_text(encoding="utf-8").split("\n", 2)[2]]
    out = T / "THESIS_DRAFT.md"
    out.write_text("\n".join(parts) + "\n", encoding="utf-8")
    words = len(out.read_text(encoding="utf-8").split())
    print(f"wrote {out.relative_to(ROOT)} ({words} words)")
