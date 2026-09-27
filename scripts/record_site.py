"""Record animated GIFs of the website for the README (GitHub cannot run the pages' JavaScript).
Needs:  pip install playwright pillow && python -m playwright install chromium
Usage:  python scripts/record_site.py [anim_mars ...]   # writes docs/figures/anim_*.gif (all five by default)
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
    rgb = []
    for f in frames:
        f.seek(0)
        im = Image.open(f).convert("RGB")
        rgb.append(im.resize((width, round(im.height * width / im.width)), Image.LANCZOS))
    # one shared palette for every frame, so unchanged pixels stay identical and Pillow stores only the changed box
    pal = rgb[len(rgb) // 2].quantize(colors=96, method=Image.Quantize.MEDIANCUT)
    ims = [im.quantize(palette=pal, dither=Image.Dither.NONE) for im in rgb]
    ims[0].save(path, save_all=True, append_images=ims[1:], duration=ms, loop=0, optimize=True, disposal=2)
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
