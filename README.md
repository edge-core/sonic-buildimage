Mellanox[![Mellanox](https://sonic-jenkins.westus.cloudapp.azure.com/job/mellanox/job/buildimage-mlnx-all/badge/icon)](https://sonic-jenkins.westus.cloudapp.azure.com/job/mellanox/job/buildimage-mlnx-all)

# Build SONiC Switch Images - buildimage

# Description
Build an [Open Network Install Environment (ONIE)](https://github.com/opencomputeproject/onie) compatiable network operating system (NOS) installer image for network switches, and also build docker images running inside the NOS.

# Prerequisite
## Clone or fetch the code repository with all git submodules
To clone the code repository recursively, assuming git version 1.9 or newer

    git clone --recursive https://github.com/Azure/sonic-buildimage.git

If it is already cloned, however there is no files under ./dockers/docker-base/ or ./src/sonic-linux-kernel/, manually fetch all the git submodules.

    git submodule update --init --recursive

# Usage
To build NOS installer image and docker images, run command line

    make configure PLATFORM=[VENDOR]
    make

Supported VENDORs are:
- broadcom
- mellanox
- cavium
- p4

You can find rules/config file useful. It contains configuration options for build process, like adding more verbosity or showing dependencies, username and password for base image etc.

Every docker image is built and saved to target/ directory.
So, for instance, to build only docker-database, execute

    make target/docker-database.gz

Same goes for debian packages, which are under target/debs/:

    make target/debs/swss_1.0.0_amd64.deb

Every target has a clean target, so in order to clean swss, execute

    make target/debs/swss_1.0.0_amd64.deb-clean

It is recommended to use clean targets to clean all packages, that are built together, like dev packages for instance.

# Note:
If you are running make for the first time, a sonic-slave-${USER} docker image will be built automatically.
It is a one time action, so be patient.

The root is disabled, but the created user could sudo.

The target directory is ./target, containing the NOS installer image and docker images.
- sonic-generic.bin: SONiC switch installer image (ONIE compatiable)
- sonic-aboot.bin: SONiC switch installer image (Aboot compatiable)
- docker-base.gz: base docker image where other docker images are built from, only used in build process (gzip tar archive)
- docker-database.gz: docker image for in-memory key-value store, used as inter-process communication (gzip tar archive)
- docker-fpm.gz: docker image for quagga with fpm module enabled (gzip tar archive)
- docker-orchagent.gz: docker image for SWitch State Service (SWSS) (gzip tar archive)
- docker-syncd.gz: docker image for the daemon to sync database and Broadcom switch ASIC (gzip tar archive)
- docker-syncd-mlnx.gz: docker image for the daemon to sync database and Mellanox switch ASIC (gzip tar archive)
- docker-sonic-p4.gz: docker image for all-in-one for p4 software switch (gzip tar archive)

# Contribution guide

All contributors must sign a contribution license agreement before contributions can be accepted.  Contact sonic-cla-agreements@microsoft.com.

### GitHub Workflow

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
