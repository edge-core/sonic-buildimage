#! /bin/bash
## Check the platform PCIe device presence and status

VERBOSE="no"
RESULTS="PCIe Device Checking All Test"
EXPECTED="PCIe Device Checking All Test ----------->>> PASSED"
MAX_WAIT_SECONDS=15

function debug()
{
    /usr/bin/logger "$0 : $1"
    if [[ x"${VERBOSE}" == x"yes" ]]; then
        echo "$(date) $0: $1"
    fi
}

function check_and_rescan_pcie_devices()
{
    PCIE_CHK_CMD=$(sudo pcieutil pcie-check |grep "$RESULTS")
    PLATFORM=$(sonic-cfggen -H -v DEVICE_METADATA.localhost.platform)

    if [ ! -f /usr/share/sonic/device/$PLATFORM/plugins/pcie.yaml ]; then
        debug "pcie.yaml does not exist! can't check pcie status!"
        exit
    fi

    begin=$SECONDS
    end=$((begin + MAX_WAIT_SECONDS))
    rescan_time=$((MAX_WAIT_SECONDS/2))
    rescan_time=$((begin + rescan_time))

    while true
    do
        now=$SECONDS
        if [[ $now -gt $end ]]; then
            break
        fi

        if [ "$PCIE_CHK_CMD" = "$EXPECTED" ]; then
            redis-cli -n 6 SET "PCIE_STATUS|PCIE_DEVICES" "PASSED"
            debug "PCIe check passed"
            exit
        else
            debug "sleep 0.1 seconds"
            sleep 0.1
        fi

        if [ $now -gt $rescan_time ]; then
            debug "PCIe check failed, try pci bus rescan"
            echo 1 > /sys/bus/pci/rescan
            rescan_time=$end
        fi

     done
     debug "PCIe check failed"
     redis-cli -n 6 SET "PCIE_STATUS|PCIE_DEVICES" "FAILED"
}

check_and_rescan_pcie_devices
