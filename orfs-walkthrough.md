# Running an example design

This assumes that the smoke test runs and you've [installed ORFS properly](orfs-installation.md).

The documentation is available at [ReadTheDocs](https://openroad.readthedocs.io/en/latest/).

ORFS uses a Makefile to run the flow scripts. Specifically, it goes through the following steps that you see in the output
of a successful run:

```
Log                            Elapsed seconds Peak Memory/MB
1_1_yosys                                    0             42
1_1_yosys_canonicalize                       0             38
2_1_floorplan                                0             97
2_2_floorplan_macro                          0             93
2_3_floorplan_tapcell                        0             93
2_4_floorplan_pdn                            0             95
3_1_place_gp_skip_io                         0             94
3_2_place_iop                                0             94
3_3_place_gp                                 1            194
3_4_place_resized                            0            113
3_5_place_dp                                 0             99
4_1_cts                                      4            120
5_1_grt                                     10            213
5_2_route                                   17           1175
5_3_fillcell                                 0             97
6_1_fill                                     0             95
6_1_merge                                    1            390
6_report                                     0            137
Total                                       33           1175
```

Step 1 (1_1_yosys and 1_1_yosys_canonicalize) is the synthesis step, where the
Verilog source files are converted to a gate-level netlist. The next steps
(2_1_floorplan to 2_4_floorplan_pdn) are the floorplanning steps, where the any
fixed blocks are placed and the power supply network is created. The next steps
(3_1_place_gp_skip_io to 3_5_place_dp) are the placement steps, where the gates
and IO cells (around the perimeter) are placed in the design. The
3_4_place_resized step is the first timing optimization step, where the gates
are resized, buffered, etc. to help meet timing. The placement is divided into
global (3_3_place_gp) and detailed placement (3_5_place_dp) steps. Clock tree
synthesis (CTS) is the next step (4_1_cts), where the clock tree is built to
ensure that the clock has low skew to all the sequential elements in the
design. Global routing (5_1_grt) is the next step, where the the general paths
of wires are created to minimize congestion and ensure that the design can be
routed. After that, the design is detail routed (5_2_route), where the wires
are placed in the routing layers. The final steps of fill cell insertion
(5_3_fillcell) and fill (6_1_fill) are done to ensure that the design has
enough density for manufacturing. The final step (6_1_merge) merges the fill
cells into the design, and the report (6_report) step describes the final
design, including the timing, area, and power information.

While running ```make``` ran the default design, you can pass a variable to the Makefile with a configuration file
to run other designs. The default runs this:

```
make DESIGN_CONFIG=./designs/nangate45/gcd/config.mk
```

You can implement this in the ASAP7 technology, but using this config:

```
make DESIGN_CONFIG=./designs/asap7/gcd/config.mk
```

# Run directories

The results (output files) are put in ```results/<techology>/<design>/base```,
where ```<technology>``` is the technology used (e.g. nangate45, asap7, etc.),
```<design>``` is the design name (e.g. gcd). The results directory is created
if it does not exist.

The log files are put in ```logs/<technology>/<design>/base```. There is one
log file per flow step.

The reports (e.g. timing, area, power) are put in
```reports/<technology>/<design>/base```. Each step has reports depending on what
it does.

# Viewing the final design

The --last-run option is also a shortcut for the last run directory. To view the last design in
the OpenROAD GUI, you can run:

```bash
make DESIGN_CONFIG=./designs/nangate45/gcd/config.mk gui_final
```

# Config files

The config files contain parameters for the design, such as the technology, the
input files, the constraints, etc. The important parts of a config file
are:

```
# Specifies the technology subdirectory.
export PLATFORM    = nangate45
# Input file list (a single file or a list of files).
export VERILOG_FILES = $(DESIGN_HOME)/src/$(DESIGN_NAME)/gcd.v
# The timing constraint file.
export SDC_FILE      = $(DESIGN_HOME)/$(PLATFORM)/$(DESIGN_NAME)/constraint.sdc
# It picks a floorplan size so that the logic cells use 55\% of the area.
export CORE_UTILIZATION ?= 55
```

You can see all of the options documented here:

# Help

There is an [ORFS tutrorial](https://openroad-flow-scripts.readthedocs.io/en/latest/tutorials/FlowTutorial.html).

OpenROAD has some options for help via the ``man`` command like most
Unix systems. These manual pages provide detailed information about how to use
a particular command or function, along with its syntax and options.

This can be used for a range of commands in different levels as follows:

* Level 1: Top-level openroad command (e.g. ``man openroad``)
* Level 2: Individual module/TCL commands (e.g. ``man clock_tree_synthesis``)
* Level 3: Info, error, warning messages (e.g. ``man CTS-0001``)

The OpenROAD documentation is available at [ReadTheDocs](https://openroad.readthedocs.io/en/latest/).

# License

Copyright 2024 VLSI-DA (see [LICENSE](LICENSE) for use)
