#!/bin/bash

PYTHON_VER=3.5.2
PYTHON_DEB_VER=8

wget -N http://http.debian.net/debian/pool/main/p/python3.5/python3.5_${PYTHON_VER}.orig.tar.xz
wget -N http://http.debian.net/debian/pool/main/p/python3.5/python3.5_${PYTHON_VER}-${PYTHON_DEB_VER}.debian.tar.xz
wget -N http://http.debian.net/debian/pool/main/p/python3.5/python3.5_${PYTHON_VER}-${PYTHON_DEB_VER}.dsc

dpkg-source -x python3.5_${PYTHON_VER}-${PYTHON_DEB_VER}.dsc

pushd python3.5-${PYTHON_VER}

dpkg-buildpackage -us -uc -b

popd

cp *.deb ../
