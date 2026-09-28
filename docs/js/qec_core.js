/* Surface-code bookkeeping for the QEC lab, a port of the parts of qll/circuits/surface_code_capacity.py the page needs
   to check itself: the syndrome of a set of X errors on the rotated code's Z plaquettes, and the parity of a pattern
   on the logical Z (column 0). The matching itself was done by PyMatching in Python; the page verifies every shot. */
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory();
  else root.QLLQec = factory();
})(typeof self !== "undefined" ? self : this, function () {
  const idx = (d, r, c) => r * d + c;
  function syndrome(d, plaquettes, qubits) {
    const on = new Set(qubits), out = [];
    plaquettes.forEach((pl, k) => { let s = 0; for (const [r, c] of pl) if (on.has(idx(d, r, c))) s ^= 1; if (s) out.push(k); });
    return out;
  }
  const xor = (a, b) => { const s = new Set(a); for (const q of b) s.has(q) ? s.delete(q) : s.add(q); return [...s].sort((x, y) => x - y); };
  const logicalParity = (d, qubits) => qubits.filter((q) => q % d === 0).length % 2;
  function checkShot(d, plaquettes, shot) {
    const syn = syndrome(d, plaquettes, shot.errors), residual = xor(shot.errors, shot.correction);
    return { syndromeMatches: JSON.stringify(syn) === JSON.stringify(shot.defects),
             residualClean: syndrome(d, plaquettes, residual).length === 0,
             logicalError: logicalParity(d, residual) === 1, residual };
  }
  return { syndrome, xor, logicalParity, checkShot };
});
