#!/bin/bash
## This script is to build the kernel-mft-dkms_4.5.0-3.16.0-4-amd64 kernel modules
##
## USAGE:
##   ./build.sh

MFT_NAME=mft-4.5.0-31-x86_64-deb
MFT_TGZ=${MFT_NAME}.tgz
MFT_KERNEL_DEB=kernel-mft-dkms_4.5.0-31_all.deb
KERNELVER=3.16.0-4-amd64

wget -N http://www.mellanox.com/downloads/MFT/${MFT_TGZ}
tar xzf $MFT_TGZ
pushd $MFT_NAME/SDEBS
dpkg -i $MFT_KERNEL_DEB
TARBALL_PATH=$(dkms mkdriverdisk kernel-mft-dkms/4.5.0 -a all -d ubuntu -k ${KERNELVER} --media tar | grep "Disk image location" | cut -d':' -f2)
echo $TARBALL_PATH
tar xvf $TARBALL_PATH
popd

cp $MFT_NAME/SDEBS/ubuntu-drivers/3.16.0/kernel-mft-dkms_4.5.0-3.16.0-4-amd64_all.deb ../
cp $MFT_NAME/DEBS/mft-4.5.0-31.amd64.deb ../
