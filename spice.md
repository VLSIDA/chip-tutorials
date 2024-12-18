# SPICE 

SPICE is an industry standard circuit file format. It is a textual schematic
representation of a circuit. It is used by many circuit simulators to simulate
the circuit. 

SPICE files are text files and can be edited with any text editor. Suffixes for
SPICE files can have many variations including:
- .sp
- .spi
- .spice
- .cdl
- .cir
- .ckt
- probably others too

## How are SPICE netlists created

SPICE netlists can be created in a number of ways:

1. By hand: You can write a SPICE netlist by hand. This is often done for simple
   circuits or for testing a simulator.
2. By exporting from a schematic capture tool: Many schematic capture tools can
   export a SPICE netlist. This is often done for more complex circuits.
3. Layout extraction: Layout extraction tools can extract a SPICE netlist from a
   layout. 

Standard cell libraries will often come with SPICE netlists for the cells. Sometimes
these will be individual files, or sometimes they might all be in a single large file. 
The Sky130 library has its cells in:
```
$PDK_ROOT/sky130A/libs.ref/sky130_fd_sc_hd/spice/sky130_fd_sc_hd.spice
```
There are also CDL versions in:
```
$PDK_ROOT/sky130A/libs.ref/sky130_fd_sc_hd/cdl/sky130_fd_sc_hd.cdl
```


## SPICE syntax

It's easiest to talk about SPICE netlists with an example. Here's the spice
netlist (actually, a CDL netlist) of an inverter:
```
* Inverter example
.SUBCKT sky130_fd_sc_hd__inv_1 A VGND VNB VPB VPWR Y
*.PININFO A:I VGND:I VNB:I VPB:I VPWR:I Y:O
MMIN1 Y A VGND VNB sky130_fd_pr__nfet_01v8 m=1 w=0.65u l=0.15u mult=1 sa=0.265
+ sb=0.265 sd=0.28 area=0.063 perim=1.14
MMIP1 Y A VPWR VPB sky130_fd_pr__pfet_01v8_hvt m=1 w=1.1u l=0.15u mult=1 sa=0.265
+ sb=0.265 sd=0.28 area=0.063 perim=1.14
.ENDS sky130_fd_sc_hd__inv_1
```

*The first line of a SPICE file is always ignored!* In this case, it is a comment. 

### Subcircuits

Subcircuits are specified with the .SUBCKT/.ENDS pair. In this case, the second 
line says that the subcircuit is named `sky130_fd_sc_hd__inv_1` and has the
following pins: A, VGND, VNB, VPB, VPWR, and Y. In general, SPICE is case insensitive,
but it is good practice to use all caps for the subcircuit pins.

The third line is technically a comment, but it is a special comment called a
pragma that tells a tool about the types of pins. By default, pins have no
direction in SPICE, but CDL (Cadence Design Language) netlists can have
directions: I for input and O for output. This pragma is ignored by SPICE
simulators that don't understand it.

### Cards

Every line in a SPICE file is a "card" that describes a device. The first character of
the first word defines the device type: M for a MOSFET, R for a resistor, C for a capacitor, etc.

A transistor card looks like this:
```
<instance name> <drain> <gate> <source> <bulk> <model name> <parameters>
```
The instance must be unique or you will get an error. The drain, gate, source, and bulk
are the connections to the transistor. The model name is the name of the model in the
library. 

The parameters for a transistor are specific to the model, but they always include width (W) and length (L) for a MOSFET.
The parameter M is the number of transistors in parallel. 

Resistor and capacitor cards are similar:
```
<instance name> <node 1> <node 2> <value>
```
where an instance name starting with R is a resistor and an instance name starting with C is a capacitor.
The value is the resistance or capacitance in ohms or farads, respectively.


Devices are connected to nets (or nodes) in SPICE which define what is connected together. 
All of the SUBCKT pins are nets, but you can also have other internal nets as well.
Ground is always node (or net) 0 in SPICE. In "old school" SPICE, nets were often just numbers,
but it is easier to give them names. 

### Instances

Instances are special SPICE cards that being with an X. They are used to instantiate
subcircuit copies like this:
```
X0 in 0 vdd 0 vdd out sky130_fd_sc_hd__inv_1
```
which creates an instance of the `sky130_fd_sc_hd__inv_1` subcircuit with the
name `X0`. The connections to this instance are in the order of the SUBCKT
definition at the start of this tutorial. Inside the SUBCKT, they have the name
of the SUBCKT pins, and outside they have these names. The VPWR and VNB pins are both
connected externally to the vdd net. The VGND and VPB pins are both connected to the 0 net. 

### SPICE hierarchy and scope

You can declare instances in a SUBCKT. For example, I can make a BUFFER subcircuit from the inverter like this:
```
.SUBCKT BUFFER IN VDD GND OUT
X0 IN 0 VDD 0 VDD n10 sky130_fd_sc_hd__inv_1
X1 n10 0 VDD 0 VDD OUT sky130_fd_sc_hd__inv_1
.ENDS BUFFER
```
SPICE has only one level of scope for SUBCKTs. This means you cannot have duplicate names. If you repeat names,
most often it will silently overwrite the previous definition.

The scope inside of each SUBCKT is separate from the global scope.

Given the above buffer SUBCKT, I can declare an instance of the buffer like this:
```
X2 bufin vdd 0 bufout BUFFER
```
You can refer to nets in a SUBCKT from the global scope, but you cannot refer to nets in the global scope from a SUBCKT.
For example, if you have an instance X2 of the BUFFER, I can refer to `X2.n10` which is the signal between the two inverters.
Similarly, `X2.X0.A` is the input of the first inverter in the buffer. At the top level, it is called "bufin". Inside the BUFFER,
it is called `X2.IN`.

## Simulating SPICE

To simulate SPICE, you need a stimulus file as well as a netlist file. These can be in the
same file, but often they are kept separate. The stimulus file will often use the .INCLUDE
directive to include the netlist file. If the netlist file has a subcircuit, the stimulus
file may also create an instance of it.

Here is an example of a stimulus file for the inverter above (again, the first line is ignored!):
```
* Inverter testbench
.INCLUDE BUFFER.spice
.TRAN 1n 10n
Vdd vdd 0 1.8

X2 bufin vdd 0 bufout BUFFER

Vinput bufin 0 PULSE(0 1.8 0 0.1n 0.1n 1n 2n)

.MEASURE tran_delay TRIG v(bufin)*0.5 RISE=1 TARG v(bufout)*0.5 RISE=1
```



