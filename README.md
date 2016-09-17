# Build SONiC Switch Images - buildimage

# Description
Build an [Open Network Install Environment (ONIE)](https://github.com/opencomputeproject/onie) compatiable network operating system (NOS) installer image for network switches, and also build docker images running inside the NOS.

# Prerequisite
## 1. Clone or fetch the code repository with all git submodules
To clone the code repository recursively, assuming git version 1.9 or newer

    git clone --recursive https://github.com/Azure/sonic-buildimage.git

If it is already cloned, however there is no files under ./dockers/docker-base/ or ./src/sonic-linux-kernel/, manually fetch all the git submodules.

    git submodule update --init --recursive

## 2. Build environment
Build a docker image by [the Dockerfile](https://github.com/Azure/sonic-build-tools/blob/master/sonic-slave/Dockerfile) and build all remains in the docker container.

## 3. Get vendor SAI SDK
Obtain Switch Abstraction Interface (SAI) SDK from one of supported vendors (see the list in [Usage](#usage) Section), and place it in the directory ./src/[VENDOR]-sdk/ as filelist.txt in that directory.

# Usage
To build NOS installer image and docker images, run command line

    make [VENDOR]-all USERNAME=[USERNAME] PASSWORD_ENCRYPTED=[PASSWORD_ENCRYPTED]

Supported VENDORs are:
- brcm: Broadcom
- mlnx: Mellanox

For example, the user name is 'admin' and the password is 'YourPaSsWoRd'. To build all the images for Broadcom platform, use the command:

    make brcm-all USERNAME="admin" PASSWORD_ENCRYPTED="$(perl -e 'print crypt("YourPaSsWoRd", "salt"),"\n"')"

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
