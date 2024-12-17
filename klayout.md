# Setting up KLayout and PDK for Sky130

## Installing KLayout

The KLayout that comes with OpenLane-2 Nix/Docker does not have Qt5 support,
which is required for the Sky130 technology files and the 2.5D viewing. You
will need to install KLayout from the [KLayout
website](https://www.klayout.de/build.html). It is pre-built for nearly all
platforms (Windows, MacOS, Linux) and is easy to install. 
- Windows 64-bit: [klayout-0.29.4-win64-install.exe](https://www.klayout.org/downloads/Windows/klayout-0.29.4-win64-install.exe)
- Ubuntu 20.04: [klayout-0.29.4-1_amd64.deb](https://www.klayout.org/downloads/Ubuntu/klayout-0.29.4-1_amd64.deb)
- MacOS: Depends on your OS Version. Check the [KLayout website](https://www.klayout.de/build.html) for the latest version.

*We have tested with version 0.29.4.* While this is not the newest, it is the same
as the version used in OpenLane-2, so it should be compatible.

*WARNING*: If you install another version, you must *UNINSTALL* KLayout before using
OpenLane-2 in subsequent parts of the class. Or, at least, remove it from
your PATH. The OL2 developers use locally installed executables instead of the
ones in the Docker container when they exist. You may run into problems during
KLayout steps in OL2 if you do not do this!

## Clone this repository

This repository contains the Sky130 technology files for KLayout. Clone this using:

```bash
git clone git@github.com:VLSIDA/cse122-222a-w25.git
cd cse122-222a-w25
```

## Starting KLayout with Sky130

The subdirectory `klayout/tech` contains the Sky130 technology files for
KLayout in one convenient place. You can start KLayout and have it use these by
running the following command:

```bash
KLAYOUT_PATH=klayout klayout -e
```
where klayout is the subdirectory with the tech subdirectory.
If you are in another directory, you can specify the absolute path to the klayout subdirectory instead.

You must specify the "-e" argument to enable edit mode. Otherwise, KLayout is
just started in read-only (viewer) mode.

You will then be greeted with the main KLayout window:

![Main window](klayout/klayout-main.png)


# Loading a GDS file

You can open a GDS file by selecting `File` -> `Open` and selecting the GDS file you want to open. Select
the GDS file in the klayout subdirectory called 'sky130_fd_sc_hd__inv_1.gds' and you will see the following:

![GDS file loaded with tech](klayout/klayout-load.png)

# Layer palette

On the right, you should see the "Layers" palette. However, this includes a lot of layers that
are not used and are grayed out. To only show the layers that are used in the cell click,
right click any layer and select "Hide Empty Layers". You should now see:

![Layer palette](klayout/klayout-layers.png)

If you double click on any layer, it will make it invisible. If you double click again, it will
make it visible. You can also select multiple layers by holding down the shift key and selecting
a range, or holding down the control key and selecting individual layers.

# Sky130 Menu

If the Sky130 technology files are properly loaded, you should see a menu called "Efabless sky130" with
the following contents:

![Sky130 menu](klayout/klayout-sky130-menu.png)

## 2.5D Viewer

The 2.5D viewer lets you look at and interact with a "3D" view of the layout:

![2.5D Cell View](klayout/klayout-d25.png)

This is useful for seeing how the the cell will look with the z-dimension
information. Note that commercial tools do not have this feature and it is only
really used for educational purposes.


## Running DRC


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





## Running LVS

Make sure to uncheck the "scale" option in the LVS dialog box. Sky130 uses an
odd scale factor in the spice netlist of microns instead of meters. If you
don't uncheck this, the transistor sizes won't match and your LVS will fail.


# Closing crash

For some reason, on my Ubuntu machine, KLayout crashes when I close it. I get this window and must select "Cancel" to
fully exit out:

![Crash on close](klayout/klayout-close-crash.png)