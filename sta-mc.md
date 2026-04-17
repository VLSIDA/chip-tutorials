# Multi-corner timing analysis

Timing a design at one operating point is rarely enough. A chip leaving the
fab lands somewhere on a process-variation distribution, runs at a supply
voltage that droops under load, and operates across a temperature range.
Collectively these dimensions are called **PVT** — process, voltage,
temperature — and each named combination we analyse is a *corner*.

## Why multiple corners?

We usually care about two timing checks:

- **Setup** — is the data at the capturing flop's D pin *at least* `T_setup`
  before the next clock edge? Setup fails when the design runs too *slow*.
- **Hold** — does the data at the capturing flop's D pin remain stable for
  *at least* `T_hold` after the clock edge? Hold fails when the design
  runs too *fast* (a short path beats the clock from the launch flop to
  the capture flop).

Put together, you need to prove setup against the *slow* worst case and
hold against the *fast* worst case. That's the minimum — two corners.

In practice neither corner is a single point:

| Axis         | Slow side                          | Fast side                         |
|--------------|------------------------------------|-----------------------------------|
| Process      | SS (slow-NMOS / slow-PMOS)         | FF                                |
| Voltage      | Low V_DD (min-rail after droop)    | High V_DD (max-rail after rise)   |
| Temperature  | For setup: usually hot (100 °C+) for delay; for hold: cold (−40 °C)      | Opposite for each check |
| Interconnect | High-R / high-C ("max" SPEF)       | Low-R / low-C ("min" SPEF)        |

The temperature story flips depending on technology: in older nodes
hot = slowest, but modern nodes can show "inverse temperature dependence"
where cold is the slow corner for some cells. This is another reason
you analyse multiple corners rather than reasoning from first principles.

Modern designs routinely check dozens of corners — different on-chip
variation seeds, multiple supply rails, ECO fixes, library recharacterisation
— but the core pattern is small. The example below uses three: a typical
(`typ`), a worst-case for setup (`wc`), and a best-case for hold (`bc`).

## Defining corners

OpenSTA supports reading different Liberty, SPEF, and parasitic files
per corner, all in one session:

```tcl
define_corners wc bc typ

read_lib -corner wc  $env(PDK_ROOT)/sky130A/libs.ref/sky130_fd_sc_hd/lib/sky130_fd_sc_hd__ss_100C_1v60.lib
read_lib -corner bc  $env(PDK_ROOT)/sky130A/libs.ref/sky130_fd_sc_hd/lib/sky130_fd_sc_hd__ff_n40C_1v95.lib
read_lib -corner typ $env(PDK_ROOT)/sky130A/libs.ref/sky130_fd_sc_hd/lib/sky130_fd_sc_hd__tt_025C_1v80.lib

read_db odb/spm.odb

read_spef -corner wc  spef/max/spm.max.spef
read_spef -corner bc  spef/min/spm.min.spef
read_spef -corner typ spef/nom/spm.nom.spef

read_sdc sdc/spm.sdc
report_checks
```

Key points:

- `define_corners` lists the corner names. Each subsequent `-corner <name>`
  flag on `read_lib` / `read_spef` associates a file with that corner.
- The slow corner (`wc`) gets the `ss` Liberty at high temperature and low
  voltage *and* the "max" (worst-case R/C) SPEF — the combination that
  produces the worst setup margin.
- The fast corner (`bc`) gets the `ff` Liberty at cold and high voltage
  *and* the "min" SPEF — worst hold margin.
- The typical corner (`typ`) uses `tt` at 25 °C, 1.8 V, and the nominal
  SPEF. Typical is informational — sign-off gates are the wc/bc pair.

## Reporting per corner

`report_checks -corner <name>` runs the path-based check in the context
of a specific corner:

```tcl
# Setup (max path) at slow corner
report_checks -corner wc -path_delay max

# Hold (min path) at fast corner
report_checks -corner bc -path_delay min

# Sanity-check at typical
report_checks -corner typ
```

Without `-corner`, OpenSTA walks *every* defined corner and returns the
worst-slack path across all of them. That's a good sign-off sweep:

```tcl
report_checks -path_delay max      # worst setup across all corners
report_checks -path_delay min      # worst hold across all corners
```

Pair this with aggregated reports (see
[STA Reporting](sta-reports.md#summary-reports)) to get per-corner TNS /
WNS summaries rather than walking individual paths.


# License

Copyright 2024 VLSI-DA (see [LICENSE](LICENSE) for use)
