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

IMAGE_VERSION=$(. functions.sh && sonic_get_version)

if [ "$IMAGE_TYPE" = "onie" ]; then
    echo "Build ONIE installer"
    mkdir -p `dirname $OUTPUT_ONIE_IMAGE`
    sudo rm -f $OUTPUT_ONIE_IMAGE

    # Copy platform-specific ONIE installer config files where onie-mk-demo.sh expects them
    rm -rf ./installer/x86_64/platforms/
    mkdir -p ./installer/x86_64/platforms/
    for VENDOR in `ls ./device`; do
        for PLATFORM in `ls ./device/$VENDOR`; do
            if [ -f ./device/$VENDOR/$PLATFORM/installer.conf ]; then
                cp ./device/$VENDOR/$PLATFORM/installer.conf ./installer/x86_64/platforms/$PLATFORM
            fi
        done
    done

    ## Generate an ONIE installer image
    ## Note: Don't leave blank between lines. It is single line command.
    ./onie-mk-demo.sh $TARGET_PLATFORM $TARGET_MACHINE $TARGET_PLATFORM-$TARGET_MACHINE-$ONIEIMAGE_VERSION \
          installer platform/$TARGET_MACHINE/platform.conf $OUTPUT_ONIE_IMAGE OS $IMAGE_VERSION $ONIE_IMAGE_PART_SIZE \
          $ONIE_INSTALLER_PAYLOAD
## Use 'aboot' as target machine category which includes Aboot as bootloader
elif [ "$IMAGE_TYPE" = "aboot" ]; then
    echo "Build Aboot installer"
    mkdir -p `dirname $OUTPUT_ABOOT_IMAGE`
    sudo rm -f $OUTPUT_ABOOT_IMAGE
    sudo rm -f $ABOOT_BOOT_IMAGE
    ## Add main payload
    cp $ONIE_INSTALLER_PAYLOAD $OUTPUT_ABOOT_IMAGE
    ## Add Aboot boot0 file
    j2 -f env files/Aboot/boot0.j2 ./onie-image.conf > files/Aboot/boot0
    sed -i -e "s/%%IMAGE_VERSION%%/$IMAGE_VERSION/g" files/Aboot/boot0
    pushd files/Aboot && zip -g $OLDPWD/$OUTPUT_ABOOT_IMAGE boot0; popd
    pushd files/Aboot && zip -g $OLDPWD/$ABOOT_BOOT_IMAGE boot0; popd
    echo "$IMAGE_VERSION" >> .imagehash
    zip -g $OUTPUT_ABOOT_IMAGE .imagehash
    zip -g $ABOOT_BOOT_IMAGE .imagehash
    rm .imagehash
    echo "SWI_VERSION=42.0.0" > version
    echo "SWI_MAX_HWEPOCH=1" >> version
    echo "SWI_VARIANT=US" >> version
    zip -g $OUTPUT_ABOOT_IMAGE version
    zip -g $ABOOT_BOOT_IMAGE version
    rm version

    zip -g $OUTPUT_ABOOT_IMAGE $ABOOT_BOOT_IMAGE
    rm $ABOOT_BOOT_IMAGE
else
    echo "Error: Non supported target platform: $TARGET_PLATFORM"
    exit 1
fi
