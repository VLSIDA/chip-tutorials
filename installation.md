# Installing OpenLane Binaries (OpenROAD, KLayout, etc.)

This assumes you are on a Unix machine or are using [WSL](wsl.md).
You must install OpenLane2 using ***either*** the Nix or the Docker method as discussed here:
[https://openlane2.readthedocs.io/en/latest/getting_started/installation_overview.html](https://openlane2.readthedocs.io/en/latest/getting_started/installation_overview.html)

For this class, we will be using *OpenLane 2.3.1* unless you are told later. Be sure to use this 
version for compatibility with our grading! The version is included in several steps below, so do not
leave it out.

# Option 1: Nix Instructions

In this method, Nix will provide the binaries, but you first need to install Nix depending on your OS:
[https://openlane2.readthedocs.io/en/latest/getting_started/common/nix_installation/index.html](https://openlane2.readthedocs.io/en/latest/getting_started/common/nix_installation/index.html)

Nix will use the binaries locally, but you need the Nix settings from the OpenLane2 repository.
To do this, you can clone this with:
```
git clone -b 2.3.1 https://github.com/efabless/openlane2
```

Change to the openlane2 directory and open a Nix shell:
```
 cd openlane2
 nix-shell
```
which should open a shell like this:
```
[nix-shell:~/openlane2]$
```

You should always use OpenLane in this shell since it is how the binaries are installed. 
The first time, it should download all of the correct binaries.

# Option 2: Docker Instructions

In this method, Docker will provide the binaries, but you first need to install Docker depending on your OS:
[https://openlane2.readthedocs.io/en/latest/getting_started/common/docker_installation/index.html](https://openlane2.readthedocs.io/en/latest/getting_started/common/docker_installation/index.html)

In this method, the binaries will be provided in a Docker image and the
OpenLane Python package will call commands in the Docker image as appropriate.

## Check Docker

Check that Docker is working by running:
```
docker run -it hello-world
```

and you should see "Hello from Docker!" with some other output.

## Install OpenLane2

You can install with Pip using:
```
python3 -m pip install openlane==2.3.1
```

From here, you can enter a Docker shell with the OpenLane tools by running:
```
openlane --dockerized
```
which should open a shell like this:
```
OpenLane Container (2.3.1):/home/<user>/<mydir>
```

You can either run OpenLane here, or you can run it from your regular OS and
the scripts will be smart enugh to run commands in the Docker image. Using this
shell will also allow you to run the GUI versions of tools since the OpenLane
scripts export the X display properly on most systems. 

For any issues refer to the Troubleshooting section.
# Smoke Test

To check your installation, run the "smoke test":
```
openlane --smoke-test
```
or (if you are using the Docker method and not in a Docker shell):
```
openlane --dockerized --smoke-test
```
This should end with the following:
```
[19:43:42] INFO     Smoke test passed.
```
Note, there might be a few "WARNING" messages, but that is ok.

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
This will give the docker container permission to access your display server (X11).

If you are on WSL and this did not resolve the issue try using the following command instead of
the regular Openlane command:
```bash
docker run -v /mnt/wslg:/mnt/wslg
           -v $HOME:$HOME
           -e PDK_ROOT=$HOME/.volare
           -w $(pwd)
           --user 1000:1000
           -e DISPLAY=:0
           -e XDG_RUNTIME_DIR=/mnt/wslg/runtime-dir
           --network host
           --security-opt seccomp=unconfined
           ghcr.io/efabless/openlane2:2.3.1 <command>
```
or this to run an interactive shell in the docker:
```bash
docker run -v /mnt/wslg:/mnt/wslg
           -v $HOME:$HOME
           -e PDK_ROOT=$HOME/.volare
           -w $(pwd)
           --user 1000:1000
           -e DISPLAY=:0
           -e XDG_RUNTIME_DIR=/mnt/wslg/runtime-dir
           --network host
           --security-opt seccomp=unconfined
           ghcr.io/efabless/openlane2:2.3.1 zsh
```
---
You may encounter the eror below depending on your Linux distrubution when trying to run the
command `python -m pip install <package>`:
```
error: externally-managed-environment

× This environment is externally managed
╰─> To install Python packages system-wide, try 'apt install
    python-xyz', where xyz is the package you are trying to
    install.
```
This means your distrubution disallows the use of `pip` to install Python packages system-wide.
You will create a [virual environment](venv.md) to resolve this.

# License

Copyright 2024 VLSI-DA (see [LICENSE](LICENSE) for use)
