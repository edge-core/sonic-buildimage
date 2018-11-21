#!/bin/bash

SWNAME=$1

pid=$(docker inspect --format '{{.State.Pid}}' $SWNAME)

echo Seting up servers

SERVERS=31

for srv in `seq 0 $SERVERS`; do

    SRV="$SWNAME-srv$srv"

    NSS="ip netns exec $SRV"

    ip netns add $SRV

    $NSS ip addr add 127.0.0.1/8 dev lo
    $NSS ip addr add ::1/128 dev lo
    $NSS ip link set dev lo up

    # add virtual link between neighbor and the virtual switch docker

    IF="eth$((srv+1))"

    ip link add ${SRV}eth0 type veth peer name $IF
    ip link set ${SRV}eth0 netns $SRV
    ip link set $IF netns ${pid}

    echo "Bring ${SRV}eth0 up"
    $NSS ip link set dev ${SRV}eth0 name eth0
    $NSS ip link set dev eth0 up

    echo "Bring $IF up in the virtual switch docker"
    nsenter -t $pid -n ip link set dev $IF up

done
