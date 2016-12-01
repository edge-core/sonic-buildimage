#!/bin/bash -x

# Install redis-server
sudo dpkg -i redis/*.deb

wget http://http.debian.net/debian/pool/main/h/hiredis/hiredis_0.13.3.orig.tar.gz
wget http://http.debian.net/debian/pool/main/h/hiredis/hiredis_0.13.3-2.debian.tar.xz
wget http://http.debian.net/debian/pool/main/h/hiredis/hiredis_0.13.3-2.dsc
dpkg-source -x hiredis_0.13.3-2.dsc
pushd hiredis-0.13.3; fakeroot debian/rules binary; popd

cp *.deb ..
