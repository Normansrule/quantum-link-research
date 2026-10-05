# Protocols

| # | Protocol | Bench tier | Time | Prerequisite reading |
|---|---|---|---|---|
| [P01](P01_odmr_nv_bench.md) | ODMR on a $100–500 NV bench | 0 | one weekend | learn 00/09, done/04 |
| [P02](P02_pulsed_nv_control.md) | Pulsed control: Rabi, Ramsey, Hahn echo, $T_1$ | 1 | two weeks | learn 00/04, done/05 |
| [P03](P03_spdc_bell_test.md) | Two-crystal SPDC source, HOM, CHSH, BB84 | 1 | one semester | learn 00/05, 00/12, done/03, done/06 |
| [P04](P04_rooftop_free_space_link.md) | Campus free-space link: loss vs distance, daylight background | 1 | two weeks after P03 | learn 03/04, proposed E4 |
| [P05](P05_single_photon_anticorrelation.md) | Single-photon anticorrelation (Grangier): is the source really single-photon? | 1 | two weekends after P03 | done/02 |
| [P06](P06_quantum_eraser.md) | Quantum eraser and delayed choice: fringes appear only when records are compared | 1 | two afternoons after P03 | done/03 |
| [P07](P07_bb84_over_a_fiber_spool.md) | BB84 over a fiber spool with quantum random bases | 1 | one semester | learn 03/10, P03 |
| [P08](P08_time_bin_encoding.md) | Time-bin encoding and a fiber interferometer | 1 | a few weekends | P07 |
| [SEE 510 ladder](../../systems/see510/10_real_world_experiments.md) | The two-site key link from a $40 bright-light analogue (Arduino, servos, polarizer film) through fiber characterization and weak-coherent BB84 to entanglement-based BBM92; every tier's log processed by `qll/link` | 0–4 | a weekend to a year | systems/see510 01–09 |
| [P09](P09_mars_link_on_a_table.md) | The Mars link on a table: planetshine, étendue, ground vs space source, errors from background, the key bank; with a tested digital twin | 0–2 (3 with P03) | 6–10 weekends, stage by stage | learn 03/21, 03/22 |
| [P10](P10_two_room_single_photon_link.md) | The two-room link: a fiber classical channel, then single-photon BB84 with decoys between two rooms for under $1,000, matched to a digital twin (mission Phase 1) | 1 | one semester part-time, stage by stage | systems/program, SEE 510 ladder |
| [P11](P11_collapse_code_on_a_cloud_processor.md) | The collapse code: can how a shared state collapses carry a message? A measured bound on a free cloud processor (mission paper 1) | 0 | two to six weeks | E17, E16 |

Every protocol has the same sections: **Safety** · **Parts** (with links to `../bench/hardware_guide.md`) · **Build** · **Align** · **Measure** · **Analyze** (with the `qll` function that fits the data) · **Expected numbers** · **If it does not work**. Log every run in a lab notebook with date, diamond/crystal ID, laser power, and temperature; the repo's `notebooks/` folder is the right place for the analysis.
