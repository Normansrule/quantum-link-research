/* The latency floor, a line-by-line port of qll/space/latency_floor.py: the light-time floor between any two sites,
   the delay and stretch of each route that can join them, and the one-way trips that security and teleportation add
   [eberhard1989] [moritz2000] [poletti2013] [handley2018] [rfc8446] [rfc9293]. Works in the browser
   (window.QLLLatency) and in Node, where tests/test_site.py holds it to the Python for every pair of sites. */
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory();
  else root.QLLLatency = factory();
})(typeof self !== "undefined" ? self : this, function () {
  const C = 299792458, R = 6371008.8, GEO = 35786e3, LEO = 550e3, FIBER = 1.47, HOLLOW = 1.003, STRETCH = 1.5;
  const SECURITY_TRIPS = { "banked key": 1, "QKD on demand": 3, "TCP + TLS 1.3, new connection": 5 };
  const TELEPORT_TRIPS = { "banked pairs": 1, "pair sent on demand": 2 };
  const rad = (d) => (d * Math.PI) / 180;
  const onEarth = (s) => s.range_m === null || s.range_m === undefined;

  function centralAngle(a, b) {
    const p1 = rad(a.lat_deg), p2 = rad(b.lat_deg), dp = p2 - p1, dl = rad(b.lon_deg - a.lon_deg);
    const h = Math.sin(dp / 2) ** 2 + Math.cos(p1) * Math.cos(p2) * Math.sin(dl / 2) ** 2;
    return 2 * Math.asin(Math.min(1, Math.sqrt(h)));
  }
  function distances(a, b) {
    if (onEarth(a) && onEarth(b)) {
      const th = centralAngle(a, b);
      return { angle_rad: th, great_circle_m: R * th, chord_m: 2 * R * Math.sin(th / 2) };
    }
    if (onEarth(a) || onEarth(b)) { const r = (onEarth(a) ? b : a).range_m; return { angle_rad: NaN, great_circle_m: r, chord_m: r }; }
    throw new Error("one end must be on Earth");
  }
  function routes(a, b, leo = LEO, stretch = STRETCH) {
    if (!(leo > 0 && stretch >= 1)) throw new Error("the LEO altitude must be positive and the fiber route stretch at least 1");
    const d = distances(a, b), floor = d.great_circle_m / C, out = {};
    const add = (name, len, n, note) => { const t = (n * len) / C; out[name] = { length_m: len, index: n, delay_s: t, stretch: floor > 0 ? t / floor : 1, note }; };
    if (onEarth(a) && onEarth(b)) {
      const th = d.angle_rad, gc = d.great_circle_m;
      add("terrestrial fiber", stretch * gc, FIBER, `n = ${FIBER}, route ${stretch}× the great circle (assumed)`);
      add("hollow-core fiber", stretch * gc, HOLLOW, `n = ${HOLLOW}, same route`);
      add("LEO laser mesh", 2 * leo + (R + leo) * th, 1, `up, across at ${Math.round(leo / 1e3).toLocaleString("en-US")} km, down`);
      const rg = R + GEO, leg = Math.sqrt(R * R + rg * rg - 2 * R * rg * Math.cos(th / 2));
      if (th / 2 < Math.acos(R / rg)) add("geostationary relay", 2 * leg, 1, "up to 35,786 km above the midpoint and down");
    } else add("free space", d.great_circle_m, 1, "the straight line, n = 1");
    return { distances: d, floor_s: floor, chord_floor_s: d.chord_m / C, routes: out };
  }
  function bestRoute(r) { return Object.entries(r.routes).reduce((m, kv) => (kv[1].delay_s < m[1].delay_s ? kv : m)); }
  function messageLatency(t) {
    if (!(Number.isFinite(t) && t >= 0)) throw new Error("route delay must be finite and non-negative");
    const scale = (o) => Object.fromEntries(Object.entries(o).map(([k, n]) => [k, n * t]));
    return { "secure message": scale(SECURITY_TRIPS), "teleported qubit": scale(TELEPORT_TRIPS) };
  }
  function report(a, b, leo, stretch) {
    const r = routes(a, b, leo, stretch), [name, best] = bestRoute(r);
    return { from: a.name, to: b.name, ...r, best: name, best_delay_s: best.delay_s, best_stretch: best.stretch, latency: messageLatency(best.delay_s) };
  }
  return { C, R, GEO, LEO, FIBER, HOLLOW, STRETCH, SECURITY_TRIPS, TELEPORT_TRIPS, centralAngle, distances, routes, bestRoute, messageLatency, report,
    antipodalFloor: () => ({ great_circle_s: (Math.PI * R) / C, chord_s: (2 * R) / C }) };
});
