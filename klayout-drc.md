
# Running DRC 


There are a few options for running DRC: 
- BEOL: "back-end of line" or device layer checks only
- FEOL: "front-end of line" or metal layer checks only
- Full: Both BEOL and FEOL checks.
- Custom: A custom set of DRC checks (BEOL, FEOL, grid, seal, etc.)

Sometimes, you might want to run just the FEOL checks to save run-time if, for
example, you are just checking the routing and you know your standard cells
pass DRC.

If you run DRC (Full), you wil get a window with the results like this:

![DRC Marker Browser with no errors](klayout/klayout-marker-browser.png)

which has the DRC errors (if any) categorized by the cell, type, etc. The
inverter should pass DRC with no errors.

If you load the "sky130_fd_sc_hd__inv_1-errors.gds" file, and run DRC, you should
see the following errors (after expanding the tabs):

![DRC Marker Browser with errors](klayout/klayout-marker-browser-errors.png)

If you click on a given error, it will open an explanation as well as highlight
the related error in the layout with a thin black line.

Detailed explanations of the DRC errors can be found in the Sky130 documentation:
[https://skywater-pdk.readthedocs.io/en/main/rules.html](https://skywater-pdk.readthedocs.io/en/main/rules.html)
We highlighted the poly rule and can go to the "poly" section to see the details:

![Poly design rules](klayout/klayout-poly-designrules.png)

Specifically, poly.7 specifies the "Extension of diffusion beyond poly" and poly.8 specifies the "Extension of poly beyond diffusion".
If you look closely at the examples, there is an example of poly.7 and poly.8 with measurement markers:

![Poly.7 and poly.8 examples](klayout/klayout-poly7-poly8.png)

In the example, there are also licon.1 and licon.5 errors which are available
in the [licon
section](https://skywater-pdk.readthedocs.io/en/main/rules/periphery.html#licon)
of the design rules.



