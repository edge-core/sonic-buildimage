#!/usr/bin/env bash

function config_acl {
    if [ -f "/etc/sonic/acl.json" ]; then
        mkdir -p /etc/swss/config.d/acl
        rm -rf /etc/swss/config.d/acl/*
        translate_acl -m /etc/sonic/minigraph.xml -o /etc/swss/config.d/acl /etc/sonic/acl.json
        for filename in /etc/swss/config.d/acl/*.json; do
            [ -e "$filename" ] || break
            swssconfig $filename
        done
    fi
}

function fast_reboot {
  case "$(cat /proc/cmdline)" in
    *fast-reboot*)
      if [[ -f /fdb.json ]];
      then
        swssconfig /fdb.json
        rm -f /fdb.json
      fi

      if [[ -f /arp.json ]];
      then
        swssconfig /arp.json
        rm -f /arp.json
      fi
      ;;
    *)
      ;;
  esac
}


# Restore FDB and ARP table ASAP
fast_reboot

HWSKU=`sonic-cfggen -m /etc/sonic/minigraph.xml -v minigraph_hwsku`

SWSSCONFIG_ARGS="00-copp.config.json ipinip.json mirror.json "

# FIXME: Temporarily disable QOS/buffer configurations for further debugging
# if [ "$HWSKU" == "Force10-S6000" ]; then
#     SWSSCONFIG_ARGS+="td2.32ports.buffers.json td2.32ports.qos.json "
# elif [ "$HWSKU" == "Force10-S6000-Q32" ]; then
#     SWSSCONFIG_ARGS+="td2.32ports.buffers.json td2.32ports.qos.json "
# elif [ "$HWSKU" == "Arista-7050-QX32" ]; then
#     SWSSCONFIG_ARGS+="td2.32ports.buffers.json td2.32ports.qos.json "
# elif [ "$HWSKU" == "ACS-MSN2700" ]; then
#     SWSSCONFIG_ARGS+="msn2700.32ports.buffers.json msn2700.32ports.qos.json "
# elif [ "$HWSKU" == "ACS-MSN2740" ]; then
#     SWSSCONFIG_ARGS+="msn2740.32ports.buffers.json msn2740.32ports.qos.json "
# fi

for file in $SWSSCONFIG_ARGS; do
    swssconfig /etc/swss/config.d/$file
    sleep 1
done

config_acl
