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
[ -z "$(git status --untracked-files=no -s --ignore-submodules)" ] || {
    echo "Error: There is local changes not committed to git repo. Cannot get a revision hash for partition metadata."
    exit 1
}
GIT_REVISION=$(git rev-parse --short HEAD)

mkdir -p `dirname $OUTPUT_ONIE_IMAGE`
sudo rm -f $OUTPUT_ONIE_IMAGE
if [ "$TARGET_MACHINE" = "generic" ]; then
    ## Generate an ONIE installer image
    ## Note: Don't leave blank between lines. It is single line command.
    ./onie-mk-demo.sh $TARGET_PLATFORM $TARGET_MACHINE $TARGET_PLATFORM-$TARGET_MACHINE-$ONIEIMAGE_VERSION \
          installer $TARGET_MACHINE/platform.conf $OUTPUT_ONIE_IMAGE OS $GIT_REVISION $ONIE_IMAGE_PART_SIZE \
          $ONIE_INSTALLER_PAYLOAD
## Use 'aboot' as target machine category which includes Aboot as bootloader
elif [ "$TARGET_MACHINE" = "aboot" ]; then
    ## Add Aboot boot0 file into the image
    cp $ONIE_INSTALLER_PAYLOAD $OUTPUT_ONIE_IMAGE
    pushd files/Aboot && sudo zip -g $OLDPWD/$OUTPUT_ONIE_IMAGE boot0; popd
    echo "$GIT_REVISION" >> .imagehash
    zip -g $OUTPUT_ONIE_IMAGE .imagehash
    rm .imagehash
else
    echo "Error: Non supported target platform: $TARGET_PLATFORM"
    exit 1
fi
