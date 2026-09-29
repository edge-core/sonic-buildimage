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

log() {
    echo "$@" | grep -qE "^ERROR" && priority=err || priority=info
    command logger --id=$$ -p syslog."$priority" -t "handle_mgmt_interface" "$@"
}

# PCI address the udev rule wants to see as eth0
MGMT_BUS=$(sed -n 's/.*KERNELS=="\([^"]*\)".*NAME:="eth0".*/\1/p' "$RULE_FILE" | head -1)
if [ -z "$MGMT_BUS" ]; then
    log "ERROR: no eth0 rule found in $RULE_FILE, giving up"
    exit 1
fi

# PCI address the udev rule wants to rename to eth3
ETH3_BUS=$(sed -n 's/.*KERNELS=="\([^"]*\)".*NAME:="eth3".*/\1/p' "$RULE_FILE" | head -1)
if [ -n "$ETH3_BUS" ]; then
    udevadm settle --timeout=5 --exit-if-exists="/sys/bus/pci/devices/${ETH3_BUS}/net/eth3" \
      || log "WARNING: cannot find eth3 on ${ETH3_BUS} after 5s"
fi

# Where to move the NIC that holds eth0: its own name from the rule file if it
# has one, otherwise the lowest ethN that no interface has and no rule claims.
# (amd-xgbe has no rule and can take eth0 if it registers after udev freed it.)
park_name_for() {
    local bus=$1
    local name
    local n
    name=$(sed -n "s/.*KERNELS==\"$bus\".*NAME:=\"\([^\"]*\)\".*/\1/p" "$RULE_FILE" | head -1)
    if [ -n "$name" ] && [ ! -e "/sys/class/net/$name" ]; then echo "$name"; return; fi
    for n in $(seq 1 31); do
        [ -e "/sys/class/net/eth$n" ] && continue
        grep -q "NAME:=\"eth$n\"" "$RULE_FILE" && continue
        echo "eth$n"; return
    done
}

# PCI address of an interface, in the form the udev rule uses for KERNELS.
# Read it from sysfs rather than 'ethtool -i': which ethtool runs depends on
# PATH, and /usr/bin/ethtool is pmon's cmd_wrapper (docker exec pmon ethtool),
# which a shell without the sbin directories on PATH picks up instead of the
# real /usr/sbin/ethtool, and which fails whenever pmon is not running.
bus_by_ifname() {
    local dev
    # Interfaces without a parent device (lo, bridges, veth) have no address.
    [ -e "/sys/class/net/$1/device" ] || return
    dev=$(readlink -f "/sys/class/net/$1/device")
    # The parent is not always the PCI function itself (virtio sits one level
    # below it), so walk up to the nearest PCI address, as udev's KERNELS does.
    while [ "$dev" != / ] && [ -n "$dev" ]; do
        case "${dev##*/}" in
            [0-9a-f][0-9a-f][0-9a-f][0-9a-f]:*) echo "${dev##*/}"; return ;;
        esac
        dev=${dev%/*}
    done
}

ifname_by_bus() {
    local dev ifname
    for dev in /sys/class/net/*; do
        ifname=$(basename "$dev")
        if [ "$(bus_by_ifname "$ifname")" = "$1" ]; then
            echo "$ifname"
            return 0
        fi
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
    PARK_NAME=$(park_name_for "$OCCUPANT_BUS")
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
exit 0
