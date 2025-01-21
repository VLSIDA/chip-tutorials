This is info on how to access design data through the OpenRoad python API. It includes both ORDB as well as the timing API.

You should install OpenROAD or [OpenLANE](installation.md) for the full API,
but if you only want the design database (no timing), you can use the Python
library which is installable like this:
```
pip install openroaddbpy
```

For the full API:
```
openroad -python
```
to expose the Python interface.


If you do not need timing information, you can read only database (design and library cell info) using the ODB python module:
```
import opendbpy as odb
import os 

current_dir = os.path.dirname(os.path.realpath(__file__))
tests_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
opendb_dir = os.path.abspath(os.path.join(tests_dir, os.pardir))
data_dir = os.path.join(tests_dir, "data")

db = odb.dbDatabase.create()
odb.read_lef(db, os.path.join(data_dir, "gscl45nm.lef"))
odb.read_def(db, os.path.join(data_dir, "design.def"))
chip = db.getChip()
if chip == None:
    exit("Read DEF Failed")
exit()
```
There is a lot of info in the [tests here](https://github.com/The-OpenROAD-Project/OpenDB/tree/master/tests/python).

# How to read a design in OpenROAD
```
import openroad
from openroad import Design, Tech, Timing
import rcx
import os
import odb


openroad.openroad_version()

TECH = "nangate45"
DESIGN = "gcd"


odb_file = f"results/{TECH}/{DESIGN}/base/6_final.odb"
def_file = f"results/{TECH}/{DESIGN}/base/6_final.def"
sdc_file = f"results/{TECH}/{DESIGN}/base/6_final.sdc"
spef_file = f"results/{TECH}/{DESIGN}/base/6_final.spef"

lef_files = ["platforms/nangate45/lef/NangateOpenCellLibrary.tech.lef"]
lib_files = ["platforms/nangate45/lib/NangateOpenCellLibrary_typical.lib"]
ext_rules = "platforms/nangate45/rcx_patterns.rules"


tech = Tech()
for lef_file in lef_files:
    tech.readLef(lef_file)
for lib_file in lib_files:
    tech.readLiberty(lib_file)

design = Design(tech)
```

You can either read the DEF or the ODB for the placement/routing:
```
design.readDef(def_file)
design.readDb(odb_file)
```

# Extraction
You can use extraction from either detailed routing or using the global routing. 
This TCL says to use either HPWL/placement or global routing:
```
estimate_parasitics
    -placement|-global_routing
    [-spef_file spef_file]
```

This is using detailed routing:
```
rcx.define_process_corner(ext_model_index=0, file="X")

#NOTE: This is position dependent
rcx.extract(ext_model_file=ext_rules,
            corner_cnt=1,
            max_res=50.0,
            coupling_threshold=0.1,
            cc_model=12,                
            context_depth=5,
            debug_net_id="",
            lef_res=False,
            no_merge_via_res=False)
```

## SPEF files

```
rcx.adjust_rc(res_factor,
             cc_factor,
             gndc_factor)
```

### Read/write SPEF

### Diff SPEF files
```
diff_spef -file 31-user_project_wrapper.spef
```
```
rcx.diff_spef(file=spef_file,
              r_conn=False,
              r_res=False,
              r_cap=False,
              r_cc_cap=False)
```

# Timing Analysis
## How to run timing analysis
```
design.evalTclString("read_sdc {}".format(sdc_file))
timing = Timing(design)
```
## Getting Timing info
See iterating below to find pins:
```
timing.getPinArrival(inTerm, Timing.Rise)
timing.getPinArrival(inTerm, Timing.Fall)
timing.getWireDelay(outTerm, inTerm, Timing.Rise)
timing.getWireDelay(outTerm, inTerm, Timing.Fall)
timing.getWireSlew(outTerm, inTerm, Timing.Rise)
timing.getWireSlew(outTerm, inTerm, Timing.Fall)
timing.getWireCap(outTerm, inTerm)
```

## Getting power
```
for corner in timing.getCorners():
    print(timing.staticPower(inst, corner),
          timing.dynamicPower(inst, corner),
          )
```


# How to iterate over the database
## Iterate over nets
```
for net in design.getBlock().getNets():
    print("**** ", net.getName())
```
## Iterate over gates
```
for inst in design.getBlock().getInsts():
    if "FILLER" in inst.getName():
        continue
    if "TAP" in inst.getName():
        continue
    if "decap" in inst.getMaster().getName():
        continue
    print(inst.getName(), 
          inst.getMaster().getName(),
          design.isSequential(inst.getMaster()), 
          design.isInClock(inst),
          design.isBuffer(inst.getMaster()),
          design.isInverter(inst.getMaster()),
          )
```
## Iterate over pins
```
for outTerm in inst.getTerms():
    if timing.isEndpoint(outTerm):
        pass
    if design.isInSupply(outTerm):
        pass
    if outTerm.isOutputSignal():
        pass
    if outTerm.isInputSignal():
        pass

```
## Iterate over library cells

