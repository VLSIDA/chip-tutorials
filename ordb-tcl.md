# OpenROAD TCL Tutorial

This tutorial provides a brief overview of how to use TCL commands within OpenROAD Flow Scripts. You'll learn how to set up your environment, use basic TCL commands, and integrate them into OpenROAD Flow Scripts. Let's get started!

## Setting Up the Environment

To begin using TCL with OpenROAD, ensure you have the [OpenROAD tools installed](orfs-installation.md).
Once installed, you can access the TCL shell by running the
OpenROAD executable:

```bash
$ openroad
OpenROAD v2.0-22053-g4e2370113b
Features included (+) or not (-): +GPU +GUI +Python : DEBUG
This program is licensed under the BSD-3 license. See the LICENSE file for details.
Components of this program may be licensed under more restrictive licenses which must be honored.
openroad>

```

## Basic TCL Commands

TCL, or Tool Command Language, is a scripting language commonly used in electronic design automation. Here are some basic TCL commands you should know:

- `set`: Assigns a value to a variable.
- `puts`: Outputs a string to the console.
- `expr`: Evaluates an expression.
- `proc`: Defines a procedure to encapsulate reusable code blocks.
- `foreach`: Iterates over each element in a list.

Example:

```tcl
set a 10
set b 20
puts "The sum is: [expr $a + $b]"
```

- Working with Lists: Create a list and iterate over its elements.

Example:

```tcl
set my_list [list 1 2 3 4 5]
foreach item $my_list {
    puts "Item: $item"
}
```

- Defining a Procedure (`proc`): Create a procedure to encapsulate reusable code blocks.

Example:

```tcl
proc greet {name greeting} {
    set msg "$greeting, $name!"
    return $msg
}

set message [greet "OpenROAD" "Hello"]
puts "Returned message: $message"
```

## Using TCL Commands in OpenROAD

To use TCL commands in OpenROAD Flow Scripts, you can embed your TCL code
directly into the scripts. The OpenROAD environment provides various commands
specific to design, such as loading design files, running synthesis, and
checking timing.

Example:

```tcl
read_lef my_design.lef
read_def my_design.def
read_liberty my_design.lib
check_timing
```

## How to read a design in OpenROAD

An example design is provided in `ordb/final.tar.gz` that you can extract with:

```bash
tar xvf ordb/final.tar.gz
```

Then you can run the following TCL commands to load the design and libraries:

```tcl
set odb_file "final/odb/spm.odb"
set def_file "final/def/spm.def"

set lef_files {"/home/mrg/.ciel/sky130A/libs.ref/sky130_fd_sc_hd/techlef/sky130_fd_sc_hd__nom.tlef"
               "/home/mrg/.ciel/sky130A/libs.ref/sky130_fd_sc_hd/lef/sky130_fd_sc_hd.lef"}
set lib_files {"/home/mrg/.ciel/sky130A/libs.ref/sky130_fd_sc_hd/lib/sky130_fd_sc_hd__tt_025C_1v80.lib"}

foreach lef_file $lef_files {
    read_lef $lef_file
}
foreach lib_file $lib_files {
    read_liberty $lib_file
}

read_def $def_file

```

There are a lot of files to load, so you can use the [ORFS scripts to load all
of the design configuration files](https://vlsida.github.io/chip-tutorials/orfs-walkthrough.html#interactive-tcl-usage).

## OpenROAD Database (ORDB)

### Iterating Over Gates

- Use the `get_cells` command to retrieve all the cells (gates) in the design.
- Iterate over each cell using a loop to access its properties.

  **Example:**

  ```tcl
  set cells [get_cells]
  foreach cell $cells {
      # Get the cell name
      set cell_name [get_property $cell full_name]
      puts "Cell: $cell_name"
  }
  ```

### Iterating Over Nets

- Use the `get_nets` command to retrieve all the nets in the design.
- Iterate over each net to access its properties.

  **Example:**

  ```tcl
  set nets [get_nets]
  foreach net $nets {
      # Get the net name
      set net_name [get_property $net full_name]
      puts "Net: $net_name"
  }
  ```

### Querying Timing Information

- Use commands like `report_timing` to extract detailed timing information.

  **Example:**

  ```tcl
  set path [lindex [find_timing_paths -sort_by_slack -group_count 1] 0]
  set slack [get_property $path slack]
  puts "Critical Path Slack: $slack"
  ```

### Querying Other Properties

- Utilize `get_property` to fetch various attributes of cells, nets, or paths.

  **Example:**

  ```tcl
  set cell [get_cells -name my_cell]
  set cell_type [get_property $cell type]
  puts "Cell Type: $cell_type"
  ```

These examples demonstrate typical usage patterns for iterating and querying
within a design in OpenROAD using TCL commands. These scripts can be adjusted
according to specific needs, leveraging the extensive set of commands available
in the OpenROAD TCL API.

## ORFS Scripts

The flow scripts for the ORFS flow are in the directory ```flow/scripts```.
There are many good examples of TCL usage in these scripts.

For example, the IO placement script is ```flow/scripts/io_placement.tcl``` and
is repeated here:

```tcl
source $::env(SCRIPTS_DIR)/load.tcl
erase_non_stage_variables place

if {![env_var_exists_and_non_empty FLOORPLAN_DEF] && \
    ![env_var_exists_and_non_empty FOOTPRINT] && \
    ![env_var_exists_and_non_empty FOOTPRINT_TCL]} {
  load_design 3_1_place_gp_skip_io.odb 2_floorplan.sdc
  log_cmd place_pins \
    -hor_layers $::env(IO_PLACER_H) \
    -ver_layers $::env(IO_PLACER_V) \
    {*}$::env(PLACE_PINS_ARGS)
  write_db $::env(RESULTS_DIR)/3_2_place_iop.odb
  write_pin_placement $::env(RESULTS_DIR)/3_2_place_iop.tcl
} else {
  log_cmd exec cp $::env(RESULTS_DIR)/3_1_place_gp_skip_io.odb $::env(RESULTS_DIR)/3_2_place_iop.odb
}
```

This sources the ```load.tcl``` script, runs ```load_design``` (after checking
for some variables) and then runs the ```place_pins``` command to do IO
placement. Finally, it saves the design and pin placement with ```write_db```
and ```write_pin_placement```, respectively. If else condition skips placement
and just copies the ODB file. Presumably the IO placement will be done with
standard cell placemen tin the next step. The ```log_cmd``` is a TCL procedure
that ensures the command output gets put in the log.

Other interesting step scripts: global_place, resize (the timing optimizer),
detail_place, cts, global_route, detailed_route, etc.

## Conclusion

More information on TCL commands for timing can be found in the [STA
Tutorial](sta.md).

Using TCL within OpenROAD Flow Scripts can greatly enhance your ability to
automate and control the design process. For more information on TCL scripting,
refer to the [OpenROAD documentation](https://openroad.readthedocs.io/).

# License

Copyright 2025 VLSI-DA (see [LICENSE](LICENSE) for use)
