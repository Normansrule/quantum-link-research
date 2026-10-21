// The landing page's spacetime diagram. Time runs down the page and distance runs across, scaled so light travels at
// exactly 45 degrees: one light time between Earth and Mars is as tall as the gap between their worldlines is wide.
// A message leaves Earth at the top; as the reader scrolls, the light front advances, and each protocol's arrival on
// Mars lights up when the front reaches it (1 trip for banked key, 3 for key made on demand, 5 for a fresh TCP + TLS
// connection; trip counts from docs/js/latency_core.js). The distance comes from the tested Kepler ephemeris
// (docs/js/ephemeris.js, held to qll/space/ephemeris.py by tests/test_site.py). With reduced motion the whole diagram
// is drawn at once and nothing follows the scroll.
(function () {
  const E = window.QLLEphemeris, L = window.QLLLatency;
  const fig = document.getElementById("cone-fig"), dateIn = document.getElementById("cone-date");
  if (!fig || !E) return;
  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const NS = "http://www.w3.org/2000/svg";
  const TRIPS = L ? L.SECURITY_TRIPS : { "banked key": 1, "QKD on demand": 3, "TCP + TLS 1.3, new connection": 5 };
  const J2000 = Date.UTC(2000, 0, 1, 12, 0, 0);
  const out = (id, v) => { const el = document.getElementById(id); if (el) el.textContent = v; };
  const dur = (s) => s < 60 ? `${s.toFixed(1)} s` : s < 3600 ? `${Math.floor(s / 60)} min ${String(Math.round(s % 60)).padStart(2, "0")} s` : `${(s / 3600).toFixed(2)} h`;
  const short = (s) => s < 60 ? `${s.toFixed(0)} s` : `${(s / 60).toFixed(1)} min`;

  let geo = null, svg = null, lit = null, cone = null, nowLine = null, nowText = null, events = [];

  function el(name, attrs, parent, text) {
    const n = document.createElementNS(NS, name);
    for (const k in attrs) n.setAttribute(k, attrs[k]);
    if (text !== undefined) n.textContent = text;
    if (parent) parent.appendChild(n);
    return n;
  }
  // a few words per line, by an estimate of glyph width; good enough for short captions in a known face
  function wrap(text, px, size) {
    const per = Math.max(8, Math.floor(px / (size * 0.53))), lines = [];
    let cur = "";
    for (const w of text.split(" ")) { if ((cur + " " + w).trim().length > per) { lines.push(cur.trim()); cur = w; } else cur += " " + w; }
    if (cur.trim()) lines.push(cur.trim());
    return lines;
  }

  function build() {
    const day = (dateIn && dateIn.valueAsNumber) ? (dateIn.valueAsNumber + 43200000 - J2000) / 864e5 : (Date.now() - J2000) / 864e5;
    const lt = E.oneWaySeconds(day), rangeAu = E.rangeM(day) / E.AU;
    out("cone-range", `${rangeAu.toFixed(2)} au`);
    out("cone-floor", dur(lt));
    out("cone-tls", dur(lt * TRIPS["TCP + TLS 1.3, new connection"]));

    const W = Math.max(300, Math.round(fig.clientWidth || 520));
    const narrow = W < 460;
    const left = narrow ? 44 : 64, labelW = narrow ? 128 : 196, gap = 16;
    const D = W - left - labelW - gap, top = 64, trips = 5, H = top + trips * D + 40;
    geo = { W, H, D, top, xE: left, xM: left + D, lt };
    fig.replaceChildren();
    svg = el("svg", { viewBox: `0 0 ${W} ${H}`, width: W, height: H, role: "img", "aria-labelledby": "cone-desc" }, fig);
    el("desc", { id: "cone-desc" }, svg,
      `Spacetime diagram for ${new Date(J2000 + day * 864e5).toISOString().slice(0, 10)}: Earth and Mars are ${rangeAu.toFixed(2)} astronomical units apart, ` +
      `so light takes ${dur(lt)} one way. A banked key is readable on Mars after one trip (${dur(lt)}), a key made on demand after three ` +
      `(${dur(3 * lt)}), and a fresh TCP plus TLS 1.3 connection after five (${dur(5 * lt)}).`);
    const { xE, xM } = geo;
    // axes and time ticks: one tick per round number of minutes, at least 56 px apart
    el("line", { x1: xE, y1: top - 8, x2: xE, y2: H - 16, class: "wl" }, svg);
    el("line", { x1: xM, y1: top - 8, x2: xM, y2: H - 16, class: "wl" }, svg);
    el("text", { x: xE, y: 22, "text-anchor": "middle", class: "wlabel" }, svg, "Earth");
    el("text", { x: xM, y: 22, "text-anchor": "middle", class: "wlabel" }, svg, "Mars");
    el("text", { x: xM, y: 40, "text-anchor": "middle", class: "wsub" }, svg, `${rangeAu.toFixed(2)} au`);
    el("text", { x: 0, y: top - 18, class: "tl" }, svg, "time ↓");
    const pxPerMin = D / (lt / 60), steps = [1, 2, 5, 10, 15, 20, 30, 60];
    const step = steps.find((m) => m * pxPerMin >= 56) || 60;
    for (let m = 0; top + m * pxPerMin <= H - 30; m += step) {
      const y = top + m * pxPerMin;
      el("line", { x1: xE - 6, y1: y, x2: xE, y2: y, class: "tick" }, svg);
      el("text", { x: xE - 10, y: y + 4, "text-anchor": "end", class: "tl" }, svg, m === 0 ? "0" : `${m}′`);
    }
    // the light cone of the emission event, clipped to the figure, and the zigzag of trips between the worldlines
    const clip = el("clipPath", { id: "cone-clip" }, el("defs", {}, svg));
    el("rect", { x: xE, y: 0, width: D, height: H }, clip);   // the cone toward Mars; its other half points away from it
    cone = el("polygon", { class: "cone", "clip-path": "url(#cone-clip)", points: "" }, svg);
    const pts = [[xE, top]];
    for (let k = 1; k <= trips; k++) pts.push([k % 2 ? xM : xE, top + k * D]);
    const d = pts.map((p, i) => (i ? "L" : "M") + p[0] + " " + p[1]).join(" ");
    el("path", { d, class: "ray future" }, svg);
    lit = el("path", { d, class: "ray" }, svg);
    geo.len = Math.SQRT2 * trips * D;
    lit.style.strokeDasharray = `${geo.len} ${geo.len}`;
    el("circle", { cx: xE, cy: top, r: 5, class: "ev hit" }, svg);
    el("text", { x: xE + 12, y: top - 8, class: "esub" }, svg, "message leaves Earth");
    // the three arrivals on Mars, each with its caption in the label column
    const NAMES = [["banked key", "Banked key", "readable on Mars on the floor itself"],
                   ["QKD on demand", "Key made on demand (QKD)", "the key exchange needs a round trip first"],
                   ["TCP + TLS 1.3, new connection", "Fresh TCP + TLS 1.3", "handshakes before the first readable byte"]];
    events = NAMES.map(([key, title, sub]) => {
      const n = TRIPS[key], y = top + n * D, g = el("g", { class: "evg" }, svg);
      el("circle", { cx: xM, cy: y, r: 5, class: "ev" }, g);
      const x = xM + gap;
      el("text", { x, y: y - 2, class: "elabel" }, g, title);
      let yy = y + 16;
      el("text", { x, y: yy, class: "esub floor" }, g, `${n} trip${n > 1 ? "s" : ""} · ${dur(n * lt)}`);
      for (const line of wrap(sub, labelW, 12.5)) { yy += 16; el("text", { x, y: yy, class: "esub" }, g, line); }
      g.style.transition = reduce ? "none" : "opacity 220ms cubic-bezier(.23,1,.32,1)";
      return { y, g, dot: g.querySelector("circle") };
    });
    nowLine = el("line", { x1: 0, x2: W - labelW - gap / 2, y1: top, y2: top, class: "now" }, svg);
    nowText = el("text", { x: xE + 8, y: top - 4, class: "nowt" }, svg, "");
    draw();
  }

  // where "now" is: the middle of the viewport, measured down the diagram, in light time
  function draw() {
    if (!geo) return;
    const { top, D, H, xE, xM, W, lt, len } = geo;
    let y = H;
    if (!reduce) { const r = svg.getBoundingClientRect(); y = innerHeight * 0.55 - r.top; }
    y = Math.max(top, Math.min(top + 5 * D, y));
    const t = y - top;                                  // px of light time since emission
    lit.style.strokeDashoffset = String(len - Math.SQRT2 * t);
    cone.setAttribute("points", `${xE},${top} ${xE + t},${y} ${xE - t},${y}`);
    const show = !reduce && t > 0 && t < 5 * D;
    nowLine.setAttribute("y1", y); nowLine.setAttribute("y2", y); nowLine.style.opacity = show ? 1 : 0;
    nowText.setAttribute("y", y - 6); nowText.style.opacity = show ? 1 : 0;
    nowText.textContent = `t = ${short(t / D * lt)}`;
    for (const e of events) { const hit = y >= e.y - 0.5; e.g.style.opacity = hit ? 1 : 0.4; e.dot.classList.toggle("hit", hit); }
  }

  let raf = 0;
  const schedule = () => { if (!raf) raf = requestAnimationFrame(() => { raf = 0; draw(); }); };
  if (dateIn) {
    if (!dateIn.value) dateIn.valueAsNumber = Date.UTC(new Date().getUTCFullYear(), new Date().getUTCMonth(), new Date().getUTCDate());
    dateIn.addEventListener("change", build);
  }
  let w = 0;
  new ResizeObserver(() => { const nw = Math.round(fig.clientWidth); if (nw !== w) { w = nw; build(); } }).observe(fig);
  if (!reduce) { addEventListener("scroll", schedule, { passive: true }); addEventListener("resize", schedule); }
  build();
})();
