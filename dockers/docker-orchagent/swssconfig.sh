#!/usr/bin/env bash

set -e

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

HWSKU=`sonic-cfggen -d -v "DEVICE_METADATA['localhost']['hwsku']"`

SWSSCONFIG_ARGS="00-copp.config.json "

if [ "$HWSKU" != "montara" ] && [ "$HWSKU" != "mavericks" ] && [ "$HWSKU" != "OSW1800-48x6q" ] && [ "$HWSKU" != "INGRASYS-S9180-32X"]; then
    SWSSCONFIG_ARGS+="ipinip.json "
fi

SWSSCONFIG_ARGS+="ports.json switch.json "

if [ "$HWSKU" == "Force10-S6000" ]; then
    SWSSCONFIG_ARGS+="td2.32ports.buffers.json td2.32ports.qos.json "
elif [ "$HWSKU" == "Force10-S6000-Q32" ]; then
    SWSSCONFIG_ARGS+="td2.32ports.buffers.json td2.32ports.qos.json "
elif [ "$HWSKU" == "Force10-S6100" ]; then
    SWSSCONFIG_ARGS+="th.64ports.buffers.json th.64ports.qos.json "
elif [ "$HWSKU" == "Arista-7050-QX32" ]; then
    SWSSCONFIG_ARGS+="td2.32ports.buffers.json td2.32ports.qos.json "
elif [[ "$HWSKU" == "ACS-MSN27"* ]]; then
    sonic-cfggen -d -t /usr/share/sonic/templates/msn27xx.32ports.buffers.json.j2 > /etc/swss/config.d/msn27xx.32ports.buffers.json
    SWSSCONFIG_ARGS+="msn27xx.32ports.buffers.json "
fi

for file in $SWSSCONFIG_ARGS; do
    swssconfig /etc/swss/config.d/$file
    sleep 1
done
