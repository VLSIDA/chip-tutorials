---
title: Technologies
nav_order: 60
has_children: true
---

# Technologies

Open-source process design kits (PDKs) that this course's tool chain
targets.

The two manufacturable PDKs — Sky130 and GF180MCU — are full foundry-signed,
distributed via [ciel](https://github.com/fossi-foundation/ciel), and
backed by free multi-project wafer runs. ASAP7 is a *predictive* PDK used
for research and EDA benchmarking; it is not manufacturable.

- **[Sky130 PDK](sky130.md)** — SkyWater 130 nm. The workhorse for
  open-source digital tape-outs since 2020. 1.8 V core, five routing
  metals plus a local-interconnect layer, HD standard cells.
- **[GF180MCU PDK](gf180mcu.md)** — GlobalFoundries 180 nm mixed-signal
  / MCU process. 3.3 V and 6 V devices, three metal-stack variants
  (A/B/C/D), used by wafer.space MPW runs.
- **[ASAP7 PDK](asap7.md)** — ASU/ARM predictive 7 nm FinFET. Four V_T
  flavors, 9 routing metals, BSIM-CMG models. Research-only — no
  foundry, no tape-out, no MPW.
