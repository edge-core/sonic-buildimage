#!/bin/bash -x

sudo pip install ctypesgen

sudo pip install crc16

pushd switch

mkdir -p p4-build/bmv2/switch
mkdir -p p4-build/bmv2/pd_thrift_gen

./autogen.sh
dpkg-buildpackage -us -uc -b -j4

popd

cp *.deb ../
