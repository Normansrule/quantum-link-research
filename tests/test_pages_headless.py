"""Headless-browser tests of the website: every page loads without a JavaScript error, and the physics each page
shows is what the tested Python says. Skipped unless Playwright and a Chromium build are available; CI installs both.
Run locally with:  pip install playwright && python -m playwright install chromium && python -m pytest -m browser"""
import functools
import http.server
import os
import threading
from pathlib import Path

import pytest

DOCS = Path(__file__).resolve().parents[1] / "docs"
pytestmark = [pytest.mark.browser, pytest.mark.slow]
sync_api = pytest.importorskip("playwright.sync_api")


@pytest.fixture(scope="module")
def server():
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(DOCS))
    handler.log_message = lambda *a, **k: None
    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{httpd.server_address[1]}"
    httpd.shutdown()


@pytest.fixture(scope="module")
def browser():
    args = ["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"]
    with sync_api.sync_playwright() as p:
        b = None
        for kw in ({}, {"executable_path": os.environ.get("QLL_CHROMIUM", "/opt/pw-browsers/chromium-1194/chrome-linux/chrome")}):
            try:
                b = p.chromium.launch(args=args, **kw); break
            except Exception:
                continue
        if b is None:
            pytest.skip("no Chromium available (python -m playwright install chromium)")
        yield b
        b.close()


def open_page(browser, url):
    page = browser.new_page(viewport={"width": 1280, "height": 860})
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
    page.route("**/*", lambda r: r.continue_() if r.request.url.startswith("http://127.0.0.1") else r.abort())  # offline: vendored only
    page.goto(url, wait_until="commit")
    page.wait_for_function("document.readyState === 'complete'", timeout=60000)
    return page, errors


def test_landing_page_renders_data_equations_and_matrix(browser, server):
    page, errors = open_page(browser, server + "/")
    page.wait_for_function("document.querySelectorAll('#matrix tbody tr').length >= 6", timeout=30000)
    assert page.locator(".katex").count() >= 9                               # every equation card typeset
    page.evaluate("document.documentElement.style.scrollBehavior='auto'; document.querySelector('#numbers').scrollIntoView()")
    page.wait_for_function("document.querySelector('[data-num=\"headline.round_trip_max_min\"]').textContent.trim() === '44.6'", timeout=30000)
    assert page.locator("#matrix td.yes").count() >= 20
    assert errors == []


def test_teleportation_explainer_reaches_unit_fidelity(browser, server):
    page, errors = open_page(browser, server + "/teleport/")
    page.evaluate("document.documentElement.style.scrollBehavior='auto'; document.querySelector('[data-step=\"5\"]').scrollIntoView({block:'center'})")
    page.wait_for_function("document.getElementById('bob').textContent.includes('fidelity')", timeout=30000)
    text = page.locator("#bob").inner_text()
    assert "1.000000" in text and "(0.00, 0.00, 0.00)" in text                # corrected state; outcome-averaged Bloch vector is zero
    assert errors == []


def test_link_monitor_refuses_without_relays_and_not_with_them(browser, server):
    page, errors = open_page(browser, server + "/monitor/")
    page.select_option("#speed", "80")
    page.wait_for_function("parseInt(document.getElementById('k-day').textContent.split('+')[1]) > 420", timeout=90000)   # past the first conjunction
    refused = int(page.locator("#k-msg").inner_text().split("refused")[1].replace(",", "").strip())
    assert refused > 0
    page.check("#relay"); page.dispatch_event("#relay", "input")                  # counters reset; the second conjunction (~day 950) must pass without refusals
    page.wait_for_function("parseInt(document.getElementById('k-day').textContent.split('+')[1]) > 1000", timeout=90000)
    refused_relay = int(page.locator("#k-msg").inner_text().split("refused")[1].replace(",", "").strip())
    assert refused_relay == 0
    assert errors == []


def test_mars_simulator_reports_light_time(browser, server):
    page, errors = open_page(browser, server + "/mars/")
    page.wait_for_function("document.getElementById('state').textContent.includes('au')", timeout=30000)
    assert "one-way light time" in page.locator("#state").inner_text()
    assert errors == []


def test_coupler_lab_parks_at_zero_zz_and_plays_a_cz(browser, server):
    page, errors = open_page(browser, server + "/coupler/")
    page.wait_for_function("document.body.dataset.ready === '1'", timeout=30000)
    assert float(page.locator("#k-zz").inner_text()) == pytest.approx(86.2, abs=0.5)      # CoupledPair().zz(6.0), in kHz
    # the idle point (the "park" button glides there with GSAP; set it directly so the test does not depend on frame rate)
    page.evaluate("const s = document.getElementById('wc'); s.value = window.QLLCoupler.idle_ghz; s.dispatchEvent(new Event('input'))")
    assert page.locator("#k-zz").inner_text() == "≈ 0"
    page.evaluate("const s = document.getElementById('tt'); s.value = 1; s.dispatchEvent(new Event('input'))")
    assert page.locator("#k-phi").inner_text() == "1.00"
    assert page.locator("#k-fid").inner_text() == "0.99998" and page.locator("#k-leak").inner_text() == "8e-5"
    page.click("#s-freq")
    assert page.locator("#k-leak").inner_text().endswith("%")                               # leakage of a few percent
    assert errors == []
    page.close()


def test_repeater_lab_shows_the_crossover_and_a_useful_long_chain(browser, server):
    page, errors = open_page(browser, server + "/repeater/")
    page.wait_for_function("document.body.dataset.ready === '1'", timeout=30000)
    page.click("#preset-mars")
    assert page.locator("#k-cross").inner_text() == "393 km"                               # crossover_distance_km(3, 1.0)
    assert "too noisy" in page.locator("#k-verdict").inner_text()                           # faster than direct, F <= 2/3
    assert page.locator("#k-best").inner_text().startswith("none")                         # best_useful_chain(393, 1) is None
    assert page.locator("#k-tmin").inner_text() == "2.29 s"                                 # minimum_useful_memory_s(393)
    page.click("#preset-purify")                                                            # 600 km, 10 s, one elementary round
    assert page.locator("#k-fid").inner_text() == "0.678" and "chain wins" in page.locator("#k-verdict").inner_text()
    assert page.locator("#k-cost").inner_text() == "547"
    page.click("#preset-good")
    assert page.locator("#k-fid").inner_text() == "0.869" and "chain wins" in page.locator("#k-verdict").inner_text()
    page.evaluate("const s = document.getElementById('tt'); s.value = 1; s.dispatchEvent(new Event('input'))")
    run = page.evaluate("({ end: QLLRepeaterLab.run.end, last: QLLRepeaterLab.run.events.at(-1) })")
    assert run["last"]["kind"] == "swap" and run["last"]["span"] == 16 and run["last"]["t"] == run["end"]
    assert errors == []
    page.close()
