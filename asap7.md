---
title: ASAP7 PDK
nav_order: 3
parent: Technologies
---

# ASU/ARM ASAP7 Predictive 7 nm FinFET PDK

ASAP7 is a **predictive** 7 nm FinFET process design kit developed by Lawrence
Clark's group at Arizona State University in collaboration with ARM, first
published in 2016. It is the most widely used open PDK for a sub-10 nm node
and the standard proving ground for research EDA tools that need to touch a
FinFET back-end.

Unlike [Sky130](sky130.md) and [GF180MCU](gf180mcu.md), ASAP7 is
**not manufacturable**. No foundry has signed off on the rules, there is no
MPW program, and you cannot tape out an ASAP7 design. It exists so that
academic tool builders, publication authors, and students can run a realistic
FinFET flow end-to-end without needing an NDA'd commercial PDK.

Primary references:

* PDK source: <https://github.com/The-OpenROAD-Project/asap7>
* ASU project page: <https://asap.asu.edu/>
* Clark et al., *"ASAP7: A 7-nm finFET predictive process design kit,"*
  Microelectronics Journal vol. 53, pp. 105–115, July 2016.

## How ASAP7 compares to Sky130 and GF180MCU

ASAP7 is a fundamentally different kind of PDK from the other two. The
headline differences:

| Dimension           | Sky130 / GF180MCU                 | ASAP7                                  |
|---------------------|-----------------------------------|-----------------------------------------|
| Foundry sign-off    | Yes — real manufacturable PDK     | **No** — predictive, not manufacturable |
| Device type         | Planar bulk CMOS                  | FinFET                                  |
| Feature size        | 130 nm / 180 nm                   | 7 nm (predictive)                       |
| Nominal V_DD        | 1.8 V / 3.3 V / 5 V               | 0.7 V                                   |
| SPICE models        | BSIM4 (level 54)                  | BSIM-CMG (common multi-gate)            |
| Model format        | ngspice + Xyce                    | HSpice `.pm` files (no ngspice build)   |
| Distribution        | `ciel` (open_pdks snapshot)       | `git clone` from GitHub                 |
| Standard-cell V_T   | 1–3 flavors per device            | 4 flavors: SLVT, LVT, RVT, SRAM         |
| Digital flow        | OpenLane, LibreLane, ORFS         | ORFS (primarily)                        |
| MPW program         | Chipforge, Tiny Tapeout, etc.     | None                                    |

The "predictive" framing is the single most important thing to keep in mind.
Timing numbers, power numbers, and area numbers from ASAP7 are meaningful
*relative to one another* for tool benchmarking — not as predictions of what
a real 7 nm chip would do.

## Installing the PDK

There is no ciel package. Clone the main repo and its submodules directly:

```bash
git clone --recurse-submodules https://github.com/The-OpenROAD-Project/asap7.git
```

The repo pulls in three submodules that hold the actual standard-cell and
PDK IP. The resulting tree:

```
asap7/
├── asap7_pdk_r1p7/         # tech files, HSpice models, Calibre decks
├── asap7_sram_0p0/         # SRAM macros (minimal)
├── asap7sc6t_26/           # 6-track standard cells (version 26)
├── asap7sc7p5t_27/         # 7.5-track standard cells (older, v27)
└── asap7sc7p5t_28/         # 7.5-track standard cells (current, v28)
```

For digital flows you almost always want `asap7sc7p5t_28`. The 6-track
library exists for area studies and dense-layout research; its cell set is
smaller.

If you are driving ASAP7 through [OpenROAD Flow Scripts](orfs.md), you
don't need to clone ASAP7 separately — ORFS ships a stripped-down copy
under `flow/platforms/asap7/` with just the LEF, Liberty, GDS, and Verilog
views the flow needs.

## PDK directory (`asap7_pdk_r1p7`)

The PDK submodule holds everything that is not a standard cell library:

| Subdirectory     | Contents                                                |
|------------------|---------------------------------------------------------|
| `calibre/`       | Mentor Calibre DRC, LVS, and xACT 3D extraction decks   |
| `cdslib/`        | Cadence Virtuoso tech library + setup scripts           |
| `models/hspice/` | HSpice device models (`7nm_TT.pm`, `7nm_SS.pm`, `7nm_FF.pm`) |
| `docs/`          | Documentation                                           |
| `asap7ssc7p5t_*/`| Sample standard cells (Virtuoso design library)         |

Two practical consequences of this layout:

- **The sign-off tool assumption is Cadence + Mentor.** DRC and LVS ship as
  Calibre SVRF decks; the techlib ships for Virtuoso. KLayout decks are
  maintained separately in the OpenROAD ORFS tree. Open-source DRC on ASAP7
  is workable but lags the Calibre decks.
- **SPICE is HSpice-only out of the box.** The `.pm` files use HSpice syntax.
  Running them in ngspice requires patching — most open-source use of ASAP7
  consumes the Liberty (`.lib`) timing files rather than the transistor
  models directly.

## Standard cells (`asap7sc7p5t_28`)

The current 7.5-track library has its views laid out as:

| Directory       | Contents                                     |
|-----------------|----------------------------------------------|
| `LEF/`          | Abstract layout per V_T flavor               |
| `LIB/NLDM/`     | Non-linear delay-model Liberty files (.7z)   |
| `LIB/CCS/`      | Composite-current-source Liberty files (.7z) |
| `GDS/`          | Full layout                                  |
| `CDL/`          | LVS netlists                                 |
| `Verilog/`      | Functional Verilog                           |
| `Datasheet/`    | Per-cell datasheets                          |
| `qrc/`          | QRC extraction tech files                    |
| `techlef_misc/` | Supplemental tech LEFs                       |

Liberty files are bundled as `.7z` archives — unpack with `p7zip` before
pointing OpenSTA or synthesis at them.

### V_T flavors

ASAP7 provides four threshold-voltage flavors per device. Every standard
cell is built in all four, picked by implant-layer choice (`SLVTN/P`,
`LVTN/P`, `RVTN/P`, plus an SRAM-only implant):

| Flavor | Name             | Use                                       |
|--------|------------------|-------------------------------------------|
| SLVT   | Super-low V_T    | Highest speed, highest leakage            |
| LVT    | Low V_T          | Speed-leakage tradeoff                    |
| RVT    | Regular V_T      | Default — most of a typical digital core  |
| SRAM   | SRAM-specific V_T| Reserved for SRAM bitcells (stability)    |

Naming in the library files encodes the flavor and the STA corner:

```
asap7sc7p5t_INVBUF_RVT_TT_nldm_220122.lib    # inverters/buffers, RVT, TT corner
asap7sc7p5t_SEQ_SLVT_SS_nldm_220123.lib      # flip-flops / latches, SLVT, SS
asap7sc7p5t_SIMPLE_LVT_FF_nldm_211120.lib    # basic combinational, LVT, FF
```

The cells themselves are split across five functional groups rather than
one monolithic library:

- `INVBUF` — inverters and buffers, including clock buffers
- `SIMPLE` — basic combinational (NAND, NOR, AOI/OAI)
- `AO`, `OA` — AND-OR / OR-AND compound gates
- `SEQ` — flip-flops and latches

For multi-V_T synthesis you give the tool all four flavors and let it pick
per-cell, usually with an SLVT/LVT budget to limit leakage.

### Cell naming

The per-cell convention is different from Sky130's double-underscore
pattern. Drive strength and width use an `xN` suffix and V_T is captured
in the library name, not the cell name:

```
INVx1_ASAP7_75t_R        # size-1 inverter, 7.5-track, RVT
NAND2x2_ASAP7_75t_L      # 2-input NAND, drive 2, LVT
DFFHQNx4_ASAP7_75t_SL    # flip-flop with negative-edge Q, drive 4, SLVT
```

The trailing letter (`R`, `L`, `SL`, `SRAM`) encodes the V_T flavor.
`75t` is the track height (7.5).

## Metal stack

ASAP7 defines **9 routing metals plus a Pad layer**. Unlike Sky130's
homogeneous routing stack, the pitches climb in three tiers that reflect
realistic FinFET back-end lithography:

```
                         (top, thickest, cheapest R)
       Pad    ──  0.080 µm pitch
       V9
       M9     ──  0.080 µm pitch, vertical
       V8
       M8     ──  0.080 µm pitch, horizontal
       V7
       M7     ──  0.064 µm pitch, vertical
       V6
       M6     ──  0.064 µm pitch, horizontal
       V5
       M5     ──  0.048 µm pitch, vertical
       V4
       M4     ──  0.048 µm pitch, horizontal
       V3
       M3     ──  0.036 µm pitch, vertical       ← tightest tier, SAQP
       V2
       M2     ──  0.036 µm pitch, horizontal     ← tightest tier, SAQP
       V1
       M1     ──  0.036 µm pitch, vertical       ← tightest tier, SAQP
       V0
       (Active / Gate / wells)
                         (bottom)
```

Key things about this stack:

- **Three pitch tiers.** M1–M3 at 36 nm (routed with self-aligned quadruple
  patterning in a real fab), M4–M5 at 48 nm, M6–M7 at 64 nm, M8–M9 and Pad
  at 80 nm. This is close to the pitch hierarchy of real 7 nm commercial
  nodes.
- **No local interconnect layer.** Unlike Sky130's `li1`, ASAP7 uses M1
  directly inside the cell. With a 36 nm pitch, M1 alone is dense enough
  to make that work.
- **Directions strictly alternate.** M1 vertical, M2 horizontal, M3
  vertical, and so on up the stack.
- **Which metals to route on.** Default OpenROAD flows typically route
  signals on M2–M7, reserve M1 for intra-cell, and use M8/M9 for power
  straps and clock trunks.

## Corners

ASAP7 ships **three** STA corners — `TT`, `FF`, `SS` — delivered as both
HSpice model files and per-group Liberty files. There are no separate
slow-fast, fast-slow, leakage, or temperature corners in the base
distribution:

| Corner | HSpice file   | Use                              |
|--------|---------------|----------------------------------|
| `TT`   | `7nm_TT.pm`   | Nominal design center            |
| `SS`   | `7nm_SS.pm`   | Setup timing, worst-case power   |
| `FF`   | `7nm_FF.pm`   | Hold timing, max-current checks  |

Liberty views exist for all three corners, across all four V_T flavors
and all five cell groups. For multi-corner STA the mechanics are the same
as in any other PDK; see [Multi-Corner Timing Analysis](sta-mc.md).

If your research needs per-device Monte Carlo mismatch or cross-corner
(SF/FS) analysis on ASAP7, you have to generate it yourself — the
distribution ships only the three global corners above.

## SRAM and I/O

- **SRAM macros:** `asap7_sram_0p0` is minimal and is normally substituted
  for [FakeRAM2.0](https://github.com/maliberty/FakeRAM2.0) blackbox
  macros in ORFS runs. If you actually need silicon-accurate SRAM
  characterization on ASAP7, expect to generate your own bitcell and
  compiler — the shipping macros are placeholders.
- **I/O cells:** `asap7sc7p5t_28/LEF/IO_cell/` ships a small set of pad
  cells, but ASAP7 does not provide a full ESD-signed-off I/O ring.
  That reinforces the point: this is a research PDK.

## Using ASAP7 from ORFS

The path of least resistance for digital experiments is
[OpenROAD Flow Scripts](orfs.md). ORFS ships a ready-to-run `asap7`
platform and a set of demo designs under `flow/designs/asap7/`:

```bash
cd OpenROAD-flow-scripts/flow
make DESIGN_CONFIG=./designs/asap7/gcd/config.mk
```

The platform directory at `flow/platforms/asap7/` contains everything
ORFS needs — LEFs, Libertys, GDS, Verilog, KLayout decks, PDN config,
tapcell script — without the Calibre / Virtuoso infrastructure from the
full PDK clone.

## Related tutorials

- **Installing ciel and the manufacturable PDK story:** [Sky130 PDK](sky130.md), [GF180MCU PDK](gf180mcu.md)
- **BSIM model structure and the difference between BSIM4 and BSIM-CMG:** [Spice Device Models](spice-models.md)
- **Multi-corner STA setup:** [Multi-Corner Timing Analysis](sta-mc.md)
- **Driving ASAP7 through a digital flow:** [ORFS & OpenROAD](orfs.md)
