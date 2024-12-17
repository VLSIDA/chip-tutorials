
# Running LVS 

Make sure to uncheck the "scale" option in the LVS dialog box. Sky130 uses an
odd scale factor in the spice netlist of microns instead of meters. If you
don't uncheck this, the transistor sizes won't match and your LVS will fail.

