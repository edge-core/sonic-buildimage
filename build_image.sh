#!/bin/bash
## This script is to generate an ONIE installer image based on a file system overload

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

## Retrieval short version of Git revision hash for partition metadata
[[ -z $(git status --untracked-files=no -s) ]] || {
    echo "Error: There is local changes not committed to git repo. Cannot get a revision hash for partition metadata."
    exit 1
}
GIT_REVISION=$(git rev-parse --short HEAD)

## Generate an ONIE installer image
## Note: Don't leave blank between lines. It is single line command.
CONSOLE_SPEED=9600 \
CONSOLE_DEV=0 \
CONSOLE_FLAG=0 \
CONSOLE_PORT=0x3f8 \
./onie-mk-demo.sh $TARGET_PLATFORM $TARGET_MACHINE $TARGET_PLATFORM-$TARGET_MACHINE-$ONIEIMAGE_VERSION \
      installer $TARGET_MACHINE/platform.conf $OUTPUT_ONIE_IMAGE OS $GIT_REVISION $ONIE_IMAGE_PART_SIZE \
      $ONIE_INSTALLER_PAYLOAD
