---
title: Timing Constraints
nav_order: 1
parent: Static Timing Analysis
---

# STA Timing Constraints

The industry-standard method of specifying STA timing constraints is the
Synopsys Design Constraints (SDC) format. This is a text file that specifies
the timing requirements for the design. The constraints are used by the
synthesis and place-and-route tools to optimize the design for the desired
performance. This is used in tools like Design Compiler, ICC, and PrimeTime as
well as OpenROAD and OpenLane.

You can get help on the TCL commands in OpenROAD by using the TCL `help` command.
For example, to get help on the `create_clock` command, you can use:
```
openroad> help create_clock
create_clock [-name name] [-period period] [-waveform waveform] [-add]
   [-comment comment] [pins]
```

You can get the units for all the commands by using the `units` command:
```
openroad> report_units
 time 1ns
 capacitance 1fF
 resistance 1kohm
 voltage 1v
 current 1mA
 power 1nW
 distance 1um
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


This defines our clock and reset port names:
```
set clock_port "clk_i"
set reset_port "rst_n"
```
This creates a 50ns clock with a 50% duty cycle:
```
create_clock -name $clock_port -period 50 [get_ports $clock_port]
```
This retrieves the pins using the `get_clocks` and `get_port` commands:
```
set clocks [get_clocks $clock_port]
set resets [get_port $reset_port]
set clock_input [get_port $clock_port]
```

The name of the clock can technically be different than the pin name.

## Generated clocks (PLLs, DLLs, and dividers)

When a clock is *derived* from another clock — by a PLL, DLL, or a
synthesised clock divider in RTL — you do not define it with
`create_clock`. Instead, you tell the tool how the derived clock
relates to its source with `create_generated_clock`. The tool can
then propagate timing from the source clock through the generator and
stop the STA engine from reporting nonsense paths between unrelated
clock domains.

The three things you always need to specify:

- `-source <pin>` — the pin where the reference clock arrives at the
  generator.
- The relationship — either a
  `-divide_by <N>` / `-multiply_by <N>` pair (for PLL outputs and
  RTL dividers) or an `-edges {e1 e2 e3}` spec (for arbitrary duty-cycle
  waveforms).
- The pin(s) where the generated clock is *observed*, which is typically
  a register Q output or a module output port.

### RTL clock divider

Suppose your RTL has a simple divide-by-2 flip-flop:

```verilog
reg clk_div2;
always @(posedge clk_i) clk_div2 <= ~clk_div2;
```

The divider produces a clock at half the input frequency on the
`clk_div2` register's Q output. Define it like this:

```tcl
create_clock -name clk_i -period 10 [get_ports clk_i]

create_generated_clock \
    -name clk_div2 \
    -source [get_ports clk_i] \
    -divide_by 2 \
    [get_pins div_reg/Q]
```

`clk_div2` now inherits the 10 ns period from `clk_i` but runs at
20 ns (divide-by-2). STA will correctly analyse paths launched by one
clock and captured by the other because it understands how they relate.

### PLL output

A PLL typically multiplies its reference. For a hard-macro PLL with a
single output pin called `CLKOUT` multiplying the reference by 8:

```tcl
create_clock -name ref_clk -period 50 [get_ports ref_clk]    ;# 20 MHz in

create_generated_clock \
    -name pll_out \
    -source [get_pins u_pll/REFCLK] \
    -multiply_by 8 \
    [get_pins u_pll/CLKOUT]
```

The generated `pll_out` runs at 50 / 8 = 6.25 ns (160 MHz). OpenSTA
will propagate the reference-clock source latency through the PLL
model when computing arrival times, which is usually what you want
for pre-place STA.

For real silicon you often also want to specify PLL jitter and lock
behaviour. That's done by attaching `set_clock_latency -source`,
`set_clock_uncertainty`, and `set_clock_jitter` to `pll_out`:

```tcl
# Model an output jitter of ±100 ps and lock time uncertainty of 300 ps:
set_clock_uncertainty 0.3 [get_clocks pll_out]
```

### DLLs and phase shifters

A DLL re-aligns phase rather than changing frequency. You typically
specify `-divide_by 1` and model the introduced phase shift with
`set_clock_latency -source`:

```tcl
create_generated_clock \
    -name dll_out \
    -source [get_pins u_dll/REFCLK] \
    -divide_by 1 \
    [get_pins u_dll/CLKOUT]

# DLL introduces a programmed 90° phase shift at 500 MHz (2 ns period):
set_clock_latency -source 0.5 [get_clocks dll_out]
```

### Multiple clock outputs

If a PLL has several outputs (common — one at 2×, one at 4×, one at /2
for slow peripherals), each gets its own `create_generated_clock`
with its own pin and ratio:

```tcl
create_generated_clock -name pll_x2  -source [get_pins u_pll/REFCLK] -multiply_by 2 [get_pins u_pll/CLK_X2]
create_generated_clock -name pll_x4  -source [get_pins u_pll/REFCLK] -multiply_by 4 [get_pins u_pll/CLK_X4]
create_generated_clock -name pll_div -source [get_pins u_pll/REFCLK] -divide_by 2   [get_pins u_pll/CLK_DIV2]
```

### Async clock groups

PLL-derived clocks that share a common reference are automatically
related by the tool, so paths between them are analysed. Two clocks
that are *not* derived from a common source — e.g. your system clock
and a separate oscillator driving a UART — should be declared
asynchronous, otherwise the tool will try to time paths across the
boundary (which are inherently unconstrained anyway):

```tcl
set_clock_groups -asynchronous \
    -group [get_clocks {clk_i clk_div2 pll_out pll_x2}] \
    -group [get_clocks uart_clk]
```

## Input constraints

The command `all_inputs` returns a list of the input ports in the design, but
this also includes the clocks and resets. We want to add delays to the inputs,
but not the clocks and resets since these are handled as special cases. (I.e.
the clock was already defined above and the reset might warrant a special
case.)

To filter out the clocks and resets, we can use the `lsearch` and `lreplace`
in TCL:
```
set clk_indx [lsearch [all_inputs] $clock_input]
set clk_input [lindex [all_inputs] $clk_indx]
set all_inputs_wo_clk [lreplace [all_inputs] $clk_indx $clk_indx ""]

set rst_indx [lsearch $all_inputs_wo_clk $resets]
set all_inputs_wo_clk_rst [lreplace $all_inputs_wo_clk $rst_indx $rst_indx ""]
```
which results in a list of all the inputs without the clock and reset
(`all_inputs_wo_clk_rst`).

Using this list, we can set the driving cells of the inputs as coming from a specific 
library cell:
```
set_driving_cell \
    -lib_cell "sky130_fd_sc_hd__inv_2" \
    -pin "Y" \
    $all_inputs_wo_clk_rst

set_driving_cell \
    -lib_cell "sky130_fd_sc_hd__clkbuf_2" \
    -pin "X" \
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
Usually you will set the uncertainty to 0 or smaller when enabling propagated clocks.

## Timing Exceptions

The default STA model — every path must complete in one clock cycle — is
almost always wrong in at least a few places. Timing exceptions let you
tell the tool about those places. Use them sparingly: an incorrectly
placed exception hides a real violation and ships a broken chip.

### `set_false_path`

Declares a path that the tool should *not* analyse at all. Common uses:

- A synchroniser on a signal crossing between two asynchronous clock
  domains — you've already sized the synchroniser for metastability
  (two-flop or Gray-coded) and further STA on that path is
  meaningless.
- A reset network that's asserted async and deasserted synchronously
  — the async assertion edge can't be timed.
- A test-only scan-enable path that is only relevant in scan mode.

```tcl
# Don't time across an async CDC synchroniser
set_false_path -from [get_clocks clk_a] -to [get_clocks clk_b]

# Don't time the async reset assertion
set_false_path -from [get_ports rst_n_async]
```

If you use `set_clock_groups -asynchronous` (shown in
[Generated clocks](#generated-clocks-plls-dlls-and-dividers)), that
implicitly false-paths every pair of clocks in different groups — you
do not also need `set_false_path` between them.

### `set_multicycle_path`

Relaxes the one-cycle requirement. If some part of your datapath can
take, say, three cycles before the result must be captured (because an
explicit enable only fires every third cycle, or because a
multi-stage FSM gate handles it), tell the tool:

```tcl
# A signed multiplier whose result is captured 3 cycles after launch.
# -setup 3: allow 3 clock periods for data arrival
# -hold 2:  relax the matching hold requirement to 2 cycles
set_multicycle_path 3 -setup -from [get_pins mult/out*] -to [get_pins acc/D*]
set_multicycle_path 2 -hold  -from [get_pins mult/out*] -to [get_pins acc/D*]
```

The hold multiplier is almost always one less than the setup multiplier.
If you set `-setup 3` without a matching `-hold`, the tool will enforce
hold at the captured-minus-2-cycles edge by default, which is usually
what you want but double-check against waveforms.

### `set_max_delay` / `set_min_delay`

For paths that *are* timed but not against a clock period — e.g. an
asynchronous output that needs to settle within 2 ns of an input
toggle — you can bound the allowed delay directly:

```tcl
set_max_delay 2.0 -from [get_ports async_in] -to [get_ports async_out]
set_min_delay 0.3 -from [get_ports async_in] -to [get_ports async_out]
```


# License

Copyright 2024 VLSI-DA (see [LICENSE](LICENSE) for use)
