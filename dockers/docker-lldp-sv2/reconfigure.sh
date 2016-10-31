#!/bin/bash

set -e

num_of_interfaces=32
if_step=4
last_if_idx=$((num_of_interfaces*if_step - if_step))

function wait_until_if_exists
{
  if=$1
  while [ ! -L /sys/class/net/"$if" ] ;
  do
    sleep 1
  done
  echo interface "$if" is created
}


function wait_until_if_not_exists
{
  if=$1
  while [ -L /sys/class/net/"$if" ] ;
  do
    sleep 1
  done
  echo interface "$if" is destroyed
}


while /bin/true ;
do
  # wait until all interfaces are created
  echo Wait until all ifaces are created
  for i in $(seq 0 $if_step $last_if_idx)
  do
    wait_until_if_exists "Ethernet$i"
  done

  echo Wait 10 seconds while lldpd finds new interfaces
  sleep 10

  # apply lldpd configuration
  echo apply lldpd configuration
  lldpcli -c /etc/lldpd.conf

  # wait until all interfaces are destroyed
  echo Wait until all ifaces are destroyed
  for i in $(seq 0 $if_step $last_if_idx)
  do
    wait_until_if_not_exists "Ethernet$i"
  done
done
