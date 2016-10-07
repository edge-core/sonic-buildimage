#!/bin/bash
## This script is to build libteam
##
## USAGE:
##   ./build.sh

# Obtain libteam
rm -rf ./libteam
git clone https://github.com/jpirko/libteam.git
pushd ./libteam
git checkout -f v1.26
popd

git clone https://anonscm.debian.org/git/collab-maint/libteam.git tmp
pushd ./tmp
git checkout -f da006f2 # v1.26
popd
mv tmp/debian libteam/
rm -rf tmp

pushd ./libteam
dpkg-buildpackage -rfakeroot -b -us -uc

popd
cp *.deb ..

