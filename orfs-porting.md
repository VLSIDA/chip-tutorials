# Porting Designs 

Porting a design to ORFS requires:

1. Adding your design source verilog code to ```OpenROAD-flow-scripts/flow/designs/src/<your-design>```
2. Creating a respective design folder and *.sdc/*.mk file for each technology you port your design to.
3. Updating ```OpenROAD-flow-scripts/flow/Makefile``` to include a target for your design.

## Example: Porting sha256 (Verilog)
[sha256](https://github.com/secworks/sha256) is a cryptographic hash function which can be implemented as a hardware accelerator. We're concerned with the RTL files in [this directory](https://github.com/secworks/sha256/tree/master/src/rtl). 

### Add source code to ```OpenROAD-flow-scripts/flow/designs/src/```
Copy the RTL verilog files to ```OpenROAD-flow-scripts/flow/designs/src/sha256```

### Create design config for respective technology
For the sake of this example, we'll assume that the technology we're porting to is sky130hd.

We'll need to make a new folder in the ```OpenROAD-flow-scripts/flow/designs/```, and we'll call it ```sha256```.

The bare minimum that this folder will require is a ```config.mk``` (defines the target platform, the source code for the design, and allows for modifying design flow parameters), ```constraint.sdc```(contains constraints for the design and timing information), and ```rules-base.json```(design rule-checking file that enforces a limit on certain component metrics).

#### Making designs/sha256/config.mk
The config file requrires that we define ```DESIGN_NAME```, ```PLATFORM```, ```VERILOG_FILES```, and ```SDC_FILE```.

```
export DESIGN_NAME = sha256   # Module name of top-level instance
export PLATFORM    = sky130hd # Intended platform to create design for
export VERILOG_FILES = $(sort $(wildcard $(DESIGN_HOME)/src/$(DESIGN_NICKNAME)/*.v)) # Verilog source file location for sha256
export SDC_FILE      = $(DESIGN_HOME)/$(PLATFORM)/$(DESIGN_NICKNAME)/constraint.sdc  # SDC file location for sha256 (not yet created)
```

*Note: the design name, ```sha256```, was not random. The top level sha256 wrapper ```sha256.v``` contains the module instantiation ```sha256```. Also note the name of the clock (for use in the ```constraint.sdc``` file).

It's up to the designer to implement other variables to modify the design to fit within desired parameters (i.e timing, power, area). For example, you can modify a variable like ```CORE_UTILIZATION``` can allow the user to define how much of the design core area is used for the design or  ```PLACE_DENSITY``` to increase or decrease the density of cells during the placement stage. A list of environment variables in which you can use to modify the design and the flow can be found [here](https://openroad-flow-scripts.readthedocs.io/en/latest/user/FlowVariables.html).

```config.mk``` for sha256:
```
export DESIGN_NICKNAME = sha256
export DESIGN_NAME = sha256
export PLATFORM    = sky130hd

export VERILOG_FILES = $(sort $(wildcard $(DESIGN_HOME)/src/$(DESIGN_NICKNAME)/*.v))
export SDC_FILE      = $(DESIGN_HOME)/$(PLATFORM)/$(DESIGN_NICKNAME)/constraint.sdc

export CORE_UTILIZATION = 40
export TNS_END_PERCENT = 100

export CTS_CLUSTER_SIZE = 25
export CTS_CLUSTER_DIAMETER = 45
```

#### (Optional) designs/sha256/fastroute.tcl
Although optional, we can also modify the global routing stage to be better optimized depending on the platform the design is created for. Creating a ```fastroute.tcl``` file allows us to define the parameters for the global routing stage of the design. It can be used to set the specific layers to route through, and can do so based on the type of path as well (i.e clock or signal).

Example ```fastroute.tcl``` (not tested with sha256):

```
set_global_routing_layer_adjustment $::env(MIN_ROUTING_LAYER)-$::env(MAX_ROUTING_LAYER) 0.4

set_routing_layers -clock $::env(MIN_CLK_ROUTING_LAYER)-$::env(MAX_ROUTING_LAYER)
set_routing_layers -signal $::env(MIN_ROUTING_LAYER)-$::env(MAX_ROUTING_LAYER)
```

#### Making designs/sha256/constraint.sdc
The sdc file is where you'll define timing information, like the clock speed and Information on creating SDC (Synopsys Design Constraint) files can be found [here](https://github.com/VLSIDA/chip-tutorials/blob/main/sta-constraints.md).

Ensure that you use the correct clock name as described in the top level verilog file of the design.

```constraint.sdc```  for sha256: 
```
current_design sha256

current_design sha256

set clk_name  clk 
set clk_port_name clk 
set clk_period 6.5
set clk_io_pct 0.25

set clk_port [get_ports $clk_port_name] 

create_clock -name $clk_name -period $clk_period $clk_port

set non_clock_inputs [lsearch -inline -all -not -exact [all_inputs] $clk_port]

set_input_delay  [expr $clk_period * $clk_io_pct] -clock $clk_name $non_clock_inputs 
set_output_delay [expr $clk_period * $clk_io_pct] -clock $clk_name [all_outputs]
```

#### Updating ```OpenROAD-flow-scripts/flow/Makefile```

Append ```DESIGN_CONFIG=./designs/sky130hd/sha256/config.mk``` to the Makefile, uncomment, run ```make``` to run ORFS on the design.

## TODO:
### Defining sha256/rules-base.json
### Replacing a ported designs RAM with fakeRAM
### Porting designs written in SystemVerilog using SYNTH_HDL_FRONTEND (slang)

