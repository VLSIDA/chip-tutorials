# STA Timing Constraints

The industry-standard method of specifying STA timing constraints is the
Synopsys Design Constraints (SDC) format. This is a text file that specifies
the timing requirements for the design. The constraints are used by the
synthesis and place-and-route tools to optimize the design for the desired
performance. This is used in tools like Design Compiler, ICC, and PrimeTime as
well as OpenROAD and OpenLane.

You can get help on the TCL commands in OpenROAD by using the TCL `help` command.
For example, to get help on the `set_clocks` command, you can use:
```
openroad> help create_clock
create_clock [-name name] [-period period] [-waveform waveform] [-add]
   [-comment comment] [pins]
```


## Clocks

All timing is based on the clock. The clock is the heartbeat of the design and
is used to synchronize all the operations in the design. The clock is specified
by the period, which is the time between clock edges. The frequency is the
inverse of the period. The clock is also specified by the duty cycle, which is
the ratio of the high time to the period. The duty cycle is usually 50% for
digital designs.

The clock is also specified by the clock uncertainty, which is the amount of
variation in the clock period. This is used to account for clock skew and
jitter. The clock uncertainty is usually specified as a percentage of the clock
period.


This defines our clock and reset port names and retrieves the pins using the
`get_clocks` and `get_port` commands:
```
set clock_port "clk_i"
set reset_port "rst_n"
set clocks [get_clocks $clock_port]
set resets [get_port $reset_port]

```

This creates a 50ns clock with a 50% duty cycle:
```
create_clock -name $clock_port -period 50 [get_ports $clock_port]
```
The name of the clock can technically be different than the pin name. 


## Input constraints

The command `all_inputs` returns a list of the input ports in the design, but
this also includes the clocks and resets. We want to add delays to the inputs,
but not the clocks and resets since these are handled as special cases. (I.e.
the clock was already defined above and the reset might warrant a special
case.)

To filter out the clocks and resets, we can use the `lsearch` and `lreplace`
in TCL:
```
set clk_indx [lsearch [all_inputs] $clocks]
set all_inputs_wo_clk [lreplace [all_inputs] $clk_indx $clk_indx ""]

set rst_indx [lsearch all_inputs_wo_clk $resets]
set all_inputs_wo_clk_rst [lreplace $all_inputs_wo_clk $rst_indx $rst_indx ""]
```
which results in a list of all the inputs without the clock and reset
(`all_inputs_wo_clk_rst`).

Using this list, we can set the driving cells of the inputs as coming from a specific 
library cell:
```
set_driving_cell \
    -lib_cell "sky130_fd_sc_hd__inv_2" \
    -pin "Y"
    $all_inputs_wo_clk_rst

set_driving_cell \
    -lib_cell "sky130_fd_sc_hd__clkbuf_2" \
    -pin "X"
    $clk_input
```
This effectively models the driving resistance of the input pin so if they are
loaded with more capactiance they will get slower. We chose the clkbuf rather
than the inv for the clock so it has more balanced rise and fall delays.

The actual delay of the input pins are set with the `set_input_delay` command:
```
set_input_delay 10 -clock $clocks $all_inputs_wo_clk_rst
```
This specifies how much delay a signal has after starting from a DFF clocked by the
specified clock.

## Output constraints

The output pins have a load capacitance that they drive. This is set with the
`set_load` command. Normally, you will want to set the load to something like 4
DFF fanouts. This command sets the output load to 0.05pF:
```
set_load 0.05 [all_outputs]
```

The output pins also have a delay that is set with the
```
set_output_delay 10 -clock $clocks [all_outputs]
```
This specifies how much additional delay is added to the output path before
it gets to a DFF clocked by the specified clock. 

## Ideal vs propagated clocks

Not all clocks are created equal. Some clocks are ideal and are used to
represent the clock that is used in the design. Other clocks are propagated
clocks that are used to represent the clock that is actually used in the
design. The propagated clock is used to account for clock skew and jitter.

This command sets the the clock to be 0.25ns:
```
set_clock_uncertainty 0.25 $clocks
```
This means that one clock can be up to 0.25ns different than another clock
and is useful if we do not yet know our clock distribution buffers and routing.

After the clock is created, however, we can turn on the propagated clock
option to use the actual clock delays through the clock distribution network:
```
set_propagated_clock $clocks
```

## Timing Exceptions

There are some exceptions to the timing constraints that can be set. 

The `set_false_path` command defines a path that is not to be analyzed by the
STA tool. If used incorrectly, it can cause the tool to miss real timing
violations!

The `set_multi_cycle_path` command is used to specify a path that is not
required to complete in a single cycle. Sometimes, you may have a memory stage,
for example, that can take multiple cycles to complete. This command is used to
specify that path.


# License

Copyright 2024 VLSI-DA (see [LICENSE](LICENSE) for use)
