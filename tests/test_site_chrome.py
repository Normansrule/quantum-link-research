"""One site, not eighteen pages: every page carries the same global navigation in the same order with the current page
marked, the labs share one strip of tabs, and every page ends with the same footer. scripts/build_site_chrome.py
writes them; this test fails when a page drifts from it."""
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_site_chrome as C  # noqa: E402

pytestmark = pytest.mark.phase1
PAGES = C.pages()


@pytest.mark.parametrize("page", PAGES, ids=lambda p: p.relative_to(C.DOCS).as_posix())
def test_page_chrome_is_current(page):
    html = page.read_text(encoding="utf-8")
    assert C.render(page, html) == html, "run python scripts/build_site_chrome.py"
    nav = re.search(r'<header class="top">.*?<nav[^>]*>(.*?)</nav>', html, re.S).group(1)
    labels = re.findall(r">([^<]+)</a>", nav)
    assert labels == [label for _, label, _ in C.NAV] + ["GitHub ↗"]
    assert nav.count('aria-current="page"') == (0 if C._here(page).startswith("apps/") else 1)
    assert html.count(C.FOOT_START) == 1 and f"v{C.version()}" in html


def test_every_nav_target_exists():
    for path, _, _ in C.NAV:
        assert (C.DOCS / path / "index.html").exists(), path
    for path, _ in C.LABS:
        assert (C.DOCS / path / "index.html").exists(), path


def test_lab_pages_share_the_tabs():
    for page in PAGES:
        html = page.read_text(encoding="utf-8")
        if C._here(page).startswith("lab/"):
            assert html.count(C.TABS_START) == 1 and 'class="lab-tabs"' in html
        else:
            assert C.TABS_START not in html
