#!/usr/bin/env bash

mkdir -p /etc/frr
mkdir -p /etc/supervisor/conf.d

CFGGEN_PARAMS=" \
    -d \
    -y /etc/sonic/constants.yml \
    -t /usr/share/sonic/templates/supervisord/frr_vars.j2 \
    -t /usr/share/sonic/templates/supervisord/supervisord.conf.j2,/etc/supervisor/conf.d/supervisord.conf \
    -t /usr/share/sonic/templates/bgpd/bgpd.conf.j2,/etc/frr/bgpd.conf \
    -t /usr/share/sonic/templates/zebra/zebra.conf.j2,/etc/frr/zebra.conf \
    -t /usr/share/sonic/templates/staticd/staticd.conf.j2,/etc/frr/staticd.conf \
    -t /usr/share/sonic/templates/frr.conf.j2,/etc/frr/frr.conf \
    -t /usr/share/sonic/templates/isolate.j2,/usr/sbin/bgp-isolate \
    -t /usr/share/sonic/templates/unisolate.j2,/usr/sbin/bgp-unisolate \
"
CONFIG_TYPE=$(sonic-cfggen $CFGGEN_PARAMS)

if [[ ! -z "$NAMESPACE_ID" ]]; then
   # FRR is not running in host namespace so we need to delete
   # default gw kernel route added by docker network via eth0 and add it back
   # with higher administrative distance so that default route learnt
   # by FRR becomes best route if/when available
   GATEWAY_IP=$(ip route show 0.0.0.0/0 dev eth0 | awk '{print $3}')
   #Check if docker default route is there
   if [[ ! -z "$GATEWAY_IP" ]]; then
      ip route del 0.0.0.0/0 dev eth0
      #Make sure route is deleted
      CHECK_GATEWAY_IP=$(ip route show 0.0.0.0/0 dev eth0 | awk '{print $3}')
      if [[ -z "$CHECK_GATEWAY_IP" ]]; then
         # Ref: http://docs.frrouting.org/en/latest/zebra.html#zebra-vrf
         # Zebra does treat Kernel routes as special case for the purposes of Admin Distance. \
         # Upon learning about a route that is not originated by FRR we read the metric value as a uint32_t.
         # The top byte of the value is interpreted as the Administrative Distance and
         # the low three bytes are read in as the metric.
         # so here we are programming administrative distance of 210 (210 << 24) > 200 (for routes learnt via IBGP)
         ip route add 0.0.0.0/0 via $GATEWAY_IP dev eth0 metric 3523215360
      fi
   fi
fi

if [ -z "$CONFIG_TYPE" ] || [ "$CONFIG_TYPE" == "separated" ]; then
    echo "no service integrated-vtysh-config" > /etc/frr/vtysh.conf
    rm -f /etc/frr/frr.conf
elif [ "$CONFIG_TYPE" == "unified" ]; then
    echo "service integrated-vtysh-config" > /etc/frr/vtysh.conf
    rm -f /etc/frr/bgpd.conf /etc/frr/zebra.conf /etc/frr/staticd.conf
fi

chown -R frr:frr /etc/frr/

chown root:root /usr/sbin/bgp-isolate
chmod 0755 /usr/sbin/bgp-isolate

chown root:root /usr/sbin/bgp-unisolate
chmod 0755 /usr/sbin/bgp-unisolate

mkdir -p /var/sonic
echo "# Config files managed by sonic-config-engine" > /var/sonic/config_status

exec /usr/bin/supervisord
