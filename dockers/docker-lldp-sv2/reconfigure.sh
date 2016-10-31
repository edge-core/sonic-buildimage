#!/bin/bash

set -e

num_of_interfaces=32
if_step=4
last_if_idx=$((num_of_interfaces*if_step - if_step))

function wait_until_if_exists
{
  while /bin/true ;
  do
    if [ -L /sys/class/net/"$if" ];
    then
      break
    fi
    sleep 1
  done
  echo interface "$if" is up
}


function wait_until_if_not_exists
{
  while /bin/true ;
  do
    if [ ! -L /sys/class/net/"$if" ];
    then
      break
    fi
    sleep 1
  done
  echo interface "$if" is down
}


while /bin/true ;
do
  # wait until all interfaces are up
  echo Wait until all ifaces are up
  for i in $(seq 0 $if_step $last_if_idx)
  do
    if=Ethernet${i}
    wait_until_if_exists
  done

  echo Wait 10 seconds
  sleep 10

  # apply lldpd configuration
  echo apply lldpd configuration
  lldpcli -c /etc/lldpd.conf

  # wait until all interfaces are down
  echo Wait until all ifaces are down
  for i in $(seq 0 $if_step $last_if_idx)
  do
    if=Ethernet${i}
    wait_until_if_not_exists
  done
done
