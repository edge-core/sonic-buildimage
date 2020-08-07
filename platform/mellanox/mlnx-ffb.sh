#!/bin/bash

FFB_SUCCESS=0
FFB_FAILURE=1

# Check if ISSU is enabled on this device
check_issu_enabled()
{
    CHECK_RESULT="${FFB_FAILURE}"
    ISSU_CHECK_CMD="show platform mlnx issu"

    # Check whether show ISSU status outputs ENABLED
    if [[ `$ISSU_CHECK_CMD` =~ "enabled" ]]; then
        # ISSU enabled, return success
        CHECK_RESULT="${FFB_SUCCESS}"
    fi

    return "${CHECK_RESULT}"
}

# Check if ISSU upgrade from current SDK to next image SDK is supported
check_sdk_upgrade()
{
    CHECK_RESULT="${FFB_FAILURE}"

    NEXT_SONIC_IMAGE="$(sonic-installer list | grep "Next: " | cut -f2 -d' ')"
    CURRENT_SONIC_IMAGE="$(sonic-installer list | grep "Current: " | cut -f2 -d' ')"

    FS_PATH="/host/image-${NEXT_SONIC_IMAGE#SONiC-OS-}/fs.squashfs"
    FS_MOUNTPOINT="/tmp/image-${NEXT_SONIC_IMAGE#SONiC-OS-}-fs"

    if [[ "${CURRENT_SONIC_IMAGE}" == "${NEXT_SONIC_IMAGE}" ]]; then
        return "${FFB_SUCCESS}"
    fi

    while :; do
        mkdir -p "${FS_MOUNTPOINT}"
        mount -t squashfs "${FS_PATH}" "${FS_MOUNTPOINT}" || {
            >&2 echo "Failed to mount next SONiC image"
            break
        }

        ISSU_VERSION_FILE_PATH="/etc/mlnx/issu-version"

        [ -f "${ISSU_VERSION_FILE_PATH}" ] || {
            >&2 echo "No ISSU version file found ${ISSU_VERSION_FILE_PATH}"
            break
        }

        [ -f "${FS_MOUNTPOINT}/${ISSU_VERSION_FILE_PATH}" ] || {
            >&2 echo "No ISSU version file found ${ISSU_VERSION_FILE_PATH} in ${NEXT_SONIC_IMAGE}"
            break
        }

        CURRENT_ISSU_VERSION="$(cat ${ISSU_VERSION_FILE_PATH})"
        NEXT_ISSU_VERSION="$(cat ${FS_MOUNTPOINT}/${ISSU_VERSION_FILE_PATH})"

        if [[ "${CURRENT_ISSU_VERSION}" == "${NEXT_ISSU_VERSION}" ]]; then
            CHECK_RESULT="${FFB_SUCCESS}"
        else
            >&2 echo "Current and next ISSU version do not match:"
            >&2 echo "Current ISSU version: ${CURRENT_ISSU_VERSION}"
            >&2 echo "Next ISSU version: ${NEXT_ISSU_VERSION}"
        fi

        break
    done

    umount -rf "${FS_MOUNTPOINT}" 2> /dev/null || true
    rm -rf "${FS_MOUNTPOINT}" 2> /dev/null || true

    return "${CHECK_RESULT}"
}

check_ffb()
{
    check_issu_enabled || {
        >&2 echo "ISSU is not enabled on this HWSKU"
        return "${FFB_FAILURE}"
    }

    check_sdk_upgrade || {
        >&2 echo "SDK upgrade check failued"
        return "${FFB_FAILURE}"
    }

    return "${FFB_SUCCESS}"
}

