---
title: GF180MCU PDK
nav_order: 2
parent: Technologies
---

# GlobalFoundries 180 nm MCU Open-Source PDK (gf180mcu)

gf180mcu is GlobalFoundries' open-sourced 180 nm process design kit, released
in 2022 as the second major fully open PDK after Sky130. Where Sky130 is a
low-voltage 130 nm technology, gf180mcu is a **mixed-signal / MCU-oriented**
180 nm technology with 3.3 V *and* 6 V device options. That makes it the
natural choice when your design needs to drive larger loads, interface with
anything above ~2 V, or include on-chip power management.

Primary references:

* PDK source: <https://github.com/google/gf180mcu-pdk>
* GF announcement: <https://globalfoundries.com/news-events/press-releases/globalfoundries-and-google-launch-new-open-source-process-design-kit-for-180nm>

## How gf180mcu compares to Sky130

If you have already read the [Sky130 PDK](sky130.md) tutorial, many things
are familiar. Both ship through open_pdks + ciel, both use the same directory
structure, both use BSIM4 (level 54) device models, and both follow the
`<foundry>_<provider>_<library>__<cell>` naming convention.

The meaningful differences:

| Dimension              | Sky130                                 | gf180mcu                                 |
|------------------------|----------------------------------------|-------------------------------------------|
| Foundry                | SkyWater Technology                    | GlobalFoundries                           |
| Feature size           | 130 nm                                 | 180 nm                                    |
| Nominal V_DD           | 1.8 V (core)                           | 3.3 V and/or 5 V                          |
| Variants               | `sky130A`, `sky130B` (SONOS flash)     | `gf180mcuA`/`B`/`C`/`D` (metal stack)     |
| Routing metal count    | 5 (met1–met5 + li1)                    | 3, 4, or 5 depending on variant           |
| Std cell libraries     | `sky130_fd_sc_hd` (plus `hvl`, etc.)   | `gf180mcu_fd_sc_mcu7t5v0` + `mcu9t5v0`    |
| SRAM macros            | OpenRAM-generated, many sizes          | 4 pre-built sizes (64/128/256/512 × 8 b)  |
| Simulator integrations | ngspice                                | ngspice **and** xyce                      |
| Digital flow tool      | OpenLane                               | LibreLane (the OpenLane 2 rename)         |

The variant story is where you have to make a real choice up front.

## The four variants

Unlike Sky130, where `A` vs `B` is a device-level distinction (SONOS
non-volatile memory), gf180mcu's `A`/`B`/`C`/`D` is a **back-end metal stack
option**. The circuit IP is the same across all four; what changes is how
many routing metals you have and how thick the top metal is:

| Variant      | Metal stack option | Routing metals          | Top metal thickness |
|--------------|--------------------|-------------------------|---------------------|
| `gf180mcuA`  | 3LM                | Metal1, Metal2, Metal3  | standard            |
| `gf180mcuB`  | 4LM                | Metal1–Metal4           | standard            |
| `gf180mcuC`  | 5LM_1TM_9K         | Metal1–Metal5           | 9 kÅ (~0.99 µm)     |
| `gf180mcuD`  | 5LM_1TM_11K        | Metal1–Metal5           | 11 kÅ (~1.19 µm)    |

`gf180mcuC` and `gf180mcuD` both have 5 routing layers and an extra-thick
"top metal" option suitable for inductors, RF matching networks, or
high-current power distribution. `D` is simply the thicker top-metal
variant.

**You cannot mix variants in one tape-out.** Pick one at the start of the
project and point your flow at it with `$PDK=gf180mcuC` (or whichever).
For general digital work, `gf180mcuC` is the most common pick — it has
enough routing metals for real SoCs without paying for the thickest top
metal.

## Installing the PDK

Install via ciel the same way as Sky130. Running `ciel enable` for
gf180mcu drops *all four* variants into place:

```bash
pip install ciel
ciel enable --pdk gf180mcu 7b70722e33c03fcb5dabcf4d479fb0822d9251c9
```

Result:

```
~/.ciel/
├── gf180mcuA/      # 3 metals
├── gf180mcuB/      # 4 metals
├── gf180mcuC/      # 5 metals, 9 kÅ top
└── gf180mcuD/      # 5 metals, 11 kÅ top
```

Each variant has the same top-level layout as Sky130:

```
gf180mcuC/
├── SOURCES           # open_pdks provenance
├── libs.tech/        # per-tool configuration
└── libs.ref/         # circuit IP libraries
```

## `libs.tech/`: tool configurations

| Directory   | Tool                    | Notes                                  |
|-------------|-------------------------|----------------------------------------|
| `ngspice`   | Ngspice                 | Design and device SPICE libs           |
| `xyce`      | Xyce                    | Sandia's parallel SPICE                |
| `magic`     | Magic VLSI              | DRC, extraction                        |
| `klayout`   | KLayout                 | Tech file, DRC, LVS decks              |
| `netgen`    | Netgen                  | LVS setup                              |
| `librelane` | LibreLane (OpenLane 2)  | Digital flow configuration             |
| `xschem`    | Xschem                  | Schematic capture                      |
| `qflow`     | Qflow (legacy)          | Older digital flow                     |

Two immediately useful files inside `libs.tech/ngspice/`:

- `sm141064.ngspice` — the master device model file. Includes 3.3 V and
  6 V MOSFETs, BJTs, diodes, resistors, and MIM capacitors (via
  `sm141064_mim.ngspice`). Device models are BSIM4 (`level = 54`).
- `design.ngspice` — a global-parameter file that controls Monte Carlo
  switches (`sw_stat_global`, `sw_stat_mismatch`), the mismatch skew
  seed (`mc_skew`), and the flicker noise corner (`fnoicor`). Include this
  once at the top of your testbench to get access to the MC infrastructure.

## `libs.ref/`: circuit IP libraries

Five libraries ship across every variant:

| Library                        | Contents                                    |
|--------------------------------|---------------------------------------------|
| `gf180mcu_fd_pr`               | Primitive devices (MOSFETs, R, C, diodes, BJTs, eFuse) |
| `gf180mcu_fd_sc_mcu7t5v0`      | 7-track, 5 V standard cells (229 cells)    |
| `gf180mcu_fd_sc_mcu9t5v0`      | 9-track, 5 V standard cells (229 cells)    |
| `gf180mcu_fd_io`               | I/O pad cells                               |
| `gf180mcu_fd_ip_sram`          | Four pre-built SRAM macros                  |

Note the absence of a `gf180mcu_fd_pr/spice/` directory — gf180mcu keeps
its SPICE device models centrally in `libs.tech/ngspice/` rather than
per-cell. Only `gds/` and `mag/` views live under `gf180mcu_fd_pr/`, and
only for structured devices that ship with physical layout (BJTs, eFuse).
Simple MOSFETs are model-only; you get their layout by drawing them.

## Device primitives (`sm141064.ngspice`)

The primary model file lists every device in the `.subckt` table at the
top. Highlights:

### MOSFETs

| Device              | V_GS max | V_DS max | Notes                             |
|---------------------|----------|----------|------------------------------------|
| `nfet_03v3`         | 3.3 V    | 3.3 V    | Standard 3.3 V NMOS                |
| `pfet_03v3`         | 3.3 V    | 3.3 V    | Standard 3.3 V PMOS                |
| `nfet_03v3_dss`     | 3.3 V    | 3.3 V    | Drain-side silicide-block (higher R) |
| `pfet_03v3_dss`     | 3.3 V    | 3.3 V    | ″                                   |
| `nfet_06v0`         | 6 V      | 6 V      | 6 V NMOS                           |
| `pfet_06v0`         | 6 V      | 6 V      | 6 V PMOS                           |
| `nfet_06v0_dss`     | 6 V      | 6 V      | Drain-side SAB variant             |
| `pfet_06v0_dss`     | 6 V      | 6 V      | ″                                   |
| `nfet_06v0_nvt`     | 6 V      | 6 V      | Native (near-zero V_T) NMOS        |

Unlike Sky130, gf180mcu has **no low-V_T / high-V_T flavor of the core
device**. You pick 3.3 V or 6 V, then pick whether you want the normal
silicided source/drain or the higher-resistance drain-side-silicide-block
(`_dss`) variant for analog.

### Capacitors

- **MIM capacitors:** `cap_mim_1f0fF`, `cap_mim_1f5fF`, `cap_mim_2f0fF` —
  three densities (1 fF/µm², 1.5 fF/µm², 2 fF/µm²). Higher density is
  lower voltage rating.
- **MOS capacitors:** `cap_nmos_03v3`/`cap_pmos_03v3` (inversion-mode at
  3.3 V), `cap_nmos_06v0`/`cap_pmos_06v0` (inversion-mode at 6 V),
  plus `_b` suffix variants in accumulation mode (NMOS in Nwell,
  PMOS in Pwell).

### Resistors

Much more variety than Sky130 because analog designs lean on this
technology:

- **Diffusion:** `nplus_u` (unsilicided N+), `pplus_u` (unsilicided P+),
  `nplus_s`, `pplus_s` (silicided variants with lower sheet R).
- **N-well under STI:** `nwell`
- **Poly:** `npolyf_u`, `ppolyf_u`, `npolyf_s`, `ppolyf_s`.
- **High-R poly:** `ppolyf_u_1k`, `ppolyf_u_2k` (3.3 V area),
  `ppolyf_u_1k_6p0`, `ppolyf_u_2k_6p0` (6 V area), `ppolyf_u_3k`.
- **Metal resistors:** `rm1`, `rm2`, `rm3`, `rm4` — 2-terminal metal
  resistors for precision trimming.
- **Top-metal high-value:** `tm6k`, `tm9k`, `tm11k`, `tm30k` — match the
  metal-stack variant (C vs D) you are using.

### BJTs, diodes, and other

- **NPN:** `npn_10p00x10p00`, `npn_05p00x05p00`, plus small-geometry
  vertical variants `npn_00p54x02p00`, `npn_00p54x04p00`,
  `npn_00p54x08p00`, `npn_00p54x16p00`.
- **PNP (vertical):** `pnp_10p00x10p00`, `pnp_05p00x05p00`,
  `pnp_10p00x00p42`, `pnp_05p00x00p42`.
- **Diodes:** `diode_nd2ps_03v3`, `diode_pd2nw_03v3`, and 6 V equivalents,
  plus well/substrate diodes and a Schottky.
- **eFuse:** `efuse` — a one-time programmable fuse.

### Device model structure and binning

Models are BSIM4 (`level = 54`) and are binned in W/L. You'll see multiple
`.model` cards per device with `lmin`/`lmax`/`wmin`/`wmax` windows, in the
same pattern as Sky130. For the general theory of BSIM4 parameters and
binning, see [Spice Device Models](spice-models.md) — the discussion there
applies directly to gf180mcu as well. The key practical difference is that
gf180mcu's corner structure is **per-device-family** (separate `typical`,
`bjt_typical`, `diode_typical`, `res_typical`, `mimcap_typical` corners)
rather than one unified corner per PVT point.

## Standard cells

gf180mcu ships **two** standard cell libraries, each with 229 cells:

- `gf180mcu_fd_sc_mcu7t5v0` — **7 tracks tall** (3.92 µm).
  Denser, smaller area. Use for area-constrained digital.
- `gf180mcu_fd_sc_mcu9t5v0` — **9 tracks tall** (5.04 µm).
  More M1 pin access, better timing for cells with many input pins.
  Use for performance-critical or complex-cell-heavy designs.

Both use a **0.56 µm site width** and target 5 V operation (hence `5v0`
in the name). You pick one library per chip; mixing 7-track and 9-track
rows in the same floorplan is not supported.

Cell naming is similar to Sky130 but with two underscores after the
library name and the drive strength as a trailing integer:

```
gf180mcu_fd_sc_mcu7t5v0__inv_1         # size-1 inverter
gf180mcu_fd_sc_mcu7t5v0__addf_4        # drive-4 full adder
gf180mcu_fd_sc_mcu9t5v0__and3_2        # drive-2 3-input AND
```

Every cell has four rail pins in its `.subckt` header: `VDD`, `VSS`,
`VNW` (N-well tap), `VPW` (P-well tap). Sky130's HD cells use `VPWR`,
`VGND`, `VPB`, `VNB`. The mapping is direct but string-substitution in
testbenches has to account for it.

### Standard cell timing views (`.lib`)

The 7-track library ships **15 Liberty files**, one per PVT corner:

- **Corners:** `ff`, `tt`, `ss`
- **Temperatures:** −40 °C, 25 °C, 125 °C
- **Voltages:** `1v62`/`1v80`/`1v98` (nominal 1.8 V), `3v00`/`3v30`/`3v60`
  (nominal 3.3 V), `4v50`/`5v00`/`5v50` (nominal 5 V)

Sky130 by contrast ships 18 `.lib` files and all at 1.8 V-ish rails.
gf180mcu's wider voltage coverage is what makes it the right PDK for
chips that talk to 5 V rails.

For multi-corner STA setup, the mechanics are identical to Sky130; see
[Multi-Corner Timing Analysis](sta-mc.md).

## Metal stack

The maximum metal stack (variant `C` or `D`, 5 routing metals) is:

```
                (top, thickest, cheapest R)
     Metal5   ─── routing + power + optional top-metal inductor
     Via4
     Metal4
     Via3
     Metal3
     Via2
     Metal2
     Via1
     Metal1
     CON     ─── contacts to poly/diff
     Poly2   ─── gate poly
     Nwell / Pwell
                (bottom)
```

gf180mcu **does not have an `li1`-style local interconnect layer**. Every
intra-cell wire you see is Metal1. That pushes more routing pressure onto
Metal1 inside standard cells than Sky130 faces, which is part of why
gf180mcu's 7-track library is less dense than Sky130's 6-track HD library.

Preferred routing direction alternates by layer: Metal1 horizontal,
Metal2 vertical, Metal3 horizontal, Metal4 vertical, Metal5 horizontal.

## Corners

gf180mcu splits corners across **device families** rather than lumping
everything into one process corner. In `sm141064.ngspice` you will find:

| Family                 | Corners available                       |
|------------------------|-----------------------------------------|
| MOSFET                 | `typical`, `ff`, `ss`, `fs`, `sf`       |
| BJT                    | `bjt_typical`, `bjt_ff`, `bjt_ss`       |
| Diode                  | `diode_typical`, `diode_ff`, `diode_ss` |
| Resistor               | `res_typical`, `res_ff`, `res_ss`       |
| MIM capacitor          | `mimcap_typical`, `mimcap_ss`, `mimcap_ff` |

This matters for mixed-signal sign-off: a bandgap reference wants the
worst-case BJT + resistor + MIM cap combination, which may not be the
same as the worst-case MOSFET corner. In your testbench you can select
each family's corner independently:

```
.lib "$PDK_ROOT/gf180mcuC/libs.tech/ngspice/sm141064.ngspice" typical
.lib "$PDK_ROOT/gf180mcuC/libs.tech/ngspice/sm141064.ngspice" res_ss
.lib "$PDK_ROOT/gf180mcuC/libs.tech/ngspice/sm141064.ngspice" bjt_ff
```

Monte Carlo mismatch is enabled via `design.ngspice` — set
`sw_stat_mismatch=1` and optionally `sw_stat_global=1` for combined
intra-die mismatch + inter-die global variation. See
[Spice Device Models](spice-models.md) for the underlying mechanism.

## I/O and SRAM

- `gf180mcu_fd_io` contains ESD-hardened pad cells for digital in/out/
  bidirectional, analog signal pass-through, power/ground, level shifters,
  and corner cells. Pad names follow the pattern `gf180mcu_fd_io__<type>`,
  e.g. `in_c`, `in_s`, `bi_t`, `bi_24t`, `asig_5p0`, `cor`, `fill1`,
  `dvdd`, `dvss`, `brk2`, `brk5`.
- `gf180mcu_fd_ip_sram` ships four pre-built SRAM macros:
  64 × 8, 128 × 8, 256 × 8, 512 × 8 (all byte-wide, with write-mask).
  If you need a different shape, generate one with OpenRAM.

## Related tutorials

- **Installing ciel and the basic PDK invocation model:** [Sky130 PDK](sky130.md) — most of the mechanics transfer.
- **BSIM4 parameters, binning, Monte Carlo mismatch:** [Spice Device Models](spice-models.md)
- **Running SPICE with PDK libraries:** [SPICE Syntax](spice.md), [Ngspice Usage](ngspice.md)
- **Multi-corner STA setup:** [Multi-Corner Timing Analysis](sta-mc.md)
- **Layout, DRC, LVS on open PDKs:** [KLayout](klayout.md), [KLayout DRC](klayout-drc.md), [KLayout LVS](klayout-lvs.md)

# License

Copyright 2026 VLSI-DA (see [LICENSE](license.md) for use)
