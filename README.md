# Build Switch Images - buildimage

# Description
Build an [Open Network Install Environment (ONIE)](https://github.com/opencomputeproject/onie) compatiable network operating system (NOS) installer image for network switches, and also build docker images running inside the NOS.

# Prerequisite
## 1. Build environment
Preferably use [the Dockerfile](https://github.com/Azure/sonic-build-tools/blob/master/sonic-slave/Dockerfile), or use Debian Jessie and manually install packages appearing in the Dockerfile.
## 2. Linux kernel with switch drivers
Build the [Azure/sonic-linux-kernel](https://github.com/Azure/sonic-linux-kernel) project and copy the output .deb file into ./deps directory.

## 3. initramfs-tools with loop device support
Run the script to build the .deb file into ./deps directory.

    ./get_deps.sh
    
## 4. Fetch the git submodule
If there is no files under ./docker-base, manually fetch them.

    git submodule update --init --recursive

# Usage
## Build NOS installer image

    ./build_debian USERNAME PASSWORD_ENCRYPTED && ./build_image.sh
    
For example, the user name is 'admin' and the password is 'YourPaSsWoRd'.

    ./build_debian.sh "admin" "$(perl -e 'print crypt("YourPaSsWoRd", "salt"),"\n"')" && ./build_image.sh

The root is disabled, but the created user could sudo.


## Build docker images

    ./build_docker.sh docker-sswsyncd
    ./build_docker.sh docker-database
    ./build_docker.sh docker-bgp
    ./build_docker.sh docker-snmp
    ./build_docker.sh docker-lldp
    ./build_docker.sh docker-basic_router

# Contribution guide

All contributors must sign a contribution license agreement before contributions can be accepted.  Contact kasubra@microsoft.com or daloher@microsoft.com.  Later this will be automated.

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
