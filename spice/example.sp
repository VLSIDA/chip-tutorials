* Example Inverter with Transient Analysis and Measure

* include the MOSFET models with TT proccess 
.lib "$PDK_ROOT/sky130A/libs.tech/ngspice/sky130.lib.spice" tt

* include the standard cell library
.include '$PDK_ROOT/sky130A/libs.ref/sky130_fd_sc_hd/spice/sky130_fd_sc_hd.spice'

* our supplies are global to the hierarchy
*.global vdd gnd
.param supply_voltage=1.8V

* set the operating temperature
.option temp=27

* include the circuit to be simulated
Xinv A gnd gnd vdd vdd Z sky130_fd_sc_hd__inv_1

* fanout 4 capacitive load on inverter output
Xinv1 Z gnd gnd vdd vdd Z1 sky130_fd_sc_hd__inv_1
Xinv2 Z gnd gnd vdd vdd Z2 sky130_fd_sc_hd__inv_1
Xinv3 Z gnd gnd vdd vdd Z3 sky130_fd_sc_hd__inv_1
Xinv4 Z gnd gnd vdd vdd Z4 sky130_fd_sc_hd__inv_1

* define the supply voltages
VDD vdd 0 supply_voltage
*VSS gnd 0 0V

* create a voltage pulse on the input
VSW A 0 PULSE (0V supply_voltage 500ps 5ps 5ps 1000p 2000ps) DC 0V

* perform a VTC analysis of the inverter
* sweep VSW from 0 to supply_voltage with step size of 0.1V
.DC VSW 0 'supply_voltage' 0.1

* perform a 3ns transient analysis
.tran 1ps 3ns

.param half_supply = '0.5*supply_voltage'
.param slew_low = '0.1*supply_voltage'
.param slew_high = '0.9*supply_voltage'

* measure the input rise to output fall delay 
* uses a calculation to compute half of 50% of the supply voltage
.meas tran rise_delay trig v(A) val=half_supply rise=1 targ v(Z) val=half_supply fall=1
* measure the output rise time (slew)
.meas tran rise_time trig v(Z) val=slew_low rise=1 targ v(Z) val=slew_high rise=1

*.control
*run
*quit
*.endc

.END
