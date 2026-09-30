/* The key bank, a line-by-line port of qll/app/key_bank.py: the sequent-peak capacity over two repetitions of a
   periodic record, and the day-by-day bank that serves what it can and fails closed on the rest [loucks2017].
   Works in the browser (window.QLLKeyBank) and in Node, where tests/test_site.py holds it to the Python. */
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory();
  else root.QLLKeyBank = factory();
})(typeof self !== "undefined" ? self : this, function () {
  function sequentPeak(supply, demand, cycles = 2) {
    let S = 0, K = 0;
    for (let c = 0; c < cycles; c++) for (let i = 0; i < supply.length; i++) {
      const d = Array.isArray(demand) ? demand[i] : demand;
      S = Math.max(0, S + d - supply[i]); K = Math.max(K, S);
    }
    return K;
  }
  function simulate(supply, demand, capacity, level0) {
    let L = level0 === undefined ? capacity : level0;
    const level = [], served = [], refused = [];
    for (let i = 0; i < supply.length; i++) {
      const d = Array.isArray(demand) ? demand[i] : demand, use = Math.min(d, L + supply[i]);
      L = Math.min(capacity, L + supply[i] - use); level.push(L); served.push(use); refused.push(d - use);
    }
    const refusedDays = refused.filter((r, i) => r > 1e-9 * (served[i] + r)).length;
    return { level, served, refused, refusedDays };
  }
  const mean = (a) => a.reduce((s, x) => s + x, 0) / a.length;
  return { sequentPeak, simulate, sustainableDemand: mean, AES_KEY_BITS: 256 };
});
