# OpenSTA Tutorial

## Running OpenSTA

OpenSTA is a command line tool. To run it, open a terminal and type `sta`.

```
$ sta
OpenSTA 2.6.0 GITDIR-NOT Copyright (c) 2024, Parallax Software, Inc.
License GPLv3: GNU GPL version 3 <http://gnu.org/licenses/gpl.html>

This is free software, and you are free to change and redistribute it
under certain conditions; type `show_copying' for details.
This program comes with ABSOLUTELY NO WARRANTY; for details type `show_warranty'.
warning: `/var/empty/.tclsh-history' is not writable.
sta [/home/user/chip-tutorials/sta]
```

However, it is also integrated into OpenROAD. You can run the same commands there:

```
$ openroad
OpenROAD edf00dff99f6c40d67a30c0e22a8191c5d2ed9d6
Features included (+) or not (-): +Charts +GPU +GUI +Python
This program is licensed under the BSD-3 license. See the LICENSE file for details.
Components of this program may be licensed under more restrictive licenses which must be honored.
warning: `/var/empty/.tclsh-history' is not writable.
openroad>
```

These tutorials all use [TCL (Tool Command
Language)](https://www.tcl.tk/man/tcl8.5/tutorial/tcltutorial.html) scripts to
interact with OpenSTA. You don't need to master TCL, but you should be familiar with
it. It is based on LISP but with customized commands for EDA tools.

This tutorial will utilize the spm design example final output that was created by OpenLane2.
You should untar the file for this tutorial:
```bash
tar -zxvf final.tar.gz
```
which will create the final subdirectory with subdirectories for the different design files.
The ones that we are concerned with are the following:
- def
- lef
- lib
- odb
- pnl
- sdc
- sdf
- spef
- spice
- vh


## Single corner timing analysis

There are four main steps to setting up a timing analysis. 
1. Read in the library file(s)
1. Read in the design file(s)
1. Read in the parasitic file(s)
1. Read in the constraints file(s)

The following is an example that does this:
```tcl
read_lib $env(PDK_ROOT)/sky130A/libs.ref/sky130_fd_sc_hd/lib/sky130_fd_sc_hd__ss_100C_1v60.lib
read_db odb/spm.odb 
read_spef spef/max/spm.max.spef
read_sdc sdc/spm.sdc
```

###  Other ways to read the design file(s)

Instead of reading the ODB (OpenROAD database format) file, you can use
gate-level verilog file or the DEF (Design Exchange Format) file. However,
these both require that you also read in the LEF technology and cell files. This would replace the
reading of the design above with these multiple steps like this for the DEF:
```tcl
read_lef $env(PDK_ROOT)/sky130A/libs.ref/sky130_fd_sc_hd/techlef/sky130_fd_sc_hd__nom.tlef
read_lef $env(PDK_ROOT)/sky130A/libs.ref/sky130_fd_sc_hd/lef/sky130_fd_sc_hd.lef
read_lef $env(PDK_ROOT)/sky130A/libs.ref/sky130_fd_sc_hd/lef/sky130_ef_sc_hd.lef
read_def def/spm.def
```
or like this for the gate-level Verilog:
```tcl
read_lef $env(PDK_ROOT)/sky130A/libs.ref/sky130_fd_sc_hd/techlef/sky130_fd_sc_hd__nom.tlef
read_lef $env(PDK_ROOT)/sky130A/libs.ref/sky130_fd_sc_hd/lef/sky130_fd_sc_hd.lef
read_lef $env(PDK_ROOT)/sky130A/libs.ref/sky130_fd_sc_hd/lef/sky130_ef_sc_hd.lef
read_verilog nl/spm.nl.v
link_design spm
```
The other steps (library files, parasitics, and constraints) are the same. Note
that with the Verilog method, the `link_design` command will report a few
missing liberty files:
```
[WARNING ORD-2011] LEF master sky130_ef_sc_hd__decap_12 has no liberty cell.
[WARNING ORD-2011] LEF master sky130_fd_sc_hd__fill_1 has no liberty cell.
[WARNING ORD-2011] LEF master sky130_fd_sc_hd__fill_2 has no liberty cell.
[WARNING ORD-2011] LEF master sky130_fd_sc_hd__tapvpwrvgnd_1 has no liberty cell.
```
but that is ok since they are special cells that do not have timing.


## Reporting timing


## Reporting power


```tcl
set_power_activity -input 0.1
set_power_activity -input_port clk 0.5
set_power_activity -input_port rst 0.0
report_power
```

You can also use VCD (Verilog Change Dump) files to get the activity for better accuracy:
```tcl
read_vcd -scope tb/spm spm.vcd
```
if you've created a file with your testbench, `tb`.


## Multi-corner timing analysis

```tcl
define_corners wc bc typ
read_lib -corner wc $env(PDK_ROOT)/sky130A/libs.ref/sky130_fd_sc_hd/lib/sky130_fd_sc_hd__ss_100C_1v60.lib
read_lib -corner bc $env(PDK_ROOT)/sky130A/libs.ref/sky130_fd_sc_hd/lib/sky130_fd_sc_hd__nom_n40C_1v95.lib
fead_lib -corner typ $env(PDK_ROOT)/sky130A/libs.ref/sky130_fd_sc_hd/lib/sky130_fd_sc_hd__tt_025C_1v80.lib
read_db odb/spm.db
read_spef -corner wc spef/max/spm.max.spef
read_spef -corner bc spef/max/spm.min.spef
read_spef -corner typ spef/max/spm.nom.spef
read_sdc sdc/spm.sdc
report_checks
```

## SDC (Synopsys Design Constraints)

## Ideal vs propagated clocks


## OpenROAD Timing GUI

OpenROAD has a GUI that can be used to view the timing results. You can open it
by running `openroad -gui` and running the previous commands in the "TCL Commands"
portion of OpenROAD. It is recommended
to use the ODB or DEF design files as these have the placement information. 
Once you do this, click on the "Timing Report" tab and then click the "Update" button
to run the timing analysis. You should see something like this:

![Timing Analysis in OpenROAD](sta/openroad-timing.png)

You can select the top ranked path (and expand the window sizes) to see the details 
of the path like this:

![Timing Path in OpenROAD](sta/openroad-timing-report.png)

The path should also be highlighted in the layout to see the placement. However, the color 
defaults to black. (Submit a PR to this tutorial if you know how to fix it!)


