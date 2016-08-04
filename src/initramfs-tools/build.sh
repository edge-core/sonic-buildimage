#!/bin/bash
## This script is to build the initramfs-tools with patches
##
## USAGE:
##   ./build.sh

# Obtaining the initramfs-tools
rm -rf ./initramfs-tools
git clone --branch v0.120 https://anonscm.debian.org/git/kernel/initramfs-tools.git ./initramfs-tools

# Patch
pushd ./initramfs-tools
patch -p1 < $OLDPWD/loopback-file-system-support.patch

# Build the package
rm -f debian/*.debhelper.log
dpkg-buildpackage -rfakeroot -b -us -uc

popd
