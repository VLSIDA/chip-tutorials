# Installing OpenROAD Flow Scripts

In this method, Docker will provide the binaries, but you first need to [install
Docker depending on your OS](docker.md).

## Clone ORFS

First, clone ORFS to get the designs and scripts:

```bash
git clone https://github.com/The-OpenROAD-Project/OpenROAD-flow-scripts.git
cd OpenROAD-flow-scripts
```

## Run ORFS Docker image

I use a bash script that I created to run ORFS:

```bash
#!/bin/bash

# Use first argument as tag if provided
if [ -n "$1" ]; then
  tag="$1"
  echo "Using user-specified tag: $tag"
else
  tag=$(git describe --tags 2>/dev/null)
  if [ -n "$tag" ]; then
    echo "Using Git tag: $tag"
  else
    echo "Warning: No tag specified and commit is not on a tag. Defaulting to 'latest'."
    tag="latest"
  fi
fi

echo "Running OpenROAD flow with tag: ${tag}"
docker run --rm -it \
  -u $(id -u ${USER}):$(id -g ${USER}) \
  -v $(pwd)/flow:/OpenROAD-flow-scripts/flow \
  -v $(pwd)/..:/OpenROAD-flow-scripts/UCSC_ML_suite \
  -e DISPLAY=${DISPLAY} \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  -v ${HOME}/.Xauthority:/.Xauthority \
  --network host \
  --security-opt seccomp=unconfined \
  openroad/orfs:${tag}

```

This will not only export your display so you can run GUI applications in the Docker, but it also
mounts the directory "flow" on your local filesystem in the Docker image. This directory contains the
designs, scripts, and the results when you run the designs.

Add the ```runorfs.sh``` to your filesystem in the ORFS cloned directory as a
file called ```runorfs.sh``` and make it executable:

```bash

chmod +x runorfs.sh

```

You can run the version corresponding to your version of ORFS by just executing
the script, or you can specify a [particular
tag](https://hub.docker.com/r/openroad/orfs/tags) or github commit ID. For
example:

```bash

# for the version corresponding to your ORFS repository
./runorfs.sh

# for a specific version, you can specify the tag
git checkout v3.0-3141-gb6d79b23
./runorfs.sh v3.0-3141-gb6d79b23

# or a commit ID
git checkout 7fcc19
./runorfs.sh 7fcc19

````

## Troubleshooting and Common mistakes

*Beware*, your cloned version of ORFS should match the version of the Docker image that you run. If it doesn't,
you may get differences if the command interfaces change. `runorfs.sh` does
this automatically via `git describe --tags`, but only if you cloned ORFS
with its full history — a `git clone --depth 1` will have no tags and
silently fall back to `openroad/orfs:latest`, which may not match the
scripts you just cloned. Prefer a full clone, or pass an explicit tag to
`./runorfs.sh`.

Recent `openroad/orfs:latest` images are built with **AVX-512**
instructions and will crash partway through the flow with "child killed:
illegal instruction" on CPUs that do not support it (this includes most
pre-Ice-Lake Intel desktops and every Zen/Zen2/Zen3 AMD part). If you see
that error, pin to an older tagged image — browse
[DockerHub tags](https://hub.docker.com/r/openroad/orfs/tags) and pass
one to `./runorfs.sh`, matching your cloned commit.

You can safely ignore the message "groups: cannot find name for group ID 1000" when you start the Docker image.

# Smoke Test

To check your installation, run a smoke test:

```bash
I have no name!@diode:/OpenROAD-flow-scripts$ cd flow
I have no name!@diode:/OpenROAD-flow-scripts/flow$ make

```

This will run, by default, the design GCD (Greatest Common Divisor) in the
Nangate 45nm technology. It will run the flow from synthesis to routing, and
you will get a lot of output, but it should end with something like this:

```
Log                        Elapsed/s Peak Memory/MB  sha1sum .odb [0:20)
1_1_yosys_canonicalize             0             38 45af71d069285cb71fba
1_2_yosys                          0             37 8f4f1609d45714b16838
1_synth                            0            102 2c0cb35f152969a57a97
2_1_floorplan                      0            121 4c0c21a703c4514a4f9e
2_2_floorplan_macro                0             98 4c0c21a703c4514a4f9e
2_3_floorplan_tapcell              0             98 41d55f307cb9baec622e
2_4_floorplan_pdn                  0            101 4b02fdf1131f9ecfb828
3_1_place_gp_skip_io              18            102 c60b97e4377b3a96d8c4
3_2_place_iop                      0            100 e10d623fff656d759c03
3_3_place_gp                      17            212 611a676ae84b63e3582b
3_4_place_resized                  0            119 611a676ae84b63e3582b
3_5_place_dp                       0            106 6f409421b824c2937041
4_1_cts                            2            128 3ae290878676cd808502
5_1_grt                           21            218 cc66d1cd20f7651b10e1
5_2_route                         25           2369 cfb6ef9f4d29c356f88b
5_3_fillcell                       0            101 e40b0e5835f90ee733e0
6_1_fill                           0             99 e40b0e5835f90ee733e0
6_1_merge                          2            424
6_report                           2            157
Total                             87           2369
```

Note, there might be a few "WARNING" messages, but that is ok.
To view the final result, you can run:

```bash
I have no name!@diode:/OpenROAD-flow-scripts/flow$ make gui_final
```

which should open the GCD design like this:
![Default GCD project in OpenROAD GUI](orfs/orfs_gcd_gui.png)

## Troubleshooting

You may get the following error if you try to run GUI applications from the docker.

```

Authorization required, but no authorization protocol specified
Could not load the Qt platform plugin "xcb" in "" even though it was found.

```

You can resolve this by running:

```bash
xhost +local:
```

before you start the Docker image. This will give the docker container
permission to access your display server (X11).

# License

Copyright 2025 VLSI-DA (see [LICENSE](LICENSE) for use)
