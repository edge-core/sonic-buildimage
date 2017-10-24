#!/bin/bash

set -e

# TODO: Listen to state database when it is ready
interfaces=$(sonic-cfggen -d -v "PORT.keys() | join(' ')")

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
  echo Wait until all interfaces are created
  for i in $interfaces
  do
    wait_until_if_exists $i
  done

  echo Wait 10 seconds while lldpd finds new interfaces
  sleep 10

  # apply lldpd configuration
  echo Apply lldpd configuration
  lldpcli -c /etc/lldpd.conf

  # wait until all interfaces are destroyed
  echo Wait until all ifaces are destroyed
  for i in $interfaces
  do
    wait_until_if_not_exists $i
  done
done
