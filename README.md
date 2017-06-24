Broadcom: [![Broadcom](https://sonic-jenkins.westus.cloudapp.azure.com/job/broadcom/job/buildimage-brcm-all/badge/icon)](https://sonic-jenkins.westus.cloudapp.azure.com/job/broadcom/job/buildimage-brcm-all)
Cavium: [![Cavium](https://sonic-jenkins.westus.cloudapp.azure.com/job/cavium/job/buildimage-cavm-all/badge/icon)](https://sonic-jenkins.westus.cloudapp.azure.com/job/cavium/job/buildimage-cavm-all/)
Centec: [![Centec](https://sonic-jenkins.westus.cloudapp.azure.com/job/centec/job/buildimage-centec-all/badge/icon)](https://sonic-jenkins.westus.cloudapp.azure.com/job/centec/job/buildimage-centec-all/)
Mellanox: [![Mellanox](https://sonic-jenkins.westus.cloudapp.azure.com/job/mellanox/job/buildimage-mlnx-all/badge/icon)](https://sonic-jenkins.westus.cloudapp.azure.com/job/mellanox/job/buildimage-mlnx-all)
P4: [![Broadcom](https://sonic-jenkins.westus.cloudapp.azure.com/job/p4/job/buildimage-p4-all/badge/icon)](https://sonic-jenkins.westus.cloudapp.azure.com/job/p4/job/buildimage-p4-all)

# sonic-buildimage

## Build SONiC Switch Images

# Description 

Following is the instruction on how to build an [(ONIE)](https://github.com/opencomputeproject/onie) compatiable network operating system (NOS) installer image for network switches, and also how to build docker images running inside the NOS. Note that SONiC image are build per ASIC platform. Switches using the same ASIC platform share a common image. For a list of supported switches and ASIC, please refer to this [document](https://sonic-jenkins.westus.cloudapp.azure.com/job/p4/job/buildimage-p4-all).

# Hardware
Any server can be a build image server. We are using a server with 1T hard disk. The OS is Ubuntu 16.04.

# Prerequisites

## SAI Version 
SONiC V2 is using [SAI 0.9.4](https://github.com/opencomputeproject/SAI/tree/v0.9.4). 

## Clone or fetch the code repository with all git submodules
To clone the code repository recursively, assuming git version 1.9 or newer:

    git clone --recursive https://github.com/Azure/sonic-buildimage.git

NOTE: If the repo has already been cloned, however there are no files under the submodule directories (e.g., src/lldpd, src/ptf, src/sonic-linux-kernel, etc.), you can manually fetch all the git submodules as follows:

    git submodule update --init --recursive

You also need to change all git paths to relative path as we build all submodules inside the docker:

    git submodule foreach --recursive '[ -f .git ] && echo "gitdir: $(realpath --relative-to=. $(cut -d" " -f2 .git))" > .git'
    
## Usage

To build SONiC installer image and docker images, run the following commands:

    make configure PLATFORM=[ASIC_VENDOR]
    make

 **NOTE**: We recommend reserving 50G free space to build one platform.
    
The SONiC installer contains all docker images needed. SONiC uses one image for all devices of a same ASIC vendor. The supported ASIC vendors are:

- PLATFORM=broadcom
- PLATFORM=marvell (*pending*)
- PLATFORM=mellanox
- PLATFORM=cavium
- PLATFORM=centec
- PLATFORM=p4

For Broadcom ASIC, we build ONIE and EOS image. EOS image is used for Arista devices, ONIE image is used for all other Broadcom ASIC based devices. 

    make configure PLATFORM=broadcom
    # build ONIE image
    make target/sonic-broadcom.bin
    # build EOS image
    make target/sonic-aboot-broadcom.swi
 
You may find the rules/config file useful. It contains configuration options for the build process, like adding more verbosity or showing dependencies, username and password for base image etc.

Every docker image is built and saved to target/ directory.
So, for instance, to build only docker-database, execute:

    make target/docker-database.gz

Same goes for debian packages, which are under target/debs/:

    make target/debs/swss_1.0.0_amd64.deb

Every target has a clean target, so in order to clean swss, execute:

    make target/debs/swss_1.0.0_amd64.deb-clean

It is recommended to use clean targets to clean all packages that are built together, like dev packages for instance. In order to be more familiar with build process and make some changes to it, it is recommended to read this short [Documentation](README.buildsystem.md).

## Notes:
- If you are running make for the first time, a sonic-slave-${USER} docker image will be built automatically.
This may take a while, but it is a one-time action, so please be patient.

- The root user account is disabled. However, the created user can sudo.

- The target directory is ./target, containing the NOS installer image and docker images.
  - sonic-generic.bin: SONiC switch installer image (ONIE compatiable)
  - sonic-aboot.bin: SONiC switch installer image (Aboot compatiable)
  - docker-base.gz: base docker image where other docker images are built from, only used in build process (gzip tar archive)
  - docker-database.gz: docker image for in-memory key-value store, used as inter-process communication (gzip tar archive)
  - docker-fpm.gz: docker image for quagga with fpm module enabled (gzip tar archive)
  - docker-orchagent-brcm.gz: docker image for SWitch State Service (SWSS) on Broadcom platform (gzip tar archive)
  - docker-orchagent-cavm.gz: docker image for SWitch State Service (SWSS) on Cavium platform (gzip tar archive)
  - docker-orchagent-mlnx.gz: docker image for SWitch State Service (SWSS) on Mellanox platform (gzip tar archive)
  - docker-syncd-brcm.gz: docker image for the daemon to sync database and Broadcom switch ASIC (gzip tar archive)
  - docker-syncd-cavm.gz: docker image for the daemon to sync database and Cavium switch ASIC (gzip tar archive)
  - docker-syncd-mlnx.gz: docker image for the daemon to sync database and Mellanox switch ASIC (gzip tar archive)
  - docker-sonic-p4.gz: docker image for all-in-one for p4 software switch (gzip tar archive)

## Contribution Guide

All contributors must sign a contribution license agreement before contributions can be accepted.  Contact sonic-cla-agreements@microsoft.com.

## GitHub Workflow

We're following basic GitHub Flow. If you have no idea what we're talking about, check out [GitHub's official guide](https://guides.github.com/introduction/flow/). Note that merge is only performed by the repository maintainer.

Guide for performing commits:

* Isolate each commit to one component/bugfix/issue/feature
* Use a standard commit message format:

>     [component/folder touched]: Description intent of your changes
>
>     [List of changes]
>
> 	  Signed-off-by: Your Name your@email.com

For example:

>     swss-common: Stabilize the ConsumerTable
>
>     * Fixing autoreconf
>     * Fixing unit-tests by adding checkers and initialize the DB before start
>     * Adding the ability to select from multiple channels
>     * Health-Monitor - The idea of the patch is that if something went wrong with the notification channel,
>       we will have the option to know about it (Query the LLEN table length).
>
>       Signed-off-by: user@dev.null


* Each developer should fork this repository and [add the team as a Contributor](https://help.github.com/articles/adding-collaborators-to-a-personal-repository)
* Push your changes to your private fork and do "pull-request" to this repository
* Use a pull request to do code review
* Use issues to keep track of what is going on

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/). For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.
