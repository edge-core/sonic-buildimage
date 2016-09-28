#!/bin/bash -x

pushd behavioral-model; ./autogen.sh; dpkg-buildpackage -us -uc -b -j4; popd

cp *.deb ../
