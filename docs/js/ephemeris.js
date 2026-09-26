/* Earth–Mars Kepler mean-element ephemeris, a line-by-line port of qll/space/ephemeris.py.
   Works in the browser (window.QLLEphemeris) and in Node (module.exports) so tests can compare it to Python.
   Elements come from docs/site_data.json at runtime; the defaults below are the same J2000 values. */
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory();
  else root.QLLEphemeris = factory();
})(typeof self !== "undefined" ? self : this, function () {
  const C = 299792458.0;
  const DEFAULTS = {
    earth: { a_au: 1.00000011, e: 0.01671022, L_deg: 100.46435, varpi_deg: 102.94719, period_days: 365.256 },
    mars: { a_au: 1.52366231, e: 0.09341233, L_deg: 355.45332, varpi_deg: 336.04084, period_days: 686.98 },
    au_m: 149597870700.0,
  };
  let EL = { earth: DEFAULTS.earth, mars: DEFAULTS.mars };
  let AU = DEFAULTS.au_m;

  function configure(data) {
    if (data && data.elements) EL = data.elements;
    if (data && data.au_m) AU = data.au_m;
  }
  function keplerE(M, e) {
    let E = e < 0.8 ? M : Math.PI;
    for (let i = 0; i < 50; i++) {
      const dE = (E - e * Math.sin(E) - M) / (1 - e * Math.cos(E));
      E -= dE;
      if (Math.abs(dE) < 1e-12) break;
    }
    return E;
  }
  function positionAU(el, tDays) {
    const d2r = Math.PI / 180;
    const L = el.L_deg * d2r + (2 * Math.PI * tDays) / el.period_days;
    const varpi = el.varpi_deg * d2r;
    const M = (((L - varpi) % (2 * Math.PI)) + 2 * Math.PI) % (2 * Math.PI);
    const E = keplerE(M, el.e);
    const nu = 2 * Math.atan2(Math.sqrt(1 + el.e) * Math.sin(E / 2), Math.sqrt(1 - el.e) * Math.cos(E / 2));
    const r = el.a_au * (1 - el.e * Math.cos(E));
    const th = nu + varpi;
    return [r * Math.cos(th), r * Math.sin(th)];
  }
  const earth = (t) => positionAU(EL.earth, t);
  const mars = (t) => positionAU(EL.mars, t);
  function rangeM(t) {
    const [ex, ey] = earth(t), [mx, my] = mars(t);
    return Math.hypot(mx - ex, my - ey) * AU;
  }
  const oneWaySeconds = (t) => rangeM(t) / C;
  function sepDeg(t) {
    const [ex, ey] = earth(t), [mx, my] = mars(t);
    const sx = -ex, sy = -ey, tx = mx - ex, ty = my - ey;
    const c = (sx * tx + sy * ty) / (Math.hypot(sx, sy) * Math.hypot(tx, ty));
    return (Math.acos(Math.max(-1, Math.min(1, c))) * 180) / Math.PI;
  }
  function l4(t) {
    const [ex, ey] = earth(t); const a = Math.atan2(ey, ex) + Math.PI / 3; const r = Math.hypot(ex, ey);
    return [r * Math.cos(a), r * Math.sin(a)];
  }
  function l5(t) {
    const [ex, ey] = earth(t); const a = Math.atan2(ey, ex) - Math.PI / 3; const r = Math.hypot(ex, ey);
    return [r * Math.cos(a), r * Math.sin(a)];
  }
  return { configure, keplerE, earth, mars, l4, l5, rangeM, oneWaySeconds, sepDeg, C, get AU() { return AU; } };
});
