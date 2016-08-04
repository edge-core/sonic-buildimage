#!/bin/bash -x

mkdir quagga

# Get debian source for 0.9.24.1-2
wget -O quagga_0.99.24.1.orig.tar.gz 'https://sonicstorage.blob.core.windows.net/packages/quagga_0.99.24.1.orig.tar.gz?sv=2015-04-05&sr=b&sig=7g3AC%2FkoX3wYztJYtXFt6Wl7zj%2BYwLkbXVNaSaRvUDU%3D&se=2026-07-21T00%3A07%3A31Z&sp=r'
tar -xzf quagga_0.99.24.1.orig.tar.gz --strip-components=1 -C quagga
ls -lrt

# Get debian packaging for 0.99.24.1-2
wget -O quagga_0.99.24.1-2.debian.tar.xz 'https://sonicstorage.blob.core.windows.net/packages/quagga_0.99.24.1-2.debian.tar.xz?sv=2015-04-05&sr=b&sig=VFEq4ec99OjVaypAx14DkO5I8N4CIBIPOuSw79qHUXg%3D&se=2026-07-21T00%3A03%3A10Z&sp=r'
tar -xJf quagga_0.99.24.1-2.debian.tar.xz -C quagga
ls -lrt

cd quagga
ls -lrt

# Enable FPM in debian/rules
awk '/--with-libpam/ { print; print "                --enable-fpm \\"; next }1' debian/rules > tmp && mv tmp debian/rules

# Update changelog
#echo 'quagga (0.99.24.1-2.1) unstable; urgency=medium
#
#   * Non-maintainer upload.
#   * enable fpm
#
#  -- Guohan Lu <gulv@microsoft.com>  Sat, 18 Jul 2015 16:10:47 -0700
#' > tmp && cat debian/changelog >> tmp && mv tmp debian/changelog

#./configure --enable-fpm
#make

sudo chmod a+x debian/rules
dpkg-buildpackage -rfakeroot -b -us -uc
cd ..
cp *.deb ..
