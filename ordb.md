This is info on how to access design data through the OpenRoad python API. It includes both ORDB as well as the timing API.

You should install OpenROAD or [OpenLANE](installation.md).

# How to access the API

You can run:
```
openroad -python
```
to expose the Python interface.


# How to read a design
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
# How to run timing analysis
```
design.evalTclString("read_sdc {}".format(sdc_file))
timing = Timing(design)
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

        rise_delay = 1.0e12*timing.getPinArrival(inTerm, Timing.Rise)
        fall_delay = 1.0e12*timing.getPinArrival(inTerm, Timing.Fall)
        print(outTerm.getName(), 
              rise_delay, 
              fall_delay
              )
```
## Iterate over library cells
