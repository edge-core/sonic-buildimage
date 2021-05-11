#!/bin/bash

CONFIGURED_ARCH=$1
IMAGE_DISTRO=$2
FILESYSTEM_ROOT=$3
http_proxy=$4

TARGET=$TARGET_PATH
[ -z "$TARGET" ] && TARGET=target

. /usr/local/share/buildinfo/scripts/buildinfo_base.sh

TARGET_BASEIMAGE_PATH=$TARGET/versions/host-base-image
mkdir -p $TARGET_BASEIMAGE_PATH

generate_version_file()
{
    sudo LANG=C chroot $FILESYSTEM_ROOT /bin/bash -c "dpkg-query -W -f '\${Package}==\${Version}\n'" > $TARGET_BASEIMAGE_PATH/versions-deb-${IMAGE_DISTRO}-${CONFIGURED_ARCH}
}

if [ "$ENABLE_VERSION_CONTROL_DEB" != "y" ]; then
    if [[ $CONFIGURED_ARCH == armhf || $CONFIGURED_ARCH == arm64 ]]; then
        if [ $MULTIARCH_QEMU_ENVIRON == y ]; then
            # qemu arm bin executable for cross-building
            sudo mkdir -p $FILESYSTEM_ROOT/usr/bin
            sudo cp /usr/bin/qemu*static $FILESYSTEM_ROOT/usr/bin || true
        fi
        sudo http_proxy=$HTTP_PROXY SKIP_BUILD_HOOK=y debootstrap --variant=minbase --arch $CONFIGURED_ARCH $IMAGE_DISTRO $FILESYSTEM_ROOT http://deb.debian.org/debian
    else
        sudo http_proxy=$HTTP_PROXY SKIP_BUILD_HOOK=y debootstrap --variant=minbase --arch $CONFIGURED_ARCH $IMAGE_DISTRO $FILESYSTEM_ROOT http://debian-archive.trafficmanager.net/debian
    fi
    RET=$?
    if [ $RET -ne 0 ]; then
        exit $RET
    fi

    generate_version_file
    exit $RET
fi

ARCH=$(dpkg --print-architecture)
DISTRO=$(grep CODENAME /etc/os-release | cut -d= -f2)
if [ "$ARCH" != "$CONFIGURED_ARCH" ] || [ "$DISTRO" != "$IMAGE_DISTRO" ]; then
    "Not support to build different ARCH/DISTRO ${CONFIGURED_ARCH}:${$IMAGE_DISTRO} in ${ARCH}:${DISTRO}."
    exit 1
fi

BASE_VERSIONS=files/build/versions/host-base-image/versions-deb-${IMAGE_DISTRO}
BASEIMAGE_TARBALLPATH=$TARGET/baseimage
BASEIMAGE_TARBALL=$(realpath -e $TARGET)/baseimage.tgz

rm -rf $BASEIMAGE_TARBALLPATH $BASEIMAGE_TARBALL

ARCHIEVES=$BASEIMAGE_TARBALLPATH/var/cache/apt/archives
APTLIST=$BASEIMAGE_TARBALLPATH/var/lib/apt/lists
TARGET_DEBOOTSTRAP=$BASEIMAGE_TARBALLPATH/debootstrap
APTDEBIAN="$APTLIST/deb.debian.org_debian_dists_buster_main_binary-${CONFIGURED_ARCH}_Packages"
DEBPATHS=$TARGET_DEBOOTSTRAP/debpaths
DEBOOTSTRAP_BASE=$TARGET_DEBOOTSTRAP/base
DEBOOTSTRAP_REQUIRED=$TARGET_DEBOOTSTRAP/required
[ -d $BASEIMAGE_TARBALLPATH ] && rm -rf $BASEIMAGE_TARBALLPATH
mkdir -p $ARCHIEVES
mkdir -p $APTLIST
mkdir -p $TARGET_DEBOOTSTRAP
PACKAGES=$(sed -E 's/=(=[^=]*)$/\1/' $BASE_VERSIONS)
URL_ARR=($(apt-get download --print-uris $PACKAGES | cut -d" " -f1 | tr -d "'"))
PACKAGE_ARR=($PACKAGES)
LENGTH=${#PACKAGE_ARR[@]}
for ((i=0;i<LENGTH;i++))
do
    package=${PACKAGE_ARR[$i]}
    packagename=$(echo $package | sed -E 's/=[^=]*$//')
    url=${URL_ARR[$i]}
    filename=$(basename "$url")
    SKIP_BUILD_HOOK=y wget $url -P $ARCHIEVES
    echo $packagename >> $DEBOOTSTRAP_REQUIRED
    echo "$packagename /var/cache/apt/archives/$filename" >> $DEBPATHS
done
touch $APTDEBIAN
touch $DEBOOTSTRAP_BASE
(cd $BASEIMAGE_TARBALLPATH && fakeroot tar -zcf $BASEIMAGE_TARBALL .)

sudo debootstrap --verbose --variant=minbase --arch $CONFIGURED_ARCH --unpack-tarball=$BASEIMAGE_TARBALL $IMAGE_DISTRO $FILESYSTEM_ROOT
RET=$?
if [ $RET -ne 0 ]; then
    exit $RET
fi

generate_version_file
