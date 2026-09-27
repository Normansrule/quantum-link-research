# Credits

## Visual techniques on the website
The website is plain HTML, CSS, and JavaScript with no build step, so GitHub Pages serves it directly. Its design draws on the open-source projects below. **No source code was copied from any of them.** Every effect was re-implemented from scratch, and the only third-party code loaded is the three pinned libraries listed in the next section. The table records what each project contributed and where to see it.

| Project | Licence | What it contributed | Where to see it |
|---|---|---|---|
| [react-bits](https://github.com/DavidHDev/react-bits) (David Haz) | see repository | animated gradient text, blur-in reveals, spotlight cards that follow the pointer | landing-page headline, every `.card` |
| [Magic UI](https://github.com/magicuidesign/magicui) | MIT | bento grid, number tickers, aurora background, **AnimatedBeam**, **Marquee** | numbers section, flagships, the `qll` stack diagram, the landmark marquee, the coupler and repeater labs' rotating border beams and the repeater lab's arcs |
| [Animate UI](https://animate-ui.com/) | see site | staggered entrances and easing curves | section reveals (GSAP timings) |
| [motion-primitives](https://github.com/ibelick/motion-primitives) (ibelick) | MIT | minimal glass panels, restrained motion | panel styling across all pages |
| [WebGL-Fluid-Simulation](https://github.com/PavelDoGreat/WebGL-Fluid-Simulation) (Pavel Dobryakov) | MIT | raw WebGL fragment shaders over a full canvas, driven by the pointer | the **interference lab** (`docs/js/interference.js`): the shader sums the two slit waves exactly |
| [folio-2019](https://github.com/brunosimon/folio-2019) (Bruno Simon) | MIT | treating the landing page as a 3-D scene to explore | the three.js hero (`docs/js/hero.js`) |
| [GSAP](https://github.com/greensock/GSAP) | GSAP standard licence (free) | used directly: ScrollTrigger, tweens | reveals, tickers, and the step triggers of the teleportation explainer |
| [llm-viz](https://github.com/bbycroft/llm-viz) (Brendan Bycroft) | see repository | explaining a system by letting the reader step through it with the real internal state on screen | the **teleportation explainer** (`docs/teleport/`): eight exact amplitudes per step; the **coupler lab** (`docs/coupler/`): the CZ gate's populations, levels, and phase at every nanosecond; the **repeater lab** (`docs/repeater/`): every herald, stored pair, and swap of one sampled run |
| [transformer-explainer](https://github.com/poloclub/transformer-explainer) (Polo Club) | MIT | a scroll-and-step explainer with a fixed visual panel and prose alongside | the explainer's sticky-stage layout |
| [gods-eye-view](https://github.com/bilawalsidhu/gods-eye-view) (Bilawal Sidhu) | see repository | a live "situation" view of a real model's state | the hero's live range / light-time / Sun-angle strip |
| [worldmonitor](https://github.com/koala73/worldmonitor) (koala73) | see repository | a dashboard of status tiles, timelines, and an event feed | the **link monitor** (`docs/monitor/`) |
| [Remotion](https://github.com/remotion-dev/remotion) | Remotion licence (company licence above a size threshold) | the idea of rendering the product itself into video for the README; realised instead with Playwright frame capture (`scripts/record_site.py`), which needs no licence review | the animated GIFs in the README |

## README images
GitHub cannot run a page's JavaScript, so the README moves in two other ways, both generated from the tested code:
- **Animated SVG** (`scripts/make_readme_art.py`, SMIL animation, which GitHub renders in `<img>`): the numbers card re-implements Magic UI's **NumberTicker** and **BentoGrid** with react-bits-style rotating "shine" borders; the stack diagram re-implements Magic UI's **AnimatedBeam**; the landmark strip re-implements Magic UI's **Marquee**; the memory-versus-round-trip chart follows llm-viz and transformer-explainer in putting the model's real internal numbers on screen. Every animation starts from the finished picture as its static default, so a renderer without animation (or a reader with reduced motion) still sees the true values, and `tests/test_readme_art.py` checks those values against `docs/site_data.json`.
- **Recorded GIFs** (`scripts/record_site.py`): the landing page, Mars simulator, teleportation explainer, interference lab, link monitor, coupler lab, and repeater lab, captured frame by frame in headless Chromium and stored as transparent frame differences over one shared palette, so a recording costs a few hundred kilobytes. This is the Remotion idea (render the product itself into video) done with Playwright; the monitor recording is the worldmonitor-style dashboard running at 80 days per second through two conjunctions.
- **Typeset equations**: `readme_equations.svg` is drawn by matplotlib's mathtext with glyphs as paths, so it looks the same in every viewer; the LaTeX source stays in the README under a disclosure.
- **Badges**: `scripts/build_status.py` writes shields.io endpoint JSON to `docs/badges/`, so the test, requirement, and reference counts in the badges are the ones in `docs/status.json`.

## Libraries used by the website (vendored in `docs/vendor/`, pinned)
- [three.js](https://threejs.org) 0.186.1 (MIT): the hero scene and the Bloch sphere.
- [GSAP](https://gsap.com) 3.15.0 with ScrollTrigger: scroll reveals, tickers, and explainer steps.
- [KaTeX](https://katex.org) 0.18.9 (MIT): equations.

They are copied from the npm packages into `docs/vendor/` (three.js minified with esbuild) with their licences, so the site needs no CDN; `docs/vendor/README.md` says how to update them.

## Physics and data
Every number on the site comes from `scripts/build_site_data.py`, which calls the tested `qll` functions. The JavaScript models are ports of tested Python, and `tests/test_site.py` checks each one against its original:
- the ephemeris agrees with `qll/space/ephemeris.py` to 10⁻¹⁵;
- the teleportation state vector agrees with Qiskit to 10⁻¹²;
- the key-buffer rule agrees with `qll.app.messenger.required_buffer_bytes` exactly.

Scientific sources are listed in [docs/references.md](docs/references.md).
