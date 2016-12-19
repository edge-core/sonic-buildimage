# SONiC Buildimage Guide
## Overview
SONiC build system is a *GNU make* based environment for build process automation.
It consists of two main parts:
 * Backend - collection of makefiles and other helpers that define generic target groups, used by recipes
 * Frontend - collection of recipes, that define metadata for each build target

## Structure
File structure of SONiC Buildimage is as follows:  
```
sonic-buildimage/  
  Makefile  
  slave.mk  
  sonic-slave/  
    Dockerfile  
  rules/  
    config  
    functions
    recipe1.mk
    ..
  dockers/  
    docker1/  
      Dockerfile.template    
    ..  
  src/  
    submodule1/    
    ..  
    package1/  
      Makefile  
    ..  
  platform/  
    vendor1/  
    ..  
  target/  
    debs/  
    python-wheels/  
```
### Backend  
**Makefile**, **slave.mk** and **sonic-slave/Dockerfile** are the backend of buildimage.  
*slave.mk* is the actual makefile. It defines a set of rules for *target groups* (more on that later).
You can find a make rules for every target that is defined in recipe there.  
*Makefile* is a wrapper over sonic-slave docker image.
Every part of build is executed in a docker container called sonic-slave, specifically crafted for this environment.
If build is started for the first time, a new sonic-slave image will be built form *sonic-slave/Dockerfile* on the machine.
It might take some time, so be patient.
After that all subsequent make commands will be executed inside this container.
*Makefile* takes every target that is passed to make command and delegates it as an entry point to a container,
making process of running container transparent.  
  
### Frontend  
**rules/** has a collection of recipes for platform independent targets.
Every recipe is a file that describes a metadata of a specific target, that is needed for its build.  
You might find **rules/config** very useful, as it is a configuration file for a build system, which enables/disables some tweaks.  
**dockers/** directory is a place where you can find Dockerfiles for generic docker images.  
**src/** is a place where a source code for generic packages goes.
It has both submodules (simple case, just run dpkg-buildpackage to build),
and directories with more complcated components, that provide their own Makefiles.  
**platform/** contains all vendor-specific recipes, submodules etc.  
Every **platform/[VENDOR]/** directory is a derived part of buildimage frontend, that defines rules and targets for a concrete vendor.  

### Build output
**target/** is basically a build output. You can find all biuld artifacts there.  
## Recipes and target groups
Now let's go over a definition of recipes and target groups.  
*Recipe* is a small makefile that defines a target and set of variables for building it.  
*Target group* is a set of targets that are built according to the same rulels.  

### Recipe example
Lets take a recipe for swss as an example:  
```make
# libswsscommon package

LIBSWSSCOMMON = libswsscommon_1.0.0_amd64.deb
$(LIBSWSSCOMMON)_SRC_PATH = $(SRC_PATH)/sonic-swss-common
$(LIBSWSSCOMMON)_DEPENDS += $(LIBHIREDIS_DEV) $(LIBNL3_DEV) $(LIBNL_GENL3_DEV) \
                            $(LIBNL_ROUTE3_DEV) $(LIBNL_NF3_DEV) \
			    $(LIBNL_CLI_DEV)
$(LIBSWSSCOMMON)_RDEPENDS += $(LIBHIREDIS) $(LIBNL3) $(LIBNL_GENL3) \
                             $(LIBNL_ROUTE3) $(LIBNL_NF3) $(LIBNL_CLI)
SONIC_DPKG_DEBS += $(LIBSWSSCOMMON)

LIBSWSSCOMMON_DEV = libswsscommon-dev_1.0.0_amd64.deb
$(eval $(call add_derived_package,$(LIBSWSSCOMMON),$(LIBSWSSCOMMON_DEV)))
```
First we define our package swsscommon.  
Then we secify **SRC_PATH** (path to sources),
**DEPENDS** (build dependencies),
and **RDEPENDS** (runtime dependencies for docker installation).  
Then we add our target to SONIC_DPKG_DEBS target group.  
At the end we define a dev package for swsscommon and make it derived from main one.
Using **add_derived_package** just makes a deep copy of package's metadata, so that we don't have to repeat ourselves.  

### Target groups
**TODO**  
## Tips & Tricks
**TODO**
