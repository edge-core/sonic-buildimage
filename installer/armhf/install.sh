#!/bin/sh

#  Copyright (C) 2014,2015 Curt Brune <curt@cumulusnetworks.com>
#  Copyright (C) 2015 david_yang <david_yang@accton.com>
#
#  SPDX-License-Identifier:     GPL-2.0

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

install_uimage() {
    echo "Copying uImage to NOR flash:"
    flashcp -v demo-${platform}.itb $mtd_dev
}

hw_load() {
    echo "cp.b $img_start \$loadaddr $img_sz"
}

. ./platform.conf

#install_uimage

#hw_load_str="$(hw_load)"

echo "Copying uImage to NAND flash:"
# global mount defines
demo_dev=ubi0
mtd_dev=/dev/$(cat /proc/mtd | grep "SONIC" | grep -o "mtd[0-9]")
mtd_num=$(echo $mtd_dev | grep -o "[0-9]")
demo_mount=/tmp
onie_dev=$(blkid | grep ONIE-BOOT | head -n 1 | awk '{print $1}' |  sed -e 's/:.*$//')

echo "Format mtd partition '$mtd_dev'"
ubiformat $mtd_dev
#attaches MTD devices (which describe raw flash) to UBI and creates corresponding UBI devices; ('-m 2' --> mtd2)
echo "ubiattach mtd '$mtd_num'"
ubiattach /dev/ubi_ctrl -m $mtd_num
#creates UBI volumes on UBI devices
ubimkvol  /dev/$demo_dev -N $demo_dev -s 3700MiB

demo_mount=$(mktemp -d)
mkdir -p $demo_mount
echo "Mounting ubifs partition"
mount -t ubifs /dev/ubi0_0 $demo_mount
echo "Mounting $demo_dev on $demo_mount..."
echo "sonic extract image starts ..."
# Decompress the file for the file system directly to the partition
unzip -o $ONIE_INSTALLER_PAYLOAD -x "$FILESYSTEM_DOCKERFS" -d $demo_mount/
cd $demo_mount
if [ -f fs.cpio ]
then
    cpio -id < fs.cpio
    rm fs.cpio
elif [ -f fs.squashfs ]
then
    unsquashfs -f -d $demo_mount fs.squashfs
    rm -f fs.squashfs
fi
cd -
TAR_EXTRA_OPTION="--numeric-owner"
mkdir -p $demo_mount/var/lib/$DOCKERFS_DIR
unzip -op $ONIE_INSTALLER_PAYLOAD "$FILESYSTEM_DOCKERFS" | tar -xpz $TAR_EXTRA_OPTION -f - -C $demo_mount/var/lib/$DOCKERFS_DIR

echo "unmounting nand partition"
umount $demo_mount

echo "Updating U-Boot environment variables"
#global uboot enviroment settings
#FW_ENV='/dev/mtd0 \t\t 0x00500000 \t 0x80000 \t 0x100000 \t 8'
FW_ENV='/dev/mtd0 \t\t 0x00500000 \t 0x80000 \t 0x100000 \t 2'

kernel_addr=0x1100000
fdt_addr=0x1000000

image_name="/boot/zImage"
fdt_name="/boot/armada-385-ET6448M_4G_Nand.dtb"

#BOOTARGS='setenv bootargs root='$demo_dev' rw rootwait ubi.mtd='$mtd_num' rootfstype=ubifs debug panic=1 ip=${ipaddr}:${serverip}:${gatewayip}:${netmask}:${hostname}:${netdev}:off console=ttyS0,115200 ${othbootargs} ${mtdparts}'
BOOTARGS='setenv bootargs root='$demo_dev' rw rootwait ubi.mtd='$mtd_num' rootfstype=ubifs panic=1 console=ttyS0,115200 ${othbootargs} ${mtdparts}'
UBI_LOAD='run ubi_sonic_boot_mount_ubi; ubifsload $kernel_addr $image_name;ubifsload $fdt_addr $fdt_name'
UBIBOOTCMD='run ubi_sonic_boot_bootargs; run ubi_sonic_boot_load; bootz $kernel_addr - $fdt_addr'


echo -e $FW_ENV > /etc/fw_env.config

fw_setenv -f image_name $image_name > /dev/null
fw_setenv -f fdt_name $fdt_name > /dev/null
fw_setenv -f kernel_addr $kernel_addr > /dev/null
fw_setenv -f fdt_addr $fdt_addr > /dev/null

#make sure ubi number (0) and ubi volume name (ubi0) are set correctly in bootargs_root:
#For example, the below command creates an 3000MiB volume on UBI device 0:
#setenv bootargs_root root=ubi0:ubi0 rw ubi.mtd=2 rootfstype=ubifs

fw_setenv -f mtdids 'nand0=armada-nand' > /dev/null
fw_setenv -f mtdparts 'mtdparts=armada-nand:10m(U-Boot)ro,208m@10m(ONIE),-(SONIC)' > /dev/null
fw_setenv -f ubi_sonic_boot_mount_ubi 'ubi part SONIC; ubifsmount ubi0' > /dev/null

fw_setenv -f ubi_sonic_boot_bootargs $BOOTARGS > /dev/null
fw_setenv -f ubi_sonic_boot_load $UBI_LOAD > /dev/null
fw_setenv -f ubi_sonic_boot $UBIBOOTCMD > /dev/null
fw_setenv -f bootcmd 'usb start; run ubi_sonic_boot' > /dev/null


cd /

# Set NOS mode if available.  For manufacturing diag installers, you
# probably want to skip this step so that the system remains in ONIE
# "installer" mode for installing a true NOS later.
if [ -x /bin/onie-nos-mode ] ; then
    /bin/onie-nos-mode -s
fi
