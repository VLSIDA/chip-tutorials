
# Ngspice Overview

Ngspice is an open-source circuit simulator that supports the standard
BSIM transistor models that were developed at UC Berkeley. There are
many similar commercial simulators such as Synopsys HSPICE, OrCAD
PSpice, LTSpice, etc. The differences are mainly simulation
performance, some minor syntax differences (primarily in the analysis
commands), and possibly some enhanced features. For full information on the
syntax of spice see the [Spice Syntax](spice.md) tutorial.


## Installing Ngspice

Ngspice is available for all major operating systems. You can download and install it from
the [Ngspice web site](http://ngspice.sourceforge.net/download.html).  
*You must use Ngspice in WSL for Windows.*

You should 
be using *at least version 37* of ngspice.  You can check the version by typing:
```bash
ngspice --version
```

Another (preferred) method is to use Nix. In this method, Nix will provide the
binaries, but you first need to install Nix depending on your OS:
[https://openlane2.readthedocs.io/en/latest/getting_started/common/nix_installation/index.html](https://openlane2.readthedocs.io/en/latest/getting_started/common/nix_installation/index.html)
If you are using Nix (such as for the OpenLane flow), you can install it with:
```bash
nix shell github:efabless/nix-eda#ngspice
```

## Installing Sky130 PDK

You can also install this using Nix and OpenLane by following [these
instructions](installation.md) through the "smoke test" which will download the
Skywater 130nm PDK. 

Or, you can do it yourself using Volare. If you have used the OpenLane "smoke
test" as above, skip this as it already installed the PDK for you. Otherwise,
you can do this with:
```bash
pip install volare
volare enable --pdk sky130 0fe599b2afb6708d281543108caf8310912f54af
```
You should now see the PDK installed:
```bash
$ ls ~/.volare
sky130A  sky130B  volare
```

## Running Ngspice

Once you create an ngspice file like [example.sp](spice/example.sp), you can run it on the command line by typing:
```bash
ngspice example.sp 
```

We provide an example spice file that should work right now and you can test
it.  Spice files usually end with the extension .sp (for spice) such
as the example provided but you may also see .spc, .spice or others. After the program runs, you will see output like this with a prompt:
```
Circuit: * example inverter with transient analysis and measure

ngspice 1 ->
```
The first line of a spice file is always the circuit name. This is
often a source of confusion if someone thinks it is a command since it
will always be ignored.  You will also see any possible errors or
warnings loading your spice file. You must fix these before you can
procede, but it is safe to ignore one about ``Note: can't find init
file.``

To actually simulate, you must type *run* at the prompt. When you
want to exit ngspice, type *quit* at the prompt. There is no elegant way
reload a spice file, so you must quit and restart the program each
time. Please ask if you don't understand a warning or error message.

You can embed those commands directly into the spice file using a control card like this:
```
.control
run
quit
.endc
```
However, this is syntax specific to Ngspice. 


## Circuit Analysis

Ngspice can perform at least three types of circuit analysis: direct
current (DC), alternating current (AC) and transient
simulation. (There are also noise and monte carlo analysis, but we
will ignore those!) DC is basically a static circuit solver. AC performance
frequency response analysis of circuits. Transient simulation
performs time simulation of circuit responses and is the most flexible
analysis for digital circuits.

### DC Analysis

The .DC statement is used in DC analysis to:
* Sweep any parameter value
* Sweep any source value
* Sweep temperature range
* Perform a DC Monte Carlo analysis (random sweep)
* Perform a DC circuit optimization
* Perform a DC model characterization
At each point of the sweep, the circuit is solved and values can be printed.
The most common use is:
```
.dc <source> <start> <stop> <step>
```
*source* is the name of the independent voltage or current source, a model
parameter, or an operating point such as the temperature (TEMP). The *start*,
*stop* and *step* give the range and accuracy of the static points to simulate.

The following example causes the value of the voltage source VIN to be
swept from 0.25 volts to 5.0 volts in increments of 0.25 volts and the circuit is solved for each value:
```
.DC VIN 0.25 5.0 0.25
```
The following example invokes a sweep of the drain-to-source voltage
from 0 to 10 V in 0.5 V increments at VGS values of 0, 1, 2, 3, 4, and
5 V:
```
.DC VDS 0 10 0.5 VGS 0 5 1
```
This type of analysis will be very useful for characterizing devices!
The following example asks for a DC analysis of the circuit from -55C
to 125C in 10C increments:
```
.DC TEMP -55 125 10
```

### AC Analysis

We won't use AC analysis in this class, but it is useful if you have
analog or radio frequency circuits. This lets you apply an alternating
current (or voltage) signal to an input over a range of frequencies to
determine frequency response (i.e., Bode) plots.
```
.ac <lin|dec|oct|> <number of samples> <freq start> <freq stop>
```

### Transient Analysis

Ngspice transient analysis computes the circuit solution as a function
of time over a time range specified in the .TRAN statement. Since
transient analysis is dependent on time, it uses different analysis
algorithms, control options with different convergence-related issues
and different initialization parameters than DC analysis. However,
a transient analysis first performs a DC operating point
analysis to know the starting point of the circuit at time 0.

The TRAN statement looks like:
```
.tran <stepsize> <endtime>
```
The following statement will perform 1ns of simulation with time
steps of roughly 1ps
```
.tran 1ps 1ns 
```
Performing too long of a simulation or too fine of a step may take a
long time!

## Ngspice Results

### Printing Results

The .PRINT statement specifies output variables for which values are
printed. The maximum number of variables in a single .PRINT statement
is 32. You can use additional .PRINT statements for more output
variables.

To simplify parsing of the output listings, a single "x" printed in
the first column indicates the beginning of the .PRINT output data,
and a single "y" in the first column indicates the end of the .PRINT
output data.

Syntax
```
.PRINT antype ov1 <ov2 ... ov32>
```
where antype specifies the type of analysis for output (DC, AC, TRAN,
etc.). ov1... specify the values to be printed.

Example
```
.PRINT TRAN v(vs) v(vo)
```
This example prints out the results of a transient analysis for the
nodal voltage named vs and vo. The output looks like this:
```
x
        time    voltage      voltage    
                    vs           vo     
    0.            0.           0.       
   10.00000u      0.           0.       
   20.00000u      0.           0.       
   30.00000u      0.           0.      
...
y
```

This example
```
.PRINT DC V(2) I(VSRC) V(23,17) I1(R1) I1(M1)
```
specifies that the DC analysis results are to be printed
for several different nodal voltages and currents through the resistor
named R1, the voltage source named VSRC, and the drain-to-source
current of the MOSFET named M1. The output of this plot will be
similar to the transient one except the first column will be the DC
voltage that is swept in the analysis instead of time.

### Plotting Results

There are generally two plot commands in spice tools: the standard text plot and a graphical one. 
The syntax for the text .PLOT command is identical to the .PRINT
command. However, plotting the results will display a text graph of
the output values. This is sometimes useful in a pinch.


More realistically, you can graphically plot results using the {\bf plot}
command at the ngspice prompt.  Since you can
have multiple analyses in one spice session, this will use the
transient one, by default, I believe.  You can list the other analyses
by typing:
```
setplot
```
which will show something like this:
```
	Type the name of the desired plot:
        new     New plot
Current tran1   * example inverter with transient analysis and measure (Transient Analysis)
        dc1     * example inverter with transient analysis and measure (DC transfer characteristic)
        const   Constant values (constants)
```
You can either type the name or press enter to quit. To view other results, you must switch to the other analysis using the {\bf setplot} command like this:
```
setplot tran1
```
Then, you can plot transient results like this, for example,
```
plot A Z
```
which plots the waveforms of the input and output.  If I want to plot
the DC voltage transfer curve, I would issue the following commands:
```
setplot dc1
plot Z
```


### Measuring Results


The .measure command is used to measure almost any parameter in your
circuit under some specified conditions. For example, it can be used
to measure rise time, fall time, delay, maxima and minima, etc.  

One use of the .measure command involves specifying a trigger and a
target (TRIG and TARG, respectively). A trigger tells the command when
to start measuring, and the target tells the command when to stop
measuring. The command will then report the value you want to measure
at the trigger condition, target condition, and the difference between
its values under those conditions. This is best illustrated through an
example that is supplied with the homework.


Let’s say we want to measure the propagation delay and the output rise
time of an inverter. First, we want to measure the delay from the
input rising to 50\% of the supply voltage to the output falling to
50\% of the supply voltage. Next, we define the output rise time metric as
the time it takes for the output to go from 10\% to 90\% of its
final value (i.e. from 0.12V to 1.08V for a 1.2V supply).

The structure of the command is as follows (note
that the plus signs allow you to continue a command on the next line
but isn't necessary):
```
.measure <ac|dc|tran> <name>
+ trig <node> val=<value> <rise|fall|cross>=<value>
+ targ <node> val=<value> <rise|fall|cross>=<value>
```
The first argument specifies what analysis statement to associate the
measurement with. For example, if measuring time the first argument
should be tran. If measuring frequency, it should be ac, and if
voltage, dc. The second argument is simply a name for your
measurement. We must
specify the trigger and target, which have identical
structure. For each, you must specify what node you want to trigger/target on, the value it needs to equal
at the time of the trigger/target, and how many rises/falls/crosses have occurred prior to the node reaching
that value. You should understand the concept of rising and falling, i.e. a signal going from low to high or
high to low. A cross is simply the sum of rises and falls.

Pay attention to the two .measure commands in the example spice file
that compute this:
```
.meas tran rise_delay 
+ trig v(vs) val=`0.5*supply_voltage` rise=1 
+ targ v(vo) val=`0.5*supply_voltage` fall=1
.meas tran rise_time 
+ trig v(vo) val=`0.1*supply_voltage` rise=1 
+ targ v(vo) val=`0.9*supply_voltage` rise=1
```
In the example for computing delay and rise time, we use the names
rise\_delay and rise\_time, respectively.  Since it is an inverter,
the rising input triggers a falling output. The rise\_delay is
triggered when v(vs), the input source, reaches half of the supply
voltage (a parameter) during the first rising crossing. The time is
then measured until the target which is when the v(vo), the output
voltage, reaches half the supply voltage during the first falling.
Similarly, the rise\_time is triggered when the output voltage, v(vo)
reaches 10\% of the supply voltage and stops when it reaches 90\% of
the supply voltage. Both of these are the first rising time.

If you simulate this netlist in Ngspice and look at the output, the
output will be:
```
rise_delay=   6.9297p  targ=  31.9797p   trig=  25.0500p
rise_time=   7.9874p  targ= 134.4470p   trig= 126.4596p
```
This gives you the trigger time, the target time, and the difference
with the label you gave for each measure.

One issue to watch out for is that you cannot set your trigger at a
zero value. If you want to trigger at zero, you can approximate the
measurement by using a very small, but non-zero, trigger value. For
example, I could trigger on the value 1n.




## Further information

There is a list of other tutorials on the Ngspice web page:
[http://ngspice.sourceforge.net/tutorials.html](http://ngspice.sourceforge.net/tutorials.html)
The ngspice manual is also available at:
[http://ngspice.sourceforge.net/docs/ngspice-manual.pdf](http://ngspice.sourceforge.net/docs/ngspice-manual.pdf)

