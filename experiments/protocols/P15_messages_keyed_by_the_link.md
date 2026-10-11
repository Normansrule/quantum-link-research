# P15 — Messages Keyed by the Link: How Many a Day, and How Big a Key Bank

**What it shows.** The point of a key is to protect messages. This protocol turns the key that [P10](P10_two_room_single_photon_link.md) makes into a working messenger between the rooms and measures the two numbers a user cares about. The first is how many messages a day the link can key. The second is how big a key bank keeps the messenger from ever refusing. It does this for four ways of spending key:

| Policy | Key per message of *b* bytes | What protects the message |
|---|---|---|
| One-time pad, with a Wegman–Carter tag | 8*b* + 127 bits | information-theoretic security: no computer can break it (Shannon, 1949; Wegman & Carter, 1981) |
| AES-256-GCM, key from the link, renewed every *n* messages | 256/*n* bits | computational security: 128-bit security against a quantum computer (Grover, 1996), and the key is never sent in public |
| Hybrid ML-KEM + link key (the repository's messenger) | 256/*n* bits | secure if either the link's key or the lattice problem holds (NIST, 2024) |
| Conventional key exchange (today's messengers) | none | a recording can be decrypted later by a large quantum computer (Shor, 1997) |

When the bank is empty the messenger refuses to send. It never falls back to a weaker policy (requirement REQ-APP-001). Latency is the light time whatever the policy: banked key adds none.

**Extra cost.** $0 above P10. The software is [`qll/link/demo_app.py`](../../qll/link/demo_app.py), with key delivery modelled on ETSI GS QKD 014, plus the repository's messenger [`qll/app/messenger.py`](../../qll/app/messenger.py).

**The twin.** [`qll/link/keyed_messaging.py`](../../qll/link/keyed_messaging.py) takes each link's daily key from its own twin:

- two rooms (P10), around the clock;
- two buildings at night at 1 km with avalanche-diode modules ([P04](P04_rooftop_free_space_link.md));
- one Micius-class satellite pass a night;
- a Mars lander with key loaded before launch.

It sizes the bank by the sequent-peak rule of reservoir design (Loucks & van Beek, 2017). [`tests/test_keyed_messaging.py`](../../tests/test_keyed_messaging.py) checks every supply against its twin, and checks that a bank of that size never refuses. The [messenger lab](https://normansrule.github.io/quantum-link-research/lab/messenger/) runs the same arithmetic and encrypts real messages in the browser.

## What the twin predicts (500 messages of 200 bytes a day, sent 08:00–22:00)

| Link | Key a day | One-time pad: messages a day at most | Bank for the pad | AES or hybrid (*n* = 100): messages a day at most |
|---|---|---|---|---|
| Two rooms (P10) | 13 MB | about 60,000 | none needed | about 40 million |
| Two buildings at night | 3.1 MB | about 14,000 | 108 kB | about 9.6 million |
| One satellite pass | 0.48 MB | about 2,200 | 108 kB | about 1.5 million |
| Mars lander, 1 TB loaded | none | — | a terabyte of pad lasts about 25,000 years | — |

The default hardware makes far more key than text messages need. A one-time pad is affordable for text on every link, while photos and video need AES or the hybrid. A satellite gives one burst a night, so a bank must carry a day's demand. A Mars messenger can be keyed today by carrying the key: a 1 TB pad outlasts the mission by orders of magnitude, and no Earth–Mars quantum link is needed to start.

## Steps

1. **Plan.** Print the twin's plan for your message volume:
   `python -m qll.link.keyed_messaging --messages 500 --bytes 200`
2. **Measure the supply.** Run a day of P10 sessions (stage 6). Add up the accepted key from each ingest report (`python -m qll.link.run ingest ...`) to get your measured key bits per day.
3. **Replace the twin's supply with yours**, and see the plan change:
   `python -m qll.link.keyed_messaging --messages 500 --measured-bits-per-day <your number>`
4. **Send messages.** Run the demonstration:
   `python -m qll.link.run demo`
   - Site A's application asks the key store for a key and encrypts a test message with it.
   - Site B's application retrieves the same key by its identifier and decrypts.
   - A session that was rejected deposits nothing.
   - An empty store refuses.
5. **Exhaust the bank on purpose.** Send faster than the link makes key until the messenger refuses, and record the time it took. Compare it with the bank size divided by the shortfall rate.
6. **Use only non-sensitive test messages.** The keys at rest in this software are ordinary memory, not a hardware security module.

## Pass criteria

- The measured daily key is within the twin's prediction for your measured parts. If not, P10's own checks say why.
- Every message round-trips.
- The messenger refuses when the bank is empty, and never sends with a weaker policy.
- The time to exhaust the bank matches bank ÷ shortfall within 10 %.

## References

Grover, L. K. (1996). A fast quantum mechanical algorithm for database search. *Proceedings of the 28th Annual ACM Symposium on Theory of Computing*, 212–219. https://doi.org/10.1145/237814.237866

Loucks, D. P., & van Beek, E. (2017). *Water resource systems planning and management*. Springer.

National Institute of Standards and Technology. (2024). *Module-lattice-based key-encapsulation mechanism standard* (FIPS 203).

Shannon, C. E. (1949). Communication theory of secrecy systems. *Bell System Technical Journal, 28*(4), 656–715.

Shor, P. W. (1997). Polynomial-time algorithms for prime factorization and discrete logarithms on a quantum computer. *SIAM Journal on Computing, 26*(5), 1484–1509.

Wegman, M. N., & Carter, J. L. (1981). New hash functions and their use in authentication and set equality. *Journal of Computer and System Sciences, 22*(3), 265–279.
