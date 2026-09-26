/* Key-buffer model for the link monitor. requiredBufferBytes is a port of qll.app.messenger.required_buffer_bytes
   (checked against Python in tests/test_site.py); simulate() steps the fail-closed messenger day by day. */
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory();
  else root.QLLLink = factory();
})(typeof self !== "undefined" ? self : this, function () {
  const C = 299792458.0;
  function requiredBufferBytes(keyRateBps, distanceM, bytesPerSession, sessionsPerMessage = 1, messagesPerS = 1) {
    const rt = (2 * distanceM) / C;
    return Math.max(0, bytesPerSession * sessionsPerMessage * messagesPerS * rt - (keyRateBps / 8) * rt);
  }
  // One day of the messenger: generate key while the link is up, spend 32 B per message, refuse when empty (fail closed).
  // capBytes: secure key storage is finite (and stored key ages), so the buffer saturates.
  function stepDay(state, { keyRateBps, available, messagesPerDay, bytesPerMessage = 32, capBytes = Infinity }) {
    const gen = available ? (keyRateBps * 86400) / 8 : 0;
    let buffer = Math.min(capBytes, state.buffer + gen), sent = 0, refused = 0;
    const affordable = Math.floor(buffer / bytesPerMessage);
    sent = Math.min(affordable, messagesPerDay); refused = messagesPerDay - sent;
    buffer -= sent * bytesPerMessage;
    return { buffer, sent: state.sent + sent, refused: state.refused + refused, lastRefused: refused };
  }
  return { requiredBufferBytes, stepDay, C };
});
