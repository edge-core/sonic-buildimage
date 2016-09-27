#!/bin/bash
## This script is to build the libnl3 3.2.27-1
##
## USAGE:
##   ./build.sh

# Obtaining the libnl3
rm -rf ./libnl3
git clone https://anonscm.debian.org/git/collab-maint/libnl3.git
pushd ./libnl3
git checkout -f b77c0e49cb

# Patch
export QUILT_PATCHES=debian/patches
quilt push
quilt push
quilt push
quilt push
quilt push
dpkg-buildpackage -rfakeroot -b -us -uc

popd
cp *.deb ..
