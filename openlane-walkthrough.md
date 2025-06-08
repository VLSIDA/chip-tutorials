# Running an example design

This assumes that the smoke test runs and you've [installed OpenLane properly](installation.md).

There is also a very good overview for
[Newcomers](https://openlane2.readthedocs.io/en/latest/getting_started/newcomers/index.html#).

You can run an example design called "SPM" by running:

```bash
openlane --run-tag foo --run-example spm
```

which will download the design, all technology files, and completely implement the design. Once
done, all of the files are in the "spm" subdirectory. The run logs and outputs of the tools are in
a directory with the current date and time like "spm/runs/RUN_2024-12-12_11-58-38".

Once you've run once, you can enter the directory and see the files:

- config.yaml: The configuration of the design.
- src: The directory with the Verilog source files.
- run: The directory containing all runs, one per directory.
- verify: The verification directory with Verilog test benches.

If you want to run again, you can specify the config file as an argument to OpenLane:

```bash
cd spm
openlane config.yaml
```

## Run directories and tags

If you want to to specify a run name like "foo", you can add the "--run-tag foo" to a command.
This will put everything in "spm/runs/foo", but if you run again, you will either need to remove
that directory to start over, or specify "--overwrite" on the command line:

```bash
openlane --run-tag foo config.yaml
openlane --run-tag foo --overwrite config.yaml
```

## Viewing the final design

The --last-run option is also a shortcut for the last run directory. To view the last design in
the OpenROAD GUI, you can run:

```bash
openlane --flow OpenInOpenROAD --last-run config.yaml
```

and you should see the following:
![Default SPM project in OpenROAD GUI](openlane/openroad_gui_spm.png)
However, this doesn't load any of the timing or constraint information.

We recommend that, instead, you use:

```bash
openroad -gui
```

and then load the design files manually. You will need to select which ODB (or DEF) file that you want to load based on
which stage of the design you want to examine. For example, you can load the final stage, like this:

```
read_lib $env(PDK_ROOT)/sky130A/libs.ref/sky130_fd_sc_hd/lib/sky130_fd_sc_hd__ss_100C_1v60.lib
read_db odb/spm.odb 
read_spef spef/max/spm.max.spef
read_sdc sdc/spm.sdc
```

where the odb, spef, and sdc file can be found in the final run directory. The .lib file is from your PDK
directory.

You can add this to a TCL file and source the script like this:

```tcl
source myscript.tcl
```

so that you don't have to type it over and over again.

You should also go through the [Newcomers Guide to
OpenLane2](https://openlane2.readthedocs.io/en/latest/getting_started/newcomers/index.html).

## Help

OpenROAD (not OpenLANE) has some options for help via the ``man`` command like most
Unix systems. These manual pages provide detailed information about how to use
a particular command or function, along with its syntax and options.

This can be used for a range of commands in different levels as follows:
- Level 1: Top-level openroad command (e.g. ``man openroad``)
- Level 2: Individual module/TCL commands (e.g. ``man clock_tree_synthesis``)
- Level 3: Info, error, warning messages (e.g. ``man CTS-0001``)

The OpenLane2 documentation is also available at [ReadTheDocs](https://openlane2.readthedocs.io/en/latest/).

The OpenROAD documentation is available at [ReadTheDocs](https://openroad.readthedocs.io/en/latest/).

# License

Copyright 2024 VLSI-DA (see [LICENSE](LICENSE) for use)
