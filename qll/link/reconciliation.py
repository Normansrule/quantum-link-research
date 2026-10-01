"""Error reconciliation with Cascade, and verification that the two keys now match.

Method
------
Cascade [brassard1994], building on the parity method of BBBSS [bennett1992exp]. In pass p both sites apply the same
public random permutation (the identity in the first pass), cut the key into blocks of k_p = k_1 2^p bits
(k_1 = 0.73 / Q), and Site A announces each block's parity. A block whose parity differs at Site B holds an odd number
of errors; a binary search over halves, Site A announcing one parity per step, finds and corrects one. Correcting a
bit flips the parity of the block that contains it in every earlier pass, so those blocks are searched again
("back-tracking"), which is what lets Cascade remove nearly every error in four passes. Every announced parity is a
bit the adversary learns and is counted in the leak.

Verification: both sites hash their keys with the same public random Toeplitz matrix (two-universal) to t bits and
compare [wegman1981]; different keys collide with probability at most 2^-t. The t tag bits are also counted as
leaked. A mismatch rejects the session, whatever the error estimate said.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from qll.link.classical_channel import AuthenticatedChannel
from qll.link.codec import pack, unpack
from qll.qkd.privacy_amplification import toeplitz_hash


@dataclass(frozen=True)
class ReconciliationOutcome:
    key_b: np.ndarray            # Site B's corrected key
    leaked_bits: int             # parities disclosed
    corrected: int               # bits Site B flipped
    passes: int
    messages: int


def _parities(bits: np.ndarray, lo: np.ndarray, hi: np.ndarray) -> np.ndarray:
    c = np.concatenate([[0], np.cumsum(bits, dtype=np.int64)])
    return ((c[hi] - c[lo]) % 2).astype(np.int8)


def reconcile(key_a: np.ndarray, key_b: np.ndarray, qber_estimate: float, passes: int, rng: np.random.Generator,
              channel: AuthenticatedChannel) -> ReconciliationOutcome:
    a, b = np.asarray(key_a, dtype=np.int8), np.asarray(key_b, dtype=np.int8).copy()
    n = len(a)
    if n == 0:
        return ReconciliationOutcome(b, 0, 0, 0, 0)
    k1 = int(min(n, max(4, round(0.73 / max(qber_estimate, 0.005)))))
    m0 = channel.n_messages
    perms, poss, sizes, par_a = [], [], [], []
    leaked = corrected = 0

    def search(q: int, blk: int) -> int:
        """Binary search inside block blk of pass q (whose parity differs); returns the key index it corrects."""
        nonlocal leaked
        perm, k = perms[q], sizes[q]
        lo, hi = blk * k, min(n, (blk + 1) * k)
        while hi - lo > 1:
            mid = (lo + hi) // 2
            pa = int(channel.send("A", "half_parity", {"pass": q, "lo": lo, "mid": mid, "parity": int(a[perm[lo:mid]].sum() % 2)})["parity"])
            leaked += 1
            if pa != int(b[perm[lo:mid]].sum() % 2):
                hi = mid
            else:
                lo = mid
        return int(perm[lo])

    def mismatched(q: int, blk: int) -> bool:
        perm, k = perms[q], sizes[q]
        return int(b[perm[blk * k:min(n, (blk + 1) * k)]].sum() % 2) != par_a[q][blk]

    for p in range(passes):
        perm = np.arange(n) if p == 0 else rng.permutation(n)
        pos = np.empty(n, dtype=np.int64)
        pos[perm] = np.arange(n)
        k = min(n, k1 * 2**p)
        perms.append(perm); poss.append(pos); sizes.append(k)
        channel.send("A", "permutation_seed", {"pass": p})                       # the shared permutation is public
        lo = np.arange(0, n, k)
        hi = np.minimum(lo + k, n)
        par_a.append(unpack(channel.send("A", "block_parities", pack(_parities(a[perm], lo, hi)))))
        leaked += len(lo)
        for blk in np.nonzero(par_a[p] != _parities(b[perm], lo, hi))[0]:
            if not mismatched(p, int(blk)):                                     # fixed by back-tracking meanwhile
                continue
            queue = [(p, int(blk))]
            while queue:
                q0, b0 = queue.pop()
                if not mismatched(q0, b0):                                      # already repaired by another correction
                    continue
                i = search(q0, b0)
                b[i] ^= 1
                corrected += 1
                for q in range(p + 1):                                          # back-track through every pass so far
                    bq = int(poss[q][i] // sizes[q])
                    if mismatched(q, bq):
                        queue.append((q, bq))
    return ReconciliationOutcome(b, leaked, corrected, passes, channel.n_messages - m0)


def verify(key_a: np.ndarray, key_b: np.ndarray, tag_bits: int, seed: int, channel: AuthenticatedChannel) -> bool:
    """Compare two-universal hashes of both keys; Site A announces its tag, Site B compares."""
    tag_a = unpack(channel.send("A", "verification_tag", {"seed": int(seed), **pack(toeplitz_hash(key_a, tag_bits, seed))}))
    return bool(np.array_equal(tag_a, toeplitz_hash(key_b, tag_bits, seed)))
