#!/bin/bash

#platform init script for Dell S6100

install_python_api_package() {
    device="/usr/share/sonic/device"
    platform=$(/usr/local/bin/sonic-cfggen -H -v DEVICE_METADATA.localhost.platform)

    rv=$(pip install $device/$platform/sonic_platform-1.0-py2-none-any.whl)
}

remove_python_api_package() {
    rv=$(pip show sonic-platform > /dev/null 2>/dev/null)
    if [ $? -eq 0 ]; then
        rv=$(pip uninstall -y sonic-platform > /dev/null 2>/dev/null)
    fi
}


if [[ "$1" == "init" ]]; then

    pericom="/sys/bus/pci/devices/0000:08:00.0"
    modprobe i2c-dev
    modprobe i2c-mux-pca954x force_deselect_on_exit=1
    modprobe dell_ich
    modprobe dell_s6100_iom_cpld
    modprobe dell_s6100_lpc
    modprobe nvram
    systemctl start s6100-reboot-cause.service

    # Disable pericom/xilinx
    echo 1 > /sys/bus/pci/devices/0000:02:00.0/remove
    [ -d $pericom ] &&  echo 1 > $pericom/remove

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
    modprobe -r nvram
    remove_python_api_package
else
     echo "s6100_platform : Invalid option !"
fi
