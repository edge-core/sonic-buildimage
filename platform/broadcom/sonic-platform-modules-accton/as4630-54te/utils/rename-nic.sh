#!/bin/bash

ETH0_INFO=$( cat /etc/udev/rules.d/70-persistent-net.rules |grep systemd |awk '{print $(NF-2)}'  |cut -d '"' -f2  )

if [ -e "/sys/class/net/eth0" ]; then
    sleep 1
    BUS_INFO=$(ethtool -i eth0 |grep bus-info |awk '{print $(NF)}')
    #eth0 already is 0000:08:00.0
    if [[ ${ETH0_INFO} == ${BUS_INFO} ]];
    then
        echo "[rename-nic] eth0 done"
        exit 0
    else
        echo "[rename-nic] eth0 not 8:00.0"
    fi
fi

if [ -e "/sys/class/net/eth3" ]; then
     ip link set eth2 name eth0
     echo "[rename-nic] set eth2 to eth0 $?"
     sleep 2
fi

#Make sure everything is OK
ETH0_INFO=$( cat /etc/udev/rules.d/70-persistent-net.rules |grep systemd |awk '{print $(NF-2)}' |cut -d '"' -f2 )
BUS_INFO=$(ethtool -i eth0 |grep bus-info |awk '{print $(NF)}')

if [[ ${ETH0_INFO} == ${BUS_INFO} ]];
then
        echo "[rename-nic] Double Check  OK"
        exit 0
else
        # Re-install the igb and ixgbe again to make the NIC sequence follow the udev rule
        modprobe -r igb
        modprobe -r ixgbe
        modprobe igb
        modprobe ixgbe
        echo "[rename-nic] Double Check failed reload ko"
        exit 1
fi


