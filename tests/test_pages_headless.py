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
    httpd.shutdown(); httpd.server_close()


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



def test_qec_lab_steps_through_a_decoded_shot_and_checks_itself(browser, server):
    import json as _json
    page, errors = open_page(browser, server + "/qec/")
    page.wait_for_function("document.body.dataset.ready === '1'", timeout=30000)
    data = _json.loads((DOCS / "site_data.json").read_text(encoding="utf-8"))["qec"]
    shots = data["codes"]["5"]["shots"]["0.08"]
    k = next(i for i, s in enumerate(shots) if s["logical_error"])
    page.evaluate(f"QLLQecLab.set(5, '0.08', {k}, 3)")
    assert "Logical error" in page.locator("#banner").inner_text()
    assert "consistent" in page.locator("#k-check").inner_text()
    assert page.locator("#k-fails").inner_text() == str(sum(s["logical_error"] for s in shots))
    j = next(i for i, s in enumerate(shots) if s["errors"] and not s["logical_error"])
    page.evaluate(f"QLLQecLab.set(5, '0.08', {j}, 3)")
    assert "intact" in page.locator("#banner").inner_text()
    page.click("[data-d='7']")
    assert page.locator("#k-n").inner_text() == "49"
    assert errors == []
    page.close()


def test_link_budget_page_matches_the_python_budget(browser, server):
    from qll.systems.mars_budget import MarsLinkDesign, budget
    from dataclasses import replace
    page, errors = open_page(browser, server + "/budget/")
    page.wait_for_function("document.body.dataset.ready === '1'", timeout=30000)
    page.evaluate("QLLBudgetPage.setDay(538)")
    js = page.evaluate("QLLBudgetPage.current.pairs_per_day")
    assert js == pytest.approx(budget(MarsLinkDesign(), 538.0).pairs_per_day, rel=1e-9)
    assert page.evaluate("QLLBudgetPage.current.purity") == pytest.approx(budget(MarsLinkDesign(), 538.0).purity, rel=1e-7)
    assert "useful pairs a day" in page.locator("#k-verdict").inner_text()
    page.evaluate("QLLBudgetPage.setDay(202)")
    assert page.evaluate("QLLBudgetPage.current.purity") == pytest.approx(budget(MarsLinkDesign(), 202.0).purity, rel=1e-7)   # sliders hold log10 values to 5 digits
    page.click("#a-earth")
    assert "No dark sky" in page.locator("#k-verdict").inner_text()                   # Mars is only up in daylight
    assert "sunlight" in page.locator("#sky-note").inner_text()
    assert "daylight" in page.locator("#k-pur").inner_text()
    page.click("#a-space"); page.evaluate("QLLBudgetPage.setDay(538)")
    page.click("#a-relay")
    assert page.evaluate("QLLBudgetPage.current.pairs_per_day") == pytest.approx(
        budget(replace(MarsLinkDesign(), architecture="relay_dual"), 538.0).pairs_per_day, rel=1e-8)   # two 1e-10 legs amplify rounding
    page.click("#a-earth"); page.click("#t-conj")
    assert "Sun is in the way" in page.locator("#k-verdict").inner_text()
    assert page.locator("#mem-rows tr").count() == 6
    from qll.systems.key_ledger import ledger
    L = ledger(MarsLinkDesign(), 1e6)
    page.click("#a-space")
    assert page.locator("#k-bank").inner_text() == f"{L.capacity_bits / 8e6:.1f} MB"          # the page's bank is the Python's
    assert page.locator("#k-refuse").inner_text() == f"{L.refused_days_without_bank} of 780"
    page.evaluate("document.getElementById('dem').value = 7.5; document.getElementById('dem').dispatchEvent(new Event('input'))")
    assert "none is enough" in page.locator("#k-bank").inner_text()
    assert errors == []
    page.close()


def test_systems_page_lists_every_requirement_and_filters(browser, server):
    from qll.systems.traceability import load_matrix
    rows = load_matrix()
    page, errors = open_page(browser, server + "/systems/")
    page.wait_for_function("document.body.dataset.ready === '1'", timeout=30000)
    assert page.locator(".req").count() == len(rows)
    page.click("[data-n='N-1']")
    assert page.locator(".req").count() == sum(r["need"] == "N-1" for r in rows)
    page.click("[data-n='']"); page.fill("#q", "REQ-HW-002")
    assert page.locator(".req").count() == 1
    assert errors == []
    page.close()


def test_operations_console_replays_the_committed_day(browser, server):
    import json
    d = json.loads((DOCS / "link" / "ops.json").read_text(encoding="utf-8"))
    page, errors = open_page(browser, server + "/link/")
    page.wait_for_function("document.getElementById('k-time').textContent !== '\u2014'", timeout=30000)
    assert "simulation" in page.locator(".replay").inner_text().lower()                 # labelled as a replay, not telemetry
    def at(i):
        page.fill("#scrub", str(i)); page.dispatch_event("#scrub", "input")
        page.wait_for_function(f"document.getElementById('k-sess').textContent.startsWith('session {i + 1} ')", timeout=10000)
        return d["sessions"][i]
    for i, s in enumerate(d["sessions"]):
        if s["status"] == "rejected" and s["reason"] == "qber":
            at(i); break
    assert page.locator("#k-status").inner_text().strip() == "rejected"
    assert page.locator("#k-qber").inner_text().strip() == f"{100 * s['qber']:.2f} %"
    assert page.locator("#k-bank").inner_text().strip() == f"{s['bank_keys']:,} keys"
    s = at(len(d["sessions"]) - 1)
    total_refused = sum(r["refused"] for r in d["sessions"])
    assert page.locator("#k-app-s").inner_text().endswith(f"{total_refused:,} refused today")
    assert page.locator("#feed .ev").count() == len(d["log"]) and "fail closed" in page.locator("#feed").inner_text()
    assert page.locator("#plan tbody tr").count() == len(d["plan"])
    page.hover("#c-q", position={"x": 300, "y": 100})
    assert page.locator("#tip").is_visible()
    page.click("#play")                                                                  # replay restarts from the start
    page.wait_for_function("!document.getElementById('k-sess').textContent.startsWith('session 96 ')", timeout=10000)
    assert errors == []
    page.close()


def _lab(browser, server, path):
    page, errors = open_page(browser, server + path)
    page.wait_for_function("document.body.dataset.ready === '1'", timeout=60000)
    return page, errors


def test_lab_gallery_lists_every_experiment_and_its_labs(browser, server):
    from qll.systems.experiment_catalog import CATALOG

    page, errors = _lab(browser, server, "/lab/")
    ids = page.eval_on_selector_all(".exp", "els => els.map(e => e.dataset.id)")
    assert ids == [e.id for e in CATALOG]
    page.click("button[data-st='lab']")
    with_lab = set(page.eval_on_selector_all(".exp", "els => els.map(e => e.dataset.id)"))
    assert {"P10", "T1", "T3", "T4", "P11", "P12", "P13"} <= with_lab and "D01" not in with_lab
    assert not errors, errors
    page.close()                                   # WebGL pages left open starve the next one in software rendering


def test_link_lab_terminal_matches_the_python_twin_and_tiers_change_the_build(browser, server):
    from qll.link import two_room
    from qll.link.expected_session import expected_session

    page, errors = _lab(browser, server, "/lab/link/#two_room")
    e = expected_session(two_room.config())
    term = page.inner_text("#term")
    assert f"{e['key_bits']:,} bits per 10 s session" in term and "[ma2005]" in term
    assert page.evaluate("window.__twin.e.key_bits") == e["key_bits"]
    assert page.evaluate("window.__twin.e.click_prob_per_pulse") == pytest.approx(e["click_prob_per_pulse"], rel=1e-12)
    ids = set(page.evaluate("window.__lab.visibleIds()"))
    assert {"diodeH", "bsAll", "nd", "sipmZ0", "hwp", "fpgaA", "mcA"} <= ids and "eveBS" not in ids
    # a slider moves the twin exactly as the Python does
    page.evaluate("""() => { const r = document.querySelector('.lab-slider[data-key="mu"] input'); r.value = 0.3; r.dispatchEvent(new Event('input')); }""")
    e3 = expected_session(two_room.config(two_room.TwoRoomParts(mu=0.3)))
    assert page.evaluate("window.__twin.e.key_bits") == e3["key_bits"]
    # the build stages reveal the parts in order
    page.evaluate("() => { const s = document.getElementById('stage'); s.value = 2; s.dispatchEvent(new Event('input')); }")
    early = set(page.evaluate("window.__lab.visibleIds()"))
    assert "mcA" in early and "sipmZ0" not in early and "diodeH" not in early
    # a session sampled in the page passes the twin check
    page.click("#run")
    page.wait_for_function("document.getElementById('runlog').dataset.pass !== undefined", timeout=60000)
    assert page.get_attribute("#runlog", "data-pass") == "true"
    assert "pulse,alice_bit,alice_basis,alice_intensity" in page.inner_text("#runlog")
    # the starter tier is a different build with its own math
    page.click("button[data-tier='tier1']")
    page.wait_for_function("window.__lab.visibleIds().includes('servoA')")
    assert "Malus reading, aligned" in page.inner_text("#term") and "sipmZ0" not in page.evaluate("window.__lab.visibleIds()")
    page.click("button[data-tier='tier4']")
    page.wait_for_function("document.getElementById('term').innerText.includes('Bell value')")
    assert page.locator("#build table.bom tbody tr").count() == 6
    assert not errors, errors
    page.close()                                   # WebGL pages left open starve the next one in software rendering


def test_circuits_lab_shows_no_signalling_and_the_teleportation_limits(browser, server):
    from qll.circuits.teleport_cloud import expected_feedforward_fidelity

    page, errors = _lab(browser, server, "/lab/circuits/#collapse")
    assert page.evaluate("window.__twin.metrics[3][1]").startswith("0.00e+0")
    page.click("button[data-tier='teleport']")
    page.wait_for_function("document.getElementById('title').textContent.includes('Teleportation')")
    assert float(page.evaluate("window.__twin.metrics[1][1]")) == pytest.approx(expected_feedforward_fidelity(0.02), abs=1e-4)
    page.select_option("select[data-k='mode']", "no_bits")
    assert float(page.evaluate("window.__twin.metrics[1][1]")) == pytest.approx(0.5, abs=1e-4)
    page.click("button[data-tier='majorana']")
    page.wait_for_function("document.getElementById('title').textContent.includes('Majorana')")
    assert float(page.evaluate("window.__twin.metrics[0][1]")) == pytest.approx(1.0)
    page.select_option("select[data-k='scheme']", "one_bit_best")
    assert float(page.evaluate("window.__twin.metrics[0][1]")) == pytest.approx(2 / 3, abs=1e-4)
    assert not errors, errors
    page.close()                                   # WebGL pages left open starve the next one in software rendering
