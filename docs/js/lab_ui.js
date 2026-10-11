/* Shared pieces of the lab pages: the math terminal, parameter sliders, the build panel (stages, bill of materials,
   selected part, commands), and file downloads. Plain DOM, no dependencies. */
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory();
  else root.QLLLabUI = factory();
})(typeof self !== "undefined" ? self : this, function () {
  "use strict";
  const GH = "https://github.com/Normansrule/quantum-link-research/blob/main/";
  const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  const el = (tag, cls, html) => { const e = document.createElement(tag); if (cls) e.className = cls; if (html != null) e.innerHTML = html; return e; };

  function fmtValue(v, unit) {
    if (unit === "Hz") return v >= 1e6 ? `${+(v / 1e6).toFixed(2)} MHz` : v >= 1e3 ? `${+(v / 1e3).toFixed(1)} kHz` : `${v} Hz`;
    if (unit === "s") {
      const a = Math.abs(v), p = (x) => +x.toPrecision(3);
      return v === 0 ? "0 s" : a < 1e-6 ? `${p(v * 1e9)} ns` : a < 1e-3 ? `${p(v * 1e6)} µs` : a < 1 ? `${p(v * 1e3)} ms` : a <= 300 ? `${+v.toFixed(2)} s` : a < 7200 ? `${p(v / 60)} min` : `${p(v / 3600)} h`;
    }
    if (unit === "m" && Math.abs(v) >= 1e4) return Math.abs(v) >= 1e9 ? `${(v / 149597870700).toFixed(2)} AU` : `${+(v / 1e3).toPrecision(4)} km`;
    if (Math.abs(v) >= 1e5) return v.toExponential(2);
    if (v !== 0 && Math.abs(v) < 1e-3) return v.toExponential(1);
    return `${+v.toPrecision(4)}${unit ? " " + unit : ""}`;
  }
  /* Sliders. A log slider moves its position linearly in log10(value). */
  function sliders(host, specs, values, onInput, onFocus) {
    host.innerHTML = "";
    const set = {};
    for (const s of specs) {
      const row = el("label", "lab-slider"); row.dataset.key = s.key;
      const name = el("span", "nm", esc(s.label)), val = el("b", "vl"), inp = el("input");
      inp.type = "range"; inp.name = s.key;
      const toPos = (v) => (s.log ? Math.log10(Math.max(v, 1e-300)) : v), fromPos = (x) => (s.log ? Math.pow(10, x) : x);
      inp.min = toPos(s.lo); inp.max = toPos(s.hi); inp.step = s.log ? (toPos(s.hi) - toPos(s.lo)) / 200 : s.step;
      const show = () => { val.textContent = fmtValue(values[s.key], s.unit); };
      set[s.key] = (v) => { values[s.key] = v; inp.value = toPos(v); show(); };
      set[s.key](values[s.key] ?? s.value);
      inp.addEventListener("input", () => { let v = fromPos(+inp.value); if (!s.log) v = Math.round(v / s.step) * s.step; values[s.key] = +v.toPrecision(10); show(); onInput(s.key); });
      for (const ev of ["focus", "pointerenter"]) inp.addEventListener(ev, () => onFocus && onFocus(s.key));
      for (const ev of ["blur", "pointerleave"]) inp.addEventListener(ev, () => onFocus && onFocus(""));
      const hd = el("span", "hd"); hd.append(name, val); row.append(hd, inp); host.append(row);
    }
    return set;
  }

  /* The terminal: a prompt line (the Python that reproduces the numbers), then numbered lines of
     label, formula, substitution, value, and reference. `animate` types them in; otherwise changed values flash. */
  let typing = 0;
  function terminal(host, prompt, lines, opt = {}) {
    const prev = host._vals || [];
    const out = [`<div class="tp"><span class="ps">$</span> ${esc(prompt)}</div>`];
    lines.forEach((l, i) => {
      const chg = prev[i] !== undefined && prev[i] !== String(l.value) ? " chg" : "";
      out.push(`<div class="tl${chg}" style="--i:${i}"><span class="no">[${String(i + 1).padStart(2, "0")}]</span> <span class="lb">${esc(l.label)}</span>` +
        `<span class="rf">${l.ref ? (l.ref.includes("/") ? `<a href="${GH + esc(l.ref)}" target="_blank" rel="noopener">${esc(l.ref.split("/").pop())}</a>` : "[" + esc(l.ref) + "]") : ""}</span>` +
        `<div class="fm">${esc(l.formula)}</div>${l.sub ? `<div class="sb">= ${esc(l.sub)}</div>` : ""}<div class="vl">→ ${esc(l.value)}</div>` +
        `${l.why ? `<div class="wy">${esc(l.why)}</div>` : ""}</div>`);
    });
    if (opt.tail) out.push(`<div class="tt">${opt.tail}</div>`);
    host.innerHTML = out.join("");
    host._vals = lines.map((l) => String(l.value));
    if (opt.animate) {
      const id = ++typing, rows = host.querySelectorAll(".tl, .tt");
      rows.forEach((r) => r.classList.add("hide"));
      rows.forEach((r, i) => setTimeout(() => { if (id === typing) r.classList.remove("hide"); }, 35 * i));
    }
  }
  function print(host, html, cls = "") { const d = el("div", "tx " + cls, html); host.append(d); host.scrollTop = host.scrollHeight; return d; }

  function download(name, text, type = "text/csv") {
    const url = URL.createObjectURL(new Blob([text], { type })); const a = el("a"); a.href = url; a.download = name; document.body.append(a); a.click();
    setTimeout(() => { URL.revokeObjectURL(url); a.remove(); }, 1000);
  }
  function copy(text, btn) {
    const done = () => { if (btn) { const t = btn.textContent; btn.textContent = "Copied"; setTimeout(() => (btn.textContent = t), 1200); } };
    if (navigator.clipboard) navigator.clipboard.writeText(text).then(done, done); else done();
  }
  const usd = (x) => (x === 0 ? "$0" : "$" + Math.round(x).toLocaleString("en-US"));

  /* The build panel: stage stepper, bill of materials, selected-part card, procedure, commands, claim. */
  function buildPanel(host, tier, state, onStage) {
    const parts = tier.parts.filter((p) => !["room", "hallway"].includes(p.kind));
    const stageList = tier.stages.map((s, i) => `<li data-stage="${i + 1}"><b>${i + 1}. ${esc(s[0])}</b><span>${esc(s[1])}</span></li>`).join("");
    const rows = tier.bom.map((r, i) => {
      const who = parts.filter((p) => p.bom === i).map((p) => `<button class="chip" data-part="${esc(p.id)}">${esc(p.label)}</button>`).join("");
      return `<tr><td>${esc(r[0])}<div class="who">${who}</div></td><td>${esc(r[1])}</td><td class="num">${r[3] ? usd(r[2]) + "–" + usd(r[3]) : "free"}</td></tr>`;
    }).join("");
    const [lo, hi] = tier.bom_total;
    const cmds = Object.entries(tier.commands).map(([k, v]) => `<div class="cmd"><span class="k">${esc(k)}</span><code>${esc(v)}</code><button class="cp" data-copy="${esc(v)}">Copy</button></div>`).join("");
    host.innerHTML = `
      <div class="bp-grid">
        <div><h3>Build it, step by step</h3><ol class="stages">${stageList}</ol>
          <p class="muted small">Procedure: <a href="${GH + esc(tier.procedure)}" target="_blank" rel="noopener">${esc(tier.procedure)}</a></p></div>
        <div><h3>Selected part</h3><div class="partcard" id="partcard"><p class="muted">Click a part in the 3D view, or a name in the bill of materials.</p></div>
          <h3>Run it</h3>${cmds}<p class="claim">${esc(tier.claim)}</p></div>
      </div>
      <h3>Bill of materials <span class="muted small">(planning prices; ${esc(tier.cost)})</span></h3>
      <div class="tablewrap"><table class="bom"><thead><tr><th>Item and the parts it pays for</th><th>For</th><th class="num">Cost</th></tr></thead><tbody>${rows}
        <tr class="tot"><td>Total of the rows</td><td></td><td class="num">${hi ? usd(lo) + "–" + usd(hi) : "free"}</td></tr></tbody></table></div>`;
    host.querySelectorAll(".stages li").forEach((li) => li.addEventListener("click", () => onStage(+li.dataset.stage)));
    host.querySelectorAll("[data-copy]").forEach((b) => b.addEventListener("click", () => copy(b.dataset.copy, b)));
    host.querySelectorAll("[data-part]").forEach((b) => b.addEventListener("click", () => state.pick(tier.parts.find((p) => p.id === b.dataset.part))));
    markStage(host, state.stage);
  }
  function markStage(host, n) { host.querySelectorAll(".stages li").forEach((li) => li.classList.toggle("on", +li.dataset.stage <= n)); }
  function partCard(host, tier, p, sliderSpecs) {
    const card = host.querySelector("#partcard"); if (!card) return;
    if (!p) { card.innerHTML = `<p class="muted">Click a part in the 3D view, or a name in the bill of materials.</p>`; return; }
    const row = p.bom != null ? tier.bom[p.bom] : null, st = p.stage ? tier.stages[p.stage - 1] : null;
    const sl = p.param ? sliderSpecs.find((s) => s.key === p.param) : null;
    card.innerHTML = `<h4>${esc(p.label)}</h4><p>${esc(p.note || "")}</p>
      <dl>${row ? `<dt>Paid by</dt><dd>${esc(row[0])} (${row[3] ? usd(row[2]) + "–" + usd(row[3]) : "free"})</dd>` : `<dt>Paid by</dt><dd>owned or shared</dd>`}
      ${st ? `<dt>Added at</dt><dd>stage ${p.stage}: ${esc(st[0])}</dd>` : ""}
      ${sl ? `<dt>Twin knob</dt><dd><a href="#" data-focus="${esc(sl.key)}">${esc(sl.label)}</a></dd>` : ""}
      <dt>Where</dt><dd>x ${p.pos[0].toFixed(2)} m, z ${p.pos[2].toFixed(2)} m</dd></dl>`;
    const a = card.querySelector("[data-focus]");
    if (a) a.addEventListener("click", (e) => { e.preventDefault(); const r = document.querySelector(`.lab-slider[data-key="${sl.key}"] input`); if (r) { r.focus(); r.scrollIntoView({ block: "center", behavior: "smooth" }); } });
  }
  function registerApp() {
    if ("serviceWorker" in navigator && location.protocol !== "file:") {
      const base = location.pathname.replace(/lab\/.*$/, "lab/");
      navigator.serviceWorker.register(base + "sw.js", { scope: base }).catch(() => {});
    }
  }
  /* A small SVG chart kit in the site's palette: every chart is labelled in words, not only in color. */
  const C = { ink: "#e8eef8", muted: "#93a1b8", faint: "#5b6780", grid: "rgba(148,170,210,.16)", cyan: "#5ef2e0", blue: "#5ea8ff", violet: "#a78bfa", warm: "#ff8a4c", green: "#45e0a0", gold: "#fde68a" };
  const svg = (w, h, body, label) => `<svg viewBox="0 0 ${w} ${h}" role="img" aria-label="${esc(label || "")}" class="chart">${body}</svg>`;
  const txt = (x, y, t, o = {}) => `<text x="${x}" y="${y}" fill="${o.fill || C.muted}" font-size="${o.size || 11}" text-anchor="${o.anchor || "start"}" font-weight="${o.weight || 400}" dominant-baseline="${o.base || "auto"}">${esc(t)}</text>`;
  function bars(rows, opt = {}) {
    /* rows: {label, value, max?, color?, note?}; horizontal bars on a shared scale, value printed at the end */
    const W = opt.width || 460, rowH = 30, lw = opt.labelWidth || 170, H = rows.length * rowH + 26, max = opt.max || Math.max(...rows.map((r) => r.value), 1e-9);
    let b = "";
    (opt.marks || []).forEach((m) => { const x = lw + (W - lw - 60) * m.at / max; b += `<line x1="${x}" x2="${x}" y1="4" y2="${H - 18}" stroke="${m.color || C.gold}" stroke-dasharray="4 3"/>` + txt(x, H - 6, m.label, { anchor: "middle", size: 10, fill: m.color || C.gold }); });
    rows.forEach((r, i) => {
      const y = 6 + i * rowH, w = Math.max(0, (W - lw - 60) * Math.min(r.value, max) / max);
      b += txt(lw - 8, y + 13, r.label, { anchor: "end", fill: C.ink }) + `<rect x="${lw}" y="${y + 3}" width="${W - lw - 60}" height="16" rx="4" fill="${C.grid}"/>` +
        `<rect x="${lw}" y="${y + 3}" width="${w}" height="16" rx="4" fill="${r.color || C.cyan}"/>` + txt(lw + w + 6, y + 15, r.text ?? (+r.value.toPrecision(3)).toString(), { fill: C.ink, size: 11 });
      if (r.note) b += txt(lw, y + 29, r.note, { size: 9, fill: C.faint });
    });
    return svg(W, H, b, opt.title);
  }
  function grid(M, opt = {}) {
    /* a labelled matrix as colored cells: blue negative, cyan positive, numbers printed */
    const n = M.length, m = M[0].length, cell = opt.cell || 54, lx = opt.labelWidth || 34, ty = 26, W = lx + m * cell + 8, H = ty + n * cell + 8, rl = opt.rows || [], cl = opt.cols || [];
    let b = "";
    cl.forEach((c, j) => (b += txt(lx + j * cell + cell / 2, 16, c, { anchor: "middle", fill: C.ink, weight: 600 })));
    M.forEach((row, i) => {
      b += txt(lx - 8, ty + i * cell + cell / 2, rl[i] || "", { anchor: "end", base: "middle", fill: C.ink, weight: 600 });
      row.forEach((v, j) => {
        const a = Math.min(1, Math.abs(v) / (opt.scale || 1)), col = v >= 0 ? `rgba(94,242,224,${0.08 + 0.75 * a})` : `rgba(94,168,255,${0.08 + 0.75 * a})`;
        b += `<rect x="${lx + j * cell + 2}" y="${ty + i * cell + 2}" width="${cell - 4}" height="${cell - 4}" rx="6" fill="${col}" stroke="${C.grid}"/>` +
          txt(lx + j * cell + cell / 2, ty + i * cell + cell / 2, Math.abs(v) < 5e-4 ? "0" : v.toFixed(opt.digits ?? 3), { anchor: "middle", base: "middle", fill: a > 0.55 ? "#04111f" : C.ink, size: 11, weight: 600 });
      });
    });
    return svg(W, H, b, opt.title);
  }
  function gauge(value, opt = {}) {
    /* a 0..1 scale with a threshold, a measured value, and an optional certified lower bound */
    const W = opt.width || 460, H = 70, x0 = 16, x1 = W - 16, X = (v) => x0 + (x1 - x0) * Math.max(0, Math.min(1, v));
    let b = `<rect x="${x0}" y="22" width="${x1 - x0}" height="14" rx="7" fill="${C.grid}"/>` +
      `<rect x="${x0}" y="22" width="${X(opt.threshold ?? 0.5) - x0}" height="14" rx="7" fill="rgba(255,138,76,.28)"/>` +
      `<line x1="${X(opt.threshold ?? 0.5)}" x2="${X(opt.threshold ?? 0.5)}" y1="14" y2="44" stroke="${C.warm}" stroke-width="2"/>` +
      txt(X(opt.threshold ?? 0.5), 58, opt.thresholdLabel || "classical limit", { anchor: "middle", fill: C.warm, size: 10 });
    if (opt.lower !== undefined) b += `<rect x="${x0}" y="24" width="${X(opt.lower) - x0}" height="10" rx="5" fill="${opt.lower > (opt.threshold ?? 0.5) ? C.green : C.faint}"/>` + txt(X(opt.lower), 12, `certified ≥ ${opt.lower.toFixed(3)}`, { anchor: X(opt.lower) > W - 90 ? "end" : X(opt.lower) < 90 ? "start" : "middle", fill: C.green, size: 10 });
    b += `<circle cx="${X(value)}" cy="29" r="7" fill="${C.cyan}" stroke="#04111f" stroke-width="2"/>` + txt(X(value), 58, `${opt.valueLabel || "value"} ${value.toFixed(3)}`, { anchor: X(value) > W - 80 ? "end" : X(value) < 80 ? "start" : "middle", fill: C.cyan, size: 10 });
    return svg(W, H, b, opt.title);
  }
  function line(xs, series, opt = {}) {
    /* series: {ys, color, label}; optional marker {x, y, label}; log y when opt.logY */
    const W = opt.width || 460, H = opt.height || 200, L = 46, R = 12, T = 12, B = 34, ys = series.flatMap((s) => s.ys).filter((v) => isFinite(v) && (!opt.logY || v > 0));
    const ymin = opt.ymin ?? (opt.logY ? Math.max(1e-9, Math.min(...ys)) : Math.min(0, ...ys)), ymax = opt.ymax ?? Math.max(...ys, ymin * 10, 1e-9);
    const fy = (v) => (opt.logY ? Math.log10(Math.max(v, ymin)) : v), Y = (v) => T + (H - T - B) * (1 - (fy(v) - fy(ymin)) / (fy(ymax) - fy(ymin) || 1)), X = (x) => L + (W - L - R) * (x - xs[0]) / (xs.at(-1) - xs[0] || 1);
    let b = `<line x1="${L}" x2="${W - R}" y1="${H - B}" y2="${H - B}" stroke="${C.faint}"/><line x1="${L}" x2="${L}" y1="${T}" y2="${H - B}" stroke="${C.faint}"/>`;
    (opt.yticks || []).forEach((v) => (b += `<line x1="${L}" x2="${W - R}" y1="${Y(v)}" y2="${Y(v)}" stroke="${C.grid}"/>` + txt(L - 6, Y(v), opt.yfmt ? opt.yfmt(v) : String(v), { anchor: "end", base: "middle", size: 10 })));
    (opt.xticks || []).forEach((v) => (b += txt(X(v), H - B + 14, String(v), { anchor: "middle", size: 10 })));
    if (opt.xlabel) b += txt((L + W - R) / 2, H - 4, opt.xlabel, { anchor: "middle", size: 10, fill: C.ink });
    if (opt.ylabel) b += txt(4, T + 4, opt.ylabel, { size: 10, fill: C.ink });
    series.forEach((s) => {
      const pts = xs.map((x, i) => [X(x), s.ys[i]]).filter(([, v]) => isFinite(v) && (!opt.logY || v > 0)).map(([x, v]) => `${x.toFixed(1)},${Y(v).toFixed(1)}`);
      if (pts.length) b += `<polyline points="${pts.join(" ")}" fill="none" stroke="${s.color || C.cyan}" stroke-width="2"/>`;
    });
    (opt.vlines || []).forEach((v) => (b += `<line x1="${X(v.x)}" x2="${X(v.x)}" y1="${T}" y2="${H - B}" stroke="${v.color || C.gold}" stroke-dasharray="4 3"/>` + txt(X(v.x) + 3, T + 10, v.label || "", { fill: v.color || C.gold, size: 10 })));
    if (opt.marker && isFinite(opt.marker.y) && (!opt.logY || opt.marker.y > 0)) b += `<circle cx="${X(opt.marker.x)}" cy="${Y(opt.marker.y)}" r="5" fill="${C.gold}" stroke="#04111f" stroke-width="2"/>` + txt(X(opt.marker.x) + 8, Y(opt.marker.y) - 8, opt.marker.label || "", { fill: C.gold, size: 10 });
    (opt.legend || series).forEach((s, i) => (b += `<rect x="${W - R - 150}" y="${T + i * 14}" width="10" height="3" fill="${s.color}"/>` + txt(W - R - 136, T + i * 14 + 4, s.label || "", { size: 10, fill: C.ink })));
    return svg(W, H, b, opt.title);
  }
  function spacetime(opt = {}) {
    /* A spacetime diagram: places across (0 = Alice, 1 = Bob), time upward in units of the light time over the whole
       distance, so light travels along 45-degree-ish lines. nodes [{x, label}], bands [{x, t0, t1, color, label}] for
       a memory holding its half, lines [{pts: [[x, t]...], color, dash, label}], events [{x, t, label, color}], and
       cone {x, t}: the future light cone of an event, shaded, outside which nothing it does can be felt. */
    const W = opt.width || 460, H = opt.height || 250, L = 52, R = 16, T = 14, B = 30, t0 = opt.tmin ?? -0.5, t1 = opt.tmax ?? 1.6;
    const X = (x) => L + (W - L - R) * (0.1 + 0.8 * x), Y = (t) => T + (H - T - B) * (1 - (t - t0) / (t1 - t0));
    let b = `<line x1="${L}" x2="${L}" y1="${T}" y2="${H - B}" stroke="${C.faint}"/>` + txt(8, T + 4, opt.ylabel || "time ↑", { size: 10, fill: C.ink });
    (opt.tticks || []).forEach((v) => (b += `<line x1="${L}" x2="${W - R}" y1="${Y(v)}" y2="${Y(v)}" stroke="${C.grid}"/>` + txt(L - 6, Y(v), opt.tfmt ? opt.tfmt(v) : String(v), { anchor: "end", base: "middle", size: 10 })));
    if (opt.cone) {
      const c = opt.cone, top = t1, dx = top - c.t;
      b += `<polygon points="${X(c.x)},${Y(c.t)} ${X(Math.min(1.12, c.x + dx))},${Y(top)} ${X(Math.max(-0.12, c.x - dx))},${Y(top)}" fill="${C.gold}" opacity=".07"/>`;
      b += txt(X(c.x + 0.2 * Math.min(dx, 1)), Y(c.t + 0.92 * dx), "inside the light cone", { size: 9, fill: C.gold });
    }
    (opt.nodes || []).forEach((n) => (b += `<line x1="${X(n.x)}" x2="${X(n.x)}" y1="${T}" y2="${H - B}" stroke="${C.faint}" stroke-dasharray="2 4"/>` + txt(X(n.x), H - B + 16, n.label, { anchor: "middle", size: 11, fill: C.ink })));
    (opt.bands || []).forEach((m) => {
      const ya = Y(Math.max(t0, m.t0)), yb = Y(Math.min(t1, m.t1));
      b += `<rect x="${X(m.x) - 5}" y="${yb}" width="10" height="${Math.max(0, ya - yb)}" rx="4" fill="${m.color || C.violet}" opacity="${m.opacity ?? 0.55}"/>`;
      if (m.label) b += txt(X(m.x) + (m.x > 0.5 ? -9 : 9), (ya + yb) / 2, m.label, { anchor: m.x > 0.5 ? "end" : "start", base: "middle", size: 9, fill: m.color || C.violet });
    });
    (opt.lines || []).forEach((l) => {
      b += `<polyline points="${l.pts.map(([x, t]) => `${X(x).toFixed(1)},${Y(t).toFixed(1)}`).join(" ")}" fill="none" stroke="${l.color || C.gold}" stroke-width="2" ${l.dash ? `stroke-dasharray="${l.dash}"` : ""}/>`;
      if (l.label) { const [xa, ta] = l.pts[0], [xb, tb] = l.pts.at(-1); b += txt(X((xa + xb) / 2) + 6, Y((ta + tb) / 2) - 6, l.label, { size: 9, fill: l.color || C.gold }); }
    });
    (opt.events || []).forEach((e) => (b += `<circle cx="${X(e.x)}" cy="${Y(e.t)}" r="5" fill="${e.color || C.gold}" stroke="#04111f" stroke-width="2"/>` +
      txt(X(e.x) + (e.x > 0.5 ? -9 : 9), Y(e.t) + (e.below ? 12 : -8), e.label, { anchor: e.x > 0.5 ? "end" : "start", size: 10, fill: e.color || C.gold })));
    return svg(W, H, b, opt.title || "spacetime diagram");
  }
  function explainToggle(btn, term) {
    const set = (on) => { term.classList.toggle("explain", on); btn.setAttribute("aria-pressed", String(on)); btn.textContent = on ? "Hide plain-language notes" : "Explain each line"; };
    btn.addEventListener("click", () => set(!term.classList.contains("explain"))); set(true);
  }
  return { esc, el, fmtValue, sliders, terminal, print, download, copy, usd, buildPanel, markStage, partCard, registerApp, GH, bars, grid, gauge, line, spacetime, explainToggle, C };
});
