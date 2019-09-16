#!/bin/sh

#  Copyright (C) Marvell Inc
#

set -e

if [ -d "/etc/sonic" ]; then
    echo "Installing SONiC in SONiC"
    install_env="sonic"
elif grep -Fxqs "DISTRIB_ID=onie" /etc/lsb-release > /dev/null
then
    echo "Installing SONiC in ONIE"
    install_env="onie"
else
    echo "Installing SONiC in BUILD"
    install_env="build"
fi

cd $(dirname $0)
if [ -r ./machine.conf ]; then
    . ./machine.conf
fi

if [ -r ./onie-image-armhf.conf ]; then
    . ./onie-image-armhf.conf
fi


echo "Installer: platform: $platform"

# install_uimage will be overriden from platform.conf as it is non generic
install_uimage() {
    echo "Copying uImage to NOR flash:"
    flashcp -v demo-${platform}.itb $mtd_dev
}

# hw_load will be overriden from platform.conf as it is non generic
hw_load() {
    echo "cp.b $img_start \$loadaddr $img_sz"
}

. ./platform.conf

install_uimage

hw_load_str="$(hw_load)"

cd /

# Set NOS mode if available.  For manufacturing diag installers, you
# probably want to skip this step so that the system remains in ONIE
# "installer" mode for installing a true NOS later.
if [ -x /bin/onie-nos-mode ] ; then
    /bin/onie-nos-mode -s
fi
