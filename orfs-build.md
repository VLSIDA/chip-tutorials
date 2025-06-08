# Building OpenROAD with ORFS

You can build OpenROAD from source either in a Docker image or locally if you have a supported machine.
The full instructions are at ORFS, but this is a document of what has worked for us.

Most people will not need to build OpenROAD from source. I encourage you to use
the [ORFS Installation](/orfs-installation.md) to avoid this unless you need to
modify the source code.

*BEWARE*, if you have local versions of tools installed, they will get priority
over the compiled versions in the Docker image. This includes Yosys, OpenSTA,
and OpenROAD. If you took CSE 125/225, you may have Yosys installed locally!

# Clone the repository

All step need to do this:

```bash
git clone https://github.com/The-OpenROAD-Project/OpenROAD-flow-scripts.git
cd OpepNROAD-flow-scripts
```

# Docker

## Dependencies

The dependencies are installed inside the Docker image, so you do not need to install them.
You do nee to [install docker](docker.md), though.

## Building the Docker image

You only need to run the build command:

```bash
./build_openroad.sh 
```

as Docker is the default build method.

### Debug symbols

*I don't use this flow, so if you have a suggestion, please let me know!*

*NOTE* the --openroad-args are not passed to the Docker build scripts, so you cannot enable debug like the
Local build method.

It does look like the docker build flow doesn't use the CMAKE parameters passed to the script:

```
# 22 175.4 [INFO] ./tools/OpenROAD/etc/Build.sh -dir=/OpenROAD-flow-scripts/tools/OpenROAD/build -threads=128 -cmake= -D CMAKE_INSTALL_PREFIX=/OpenROAD-flow-scripts/tools/install/OpenROAD -D CMAKE_INSTALL_RPATH=/OpenROAD-flow-scripts/dependencies/lib:/OpenROAD-flow-scripts/dependencies/lib64 -D CMAKE_INSTALL_RPATH_USE_LINK_PATH=TRUE
```

This is where it is called for local:

```
build_openroad.sh
```

```
254:        eval ${NICE} ./tools/OpenROAD/etc/Build.sh -dir="$DIR/tools/OpenROAD/build" -threads=${PROC} -cmake=\'${OPENROAD_APP_ARGS}\'
```

This is where it is called for docker:

```
tools/OpenROAD/docker/Dockerfile.builder
```

```
21:RUN ./etc/Build.sh -compiler=${compiler} -threads=${numThreads} -deps-prefixes-file=${depsPrefixFile}
```

Docker.builder docker image gets built from DockerHelper.sh, but that doesn't take any of the args in build_openroad.sh:

```
        ./etc/DockerHelper.sh create -target=builder -os="${DOCKER_OS_NAME}" -threads="${PROC}"
```

## Using OpenROAD in Docker

This is very similar to the ORFS docker image that you used in the [walkthrough](/orfs-walkthrough.md)
except that you need to specify a local docker image and tag:

```bash
```

# Local

## Dependencies

You need to run the commands in ```setup.sh``` to install dependencies. This does three things.
You can run this script if you are root access, but I break down each step since some do not
require root access.

1. (NO ROOT) It recursively clones the repsositories needed to build OpenROAD:

```bash
git submodule update --init --recursive
```

(Note, you could have run --recursive when you clone the repository as well,
but this is a good way to ensure you have the latest submodules.)

2. (NEEDS ROOT) Install system dependencies:

```bash
sudo ./etc/DependencyInstaller.sh -base
```

This is a script that comes with ORFS. It will install the dependencies
assuming that you have a supported OS.

3. (NO ROOT) Install the other common depdencies:

```bash
./etc/DependencyInstaller.sh -common -prefix="./dependencies"
```

This builds things such as specific versions of SWIG, cmake, etc. in the
subdirectory "dependencies".

## Building the code

tl;dr My command line looks like this:

```bash
source dev_env.sh
./build_openroad.sh --no_init --openroad-args "-DCMAKE_BUILD_TYPE=DEBUG" --local
```

The dev environment ensures that you use the dependencies in "./dependencies".
To compile the code locally (not in Docker), you specify ```--local```.

To add debug symbols, you can specify the ```--openroad-args``` flag with and
argument to cmake.

The ```--no_init``` flag is used to not re-initialize the submodules. In
addition to this, you can specify to use a particular repository and branch of
code with: ```--or_repo <REPO> --or_branch <BRANCH>```. By default this is the
ORFS repo and branch. I usually manually clone it and use the no init option.

```bash
./build_openroad.sh --local
```

This will update submodules to the version needed by the current commit.

# Using OpenROAD

To set your path with the newly built openroad, you should source the environment script:

```bash
source env.sh
```

You can then see that you are using the correct version of OpenROAD by running:

```bash
which openroad
```

which should point to

```
OpenROAD-flow-scripts/tools/install/OpenROAD/bin/openroad
```

## OpenROAD Regression Tests

You can run regression tests for OpenROAD overall by doing:

```bash
cd tools/OpenROAD/tests
# For a single test
./regression gcd_nangate45
# For all the tests (very slow!)
./regression.sh
```

or just:

```bash
openroad gcd_nangate45.tcl
```

## Module Regression Tests

You can run regression tests for a specific submodule like this:

```bash
cd tools/OpenROAD/src/rsz/tests
# Run all the tests, with 10 threads
./regression -j 10
# Run the tests that match the regex
./regression -R repair_setup
# Run a regression test TCL directly
openroad repair_setup1.tcl
```

The correct log output of a regression test is saved with the extension ".ok"
and the correct Verilog or DEF is saved with ".vok" and ".defok", respectively.
To determine correctness, the final result is compared with these. A simple
diff is usually used unless the test has equivalence checking enabled.

The outputs of the regression test will be saved in the results subdirectory.
The log is called ```<TEST>-tcl.log``` and the diff with the ".ok" log is in
```<TEST>-tcl.diff```. If there is a Verilog or DEF output, it is saved with
the extension ```<TEST>_out-tcl.v``` (or def).
