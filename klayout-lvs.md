
# Running LVS 

*WARNING*: Make sure you are using a DRC clean layout for this tutorial. While layouts with
DRC errors *might* work, they also might not. It depends on the DRC error.

LVS will compare a layout with a netlist in SPICE (or CDL) format. CDL is
"Cadence Description Language" and is essentially the same as SPICE. For more
understanding of SPICE syntax, take a look at the [SPICE](spice.md) tutorial.

After running LVS, you are presented with an option to import the SPICE netlist:

![LVS netlist](klayout/klayout-lvs-netlist.png)

where you should select the SPICE netlist: ``sky130_fd_sc_hd__inv_1.spice``. 
After this, the LVS options menu will appear:

![LVS menu](klayout/klayout-lvs-menu.png)

Make sure to uncheck the "scale" option in the LVS dialog box. Sky130 uses an
odd scale factor in the SPICE netlist of microns instead of meters. If you
don't uncheck this, the transistor sizes won't match and your LVS will fail.

After running LVS, you will get a window with the results like this:

![LVS Netlist Browser with no errors](klayout/klayout-lvs-browser.png)

The "objects" in the netlist are pins (inputs and outputs), nets (connections 
in the netlist), and devices (transistors, resistors, capacitors, etc.). In this
case, they are all green because they all match. The numbers by the nets and
the pins are the number of objects that things are connected to. For example, net
A is connected to the input pin A and the gate of both the PMOS and NMOS transistor.

If you select the "Netlist" tab in the browser, you can click on nets, pins, and
devices and they will highlight in the layout window. For example, if you click
on the "A" net, it will highlight the input pin A and the gate of the PMOS and NMOS.
This includes all of the polysilicon and the licon and li shapes for the A input.
Under "Configuration", you can also change the color and pattern of the highlighting
if it is difficult to see.

## Understanding LVS

Net and device names do not need to match in LVS. In fact, the extracted layout names
are often randomly assigned. If you look at the extracted layout you might see names like "$3"
and devices like "$6".


## Common LVS errors

There are a few common LVS errors that you might encounter and becoming an experienced engineer
will help you solve some of these. LVS is notoriously hard to debug. I've made examples using a nand3
test case for a few of them.

### Parameter mismatch

In this case, the W and L of the transistors might not match. Sometimes there will be a "tolerance"
that allows some deviation, but usually sizes should match exactly.

If you load the layout `sky130_fd_sc_hd_nand3_1-parameter.gds` and run LVS, you should see the following:

![LVS parameter mismatch](klayout/klayout-nand3-lvs-parameter.png)

Note that the PMOS device widths are 0.97um in the layout and 1.0um in the SPICE netlist. The NMOS
match without an error. If you compare with the working nand3 layout, you will see that the PMOS
diffusion is "shorter" and makes the width 0.97um for all three PMOS.

### Substrate connection

This one is a bit tricky since well taps are not always included in each cell. At the chip level,
you will have your nwell connected and the pwell/substrate also connected. However, 
this is usually done by the "tap" cells during placement. At the cell level, there is usually a setting
that tells LVS to connect the wells and substrate. In our LVS settings, for example, there is the
option to set the value of "lvs_sub" which is the substrate. In the cell netlist, this is the "VNB" pin.
But, remember, names don't have to match!

### Missing devices

In this case, you might be entirely missing a device. This could be a missing
transistor, resistor, or capacitor.

### Unconnected net

This is a common error where a net in the layout is not connected to anything.
This could be a floating net due to a missing contact or via. It could also be
a missing piece of metal. Often when you have metal that goes from a lower
level to a higher level, you need a via and piece of metal (a "via stack") to
connect them. A disconnect can happy if a via or metal is missed at any level.

If you load the `sky130_fd_sc_hd_nand3_1-disconnected.gds` layout and run LVS, you should see the following:

![LVS disconnected net](klayout/klayout-nand3-lvs-disconnected.png)

In this case, the licon contacts for one device to the Y output are missing.
While a lot of the circuit matches, the Y output in the layout has "(3)"
connections whereas the netlist has "(4)" connections. This also causes the A
input to mismatch since it is connected to the $6 transistor which is
disconnected from the output. That is just a side effect though!

### Short-circuit connection

This is a common error where there is an inadvertent connection. This could be
due to an extra via/contact or due to extra metal connecting two other pieces
of metal. If it is wide enough and spacing rules are satisfied, it won't cause a DRC error!

If you load the `sky130_fd_sc_hd_nand3_1-short.gds` layout and run LVS, you should see the following:

![LVS disconnected net](klayout/klayout-nand3-lvs-short.png)

In this example, pins A and B are connected together in the layout but not in the netlist. This is
shown with "A,B (4)" in the layout whereas the reference netlist has "B(3)" and "A(3)", separated.
This also causes some other mismatches, but again these are just side effects.

### Pin mismatch

This is a common error where the pins in the layout don't match the pins in the netlist. Whether this is
flagged as an error depends on the LVS tool settings. 

If you load the `sky130_fd_sc_hd_nand3_1-pin.gds` layout and run LVS, you should see the following:

![LVS disconnected net](klayout/klayout-nand3-lvs-pin.png)

In the example below, the A and B pins are swapped
but LVS correctly passes. However, notice that A in the layout matches with B in the netlist and vice versa.


### Bus flips

At higher levels, you might have a bus that is flipped. This is common when you mix up big-endian and
little-endian. For example, if you have a 4-bit bus and the layout has the MSB on the left and the netlist
has the MSB on the right, you can run into this problem.


