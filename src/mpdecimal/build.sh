#!/bin/bash

MPDECIMAL_VER=2.4.2
MPDECIMAL_DEB_VER=1

wget -N http://http.debian.net/debian/pool/main/m/mpdecimal/mpdecimal_${MPDECIMAL_VER}.orig.tar.gz
wget -N http://http.debian.net/debian/pool/main/m/mpdecimal/mpdecimal_${MPDECIMAL_VER}-${MPDECIMAL_DEB_VER}.debian.tar.xz
wget -N http://http.debian.net/debian/pool/main/m/mpdecimal/mpdecimal_${MPDECIMAL_VER}-${MPDECIMAL_DEB_VER}.dsc

dpkg-source -x mpdecimal_${MPDECIMAL_VER}-${MPDECIMAL_DEB_VER}.dsc

pushd mpdecimal-${MPDECIMAL_VER}

sudo apt-get -y build-dep mpdecimal

dpkg-buildpackage -us -uc -b

popd

cp *.deb ../
