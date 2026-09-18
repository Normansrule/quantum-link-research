# protocols/ — procedures you can follow line by line

| # | Protocol | Bench tier | Time | Prerequisite reading |
|---|---|---|---|---|
| [P01](P01_odmr_nv_bench.md) | ODMR on a $100–500 NV bench | 0 | one weekend | learn 00/09, done/04 |
| [P02](P02_pulsed_nv_control.md) | Pulsed control: Rabi, Ramsey, Hahn echo, $T_1$ | 1 | two weeks | learn 00/04, done/05 |
| [P03](P03_spdc_bell_test.md) | Two-crystal SPDC source, HOM, CHSH, BB84 | 1 | one semester | learn 00/05, 00/12, done/03, done/06 |
| [P04](P04_rooftop_free_space_link.md) | Campus free-space link: loss vs distance, daylight background | 1 | two weeks after P03 | learn 03/04, proposed E4 |

Every protocol has the same sections: **Safety** · **Parts** (with links to `../bench/hardware_guide.md`) · **Build** · **Align** · **Measure** · **Analyze** (with the `qll` function that fits the data) · **Expected numbers** · **If it does not work**. Log every run in a lab notebook with date, diamond/crystal ID, laser power, and temperature; the repo's `notebooks/` folder is the right place for the analysis.
