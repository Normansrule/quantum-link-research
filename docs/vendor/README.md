# Vendored libraries

Copied from the pinned npm packages so the website works without a CDN (and so the headless page tests can run offline). Minified with esbuild where the package ships only unminified modules; the code is otherwise unchanged.

| Library | Version | Licence | Files |
|---|---|---|---|
| three.js | 0.186.1 | MIT (`three/LICENSE`) | `three/three.module.js`, `three/three.core.js`, `three/addons/controls/OrbitControls.js` |
| GSAP + ScrollTrigger | 3.15.0 | GreenSock standard licence, free for this use (header in each file; https://gsap.com/standard-license) | `gsap/gsap.min.js`, `gsap/ScrollTrigger.min.js` |
| KaTeX | 0.18.9 | MIT (`katex/LICENSE`) | `katex/katex.min.js`, `katex/katex.min.css`, `katex/contrib/auto-render.min.js`, `katex/fonts/*.woff2` |

To update: `npm pack <pkg>@<version>`, copy the same files, and change the version here and in CREDITS.md.
