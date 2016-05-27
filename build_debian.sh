#!/bin/bash
## This script is to automate the preparation for a debian file system, which will be used for
## an ONIE installer image.
##
## USAGE:
##   ./build_debian USERNAME PASSWORD_ENCRYPTED
## PARAMETERS:
##   USERNAME
##          The name of the default admin user
##   PASSWORD_ENCRYPTED
##          The encrypted password, expected by chpasswd command

## Default user
USERNAME=$1
[ -n "$USERNAME" ] || {
    echo "Error: no or empty USERNAME argument"
    exit 1
}

## Password for the default user, customizable by environment variable
## By default it is an empty password
## You may get a crypted password by: perl -e 'print crypt("YourPaSsWoRd", "salt"),"\n"'
PASSWORD_ENCRYPTED=$2
[ -n "$PASSWORD_ENCRYPTED" ] || {
    echo "Error: no or empty PASSWORD_ENCRYPTED argument"
    exit 1
}

## Include common functions
. functions.sh

## Enable debug output for script
set -x -e

## Working directory to prepare the file system
FILESYSTEM_ROOT=./fsroot
## Hostname for the linux image
HOSTNAME=acs
DEFAULT_USERINFO="Default admin user,,,"

## Read ONIE image related config file
. ./onie-image.conf
[ -n "$ONIE_IMAGE_PART_SIZE" ] || {
    echo "Error: Invalid ONIE_IMAGE_PART_SIZE in onie image config file"
    exit 1
}
[ -n "$ONIE_INSTALLER_PAYLOAD" ] || {
    echo "Error: Invalid ONIE_INSTALLER_PAYLOAD in onie image config file"
    exit 1
}
[ -n "$FILESYSTEM_SQUASHFS" ] || {
    echo "Error: Invalid FILESYSTEM_SQUASHFS in onie image config file"
    exit 1
}

## Prepare the file system directory
if [[ -d $FILESYSTEM_ROOT ]]; then
    sudo rm -r $FILESYSTEM_ROOT || die "Failed to clean chroot directory"
fi
mkdir -p $FILESYSTEM_ROOT

## Build a basic Debian system by debootstrap
echo '[INFO] Debootstrap...'
sudo debootstrap --variant=minbase --arch amd64 jessie $FILESYSTEM_ROOT http://ftp.us.debian.org/debian

## Config hostname and hosts, otherwise 'sudo ...' will complain 'sudo: unable to resolve host ...'
sudo LANG=C chroot $FILESYSTEM_ROOT /bin/bash -c "echo '$HOSTNAME' > /etc/hostname"
sudo LANG=C chroot $FILESYSTEM_ROOT /bin/bash -c "echo '127.0.0.1       $HOSTNAME' >> /etc/hosts"

## Config basic fstab
sudo LANG=C chroot $FILESYSTEM_ROOT /bin/bash -c 'echo "proc /proc proc defaults 0 0" >> /etc/fstab'
sudo LANG=C chroot $FILESYSTEM_ROOT /bin/bash -c 'echo "sysfs /sys sysfs defaults 0 0" >> /etc/fstab'

## Note: mounting is necessary to makedev and install linux image
echo '[INFO] Mount all'
## Output all the mounted device for troubleshooting
mount
trap_push 'sudo umount $FILESYSTEM_ROOT/proc || true'
sudo LANG=C chroot $FILESYSTEM_ROOT mount proc /proc -t proc
clean_sys() {
    sudo umount $FILESYSTEM_ROOT/sys/fs/cgroup/*            \
                $FILESYSTEM_ROOT/sys/fs/cgroup              \
                $FILESYSTEM_ROOT/sys || true
}
trap_push clean_sys
sudo LANG=C chroot $FILESYSTEM_ROOT mount sysfs /sys -t sysfs

## Pointing apt to public apt mirrors and getting latest packages, needed for latest security updates
sudo cp docker-base/sources.list $FILESYSTEM_ROOT/etc/apt/
sudo cp files/apt/apt.conf.d/81norecommends $FILESYSTEM_ROOT/etc/apt/apt.conf.d/
sudo LANG=C chroot $FILESYSTEM_ROOT bash -c 'apt-mark auto `apt-mark showmanual`'

## Note: set lang to prevent locale warnings in your chroot
sudo LANG=C chroot $FILESYSTEM_ROOT apt-get -y update
sudo LANG=C chroot $FILESYSTEM_ROOT apt-get -y upgrade
echo '[INFO] Install packages for building image'
sudo LANG=C chroot $FILESYSTEM_ROOT apt-get -y install makedev psmisc

## Create device files
echo '[INFO] MAKEDEV'
sudo LANG=C chroot $FILESYSTEM_ROOT /bin/bash -c 'cd /dev && MAKEDEV generic'
## Install initramfs-tools and linux kernel
## Note: initramfs-tools recommends depending on busybox, and we really want busybox for
## 1. commands such as touch
## 2. mount supports squashfs
## However, 'dpkg -i' plus 'apt-get install -f' will ignore the recommended dependency. So
## we install busybox explicitly
sudo LANG=C chroot $FILESYSTEM_ROOT apt-get -y install busybox
echo '[INFO] Install ACS linux kernel image'
## Note: duplicate apt-get command to ensure every line return zero
sudo dpkg --root=$FILESYSTEM_ROOT -i deps/initramfs-tools_*.deb || \
    sudo LANG=C DEBIAN_FRONTEND=noninteractive chroot $FILESYSTEM_ROOT apt-get -y install -f
sudo dpkg --root=$FILESYSTEM_ROOT -i deps/linux-image-3.16.0-4-amd64_*.deb || \
    sudo LANG=C DEBIAN_FRONTEND=noninteractive chroot $FILESYSTEM_ROOT apt-get -y install -f

## Update initramfs for booting with squashfs+aufs
cat files/initramfs-tools/modules | sudo tee -a $FILESYSTEM_ROOT/etc/initramfs-tools/modules > /dev/null

## Hook into initramfs: after partition mount and loop file mount
## 1. Prepare layered file system
## 2. Bind-mount docker working directory (docker aufs cannot work over aufs rootfs)
sudo cp files/initramfs-tools/union-mount $FILESYSTEM_ROOT/etc/initramfs-tools/scripts/init-bottom/union-mount
sudo chmod +x $FILESYSTEM_ROOT/etc/initramfs-tools/scripts/init-bottom/union-mount
sudo cp files/initramfs-tools/union-fsck $FILESYSTEM_ROOT/etc/initramfs-tools/hooks/union-fsck
sudo chmod +x $FILESYSTEM_ROOT/etc/initramfs-tools/hooks/union-fsck
sudo chroot $FILESYSTEM_ROOT update-initramfs -u

## Install docker
echo '[INFO] Install docker'
curl -sSL https://get.docker.com/ | sudo LANG=C chroot $FILESYSTEM_ROOT sh
## Remove garbage left by docker installation script
sudo rm $FILESYSTEM_ROOT/etc/apt/sources.list.d/docker.list
sudo chroot $FILESYSTEM_ROOT service docker stop
## Add docker config drop-in to select aufs, otherwise it may other storage driver
## Note: $_ means last argument of last command
sudo mkdir -p $FILESYSTEM_ROOT/etc/systemd/system/docker.service.d/
sudo cp files/docker/docker.service.conf $_

## Create default user
## Note: user should be in the group with the same name, and also in sudo/docker group
sudo LANG=C chroot $FILESYSTEM_ROOT useradd -G sudo,docker $USERNAME -c "$DEFAULT_USERINFO" -m -s /bin/bash
## Create password for the default user
echo $USERNAME:$PASSWORD_ENCRYPTED | sudo LANG=C chroot $FILESYSTEM_ROOT chpasswd -e

## Pre-install hardware drivers
sudo LANG=C chroot $FILESYSTEM_ROOT apt-get -y install      \
    firmware-linux-nonfree

## Pre-install the fundamental packages
## Note: gdisk is needed for sgdisk in install.sh
## Note: parted is needed for partprobe in install.sh
sudo LANG=C chroot $FILESYSTEM_ROOT apt-get -y install      \
    file                    \
    ifupdown                \
    iproute2                \
    isc-dhcp-client         \
    sudo                    \
    vim                     \
    tcpdump                 \
    ntp                     \
    ntpstat                 \
    openssh-server          \
    python                  \
    python-setuptools       \
    rsyslog                 \
    python-apt              \
    traceroute              \
    iputils-ping            \
    net-tools               \
    efibootmgr

## docker-py is needed by Ansible docker module
sudo LANG=C chroot $FILESYSTEM_ROOT easy_install pip
sudo LANG=C chroot $FILESYSTEM_ROOT pip install 'docker-py==1.6.0'
## Remove pip which is unnecessary in the base image
sudo LANG=C chroot $FILESYSTEM_ROOT pip uninstall -y pip

## Config DHCP for eth0
sudo tee -a $FILESYSTEM_ROOT/etc/network/interfaces > /dev/null <<EOF

auto eth0
allow-hotplug eth0
iface eth0 inet dhcp
EOF

sudo cp files/dhcp/rfc3442-classless-routes $FILESYSTEM_ROOT/etc/dhcp/dhclient-exit-hooks.d

## Clean up apt
sudo LANG=C chroot $FILESYSTEM_ROOT apt-get autoremove
sudo LANG=C chroot $FILESYSTEM_ROOT apt-get autoclean
sudo LANG=C chroot $FILESYSTEM_ROOT apt-get clean
sudo LANG=C chroot $FILESYSTEM_ROOT bash -c 'rm -rf /usr/share/doc/* /usr/share/locale/* /var/lib/apt/lists/* /tmp/*'

## Umount all
echo '[INFO] Umount all'
sudo LANG=C chroot $FILESYSTEM_ROOT fuser -km /sys || true
sudo LANG=C chroot $FILESYSTEM_ROOT umount -lf /sys
sudo LANG=C chroot $FILESYSTEM_ROOT fuser -km /proc || true
sudo LANG=C chroot $FILESYSTEM_ROOT umount /proc

## Prepare empty directory to trigger mount move in initramfs-tools/mount_loop_root, implemented by patching
sudo mkdir $FILESYSTEM_ROOT/host

## Compress most file system into squashfs file
sudo rm -f $ONIE_INSTALLER_PAYLOAD $FILESYSTEM_SQUASHFS
## Output the file system total size for diag purpose
sudo du -hs $FILESYSTEM_ROOT
sudo mksquashfs $FILESYSTEM_ROOT $FILESYSTEM_SQUASHFS -e boot -e var/lib/docker

## Compress together with /boot and /var/lib/docker as an installer payload zip file
pushd $FILESYSTEM_ROOT && sudo zip $OLDPWD/$ONIE_INSTALLER_PAYLOAD -r boot/ -r var/lib/docker; popd
sudo zip -g $ONIE_INSTALLER_PAYLOAD $FILESYSTEM_SQUASHFS
