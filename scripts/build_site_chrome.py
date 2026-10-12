"""Write the same navigation, lab tabs, and footer into every page of the website, so the site reads as one product:
one global menu in the same order everywhere with the current page marked, one strip of tabs across the labs, and one
footer with the version and the honest scope line. tests/test_site_chrome.py checks the committed pages are current.

    python scripts/build_site_chrome.py
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
REPO = "https://github.com/Normansrule/quantum-link-research"

# (path under docs/, label, optional): optional links fold into the menu first on narrower screens
NAV = [("", "Home", False), ("latency/", "Anywhere", False), ("lab/", "Lab", False), ("mars/", "Mars", False), ("budget/", "Budget", False),
       ("teleport/", "Teleport", False), ("monitor/", "Monitor", True), ("link/", "Link ops", True), ("repeater/", "Repeater", True),
       ("coupler/", "Coupler", True), ("qec/", "QEC", True), ("systems/", "Systems", True)]
LABS = [("lab/", "All labs"), ("lab/link/", "Two-room link"), ("lab/channel/", "Quantum channels"), ("lab/outdoor/", "Outdoors and orbit"),
        ("lab/frontier/", "Frontier"), ("lab/messenger/", "Messenger"), ("lab/circuits/", "Cloud circuits")]
FOOT_START, FOOT_END = "<!-- site-foot:start -->", "<!-- site-foot:end -->"
TABS_START, TABS_END = "<!-- lab-tabs:start -->", "<!-- lab-tabs:end -->"


def pages() -> list[Path]:
    return sorted(p for p in DOCS.rglob("index.html") if "vendor" not in p.parts)


def _rel(page: Path) -> str:
    return "../" * (len(page.relative_to(DOCS).parts) - 1)


def _here(page: Path) -> str:
    parts = page.relative_to(DOCS).parts[:-1]
    return "/".join(parts) + "/" if parts else ""


def version() -> str:
    return re.search(r'^version = "([^"]+)"', (ROOT / "pyproject.toml").read_text(encoding="utf-8"), re.M).group(1)


def nav_html(page: Path) -> str:
    rel, here = _rel(page), _here(page)
    section = here.split("/")[0] + "/" if here else ""
    out = []
    for path, label, opt in NAV:
        current = path == here or (path == section and path != "")
        attrs = (' class="opt"' if opt else "") + (' aria-current="page"' if current else "")
        out.append(f'<a{attrs} href="{(rel + path) or "./"}">{label}</a>')
    out.append(f'<a class="gh" href="{REPO}">GitHub ↗</a>')
    return "".join(out)


def tabs_html(page: Path) -> str:
    rel, here = _rel(page), _here(page)
    links = "".join(f'<a href="{rel}{p}"' + (' aria-current="page"' if p == here else "") + f">{label}</a>" for p, label in LABS)
    return f'{TABS_START}<nav class="lab-tabs" aria-label="Labs">{links}</nav>{TABS_END}'


def foot_html(page: Path) -> str:
    rel = _rel(page)
    return (f'{FOOT_START}<div class="site-foot" role="contentinfo"><span class="brand-s">Quantum Link Research</span>'
            f'<span>v{version()}</span>'
            f'<a href="{rel}latency/">Anywhere at light speed</a><a href="{REPO}">Source</a>'
            f'<a href="{REPO}/blob/main/CHANGELOG.md">Changelog</a><a href="{REPO}/blob/main/docs/audit/2026-10-11_findings.md">Audit findings</a>'
            f'<a href="{REPO}/blob/main/CREDITS.md">Credits</a>'
            '<span class="grow">No signal outruns light. Numbers are model outputs unless a page says measured; nothing here is a security-reviewed link.</span>'
            f"</div>{FOOT_END}")


def render(page: Path, html: str) -> str:
    # 1. the global navigation inside the fixed header
    html = re.sub(r'(<header class="top">.*?<nav[^>]*>).*?(</nav>)', lambda m: m.group(1) + nav_html(page) + m.group(2), html, count=1, flags=re.S)
    # 2. the lab tabs, first thing in each lab's head
    if _here(page).startswith("lab/"):
        if TABS_START in html:
            html = re.sub(re.escape(TABS_START) + ".*?" + re.escape(TABS_END), lambda m: tabs_html(page), html, count=1, flags=re.S)
        else:
            html = re.sub(r'(<section class="lab-head"[^>]*>)', lambda m: m.group(1) + "\n  " + tabs_html(page), html, count=1)
    # 3. the shared footer, after the page's own footer and before its scripts
    if FOOT_START in html:
        html = re.sub(re.escape(FOOT_START) + ".*?" + re.escape(FOOT_END), lambda m: foot_html(page), html, count=1, flags=re.S)
    else:
        main_end = html.find("</main>")
        tail = html[main_end:] if main_end >= 0 else html
        m = re.search(r"\n<script(?![^>]*importmap)", tail)
        at = (main_end if main_end >= 0 else 0) + (m.start() if m else tail.rfind("</body>"))
        html = html[:at] + "\n" + foot_html(page) + html[at:]
    return html


def main() -> None:
    for p in pages():
        old = p.read_text(encoding="utf-8")
        new = render(p, old)
        if new != old:
            p.write_text(new, encoding="utf-8")
            print(f"updated {p.relative_to(ROOT).as_posix()}")


if __name__ == "__main__":
    main()
