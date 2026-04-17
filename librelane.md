---
title: LibreLane
nav_order: 25
---

# LibreLane

LibreLane is the successor to OpenLane 2. It is an infrastructure library for
building digital ASIC implementation flows — synthesis, floorplanning, PDN,
placement, CTS, routing, DRC/LVS, sign-off timing — out of open-source EDA
tools. You write a small configuration file describing your design and
LibreLane runs each step in sequence, capturing every intermediate artifact
so that runs are reproducible and steppable.

The project was renamed from OpenLane 2 to LibreLane in early 2026 and moved
from `efabless/openlane2` to `librelane/librelane`. The code is the same
lineage, with the OpenLane 2 history intact; only the name, URL, and
version series (3.0.0 was the first LibreLane-branded release) changed.
See the [Migrating from OpenLane](#migrating-from-openlane-23) section below.

Key links:

* Documentation: <https://librelane.readthedocs.io/>
* Source: <https://github.com/librelane/librelane>
* Project page: <https://librelane.org>

## Table of contents

- [Prerequisites](#prerequisites)
- [Installing LibreLane](#installing-librelane)
- [Smoke test](#smoke-test)
- [Running the SPM example](#running-the-spm-example)
- [The config file](#the-config-file)
- [Run directories and tags](#run-directories-and-tags)
- [Viewing the final design](#viewing-the-final-design)
- [Targeting gf180mcu with wafer.space](#targeting-gf180mcu-with-waferspace)
- [Migrating from OpenLane 2.3](#migrating-from-openlane-23)
- [Help](#help)

## Prerequisites

- **Nix.** LibreLane's first-class install path is Nix with the FOSSi
  binary cache. Set that up first with the [Nix tutorial](nix.md) if you
  haven't already.
- **git.** The install clones the LibreLane repository.
- **Python 3.10+.** LibreLane 3.x requires it; Nix takes care of this for
  you.
- **ciel** with a PDK enabled (see [Sky130](sky130.md) or
  [gf180mcu](gf180mcu.md)). LibreLane defaults to `$HOME/.ciel` as its PDK
  root.
- On Windows, run everything inside [WSL](wsl.md).

## Installing LibreLane

Inside a Nix-enabled shell:

```bash
git clone https://github.com/librelane/librelane
cd librelane
nix-shell
```

The first `nix-shell` pulls prebuilt binaries from the FOSSi cache and
takes roughly 10 minutes. Subsequent invocations open in seconds.

Every time you want to use LibreLane, `cd` into the cloned repo and run
`nix-shell` to enter the environment. Running `exit` (or Ctrl-D) returns
you to your normal shell.

**Docker alternative.** If Nix is impractical for your setup (e.g. a
corporate-managed macOS that blocks the installer), LibreLane also ships
a Docker image. After installing it with `pip install --upgrade librelane`,
prefix every `librelane` command with `--dockerized`:

```bash
python3 -m pip install --upgrade librelane
librelane --dockerized --smoke-test
```

The Docker path uses the same workflow as the Nix path, just with
`--dockerized` added to every invocation.

**pip-only installation is unsupported.** You would have to bring your
own compiled versions of OpenROAD, Yosys, KLayout, Magic, and Netgen,
which defeats the point. Use Nix or Docker.

## Smoke test

Inside the nix-shell, verify the install with:

```bash
librelane --smoke-test
```

This runs a minimal design end-to-end through every built-in step. It
should finish with `Smoke test passed.` Warnings are normal; errors are
not.

## Running the SPM example

LibreLane ships with a collection of example designs. The canonical first
run is SPM (a small serial-parallel multiplier):

```bash
python3 -m librelane --pdk-root $HOME/.ciel ./librelane/examples/spm/config.yaml
```

This pulls in the shipped configuration, runs the full Classic flow, and
produces the final GDS. Artifacts land in
`./librelane/examples/spm/runs/RUN_<timestamp>/`.

Inside the run directory you will find:

| Subdirectory  | Contents                                             |
|---------------|------------------------------------------------------|
| `final/`      | Post-flow GDS, DEF, ODB, SDC, SPEF, Liberty timing   |
| `*-*/`        | One directory per flow step, numbered in order       |
| `logs/`       | Per-step tool logs                                   |
| `reports/`    | Per-step reports (timing, DRC, LVS summaries)        |
| `metrics.csv` | Aggregated metrics for the whole run                 |

## The config file

LibreLane accepts configs in either JSON or YAML. A minimal example for a
Sky130 synthesis run:

```yaml
# config.yaml
DESIGN_NAME: my_design
VERILOG_FILES: ["./src/my_design.v"]
CLOCK_PORT: clk
CLOCK_PERIOD: 10       # ns
PDK: sky130A
```

Every other knob has a default. The [Universal Flow Configuration
Variables](https://librelane.readthedocs.io/en/latest/reference/flow_config_vars.html)
reference lists all of them. The most-common ones to override in
practice:

- `FP_CORE_UTIL` — target core utilization percentage
- `FP_ASPECT_RATIO` — core aspect ratio (height/width)
- `DIE_AREA` / `CORE_AREA` — explicit floorplan override
- `PL_TARGET_DENSITY` — placer density target
- `SYNTH_STRATEGY` — yosys synthesis strategy
- `RUN_HEURISTIC_DIODE_INSERTION` — antenna mitigation
- `MAX_FANOUT_CONSTRAINT` — fanout limit
- `CLOCK_TREE_SYNTHESIS` — CTS tool selection
- `USE_SLANG` — use Slang for SystemVerilog parsing (LibreLane 3+)

If you have a working OpenLane 2 config, read the [Migrating from
OpenLane](#migrating-from-openlane-23) section first — several variable
names changed.

## Run directories and tags

By default, each run creates a fresh directory named
`RUN_<YYYY-MM-DD>_<HH-MM-SS>`. To name a run explicitly, pass
`--run-tag`:

```bash
python3 -m librelane --run-tag my_run --pdk-root $HOME/.ciel config.yaml
```

Re-running with the same tag requires `--overwrite`:

```bash
python3 -m librelane --run-tag my_run --overwrite --pdk-root $HOME/.ciel config.yaml
```

The shortcut `--last-run` refers to whichever run finished most recently.

## Viewing the final design

You can launch OpenROAD directly against the final database:

```bash
openroad -gui
```

and then inside the OpenROAD GUI load the final ODB, SPEF, SDC, and a
Liberty view that matches the corner you want to analyse. For example:

```tcl
read_lib $env(PDK_ROOT)/sky130A/libs.ref/sky130_fd_sc_hd/lib/sky130_fd_sc_hd__ss_100C_1v60.lib
read_db designs/spm/runs/RUN_<timestamp>/final/odb/spm.odb
read_spef designs/spm/runs/RUN_<timestamp>/final/spef/max/spm.nom.max.spef
read_sdc designs/spm/runs/RUN_<timestamp>/final/sdc/spm.sdc
```

Save this as a `.tcl` script and `source` it to avoid retyping.

See [Static Timing Analysis](sta.md) and
[Multi-Corner Timing Analysis](sta-mc.md) for the report-generation side
of things once the design is loaded.

## Targeting gf180mcu with wafer.space

[wafer.space](https://wafer.space) is a budget MPW service that currently
runs a gf180mcu flow on a forked branch of LibreLane. If you are
submitting a chip there, you should use their project template rather
than the upstream LibreLane you just installed — the template pins the
exact LibreLane branch they've validated against their PDK fork.

```bash
git clone https://github.com/wafer-space/gf180mcu-project-template
cd gf180mcu-project-template
make clone-pdk      # clones wafer.space's gf180mcu PDK fork
nix-shell           # enters the pinned LibreLane branch
make librelane      # run the flow
```

A few useful make targets once inside the Nix shell:

| Target                   | What it does                                  |
|--------------------------|-----------------------------------------------|
| `make librelane`         | Full digital flow                             |
| `make librelane-padring` | Build the analog pad ring only                |
| `make librelane-openroad`| Open the run in the OpenROAD GUI              |
| `make librelane-klayout` | Open the run in KLayout                       |
| `make sim`               | RTL simulation via cocotb + Icarus            |
| `make sim-gl`            | Gate-level simulation                         |
| `make sim-view`          | GTKWave on the latest waveform                |

Slot geometry (die size) is selectable via the `SLOT` environment
variable. Supported values:

```bash
make librelane                    # default: 1x1 slot
SLOT=0p5x1 make librelane         # half-width slot
SLOT=1x0p5 make librelane         # half-height slot
SLOT=0p5x0p5 make librelane       # quarter slot
```

Before submitting, run the precheck tool against your final GDS:

```bash
export PDK_ROOT=gf180mcu
export PDK=gf180mcuD
python3 precheck.py --input chip_top.gds --slot 1x1
```

Precheck verifies DRC, density, antenna rules, and that the top cell is
named `chip_top` at origin (0, 0) with a 0.001 µm DBU.

Current wafer.space run info, slot pricing, and any submission-packaging
rules live on <https://wafer.space>. Check the site before submission —
those details change per run.

## Migrating from OpenLane 2.3

If you have a working OpenLane 2.3-era config or tutorial, the main
breaking changes you will hit when moving to LibreLane 3.x are:

- **Python 3.10+** is required. Older Pythons no longer work.
- **Synlig → Slang** for SystemVerilog. Set `USE_SLANG: true` in your
  config if you previously relied on Synlig.
- **"The great `FP_` removal."** Many floorplan variables lost their
  `FP_` prefix. Check the
  [Variable Migration Guide](https://librelane.readthedocs.io/en/latest/migrating/index.html)
  and rename anything the loader complains about.
- **Tilde paths are rejected.** The CLI no longer accepts paths with
  ambiguous `~` expansion. Use absolute paths or `$HOME`.
- **DRT antenna repair is on by default.** If you had previously enabled
  it explicitly, remove the redundant flag.
- **`MAGIC_NO_EXT_UNIQUE` → `MAGIC_EXT_UNIQUE`** (enum). Read the
  reference for the new values.
- **`readable_paths` preprocessor directive removed.** Replace with
  plain paths.

The
[Migrating from OpenLane](https://librelane.readthedocs.io/en/latest/migrating/index.html)
guide in the official docs is authoritative; use it as the checklist.

## Help

LibreLane has a `--help` at every level:

```bash
librelane --help
librelane --list-flows
librelane --list-steps
```

OpenROAD (not LibreLane) has `man` pages accessible from inside its TCL
shell at three levels:

- Top-level: `man openroad`
- Per-module / TCL command: `man clock_tree_synthesis`
- Error / warning codes: `man CTS-0001`

Documentation:

- LibreLane: <https://librelane.readthedocs.io/>
- OpenROAD: <https://openroad.readthedocs.io/>
- Community chat: <https://fossi-chat.org>

# License

Copyright 2024 VLSI-DA (see [LICENSE](LICENSE) for use)
