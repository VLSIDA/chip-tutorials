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
