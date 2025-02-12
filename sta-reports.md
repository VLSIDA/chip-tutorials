
# Reporting Timing
## Max paths

You can get the a timing report by doing:
```
openroad> report_checks
Startpoint: rst (input port clocked by clk)
Endpoint: _302_ (recovery check against rising-edge clock clk)
Path Group: asynchronous
Path Type: max

  Delay    Time   Description
---------------------------------------------------------
   0.00    0.00   clock clk (rise edge)
   0.00    0.00   clock network delay (propagated)
   2.00    2.00 ^ input external delay
   0.02    2.02 ^ rst (in)
   0.17    2.19 ^ input33/X (sky130_fd_sc_hd__clkbuf_1)
   0.40    2.59 ^ fanout52/X (sky130_fd_sc_hd__buf_2)
   0.49    3.08 ^ fanout46/X (sky130_fd_sc_hd__clkbuf_4)
   0.00    3.08 ^ _302_/RESET_B (sky130_fd_sc_hd__dfrtp_1)
           3.08   data arrival time

  10.00   10.00   clock clk (rise edge)
   0.67   10.67   clock network delay (propagated)
  -0.25   10.42   clock uncertainty
   0.00   10.42   clock reconvergence pessimism
          10.42 ^ _302_/CLK (sky130_fd_sc_hd__dfrtp_1)
   0.40   10.81   library recovery time
          10.81   data required time
---------------------------------------------------------
          10.81   data required time
          -3.08   data arrival time
---------------------------------------------------------
           7.73   slack (MET)


Startpoint: _314_ (rising edge-triggered flip-flop clocked by clk)
Endpoint: y (output port clocked by clk)
Path Group: clk
Path Type: max

  Delay    Time   Description
---------------------------------------------------------
   0.00    0.00   clock clk (rise edge)
   0.68    0.68   clock network delay (propagated)
   0.00    0.68 ^ _314_/CLK (sky130_fd_sc_hd__dfrtp_1)
   0.72    1.40 v _314_/Q (sky130_fd_sc_hd__dfrtp_1)
   0.34    1.74 v output35/X (sky130_fd_sc_hd__buf_2)
   0.00    1.74 v y (out)
           1.74   data arrival time

  10.00   10.00   clock clk (rise edge)
   0.00   10.00   clock network delay (propagated)
  -0.25    9.75   clock uncertainty
   0.00    9.75   clock reconvergence pessimism
  -2.00    7.75   output external delay
           7.75   data required time
---------------------------------------------------------
           7.75   data required time
          -1.74   data arrival time
---------------------------------------------------------
           6.01   slack (MET)

```

This shows the max paths for each "path group". Since our SDC file did not add
constraints (see [STA Constraints Tutorial](sta-constraints.md)) for the rst
pin, it is left in an "asynchronous" group. Whereas our other paths are in the
"clk" group. You can specify a particular group as well as format like this:
```
openroad> report_checks -path_group clk
Startpoint: _314_ (rising edge-triggered flip-flop clocked by clk)
Endpoint: y (output port clocked by clk)
Path Group: clk
Path Type: max

  Delay    Time   Description
---------------------------------------------------------
   0.00    0.00   clock clk (rise edge)
   0.68    0.68   clock network delay (propagated)
   0.00    0.68 ^ _314_/CLK (sky130_fd_sc_hd__dfrtp_1)
   0.72    1.40 v _314_/Q (sky130_fd_sc_hd__dfrtp_1)
   0.34    1.74 v output35/X (sky130_fd_sc_hd__buf_2)
   0.00    1.74 v y (out)
           1.74   data arrival time

  10.00   10.00   clock clk (rise edge)
   0.00   10.00   clock network delay (propagated)
   0.00   10.00   clock reconvergence pessimism
  -2.00    8.00   output external delay
           8.00   data required time
---------------------------------------------------------
           8.00   data required time
          -1.74   data arrival time
---------------------------------------------------------
           6.26   slack (MET)

```
Each of these path reports shows the detailed information about a path that
goes from a startpoint (either a DFF or primary input) to an endpoint (another
DFF or primary output). In our case, the path starts at DFF `_314_` and goes to
the primary output `y`. 

It's also important to note that the rising transition is noted with a `^` and
a falling transition is noted with a `v`. So this is a rising clock transition
because the DFF is positive edge triggered.

The launching clock is show first with a summary:
```
   0.00    0.00   clock clk (rise edge)
   0.68    0.68   clock network delay (propagated)
   0.00    0.68 ^ _314_/CLK (sky130_fd_sc_hd__dfrtp_1)
```
This shows that the clock arrives at the clock pin of the DFF at 0.68ns.

From there, you can see the "data path" part of the report here:
```
   0.00    0.68 ^ _314_/CLK (sky130_fd_sc_hd__dfrtp_1)
   0.72    1.40 v _314_/Q (sky130_fd_sc_hd__dfrtp_1)
   0.34    1.74 v output35/X (sky130_fd_sc_hd__buf_2)
   0.00    1.74 v y (out)
           1.74   data arrival time
```
This shows the clock arrives at 0.68ns and there is a CLK-to-Q delay of 0.72ns
before the output of the DFF changes. The signal then goes through a single
buffer with a delay of 0.34ns before arriving at the primary output pin `y` at
a total delay of 1.74ns, the data arrival time. This path is showing the
falling output of a DFF (denoted by `v`) that goes through a buffer whose
output is also falling (denoted by `v`). 

The capturing clock path is then shown in the report:
```
  10.00   10.00   clock clk (rise edge)
   0.00   10.00   clock network delay (propagated)
   0.00   10.00   clock reconvergence pessimism
  -2.00    8.00   output external delay
           8.00   data required time
```
Since the clock period is set to 10ns in the SDC file, the clock arrives at 
Since this is an primary output, it is not really driven by a clock, so there is no
propagated clock delay. The output external delay is set to 2ns in the SDC file
which subtracts from the clock period and means that the data is needed at the output by 8ns, the
data required time.

The final slack computation is then the data required time minus the data arrival time:
```
---------------------------------------------------------
           8.00   data required time
          -1.74   data arrival time
---------------------------------------------------------
           6.26   slack (MET)
```
which means we had plenty of time for this path!

# Report options

This command has a lot of options that you can see:
```
openroad> help report_checks
report_checks [-from from_list|-rise_from from_list|-fall_from from_list]
   [-through through_list|-rise_through through_list|-fall_through through_list]
   [-to to_list|-rise_to to_list|-fall_to to_list] [-unconstrained]
   [-path_delay min|min_rise|min_fall|max|max_rise|max_fall|min_max]
   [-corner corner] [-group_path_count path_count]
   [-endpoint_path_count path_count] [-unique_paths_to_endpoint]
   [-slack_max slack_max] [-slack_min slack_min] [-sort_by_slack]
   [-path_group group_name]
   [-format full|full_clock|full_clock_expanded|short|end|slack_only|summary|json]
   [-fields capacitance|slew|input_pin|net|src_attr] [-digits digits]
   [-no_line_splits] [> filename] [>> filename]
``` 

## Path type options

You can specify the path type with the `-path_delay` option which can include
max, min, rise, fall, and combinations of these. Usually, you will specify
either `min` for hold time checks or `max` for setup time checks, but will want
to consider both rise and fall simultaneously.

In multi-corner timing (see [STA Multi-Corner Tutorial](sta-mc.md)) , you can specify the corner with `-corner`:
```
openroad> report_checks -corner tt
```
which would perform checks only the the typical (tt) corner.

## Path format options

The path details can be controlled with the `-format` options.

With the `full_clock` format, you can see that the
details of the launching clock are shown in the previous example:
```
   0.00    0.00   clock clk (rise edge)
   0.00    0.00   clock source latency
   0.08    0.08 ^ clk (in)
   0.32    0.39 ^ clkbuf_0_clk/X (sky130_fd_sc_hd__clkbuf_16)
   0.28    0.67 ^ clkbuf_3_0__f_clk/X (sky130_fd_sc_hd__clkbuf_16)
   0.00    0.68 ^ _314_/CLK (sky130_fd_sc_hd__dfrtp_1)
```
The input clk pin goes through two clock buffers before reaching the DFF. The clock
input itself is delayed 0.08ns since the inputs are driven by a driving cell in
the SDC constraints. The buffers have a delay of 0.32ns and 0.28ns. The total
delay is in the second column which shows that the clock arrives at the DFF at
0.68ns. A similar level of detail would be supplied for the capturing clock.

The `short` format only deisplays the startpoint, endpoint and path groups. The
`end` format will only show the end points with the required time, arrival
time, and slack summarized without any path details. The `summary` option will
show both the startpoint and entpoints with the summary.


## Path detail options

The `-fields` option lets you add more details to the path report. For example,
* `-fields capacitance` will show the capacitance of the nets
* `-fields slew` will show the slew the signals
* `-fields input_pin` will show the input timing at the gate inputs in addition to outputs
* `-fields net` will show the net names
These are somes useful if you want to diagnose delay due to a long wire or a
nhigh fanout net.

## Path filtering options
 
In some cases, you may want to look at critical paths to a particular output,
from a particular input, or through a particular cell. You can use the `-from`,
`-to`, and `-through` options to filter the paths using these criteria.



# Reporting Edges and Pins

You can get arrival and required times of specific timing points in a circuit like this:
```
openroad> report_arrival input33/X
 (clk ^) r 2.19:2.19 f 2.17:2.17
```
which says that the min:max rising and falling delays are 2.19:2.19 and 2.17:2.17, respectively.
Similarly, you can get the delays of an edge with:
```
openroad> report_edges -to input1/X
A -> X combinational
  ^ -> ^ 0.30:0.30
  v -> v 0.24:0.24
```
Which shows the risting input to rising output and falling input to falling
output of the non-inverting gate.



# Reporting power

The previous material focused on timing, but STA can also report power. For example, you can get a summary 
of your design power with:
```
openroad> report_power
Group                  Internal  Switching    Leakage      Total
                          Power      Power      Power      Power (Watts)
----------------------------------------------------------------
Sequential             3.02e-04   3.49e-05   1.21e-06   3.39e-04  37.1%
Combinational          1.93e-04   1.27e-04   1.33e-06   3.22e-04  35.3%
Clock                  1.72e-04   8.02e-05   2.41e-07   2.52e-04  27.6%
Macro                  0.00e+00   0.00e+00   0.00e+00   0.00e+00   0.0%
Pad                    0.00e+00   0.00e+00   0.00e+00   0.00e+00   0.0%
----------------------------------------------------------------
Total                  6.67e-04   2.42e-04   2.78e-06   9.12e-04 100.0%
                          73.2%      26.5%       0.3%
```
The total power is broken down into internal, switching and leakage power. 
Internal power is the power dissipated within the cells (i.e. short circuit power). 
Switching power is the dynamic power of charging and discharging the capacitances in the circuit.
The leakage power is the power dissipated by leakage through the transistors in the off state.

In addition to the types of power, the power is also broken down into the
category. The sequential elements (flip-flops and latches), combinational
logic, and the clock network are the most significant. If you have macros in
your design, like a memory, it may also consume power.

## Switching activity

By default, the power is computed assuming a default 0.5 switching activity on
all nets. However, this may not always be true. For example, your reset signal
will only transition once! The clock, however, will switch every cycle. All
other inputs might switch at, say, 10% of the clock periods. You can get a
slightly more accurate estimate by setting these:
```tcl
openroad> set_power_activity -input -activity 0.1
openroad> set_power_activity -input_ports rst -activity 0.0
openroad> report_power
Group                  Internal  Switching    Leakage      Total
                          Power      Power      Power      Power (Watts)
----------------------------------------------------------------
Sequential             3.04e-04   3.49e-05   1.21e-06   3.40e-04  37.5%
Combinational          1.92e-04   1.23e-04   1.33e-06   3.16e-04  34.8%
Clock                  1.72e-04   8.02e-05   2.41e-07   2.52e-04  27.8%
Macro                  0.00e+00   0.00e+00   0.00e+00   0.00e+00   0.0%
Pad                    0.00e+00   0.00e+00   0.00e+00   0.00e+00   0.0%
----------------------------------------------------------------
Total                  6.68e-04   2.38e-04   2.78e-06   9.08e-04 100.0%
                          73.5%      26.2%       0.3%
```
However, this is a small design so it didn't change *that* much.
Note that you cannot set the activity of the clock. However, if I set all the inputs to 0.0, it would have no combinational
internal or switching power:
```
openroad> set_power_activity -input -activity 0
openroad> report_power
Group                  Internal  Switching    Leakage      Total
                          Power      Power      Power      Power (Watts)
----------------------------------------------------------------
Sequential             2.00e-04   0.00e+00   1.21e-06   2.01e-04  44.2%
Combinational          0.00e+00   0.00e+00   1.33e-06   1.33e-06   0.3%
Clock                  1.72e-04   8.02e-05   2.41e-07   2.52e-04  55.5%
Macro                  0.00e+00   0.00e+00   0.00e+00   0.00e+00   0.0%
Pad                    0.00e+00   0.00e+00   0.00e+00   0.00e+00   0.0%
----------------------------------------------------------------
Total                  3.72e-04   8.02e-05   2.78e-06   4.55e-04 100.0%
                          81.7%      17.6%       0.6%
```
But there is still leakage of the combinational logic gates when they aren't switching.

### Simulation-based switching

You can also use VCD (Verilog Change Dump) files to get the activity for better accuracy:
```tcl
read_vcd -scope tb/spm spm.vcd
```
if you've created a file with your testbench, `tb`. However, if you don't run your design in all the modes
of operation, this can also be inaccurate.

# License

Copyright 2024 VLSI-DA (see [LICENSE](LICENSE) for use)
