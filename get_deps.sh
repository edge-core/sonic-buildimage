#!/bin/bash
## This script is to build the dependencies of an ONIE installer image
##
## USAGE:
##   ./get_deps.sh

# Obtaining the initramfs-tools
rm -rf deps/initramfs-tools
git clone --branch v0.120 https://anonscm.debian.org/git/kernel/initramfs-tools.git deps/initramfs-tools

# Patch
pushd deps/initramfs-tools
patch -p1 < $OLDPWD/patch/initramfs-tools/loopback-file-system-support.patch

# Build the package
fakeroot debian/rules clean
fakeroot debian/rules binary

popd
