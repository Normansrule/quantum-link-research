# Chapter 1 — Introduction (draft)

## 1.1 The question

Can two parties, one on Earth and one on Mars, share a secret whose security rests on physics rather than on the difficulty of a mathematical problem, and can they use that secret to communicate? The question is not rhetorical. Every classical key exchange in use today, including the post-quantum schemes standardized by the National Institute of Standards and Technology (NIST) in 2024, is secure only under a computational assumption. Quantum key distribution (QKD) replaces that assumption with the no-cloning theorem and the disturbance that measurement causes (Bennett & Brassard, 1984; Ekert, 1991), and quantum teleportation moves a quantum state itself using entanglement and two classical bits (Bennett et al., 1993). Both have been demonstrated on Earth, over fiber and through low-Earth-orbit satellites (Yin et al., 2017; Li et al., 2025). Neither has been attempted at planetary distance.

## 1.2 The catch

Two physical facts make the interplanetary case different in kind, not only in degree. The first is the no-communication theorem: entanglement by itself carries no message, so every protocol that uses it also needs classical information that travels at, or below, the speed of light. Between Earth and Mars that is 3.1 to 22.3 minutes one way. The second is that the receiving half of an entangled pair must remain coherent until those classical bits arrive. A memory that lasts a millisecond, which is ample for a metropolitan link, is useless across a 6-to-45-minute round trip. The question therefore reduces to a comparison between two numbers: the coherence time of a quantum memory and the light time of the channel.

## 1.3 What this thesis does

This work is a systems-engineering treatment of that comparison. It builds, as open-source and tested software, the chain of physical models from a single qubit to a planetary link: the thermal occupation that sets where each component must live, the loss laws of fiber and free space, the circuits that create and consume entanglement, the key-distribution protocols and their capacity bounds, the memories and repeaters that extend range, the orbital geometry that sets light time and blackout, and the application layer that must refuse to send when it runs out of key. Every model cites its source, carries an analytic test, and traces to a requirement in a machine-checked matrix. Three experiments organize the work: F1, entanglement between two computers in one city; F2, a downlink from a satellite; and F3, the Earth–Mars link, which is F1 and F2 with the time axis stretched by a factor of a million.

## 1.4 Contributions

1. A physics-first, modular codebase (`qll`) in which no-signaling, no-cloning, the two-bit cost of teleportation, trace preservation, and the repeaterless capacity bound are enforced as runtime invariants rather than assumed.
2. A verified reproduction of the Micius satellite link budget within 3 dB, and a Kepler ephemeris whose Earth–Mars range envelope matches tabulated constants to 1 %.
3. A memory capability matrix that answers the thesis question quantitatively: at an initial fully entangled fraction of 0.95, only rare-earth nuclear-spin memories and hour-class trapped-ion memories survive the Mars round trip, and the rare-earth ones do so at retrieval efficiencies below 5 %.
4. A fail-closed messenger and a buffer-sizing rule for a channel with a 20-minute round trip, showing that the key buffer is small and the wait is not.
5. A library, a lab manual, and proposals E1–E10 that let a student laboratory reproduce the landmark experiments on a bench budget and extend them toward the interplanetary case.

## 1.5 Structure

Chapter 2 gives the physics background; Chapter 3 the method; Chapter 4 the computed results by phase; Chapter 5 the experiments performed and proposed; Chapter 6 the discussion, including what has scaled in the field, what has been retracted, and what remains open; Chapter 7 concludes.
