# Multi-corner timing analysis

Often we are not concerned with a single operating condition, but a range of
them. This can include manufacturing conditions (usually called "process"),
temperatures, and voltages. Collectively, these are referred to as "PVT". 

## What is a corner?

We are usually concerned with setup and hold times, which lead us to the idea
of fast and slow corners. We want slow corners for setup times, because they
will have the worst-case timing. We want fast corners for hold times, because
they will have the best-case timing. However, it is difficult to predict what
consistutes "fast" or "slow" for a given design. This is why multiple corners
are used. Modern designs can have dozens or even hundreds of corners. We will
illustrate with just a few in this tutorial which we will call "typical" (typ),
"best case" (bc), and "worst case" (wc).



An entire 

## Defining corners

```tcl
define_corners wc bc typ
read_lib -corner wc $env(PDK_ROOT)/sky130A/libs.ref/sky130_fd_sc_hd/lib/sky130_fd_sc_hd__ss_100C_1v60.lib
read_lib -corner bc $env(PDK_ROOT)/sky130A/libs.ref/sky130_fd_sc_hd/lib/sky130_fd_sc_hd__nom_n40C_1v95.lib
fead_lib -corner typ $env(PDK_ROOT)/sky130A/libs.ref/sky130_fd_sc_hd/lib/sky130_fd_sc_hd__tt_025C_1v80.lib
read_db odb/spm.db
read_spef -corner wc spef/max/spm.max.spef
read_spef -corner bc spef/max/spm.min.spef
read_spef -corner typ spef/max/spm.nom.spef
read_sdc sdc/spm.sdc
report_checks
```

## Reporting MC checks

```tcl
report_checks -corner wc
report_checks -corner bc
report_checks -corner typ
```


# License

Copyright 2024 VLSI-DA (see [LICENSE](LICENSE) for use)
