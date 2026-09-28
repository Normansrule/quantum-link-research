"""Record animated GIFs of the website for the README (GitHub cannot run the pages' JavaScript).
Needs:  pip install playwright pillow && python -m playwright install chromium
Usage:  python scripts/record_site.py [anim_mars ...]   # writes docs/figures/anim_*.gif (all nine by default)
Frames are captured from a local server in headless Chromium, so the animation is the real page, not a mock-up."""
from __future__ import annotations

import functools
import http.server
import os
import threading
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS, OUT = ROOT / "docs", ROOT / "docs" / "figures"

SHOTS = {
    # name: (path, setup JS, clip (x, y, w, h) or None, frames, ms between frames)
    "anim_hero": ("/", "", None, 24, 140),
    "anim_mars": ("/mars/", "document.getElementById('play').click(); document.getElementById('speed').value='40'",
                  "#orbit", 30, 120),
    "anim_teleport": ("/teleport/", None, None, 0, 0),   # handled specially: one frame per step
    "anim_interference": ("/", "document.documentElement.style.scrollBehavior='auto'; document.querySelector('#slit-canvas').scrollIntoView({block:'center'})",
                          "#slit-canvas", 20, 130),
    # worldmonitor-style dashboard: two years of light time, blackouts, and the key buffer at 80 days per second
    "anim_monitor": ("/monitor/", "document.getElementById('speed').value='80'",   # the page auto-plays
                     None, 28, 150),
    # the coupler lab's CZ player, scrubbed frame by frame so the recording does not depend on the frame rate
    "anim_coupler": ("/coupler/", None, "#cz", 36, 110),
    # the repeater lab's chain: one sampled run of a 16-segment, 1000 km chain, scrubbed frame by frame
    "anim_repeater": ("/repeater/", "document.getElementById('preset-good').click()", "section.grid >> nth=0", 40, 110),
    # the QEC lab: three decoded d = 5 shots at 8 % stepped through errors, syndrome, matching, correction
    "anim_qec": ("/qec/", None, ".p.w7", 0, 700),
    # the link budget's stream as Mars recedes from closest approach toward conjunction
    "anim_budget": ("/budget/", None, "section.grid >> nth=0", 36, 120),
}


def serve():
    h = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(DOCS))
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a):
            pass
    h = functools.partial(Quiet, directory=str(DOCS))
    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), h)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd, f"http://127.0.0.1:{httpd.server_address[1]}"


def save_gif(frames, path, ms, width=640):
    from PIL import Image
    import numpy as np
    rgb = []
    for f in frames:
        f.seek(0)
        im = Image.open(f).convert("RGB")
        rgb.append(im.resize((width, round(im.height * width / im.width)), Image.LANCZOS))
    tallest = max(im.height for im in rgb)            # an element that changed height: pad every frame to the tallest
    for k, im in enumerate(rgb):
        if im.height != tallest:
            canvas = Image.new("RGB", (width, tallest), im.getpixel((2, im.height - 2)))
            canvas.paste(im, (0, 0))
            rgb[k] = canvas
    # one shared palette for every frame, so unchanged pixels stay identical; then every pixel that did not change since
    # the previous frame is written as a transparent index, which LZW compresses to almost nothing
    # palette from first, middle, and last frames together, by octree, so small saturated curves keep their colour
    sheet = Image.new("RGB", (rgb[0].width, 3 * rgb[0].height))
    for j, im in enumerate((rgb[0], rgb[len(rgb) // 2], rgb[-1])):
        sheet.paste(im, (0, j * rgb[0].height))
    pal = sheet.quantize(colors=160, method=Image.Quantize.FASTOCTREE)
    idx = [np.array(im.quantize(palette=pal, dither=Image.Dither.NONE)) for im in rgb]
    TRANSPARENT = 255
    ims = []
    for k, a in enumerate(idx):
        b = a.copy()
        if k:
            b[a == idx[k - 1]] = TRANSPARENT
        im = Image.fromarray(b.astype(np.uint8), mode="P")
        im.putpalette(pal.getpalette())
        ims.append(im)
    ims[0].save(path, save_all=True, append_images=ims[1:], duration=ms, loop=0, disposal=1, transparency=TRANSPARENT,
                optimize=False)
    print(f"wrote {path.relative_to(ROOT)}  {path.stat().st_size / 1e6:.2f} MB")


def main() -> None:
    import io
    import sys
    only = set(sys.argv[1:])
    from playwright.sync_api import sync_playwright

    httpd, base = serve()
    args = ["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"]
    with sync_playwright() as p:
        try:
            b = p.chromium.launch(args=args)
        except Exception:
            b = p.chromium.launch(args=args, executable_path=os.environ.get("QLL_CHROMIUM", "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"))
        for name, (path, js, clip, n, ms) in SHOTS.items():
            if only and name not in only:
                continue
            page = b.new_page(viewport={"width": 1280, "height": 720})
            page.goto(base + path, wait_until="commit")
            page.wait_for_function("document.readyState === 'complete'", timeout=60000)
            page.wait_for_timeout(1500)
            frames = []
            if name == "anim_teleport":
                for k in range(6):
                    page.evaluate(f"document.documentElement.style.scrollBehavior='auto'; document.querySelector('[data-step=\"{k}\"]').scrollIntoView({{block:'center'}})")
                    page.wait_for_timeout(1400 if k != 4 else 4300)
                    frames += [io.BytesIO(page.screenshot(timeout=120000))] * 4
                save_gif(frames, OUT / f"{name}.gif", 400)
                page.close(); continue
            if name == "anim_budget":
                page.add_style_tag(content=".p::before{animation:none!important}.aurora{animation:none!important}")
                page.wait_for_function("document.body.dataset.ready === '1'", timeout=60000)
                page.evaluate("document.documentElement.style.scrollBehavior='auto'; window.scrollTo(0, document.querySelector('#flow').getBoundingClientRect().top + scrollY - 120)")
                page.wait_for_timeout(1500)                                       # let the particle stream fill
                for k in range(n):
                    page.evaluate(f"QLLBudgetPage.setDay({538 + round(k * 340 / (n - 1))})")
                    page.wait_for_timeout(90)
                    frames.append(io.BytesIO(page.locator(clip).screenshot(timeout=120000)))
                save_gif(frames, OUT / f"{name}.gif", ms)
                page.close(); continue
            if name == "anim_qec":
                page.set_viewport_size({"width": 1280, "height": 1400})     # the lattice panel is taller than 720 px
                page.add_style_tag(content=".p::before{animation:none!important}.aurora{animation:none!important}")
                page.wait_for_function("document.body.dataset.ready === '1'", timeout=60000)
                page.evaluate("document.documentElement.style.scrollBehavior='auto'; window.scrollTo(0, document.querySelector('.p.w7').offsetTop - 70)")
                shots = page.evaluate("QLLQecLab.data.codes['5'].shots['0.08'].map((s) => [s.errors.length, s.logical_error])")
                pick = [i for i, (e, f) in enumerate(shots) if e >= 2 and not f][:2] + [i for i, (e, f) in enumerate(shots) if f][:1]
                for k in pick:
                    for st in range(4):
                        page.evaluate(f"QLLQecLab.set(5, '0.08', {k}, {st})"); page.wait_for_timeout(80)
                        shot = io.BytesIO(page.locator(clip).screenshot(timeout=120000))
                        frames += [shot] * (3 if st == 3 else 2)
                save_gif(frames, OUT / f"{name}.gif", ms)
                page.close(); continue
            if name == "anim_repeater":
                page.add_style_tag(content=".p::before{animation:none!important}.aurora{animation:none!important}")
                page.evaluate(js); page.wait_for_timeout(400)
                page.evaluate("document.documentElement.style.scrollBehavior='auto'; document.querySelector('#chain').scrollIntoView({block:'start'}); window.scrollBy(0, -90)")
                for k in range(n):
                    page.evaluate(f"const s = document.getElementById('tt'); s.value = {k / (n - 1)}; s.dispatchEvent(new Event('input'))")
                    page.wait_for_timeout(40)
                    frames.append(io.BytesIO(page.locator(clip).screenshot(timeout=120000)))
                frames += [frames[-1]] * 10
                save_gif(frames, OUT / f"{name}.gif", ms)
                page.close(); continue
            if name == "anim_coupler":
                page.add_style_tag(content=".p::before{animation:none!important}.aurora{animation:none!important}")   # static borders: a smaller GIF
                page.evaluate("document.documentElement.style.scrollBehavior='auto'; window.scrollTo(0, document.querySelector('#cz').offsetTop - 70)")
                page.wait_for_timeout(800)
                for k in range(n):
                    page.evaluate(f"const s = document.getElementById('tt'); s.value = {k / (n - 1)}; s.dispatchEvent(new Event('input'))")
                    page.wait_for_timeout(60)
                    frames.append(io.BytesIO(page.locator(clip).screenshot(timeout=120000)))
                frames += [frames[-1]] * 8                                   # hold on the finished gate
                save_gif(frames, OUT / f"{name}.gif", ms)
                page.close(); continue
            if js:
                page.evaluate(js); page.wait_for_timeout(1200)
            target = page.locator(clip) if clip else page
            for _ in range(n):
                frames.append(io.BytesIO(target.screenshot(timeout=120000)))
                page.wait_for_timeout(ms)
            save_gif(frames, OUT / f"{name}.gif", ms)
            page.close()
        b.close()
    httpd.shutdown()


if __name__ == "__main__":
    main()
