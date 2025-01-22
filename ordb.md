This is info on how to access design data through the OpenRoad python API. It includes both ORDB as well as the timing API.
The [ASP-DAC24 Tutorial](https://github.com/ASU-VDA-Lab/ASP-DAC24-Tutorial) also has a lot of good examples.

You should install OpenROAD or [OpenLANE](installation.md).

For the full API:
```
openroad -python
```
to expose the Python interface.


There is a lot of info in the [tests here](https://github.com/The-OpenROAD-Project/OpenDB/tree/master/tests/python).

An example design is provided in `ordb/final.tar.gz` that you can extract with:
```
tar zxvf ordb/final.tar.gz
```


# How to read a design in OpenROAD
```
import openroad
from openroad import Design, Tech, Timing
import rcx
import os
import odb


openroad.openroad_version()

odb_file = "final/odb/spm.odb"
def_file = "final/def/spm.def"

lef_files = ["/home/mrg/.volare/sky130A/libs.ref/sky130_fd_sc_hd/techlef/sky130_fd_sc_hd__nom.tlef",
             "/home/mrg/.volare/sky130A/libs.ref/sky130_fd_sc_hd/lef/sky130_fd_sc_hd.lef"]
lib_files = ["/home/mrg/.volare/sky130A/libs.ref/sky130_fd_sc_hd/lib/sky130_fd_sc_hd__tt_025C_1v80.lib"]

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


# Design Database

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
## Iterate over library cells (masters)
```
for lib in tech.getDB().getLibs():
    for master in lib.getMasters():
        print(master.getName())
        for mterm in master.getMTerms():
            print(" ", mterm.getName())
```

# Timing Analysis

## How to run timing analysis
```
design.evalTclString("read_sdc {}".format("final/spm/sdc/spm.sdc")
timing = Timing(design)
```
## Getting Timing info
See iterating below to find pins:
```
timing.getPinArrival(inTerm, Timing.Rise)
timing.getPinSlew(inTerm, Timing.Rise)
timing.getPinSlack(inTerm, Timing.Ries, Timing.Max)
timing.getNetCap(net, corner, Timing.Max)
timing.getNetCap(net, corner, Timing.Min)
```

## Getting power
```
for corner in timing.getCorners():
    print(timing.staticPower(inst, corner),
          timing.dynamicPower(inst, corner),
          )
```

## Getting cell arcs
```
for lib in tech.getDB().getLibs():
    for master in lib.getMasters():
        print(master.getName())
        for mterm in master.getMTerms():
            print(" ", mterm.getName())
            for m in timing.getTimingFanoutFrom(mterm):
                print("  -> ", m.getName())

```

# Getting function and data names

The best way I've found to get additional API info is to set a breakpoint in your code and then use auto-complete to see what is available. Set a breakpoint:
```
for lib in tech.getDB().getLibs():
    for master in lib.getMasters():
        print(master.getName())
        for mterm in master.getMTerms():
            print(" ", mterm.getName())
            breakpoint()
```
and run your script:
```
OpenLane Container (2.2.9):/home/USER/class/chip-tutorials% openroad -python load.py
OpenROAD edf00dff99f6c40d67a30c0e22a8191c5d2ed9d6
Features included (+) or not (-): +Charts +GPU +GUI +Python
This program is licensed under the BSD-3 license. See the LICENSE file for details.
Components of this program may be licensed under more restrictive licenses which must be honored.
[WARNING ORD-0039] .openroad ignored with -python
[INFO ODB-0227] LEF file: /home/mrg/.volare/sky130A/libs.ref/sky130_fd_sc_hd/techlef/sky130_fd_sc_hd__nom.tlef, created 14 layers, 25 vias
[WARNING ODB-0220] WARNING (LEFPARS-2008): NOWIREEXTENSIONATPIN statement is obsolete in version 5.6 or later.
The NOWIREEXTENSIONATPIN statement will be ignored. See file /home/mrg/.volare/sky130A/libs.ref/sky130_fd_sc_hd/lef/sky130_fd_sc_hd.lef at line 2.

[INFO ODB-0227] LEF file: /home/mrg/.volare/sky130A/libs.ref/sky130_fd_sc_hd/lef/sky130_fd_sc_hd.lef, created 437 library cells
[ERROR STA-0340] cannot open 'final/spm/sdc/spm.sdc'.
sky130_fd_sc_hd__a2bb2o_1
  A1_N
> /home/mrg/class/chip-tutorials/load.py(31)<module>()
-> for mterm in master.getMTerms():
(Pdb) 
```
At the debug prompt, you can use the "p" command like this and press tab or indent twice to autocomplete:
```
(Pdb) p mterm.get
mterm.getBBox                 mterm.getDiffArea             mterm.getMPins                mterm.getName                 mterm.getSigType
mterm.getConstName            mterm.getIndex                mterm.getMTerm                mterm.getOxide2AntennaModel   mterm.getTargets
mterm.getDefaultAntennaModel  mterm.getIoType               mterm.getMaster               mterm.getShape
(Pdb) p mterm.get
```
Note that it doesn't do it unless you print. So this does not work:
```
(Pdb) mterm.get
```
