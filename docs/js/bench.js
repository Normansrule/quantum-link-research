// The optical bench: the main experiment (protocol P10, the two-room single-photon link) drawn as a top-down laser
// table you can run. Alice's 405 nm laser fires weak pulses (μ photons on average) through a polarizer; most are lost
// in the hallway; the few that reach Bob meet a 50:50 beamsplitter that picks his basis at random, then a polarizing
// beamsplitter and two of four SiPM (silicon photomultiplier) detectors. Every probability comes from the tested
// planning model in docs/js/lab_twin.js (twoRoomPredict and expectedSession, held to qll/link/two_room.py and
// qll/link/expected_session.py by tests/test_lab_js.py); the bench draws pulses from those probabilities, so every
// count here is SIMULATED, never measured. Flights are slowed about 10⁸ times: a real pulse crosses 10 m in 33 ns.
(function () {
  const host = document.getElementById("bench-table");
  if (!host) return;
  const T = window.QLLTwin;
  const $ = (id) => document.getElementById(id);
  const verdict = $("bench-verdict");
  if (!T) { verdict.className = "bench-verdict state error"; verdict.textContent = "The link model (docs/js/lab_twin.js) did not load, so the bench cannot run."; return; }
  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const NS = "http://www.w3.org/2000/svg";
  const el = (name, attrs, parent, text) => { const n = document.createElementNS(NS, name); for (const k in attrs) n.setAttribute(k, attrs[k]); if (text !== undefined) n.textContent = text; if (parent) parent.appendChild(n); return n; };

  // ---------------------------------------------------------------- the table, drawn once (units: about 2 mm)
  const W = 760, H = 380, Y = 200;
  const svg = el("svg", { viewBox: `0 0 ${W} ${H}`, role: "img", "aria-labelledby": "bench-desc" }, $("bench-table"));
  el("desc", { id: "bench-desc" }, svg, "Top view of the two-room link: in room A a 405 nm laser, an attenuator, and a polarizer; a free-space path through the hallway; in room B a 50:50 beamsplitter that sends each photon to the rectilinear (+) or diagonal (×) analyzer, each a polarizing beamsplitter with two detectors. A separate fiber carries only the classical channel.");
  const holes = [];
  for (let x = 10; x < W; x += 20) for (let y = 10; y < H; y += 20) holes.push(`M${x - 1.2} ${y}a1.2 1.2 0 1 0 2.4 0a1.2 1.2 0 1 0 -2.4 0`);
  el("path", { d: holes.join(""), class: "holes" }, svg);
  el("rect", { x: 14, y: 30, width: 268, height: 300, rx: 4, class: "room" }, svg);
  el("rect", { x: 470, y: 30, width: 276, height: 300, rx: 4, class: "room" }, svg);
  el("text", { x: 272, y: 320, "text-anchor": "end", class: "roomt" }, svg, "Room A · Alice");
  el("text", { x: 480, y: 320, class: "roomt" }, svg, "Room B · Bob");
  el("text", { x: 376, y: Y - 14, "text-anchor": "middle", class: "partt" }, svg, "hallway · 10 m, drawn short");
  // beams: Alice's line, Bob's two arms
  el("path", { d: `M110 ${Y}H560 M560 ${Y}H700 M560 ${Y}V60 M560 120H700 M650 ${Y}V290`, class: "beam" }, svg);
  el("path", { d: `M60 ${Y + 40}V350H700V${Y + 110}`, class: "fiber" }, svg);
  el("text", { x: 376, y: 368, "text-anchor": "middle", class: "partt" }, svg, "fiber · classical channel only (bases, never bits)");
  const part = (x, y, w, h, label, cls = "part", ly) => { el("rect", { x: x - w / 2, y: y - h / 2, width: w, height: h, rx: 2, class: cls }, svg); if (label) el("text", { x, y: ly ?? y + h / 2 + 14, "text-anchor": "middle", class: "partt" }, svg, label); };
  part(70, Y, 70, 26, "405 nm laser");
  part(145, Y, 8, 34, "attenuator", "opt", Y + 32);
  part(200, Y, 8, 34, "polarizer", "opt", Y - 24);
  part(250, Y, 14, 14, "", "part");                                    // iris
  el("text", { x: 250, y: Y + 26, "text-anchor": "middle", class: "partt" }, svg, "iris");
  // Bob: the 50:50 beamsplitter (a cube seen from above, its diagonal drawn) and the two analyzers
  const cube = (x, y, label, ly) => { el("rect", { x: x - 12, y: y - 12, width: 24, height: 24, class: "opt" }, svg); el("path", { d: `M${x - 12} ${y + 12}L${x + 12} ${y - 12}`, class: "beam", style: "opacity:.8" }, svg); el("text", { x, y: ly, "text-anchor": "middle", class: "partt" }, svg, label); };
  cube(560, Y, "50:50 BS", Y + 30);
  cube(650, Y, "PBS +", Y - 18);
  part(560, 160, 30, 6, "half-wave plate 22.5°", "opt", 156);
  svg.lastChild.setAttribute("x", 582); svg.lastChild.setAttribute("text-anchor", "start"); svg.lastChild.setAttribute("y", 163);
  cube(560, 120, "", 0);
  el("text", { x: 540, y: 116, "text-anchor": "end", class: "partt" }, svg, "PBS ×");
  const det = {};
  const D = (key, x, y, label, lx, ly, anchor = "middle") => { det[key] = el("rect", { x: x - 11, y: y - 11, width: 22, height: 22, rx: 3, class: "det" }, svg); el("text", { x: lx, y: ly, "text-anchor": anchor, class: "partt" }, svg, label); };
  D("+0", 715, Y, "H · 0", 715, Y + 26);
  D("+1", 650, 290, "V · 1", 672, 294, "start");
  D("×0", 715, 120, "D · 0", 715, 146);
  D("×1", 560, 50, "A · 1", 582, 54, "start");
  const flights = el("g", {}, svg);

  // ---------------------------------------------------------------- the model and the tally
  const st = { mu: 0.5, loss: 2.0, eve: false, sent: 0, clicks: 0, sifted: 0, errors: 0 };
  let model = null;
  const pct = (x, d = 2) => `${(100 * x).toFixed(d)} %`;
  const big = (n) => n.toLocaleString("en-US");
  function remodel() {
    const parts = { mu: st.mu, free_space_loss_db: st.loss };
    const p = T.twoRoomPredict(parts);
    const q = st.eve ? T.expectedSession(Object.assign(T.twoRoomConfig(parts), { eve_fraction: 1 })).qber : p.expected_qber;
    model = { click: p.click_prob_per_pulse, qber: q };
    $("bench-mu").textContent = st.mu.toFixed(2); $("bench-loss").textContent = `${st.loss.toFixed(1)} dB`;
    $("bench-model").textContent = `Model: a pulse clicks ${pct(model.click)} of the time; sifted error rate ${pct(model.qber)}${st.eve ? " with Eve measuring every pulse" : ""}.`;
  }
  function paint() {
    $("bench-sent").textContent = big(st.sent);
    $("bench-clicks").textContent = big(st.clicks);
    $("bench-clicks-r").textContent = st.sent ? `${pct(st.clicks / st.sent)} of pulses` : "of pulses";
    $("bench-sifted").textContent = big(st.sifted);
    $("bench-qber").textContent = st.sifted ? pct(st.errors / st.sifted, 1) : "—";
    $("bench-qber-r").textContent = st.sifted ? `${big(st.errors)} errors in ${big(st.sifted)}` : "no sifted bits yet";
    if (!st.sent) { verdict.className = "bench-verdict"; verdict.textContent = "No pulses yet. Send one and watch it cross the hallway."; return; }
    if (st.sifted < 200) { verdict.className = "bench-verdict"; verdict.textContent = `Collecting: ${big(st.sifted)} of the 200 sifted bits needed before the error rate means anything.`; return; }
    const qb = st.errors / st.sifted;
    if (qb < 0.11) { verdict.className = "bench-verdict ok"; verdict.textContent = `Error rate ${pct(qb, 1)} is under the 11 % BB84 threshold, so a secret key can be distilled.`; }
    else { verdict.className = "bench-verdict bad"; verdict.textContent = `Error rate ${pct(qb, 1)} is over 11 %: someone is measuring the photons, or the link is broken. Abort; no key.`; }
  }
  // one pulse: Alice's bit and basis, the click, Bob's basis (the 50:50 splitter), and the outcome
  function draw1() {
    const a = { bit: Math.random() < 0.5 ? 0 : 1, basis: Math.random() < 0.5 ? "+" : "×" };
    const click = Math.random() < model.click, bob = Math.random() < 0.5 ? "+" : "×";
    let out = null, sifted = false, err = false;
    if (click) {
      sifted = bob === a.basis;
      err = sifted && Math.random() < model.qber;
      out = sifted ? (err ? 1 - a.bit : a.bit) : (Math.random() < 0.5 ? 0 : 1);
    }
    st.sent++; if (click) st.clicks++; if (sifted) { st.sifted++; if (err) st.errors++; }
    return { click, bob, out, err };
  }
  function flash(r) {
    const d = det[r.bob + r.out];
    d.classList.add(r.err ? "err" : "click");
    setTimeout(() => d.classList.remove("click", "err"), 160);
  }
  // a photon's flight, linear like light: laser → (lost in the hallway | splitter → analyzer → detector)
  function fly(r) {
    if (reduce) { if (r.click) flash(r); return; }
    const dot = el("circle", { r: 3.2, cx: 110, cy: Y, class: "ph" }, flights);
    const path = r.click ? (r.bob === "+" ? [[110, Y], [560, Y], [r.out ? 650 : 715, Y], ...(r.out ? [[650, 290]] : [])]
                                          : [[110, Y], [560, Y], [560, 120], ...(r.out ? [[560, 50]] : [[715, 120]])])
                         : [[110, Y], [300 + Math.random() * 160, Y]];
    const segs = path.slice(1).map((p, i) => Math.hypot(p[0] - path[i][0], p[1] - path[i][1])), total = segs.reduce((a, b) => a + b, 0);
    const speed = 0.7, t0 = performance.now();                      // svg units per millisecond
    (function step(now) {
      let s = (now - t0) * speed;
      if (s >= total) { if (r.click) flash(r); dot.remove(); return; }
      let i = 0; while (s > segs[i]) { s -= segs[i]; i++; }
      const f = s / segs[i], [x0, y0] = path[i], [x1, y1] = path[i + 1];
      dot.setAttribute("cx", x0 + (x1 - x0) * f); dot.setAttribute("cy", y0 + (y1 - y0) * f);
      if (!r.click) dot.classList.toggle("lost", i === 0 && (x0 + (x1 - x0) * f) > 290);
      requestAnimationFrame(step);
    })(t0);
  }
  function send(n) {
    if (n === 1) { fly(draw1()); paint(); return; }
    // a burst: draw every pulse, but show only a stream of them in flight so the table stays readable
    const shown = reduce ? 0 : 48, every = Math.max(1, Math.floor(n / Math.max(shown, 1)));
    let left = n, k = 0;
    (function tick() {
      const batch = Math.min(left, Math.ceil(n / 30));
      for (let i = 0; i < batch; i++) { const r = draw1(); if (shown && k++ % every === 0) fly(r); else if (r.click && Math.random() < 0.05) flash(r); }
      left -= batch; paint();
      if (left > 0) reduce ? tick() : setTimeout(tick, 50);
    })();
  }
  $("bench-one").addEventListener("click", () => send(1));
  $("bench-many").addEventListener("click", () => send(10000));
  $("bench-reset").addEventListener("click", () => { Object.assign(st, { sent: 0, clicks: 0, sifted: 0, errors: 0 }); paint(); });
  const eve = $("bench-eve");
  eve.addEventListener("click", () => { st.eve = !st.eve; eve.setAttribute("aria-pressed", String(st.eve)); Object.assign(st, { sent: 0, clicks: 0, sifted: 0, errors: 0 }); remodel(); paint(); });
  // a new setting is a new session: the tally restarts so it never mixes two configurations
  const clear = () => { Object.assign(st, { sent: 0, clicks: 0, sifted: 0, errors: 0 }); paint(); };
  $("bench-mu-in").addEventListener("input", (e) => { st.mu = +e.target.value; remodel(); clear(); });
  $("bench-loss-in").addEventListener("input", (e) => { st.loss = +e.target.value; remodel(); clear(); });
  remodel(); paint();
  window.QLLBench = { state: st, model: () => model, send };
})();
