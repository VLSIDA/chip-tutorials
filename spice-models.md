# SPICE Device Models

The `M` card in a SPICE netlist only specifies *how* a transistor is connected
and its geometry (W, L). The transistor's electrical behavior — how much
current flows for a given V_GS and V_DS, how the threshold voltage shifts with
bulk bias, how capacitance depends on the operating region — all comes from a
`.MODEL` statement referenced by the `M` card.

This tutorial walks through what is inside a `.MODEL`, starting from the
simplest Level 1 MOSFET model and building up to the BSIM4 model that Sky130
actually ships. It also explains *binning*, which is how Sky130 (and most
modern PDKs) stitch together dozens of separate model cards to cover the full
W/L design space.

## The `.MODEL` card

A `.MODEL` card has this general form:

```
.MODEL <name> <type> ( <param1>=<value> <param2>=<value> ... )
```

- `name` is the identifier referenced by the `M` card (e.g. `PCH`, `NCH`).
- `type` is `nmos` or `pmos` for MOSFETs.
- The parameter list is what selects the *flavor* of the model and supplies
  all of its fitting coefficients.

The single most important parameter is `level`, which selects *which physical
model the simulator will evaluate*. Different levels are different equations
with different parameter sets. A few common levels:

| `level` | Model              | Notes                                     |
|---------|--------------------|-------------------------------------------|
| 1       | Shichman-Hodges    | Textbook square-law model. ~10 parameters.|
| 2, 3    | Early short-channel fixes | Still simple, mostly obsolete.      |
| 8       | BSIM3v3 (in some sims)    | Legacy.                             |
| 49      | BSIM3                      | First widely-used sub-micron model. |
| 54      | BSIM4                      | Sky130, most 180nm–14nm PDKs.       |
| 72      | BSIM-CMG                   | FinFET / multi-gate.                |

A simulator will *silently ignore* parameters that are not used by the
selected `level`, so a level mismatch can produce results that look
plausible but are actually wrong.

## Level 1: Shichman-Hodges

Level 1 is the model taught in every first-course on CMOS. The saturation
drain current is the familiar square law:

```
I_D = (KP/2) * (W/L) * (V_GS - V_T)^2 * (1 + LAMBDA * V_DS)
```

with `V_T` modulated by the body effect:

```
V_T = VTO + GAMMA * ( sqrt(PHI - V_BS) - sqrt(PHI) )
```

The whole DC model is controlled by a handful of parameters:

| Parameter | Meaning                                        | Typical units |
|-----------|------------------------------------------------|---------------|
| `VTO`     | Zero-bias threshold voltage                    | V             |
| `KP`      | Transconductance parameter, `µ * Cox`          | A/V^2         |
| `GAMMA`   | Body-effect coefficient                        | V^0.5         |
| `PHI`     | Surface inversion potential, `2 * φ_F`         | V             |
| `LAMBDA`  | Channel-length modulation                      | 1/V           |
| `TOX`     | Gate oxide thickness (used to derive `Cox`)    | m             |
| `NSUB`    | Substrate doping                               | cm^-3         |
| `LD`      | Lateral diffusion (effective L shortening)     | m             |
| `CGSO`, `CGDO` | Gate-source/drain overlap capacitance     | F/m           |
| `CJ`, `CJSW`   | Zero-bias junction cap (area / sidewall)  | F/m^2, F/m    |

A complete Level 1 NMOS card looks like this:

```
.MODEL NCH nmos
+ level=1
+ VTO=0.5 KP=120u GAMMA=0.4 PHI=0.7 LAMBDA=0.02
+ TOX=4.1n LD=0.01u
+ CGSO=0.3n CGDO=0.3n CJ=1m CJSW=0.3n
```

Level 1 is perfect for hand analysis and for teaching, but it is useless for
real design below roughly 1 µm:

- `I_D` is a pure square law. Real short-channel devices enter *velocity
  saturation* well before `V_DS = V_GS - V_T`, so the square law
  over-predicts current by large factors.
- There is no drain-induced barrier lowering (DIBL), no subthreshold slope
  parameter (the model is literally zero below threshold), no mobility
  degradation with vertical field, no gate leakage, no temperature model
  beyond a constant `TNOM`.
- W and L do not appear in any of the parameters above — there is a single
  set of coefficients for *every* device size.

That last point is what motivates both BSIM and binning.

## BSIM4 (level 54): what Sky130 ships

Sky130's `sky130_fd_pr__nfet_01v8` is a BSIM4 model. The first few lines of
one model card show the pattern (file
`sky130A/libs.ref/sky130_fd_pr/spice/sky130_fd_pr__nfet_01v8.pm3.spice`):

```
.model sky130_fd_pr__nfet_01v8__model.0 nmos
+ lmin = 1.45e-07 lmax = 1.55e-07 wmin = 1.255e-06 wmax = 1.265e-6
+ level = 54.0
+ version = 4.5
+ tnom = 30.0
+ toxe = 4.148e-9
+ vth0 = 0.49439 + sky130_fd_pr__nfet_01v8__vth0_diff_0
+ u0   = 0.030197 + sky130_fd_pr__nfet_01v8__u0_diff_0
+ vsat = 176320 + sky130_fd_pr__nfet_01v8__vsat_diff_0
+ ...
```

BSIM4 has on the order of 200+ parameters. A few are direct descendants of
the Level 1 names:

| BSIM4    | Level 1 analogue         |
|----------|--------------------------|
| `vth0`   | `VTO`                    |
| `u0`     | part of `KP` (`µ`)       |
| `toxe`   | `TOX`                    |
| `k1`, `k2` | refined body-effect, replacing `GAMMA`/`PHI` |
| `pclm`   | replaces `LAMBDA`        |

The rest are what make BSIM4 usable at 130 nm:

- Short-channel effects: `dvt0`, `dvt1`, `dvt2`, `lpe0`, `lpeb`
- Velocity saturation: `vsat`, `a0`, `ags`
- Mobility degradation: `ua`, `ub`, `uc`, `eu`
- Subthreshold: `voff`, `nfactor`, `cdsc*`, `eta0`
- DIBL and output conductance: `pclm`, `pdiblc1`, `pdiblc2`, `drout`
- Gate leakage: `aigc`, `bigc`, `cigc`, `nigc`, ...
- GIDL, noise, RF, temperature, layout-dependent parasitics: their own
  sub-blocks of parameters

Two Sky130-specific idioms are worth noting in that model card:

1. **Parameter arithmetic with a `_diff_N` suffix.** Values like
   `0.49439 + sky130_fd_pr__nfet_01v8__vth0_diff_0` let the nominal
   coefficient be adjusted per bin without touching the base number. The
   `_diff_0`, `_diff_1`, ... values live in the corner files
   (`corners/tt/discrete.spice`, `corners/ss/...`), which is how one set of
   model cards can be retargeted across TT / SS / FF / SF / FS without
   duplication.
2. **Mismatch injection.** Many parameters also include a term like
   `MC_MM_SWITCH * AGAUSS(0, 1.0, 1) * (vth0_slope / sqrt(l*w*mult))`. When
   `MC_MM_SWITCH` is set to 1 for a Monte Carlo mismatch run, each instance
   gets an independent Gaussian perturbation scaled by `1/sqrt(W*L)` — the
   Pelgrom law, built straight into the model.

## Binning

Sky130's `nfet_01v8` does not contain one BSIM4 model card; it contains
**63** of them, one per bin. The header comment says so explicitly:

```
* SKY130 Spice File.
* Number of bins: 63
```

Each bin is a full `.model` card with its own `lmin`/`lmax`/`wmin`/`wmax`
range and its own tuned coefficients.

### Why binning exists

Even a 200-parameter model like BSIM4 cannot fit every combination of W and
L across two decades of geometry with a single set of numbers. The fitting
residuals are acceptable in a narrow W/L window but grow as you move away
from the device sizes that were measured. Rather than accept a compromise
fit, foundries **partition the W/L plane into bins** and fit each bin
separately. Inside a bin, the model is accurate; across bin boundaries, the
coefficients jump.

### How a simulator picks a bin

The BSIM4 bin-selection convention uses `lmin`, `lmax`, `wmin`, `wmax` on
each model card. The simulator matches the `M` card's instance W and L
against those ranges and picks the first model whose range contains the
requested geometry. In the Sky130 Ngspice files this is exposed with the
Berkeley-style `.N` suffix on the model name:

```
.model sky130_fd_pr__nfet_01v8__model.0 nmos ...
.model sky130_fd_pr__nfet_01v8__model.1 nmos ...
.model sky130_fd_pr__nfet_01v8__model.2 nmos ...
...
```

All 63 cards share the base name `sky130_fd_pr__nfet_01v8__model`; the `.0`,
`.1`, ... are the bin indices. When an instance references the base name,
Ngspice scans the bin table and chooses the one whose `lmin..lmax` and
`wmin..wmax` window brackets the requested L and W.

### Sky130's bin grid

The bins are *not* a regular grid. They are a hand-picked list of (W, L)
rectangles that covers the geometries the foundry cares about supporting:

- Minimum-length devices are binned densely in W, from the minimum
  ~0.36 µm up through 7 µm, because standard cells live here.
- Longer devices (L = 0.25, 0.5, 1, 2, 5, 8 µm) are binned more sparsely
  because they are used for analog where a few canonical sizes dominate.
- Each bin window is extremely tight — e.g. `lmin=0.145 µm`,
  `lmax=0.155 µm`, a ±5 nm window around L=0.15 µm. **You must instantiate
  the transistor at a W and L that falls inside a bin window** or the
  simulator will fail to find a matching model.

This is why you see Sky130 standard cells use specific magic sizes like
`l=0.15u w=0.65u`, `l=0.15u w=1.0u`, `l=0.15u w=1.26u`, and so on: those are
the centers of bins. Picking an arbitrary W like 0.73 µm is not safe — it
may fall in a gap between bins, and even if it doesn't, the foundry never
characterized the device at that size.

### Practical consequences

- **Do not linearly sweep W or L in a simulation** without checking that
  every point lands inside a bin. A continuous sweep across a bin boundary
  will show a visible discontinuity in I-V curves; a point that falls in a
  gap will fail outright.
- **Sky130 ships a Python helper** (`parameters/` directory) that enumerates
  the legal bin centers. For analog work, pick from that list.
- **Every corner file must carry the same bin structure.** That's why
  `corners/tt/discrete.spice` and `corners/ss/discrete.spice` each
  define 63 `_diff_N` rows — one per bin.

## Summary

- A SPICE MOSFET's electrical behavior is defined by a `.MODEL` card; `level`
  selects which equations are evaluated.
- Level 1 (Shichman-Hodges) has ~10 parameters and is a teaching model only.
- Sky130 uses BSIM4 (level 54), which has hundreds of parameters covering
  short-channel effects, mobility, subthreshold conduction, gate leakage,
  noise, and temperature.
- No single BSIM4 card fits all device sizes, so Sky130 ships 63 bins per
  device flavor, each with tight `lmin`/`lmax`/`wmin`/`wmax` windows and its
  own fitted coefficients. Instances must be sized to land inside a bin.

# License

Copyright 2024 VLSI-DA (see [LICENSE](LICENSE) for use)
