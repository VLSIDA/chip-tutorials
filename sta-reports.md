# STA Reports

## Reporting timing

### Max paths

### Min paths

## Reporting power


```tcl
set_power_activity -input 0.1
set_power_activity -input_port clk 0.5
set_power_activity -input_port rst 0.0
report_power
```

You can also use VCD (Verilog Change Dump) files to get the activity for better accuracy:
```tcl
read_vcd -scope tb/spm spm.vcd
```
if you've created a file with your testbench, `tb`.

# Reading Materials

- Digital Integrated Circuits (2nd Edition) - A Design Perspective by Rabaey, Chandrakasan, & Nikolic (ISBN-10: 0130909963) 
- Electronic Design Automation for IC Implementation, Circuit Design, and Process Technology Edited by Luciano Lavagno, Igor L. Markov, Grant Martin, and Louis K. Scheffer, CRC Press 2016. (ISBN-10: 0849379245) It is [available through the campus library](https://ucsc.primo.exlibrisgroup.com/permalink/01CDL_SCR_INST/gfkjds/informaworld_s10_1201_9781315215112_version2) and 
  
# License

Copyright 2024 VLSI-DA (see LICENSE for use)
