#!/bin/bash

#platform init script for Dell S6100

track_reboot_reason() {
    if [[ -d /sys/devices/platform/SMF.512/hwmon/ ]]; then
        rv=$(cd /sys/devices/platform/SMF.512/hwmon/*; cat mb_poweron_reason)
        reason=$(echo $rv | cut -d 'x' -f2)
        if [ $reason == "ff" ]; then
            cd /sys/devices/platform/SMF.512/hwmon/*
            if [[ -e /tmp/notify_firstboot_to_platform ]]; then
                echo 0x01 > mb_poweron_reason
            else
                echo 0xbb > mb_poweron_reason
            fi
        elif [ $reason == "bb" ] || [ $reason == "1" ]; then
            cd /sys/devices/platform/SMF.512/hwmon/*
            echo 0xaa > mb_poweron_reason
        fi
    fi
}

install_python_api_package() {
    device="/usr/share/sonic/device"
    platform=$(/usr/local/bin/sonic-cfggen -H -v DEVICE_METADATA.localhost.platform)

    rv=$(pip install $device/$platform/sonic_platform-1.0-py2-none-any.whl)
}

remove_python_api_package() {
    rv=$(pip show sonic-platform > /dev/null 2>/dev/null)
    if [ $? -eq 0 ]; then
        rv = $(pip uninstall -y sonic-platform > /dev/null 2>/dev/null)
    fi
}

if [[ "$1" == "init" ]]; then
    modprobe i2c-dev
    modprobe i2c-mux-pca954x force_deselect_on_exit=1
    modprobe dell_ich
    modprobe dell_s6100_iom_cpld
    modprobe dell_s6100_lpc
    track_reboot_reason

    # Disable Watchdog Timer
    if [[ -e /usr/local/bin/platform_watchdog_disable.sh ]]; then
        /usr/local/bin/platform_watchdog_disable.sh
    fi

    is_fast_warm=$(cat /proc/cmdline | grep SONIC_BOOT_TYPE | wc -l)

    if [[ "$is_fast_warm" == "1" ]]; then
        systemctl start --no-block s6100-i2c-enumerate.service
    else
        systemctl start s6100-i2c-enumerate.service
    fi

    install_python_api_package

elif [[ "$1" == "deinit" ]]; then
    /usr/local/bin/s6100_i2c_enumeration.sh deinit

    modprobe -r dell_s6100_lpc
    modprobe -r dell_s6100_iom_cpld
    modprobe -r i2c-mux-pca954x
    modprobe -r i2c-dev
    modprobe -r dell_ich
    remove_python_api_package
else
     echo "s6100_platform : Invalid option !"
fi
