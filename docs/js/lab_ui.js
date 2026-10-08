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
    if (unit === "s") return v < 1e-6 ? `${+(v * 1e9).toFixed(1)} ns` : `${+v.toFixed(2)} s`;
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
        `<div class="fm">${esc(l.formula)}</div>${l.sub ? `<div class="sb">= ${esc(l.sub)}</div>` : ""}<div class="vl">→ ${esc(l.value)}</div></div>`);
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
  return { esc, el, fmtValue, sliders, terminal, print, download, copy, usd, buildPanel, markStage, partCard, registerApp, GH };
});
