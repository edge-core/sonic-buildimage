#!/bin/bash
#
# The front panel management port is the ixgbe at the PCI address declared as
# eth0 in /etc/udev/rules.d/70-persistent-net.rules. The other ixgbe is parked
# at eth3 by the same rule file.
#
# udev cannot always complete the swap on its own: when it processes the panel
# port before the parked NIC has released eth0, the rename fails with
#   Failed to rename network interface N from 'ethX' to 'eth0': File exists
# This service fixes up whatever udev left behind. It must run before
# networking.service, which brings up eth0 from /etc/network/interfaces.

RULE_FILE="/etc/udev/rules.d/70-persistent-net.rules"

#From 70-persistent-net.rules we can use eth3 for the unused interface name
PARK_NAME="eth3"

log() {
    command logger --id=$$ -t "handle_mgmt_interface" "$@"
}

# PCI address the udev rule wants to see as eth0
MGMT_BUS=$(sed -n 's/.*KERNELS=="\([^"]*\)".*NAME:="eth0".*/\1/p' "$RULE_FILE" | head -1)
if [ -z "$MGMT_BUS" ]; then
    log "ERROR: no eth0 rule found in $RULE_FILE, giving up"
    exit 1
fi

# Resolve the PCI bus address of an interface from sysfs.
# /sys/class/net/<if>/device -> ../../../<domain:bus:dev.fn>
bus_by_ifname() {
    local bus target
    target=$(readlink -f "/sys/class/net/$1/device" 2>/dev/null)
    bus=$(basename "$target" 2>/dev/null)
    # Only accept things that look like a PCI address (dddd:bb:dd.f). Virtual
    # interfaces (bridge, veth, lo) have no 'device' symlink; guard those out.
    case "$bus" in
        [0-9a-fA-F]*:[0-9a-fA-F]*:*) ;;
        *) bus="" ;;
    esac
    #log "DEBUG: sysfs device for $1 -> ${target:-<none>}"
    #log "DEBUG: bus_by_ifname($1) -> ${bus:-<none>}"
    echo "$bus"
}

ifname_by_bus() {
    local dev ifname tries
    for tries in $(seq 1 30); do
        for dev in /sys/class/net/eth*; do
            ifname=$(basename "$dev")
            if [ "$(bus_by_ifname "$ifname")" = "$1" ]; then
                echo "$ifname"
                return 0
            fi
        done
        log "DEBUG: ifname_by_bus($1) not found (attempt $tries), sleeping 1s"
        sleep 1
    done
    return 1
}



MGMT_IF=$(ifname_by_bus "$MGMT_BUS")
if [ -z "$MGMT_IF" ]; then
    log "ERROR: no netdev found for $MGMT_BUS"
    exit 1
fi

if [ "$MGMT_IF" = "eth0" ]; then
    log "eth0 is already $MGMT_BUS, nothing to do"
    exit 0
fi

# eth0 is held by the wrong NIC (udev did not park it) - move it out of the way
if [ -e /sys/class/net/eth0 ]; then
    OCCUPANT_BUS=$(bus_by_ifname eth0)
    log "eth0 is held by ${OCCUPANT_BUS:-unknown}, renaming it to $PARK_NAME"
    ip link set dev eth0 down
    if ! ip link set dev eth0 name "$PARK_NAME"; then
        log "ERROR: failed to rename eth0 (${OCCUPANT_BUS:-unknown}) to $PARK_NAME"
        exit 1
    fi
fi

log "renaming $MGMT_IF ($MGMT_BUS) to eth0"
ip link set dev "$MGMT_IF" down
if ! ip link set dev "$MGMT_IF" name eth0; then
    log "ERROR: failed to rename $MGMT_IF to eth0"
    exit 1
fi

log "eth0 is now $MGMT_BUS"

ip link set dev eth0 up || log "ERROR: failed to set eth0 up"
log "bring up eth0"

