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

    NEXT_SONIC_IMAGE="$(sonic_installer list | grep "Next: " | cut -f2 -d' ')"
    CURRENT_SONIC_IMAGE="$(sonic_installer list | grep "Current: " | cut -f2 -d' ')"

    FS_PATH="/host/image-${NEXT_SONIC_IMAGE#SONiC-OS-}/fs.squashfs"
    FS_MOUNTPOINT="/tmp/image-${NEXT_SONIC_IMAGE#SONiC-OS-}-fs"

    if [[ "${CURRENT_SONIC_IMAGE}" == "${NEXT_SONIC_IMAGE}" ]]; then
        return "${FFB_SUCCESS}"
    fi

    while :; do
        mkdir -p "${FS_MOUNTPOINT}"
        mount -t squashfs "${FS_PATH}" "${FS_MOUNTPOINT}" || {
            >&2 echo "Failed to mount next SONiC image"
            break;
        }

        SDK_VERSION_FILE_PATH="${FS_MOUNTPOINT}/etc/mlnx/sdk-version"

        [ -f "${SDK_VERSION_FILE_PATH}" ] && {
            NEXT_SDK_VERSION="$(cat ${FS_MOUNTPOINT}/etc/mlnx/sdk-version)"
        } || {
            >&2 echo "No SDK version file ${SDK_VERSION_FILE_PATH}"
            break;
        }

        ISSU_CHECK_CMD="docker exec -t syncd issu --check ${NEXT_SDK_VERSION}"

        ${ISS_CHECK_CMD} > /dev/null && CHECK_RESULT="${FFB_SUCCESS}"

        break
    done

    umount -rf "${FS_MOUNTPOINT}" 2> /dev/null || true
    rm -rf "${FS_MOUNTPOINT}" 2> /dev/null || true

    return "${CHECK_RESULT}"
}

# Perform ISSU start
issu_start()
{
    ISSU_START_CMD="docker exec -t syncd issu --start"
    ${ISSU_START_CMD} > /dev/null

    EXIT_CODE=$?

    touch /host/warmboot/issu_started

    return $EXIT_CODE
}

# Perform ISSU end
issu_end()
{
    ISSU_END_CMD="docker exec -t syncd issu --end"
    ${ISSU_END_CMD} > /dev/null

    EXIT_CODE=$?

    return $EXIT_CODE
}
