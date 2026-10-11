/* The messenger keyed by the program's links, for the messenger lab, line for line the tested Python:
     qll/link/keyed_messaging.py     supplies from the twins, spending per policy, the bank, latency
     qll/app/key_bank.py             the sequent-peak bank
     qll/link/authentication.py      Wegman-Carter tags over GF(2^127 - 1)
   tests/test_lab_js.py compares every function here with the Python. Needs lab_twin.js and lab_outdoor.js. */
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory(require("./lab_twin.js"), require("./lab_outdoor.js"));
  else root.QLLMessenger = factory(root.QLLTwin, root.QLLOutdoor);
})(typeof self !== "undefined" ? self : this, function (T, O) {
  "use strict";
  const C = 299792458, AES_KEY_BITS = 256, TAG_BITS = 127, P127 = (1n << 127n) - 1n, BLOCK = 15;
  const POLICIES = ["one-time pad", "QKD-keyed AES-256-GCM", "hybrid ML-KEM + QKD", "conventional ECDHE + AES (today)"];
  const SECURITY = {
    "one-time pad": ["information-theoretic: unbreakable with any computer, if the key is truly secret and never reused", "shannon1949"],
    "QKD-keyed AES-256-GCM": ["computational: 128-bit security against a quantum computer; the key is never sent in public", "grover1996"],
    "hybrid ML-KEM + QKD": ["secure if either the quantum key or the lattice problem holds", "nist2024fips203"],
    "conventional ECDHE + AES (today)": ["recorded traffic can be decrypted later by a large quantum computer", "shor1997"],
  };
  const WAKING = (h) => h >= 8 && h < 22, NIGHT = [22, 23, 0, 1, 2, 3, 4, 5], PASS_HOUR = 1;
  function bitsPerMessage(policy, msgBytes = 200, rekeyEvery = 100) {
    if (policy === "one-time pad") return 8 * msgBytes + TAG_BITS;
    if (policy === "QKD-keyed AES-256-GCM" || policy === "hybrid ML-KEM + QKD") return AES_KEY_BITS / rekeyEvery;
    if (policy === "conventional ECDHE + AES (today)") return 0;
    throw new Error("unknown policy");
  }
  let cache = null;
  function sources() {
    if (cache) return cache;
    const c = T.twoRoomConfig({}), roomsBps = T.expectedSession(c).key_bits / (c.n_pulses / c.pulse_rate_hz);
    const p = { distance_m: 1000, receiver: O.RECEIVERS.spad }, r = O.predict(p), bldgBps = r.key_bits / (r.config.n_pulses / r.config.pulse_rate_hz);
    const passBits = O.passSummary(O.PRESETS.micius).key_bits, hrs = [...Array(24).keys()];
    const out = {
      "two rooms (P10)": hrs.map(() => roomsBps * 3600),
      "two buildings at night, 1 km": hrs.map((h) => (NIGHT.includes(h) ? bldgBps * 3600 : 0)),
      "one satellite pass a night": hrs.map((h) => (h === PASS_HOUR ? passBits : 0)),
      "a Mars lander (key loaded before launch)": hrs.map(() => 0),
    };
    cache = Object.fromEntries(Object.entries(out).map(([k, v]) => [k, { hourly_bits: v, bits_per_day: v.reduce((a, b) => a + b, 0) }]));
    return cache;
  }
  function demandHourly(messagesPerDay, bitsEach) { const per = messagesPerDay * bitsEach / 14; return [...Array(24).keys()].map((h) => (WAKING(h) ? per : 0)); }
  function sequentPeak(supply, demand, cycles = 2) {
    let S = 0, K = 0;
    for (let c = 0; c < cycles; c++) for (let i = 0; i < supply.length; i++) { S = Math.max(0, S + demand[i] - supply[i]); K = Math.max(K, S); }
    return K;
  }
  function plan(source, policy, o = {}) {
    const q = Object.assign({ messages_per_day: 500, msg_bytes: 200, rekey_every: 100, distance_m: 10, preloaded_bits: 0 }, o);
    const src = sources()[source], b = bitsPerMessage(policy, q.msg_bytes, q.rekey_every), daily = q.messages_per_day * b;
    const sustainable = daily <= src.bits_per_day + 1e-9, net = daily - src.bits_per_day, ow = q.distance_m / C;
    return { bits_per_message: b, supply_bits_per_day: src.bits_per_day, demand_bits_per_day: daily, messages_per_day_max: b > 0 ? src.bits_per_day / b : Infinity,
      sustainable, bank_bits: sustainable ? sequentPeak(src.hourly_bits, demandHourly(q.messages_per_day, b)) : Infinity,
      preload_days: net <= 0 ? Infinity : q.preloaded_bits / net, one_way_s: ow, round_trip_s: 2 * ow, security: SECURITY[policy][0], security_ref: SECURITY[policy][1] };
  }
  // ------------------------------------------------------------------------------------- Wegman-Carter tags
  function polyHash(key, bytes) {
    key = BigInt(key);
    if (!(key > 0n && key < P127)) throw new Error("hash key must lie in (0, p)");
    let acc = BigInt(bytes.length) % P127;
    for (let i = 0; i < bytes.length; i += BLOCK) {
      let m = 0n; for (const x of bytes.slice(i, i + BLOCK)) m = (m << 8n) | BigInt(x);
      acc = (acc * key + m + 1n) % P127;
    }
    return (acc * key) % P127;
  }
  const tag = (key, pad, bytes) => (polyHash(key, bytes) + BigInt(pad)) % P127;
  const bigFromBytes = (b) => { let v = 0n; for (const x of b) v = (v << 8n) | BigInt(x); return v; };
  // ------------------------------------------------------------------------------------- the terminal
  const f = (x, d = 4) => (!isFinite(x) ? (x > 0 ? "unlimited" : String(x)) : Math.abs(x) >= 1e5 || (x !== 0 && Math.abs(x) < 1e-3) ? x.toExponential(d - 1) : (+x.toPrecision(d)).toString());
  const S = (label, formula, sub, value, ref, why) => ({ label, formula, sub, value, ref, why });
  function bitsText(b) { if (!isFinite(b)) return "no bank is big enough"; const B = b / 8; return B >= 999.5e9 ? `${f(B / 1e12, 3)} TB` : B >= 999.5e6 ? `${f(B / 1e9, 3)} GB` : B >= 999.5e3 ? `${f(B / 1e6, 3)} MB` : B >= 999.5 ? `${f(B / 1e3, 3)} kB` : `${f(B, 3)} bytes`; }
  function daysText(d) { return !isFinite(d) ? "forever" : d >= 365 ? `${f(d / 365.25, 3)} years` : `${f(d, 3)} days`; }
  function steps(source, policy, o = {}) {
    const q = Object.assign({ messages_per_day: 500, msg_bytes: 200, rekey_every: 100, distance_m: 10, preloaded_bits: 0 }, o), r = plan(source, policy, q);
    const ref = { "two rooms (P10)": "qll/link/two_room.py", "two buildings at night, 1 km": "qll/link/outdoor_link.py", "one satellite pass a night": "qll/link/satellite_pass.py", "a Mars lander (key loaded before launch)": "qll/link/keyed_messaging.py" }[source];
    const L = [
      S("Key from the link", "Σ hourly key", source, `${bitsText(r.supply_bits_per_day)} a day`, ref, "The link's twin says how much secret key it distils each day, and when."),
      S("Key per message", { "one-time pad": "8b + 127", "QKD-keyed AES-256-GCM": "256 / n", "hybrid ML-KEM + QKD": "256 / n", "conventional ECDHE + AES (today)": "0" }[policy], `b = ${q.msg_bytes} bytes, n = ${q.rekey_every}`, `${f(r.bits_per_message)} bits`,
        policy === "one-time pad" ? "vernam1926" : policy === "conventional ECDHE + AES (today)" ? "shor1997" : "nist2007sp800-38d",
        policy === "one-time pad" ? "A one-time pad uses one key bit per message bit, plus a fresh pad for the authentication tag." : policy === "conventional ECDHE + AES (today)" ? "Today's messengers make keys from public-key maths, not from a link." : "A 256-bit session key encrypts many messages; only the key comes from the link."),
      S("Your demand", "messages × key each", `${f(q.messages_per_day)} a day`, `${bitsText(r.demand_bits_per_day)} a day`, "qll/link/keyed_messaging.py", "Messages are sent between 08:00 and 22:00."),
    ];
    if (r.supply_bits_per_day > 0) L.splice(2, 0, S("Messages the link can key", "key per day / key per message", "", `${f(r.messages_per_day_max)} a day`, "qll/link/keyed_messaging.py", "More than this and the messenger runs out of key."));
    if (r.supply_bits_per_day > 0) L.push(S("Bank that never refuses", "K = max S_t, S_t = max(0, S_{t−1} + d_t − s_t)", "", bitsText(r.bank_bits), "loucks2017", "Key arrives on the link's schedule and is spent by day; the bank bridges the gap."));
    if (r.supply_bits_per_day === 0) L.push(S("Preloaded key lasts", "bank / daily use", bitsText(q.preloaded_bits), daysText(r.preload_days), "qll/link/keyed_messaging.py", "With no link, key loaded before launch is all there is; a one-time pad spends it fastest."));
    L.push(S("Latency", "d / c each way", `d = ${f(q.distance_m / 1000)} km`, `${f(r.one_way_s, 3)} s one way, ${f(r.round_trip_s, 3)} s round trip`, "qll/channels/light_time_delay.py", "Banked key adds no delay, and nothing removes the light time."));
    L.push(S("Security", policy, "", r.security, r.security_ref, "What protects the message if someone records everything on the wire."));
    return L;
  }
  return { POLICIES, SECURITY, AES_KEY_BITS, TAG_BITS, P127, bitsPerMessage, sources, demandHourly, sequentPeak, plan, polyHash, tag, bigFromBytes, bitsText, daysText, steps };
});
