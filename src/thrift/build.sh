#!/bin/bash -x

wget -nc http://http.debian.net/debian/pool/main/t/thrift/thrift_0.9.3.orig.tar.gz
wget -nc http://http.debian.net/debian/pool/main/t/thrift/thrift_0.9.3-2.debian.tar.xz
wget -nc http://http.debian.net/debian/pool/main/t/thrift/thrift_0.9.3-2.dsc
dpkg-source -x thrift_0.9.3-2.dsc
cd thrift-0.9.3
dpkg-buildpackage -d -rfakeroot -b -us -uc
cd ..
cp *.deb ../
