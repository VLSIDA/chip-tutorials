# STA Reports

## Constraints

One useful command is `report_constraints` which will show all the unconstrained paths:
```
report_checks -unconstrained
```


## Reporting timing

You can get arrival and required times of specific points in a circuit like this:
```
openroad> report_arrival input33/X
 (clk ^) r 2.19:2.19 f 2.17:2.17
```
which says that the min:max rising and falling delays are 2.19:2.19 and 2.17:2.17, respectively.
Similarly, you can get the delays of an edge with:
```
openroad> report_edges -to input1/X
A -> X combinational
  ^ -> ^ 0.30:0.30
  v -> v 0.24:0.24
```
Which shows the risting input to rising output and falling input to falling
output of the non-inverting gate.

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

# License

Copyright 2024 VLSI-DA (see [LICENSE](LICENSE) for use)
