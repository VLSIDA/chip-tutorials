# SPICE Overview

SPICE is an industry standard circuit file format. It is a textual schematic
representation of a circuit. It is used by many circuit simulators to simulate
the circuit. 

For full information on the
how to run and use Ngspice, see the [Ngspice Usage](ngspice.md) tutorial.

## How are SPICE netlists created

SPICE files are text files and can be edited with any text editor. Suffixes for
SPICE files can have many variations including:
- .sp
- .spi
- .spice
- .cdl
- .cir
- .ckt
- probably others too

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

### Passives (R, C, and L cards)

This section describes passive elements: resistors,
inductors, and capacitors. Assorted magnetic elements are supported by
spice but they are not presented.

Resistors, inductors, and capacitors come in two types:
* a simple, linear element with a value and some dependence on temperature, initialization, and scaling
* an element that refers to a more complicated model statement

Using the set of passive elements and model statements available, you
can construct a wide range of board and integrated circuit designs. To
use a particular element, an element statement is needed. It specifies
the type of element used and has fields for the element name, the
connecting nodes, a component value and optional parameters. The
```
name node1 node2 ... nodeN [model reference] value [optional parameters]
```
Element parameters within the element statement describes the device
type, device terminal connections, associated model reference, element
value, DC initialization voltage or current, element temperature, and
parasitic.

We can specify these three passive devices merely by using the first
letter of the device name such as:
* Rxxx for resistor
* Lxxx for inductor
* Cxxx for capacitor

To specify the device in the circuit file, we include the name of the
device, how it is connected into the circuit, and its value. Ngspice
uses the basic electrical units for voltage (volts) and current
(amperes) and uses the basic electrical units for device values: ohms,
farads, and henries. You will find that common prefixes also work such
as m for milli-, u for micro-, p for pico-, n for nano-, f for femto-, etc.

Here are some example devices:
```
R12 A B 5k *a 5-kiloohm resistor connected between node A and node B
C7 OUT GND 3u *a 3-microfarad capacitor connected between node OUT and node GND
L5 6 8 1m *a 1-milihenry inductor connected between node 6 and node 8
```
Nodes are essentially ideal wires that connect a circuit by sharing a
name. Often these are given numbers because of very old spice
standards, but they can also be given names such as ``in'', ``a'',
etc. Some spice simulators have a limit on how long the names can be
and whether they are case sensitive. *Node 0 is always considered
  ground.* In "old school" SPICE, nets were often just numbers,
but it is easier to give them names. 

### Transistors (M cards)

A MOS transistor is described by use of an element statement and a
.MODEL statement. These are usually provided to you by a foundry using
characterized data from their fabrication technology. In this case, it
will be included as a library like this:
```
.lib "/software/PDKs/sky130A/libs.tech/ngspice/sky130.lib.spice" tt 
```
where
the second parameter specifies the process corner. In this case, it is
typical PMOS and typial NMOS devices. Other options are slow or fast
in all combinations: ss, ff, fs, sf.

The element statement defines the connectivity of the transistor and
references the .MODEL statement. The .MODEL statement specifies either
an n- or p-channel device, the level of the model, and a number of
user-selectable model parameters.  

The following example specifies a PMOS MOSFET with a model reference
name, PCH.  The parameters are selected from the model parameters. The
most common are the width (W) and length (L) of the transistor.
```
M3 3 2 1 0 PCH <parameters such as L=50n W=180n>
```
Note that the connections in the MOSFET are given in the order: drain,
gate, source, and body. Since MOSFETs are generally symmetric, you can
usually swap the drain and source.

### Instances (X cards)

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

### Voltage/Current Sources

To simulate your circuits you will need some way to tell Ngspice what
is stimulating or supplying electrical power to the circuit. We specify
these sources in a way similar to the passive devices described
earlier: name, connecting nodes, and value. As you might have expected
* Vxxx is a voltage source
* Ixxx is a current source

Using basic electrical units, the following examples are easy to understand:
```
Vin 1 0 3 *a 3V independent voltage supply between node 1 and node 0
Iin 2 0 5m * a 5mA independent current between node 2 and node 0
```
A voltage source is like a battery power supply. Using positive
current convention, current flows out from the first node, through the
circuit and then into the second node. A current source provides a
fixed value of current to the circuit. However, its current flows into
the first node, through the source, and then out of the second
node. This is the opposite direction of the voltage source.


A more complete representation of the source statement is
```
name node node [DC_value] [AC_value] [transient_value]
```
The DC value will be used for the operating point analysis and DC
sweeps. The AC value may combine with DC value to set the operating
point for the small-signal analysis. The transient value will override
the other specifications only during the transient analysis. If
a transient value is not specified, the DC value will be used and the
source is assumed to remain constant during the simulation.

The transient value portion of the statement has several forms, one
for each type of waveform. The most commonly used forms are:
* EXP - exponential waveform
* PULSE - pulse waveform
* PWL - piecewise linear waveform
* SIN - sinusoidal waveform
During the transient analysis, all of the independent voltage sources
having a transient specification will be activated. The remaining
independent sources will maintain the value of the DC specification,
or zero if there is no DC specification.

 
#### Piecewise Linear Waveform (PWL)

The PWL form describes a piecewise linear waveform. Each pair of
time-voltage value pairs specifies a corner of the waveform. The
voltage at times between corners is the linear interpolation of the
voltage at the corners. If the first pair's time is not zero, then the
source's DC voltage will be used as the initial value. If the
simulation continues beyond the last pair's time, then that pair's
voltage will be maintained for the remainder of the simulation.
 
General form
```
PWL (T1 V1 T2 V2 T3 V3 ... Tn Vn ... )
```

Examples
```
V3 10 5 PWL(0us 0V 1us 0V 1.3us 2V 2us 2.5V 3us 0.5V 3.4us 0.5V)
V3 10 5 PWL(0us,0V 1us,0V 1.3us,2V 2us,2.5V 3us,0.5V 3.4us,0.5V)
```
 

#### Pulse Waveform (PULSE)

The PULSE form causes the voltage to start at V1 and stay there for Td
seconds (the offset). Then, the voltage goes linearly from V1 to V2 in Tr seconds
(the slew time).  Then, it stays at V2 for Pw seconds (the pulse
time). After this, the voltage goes linearly from V2 back to V1 during
the next Tf seconds (the slew time). The voltage stays at V1 for the
remainder of the period (technically, Period-Tr-Pw-Tf seconds), and
the cycle is repeated starting with another pulse. The second pulse, however,
does not use the initial offset value.

General form
```
PULSE (V1 V2 Td Tr Tf Pw Period)
```

Example
```
VSW 10 5 PULSE (0V 5V 5us 0.5us 0.5us 4.5us 10us)
```


### Including Files

During the course of the quarter, you will often have to use models that
we provide on the course website.  Instead of copying and pasting the
models, you can just include the model file in your circuit. To do
this, place the model file in the same directory as your
netlist. Then, in your netlist, include the following line:
```
.inc '<filename>'
```
You can also give a full path to the file.

### Parameters

Sometimes electronic circuits are often designed iteratively. In
creating a design, you may not want to commit to particular component
values because you have only general constraits for the circuit when
you are getting started. These design values you want to specify will
be parameters, which can be defined by the following form:
```
.PARAM name=value ...
```
You may define more than one parameter on the same line. This is
useful for defining a supply voltage, for example, which may later
change.


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



