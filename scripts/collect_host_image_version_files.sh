#!/bin/bash

TARGET=$1
FILESYSTEM_ROOT=$2
VERSIONS_PATH=$TARGET/versions/host-image

mkdir -p $VERSIONS_PATH

sudo LANG=C chroot $FILESYSTEM_ROOT post_run_buildinfo

cp -r $FILESYSTEM_ROOT/usr/local/share/buildinfo/pre-versions $VERSIONS_PATH/
cp -r $FILESYSTEM_ROOT/usr/local/share/buildinfo/post-versions $VERSIONS_PATH/
