#!/bin/bash

#platform init script for Dell Z9100

source dell_i2c_utils.sh

init_devnum() {
    found=0
    for devnum in 0 1; do
        devname=`cat /sys/bus/i2c/devices/i2c-${devnum}/name`
        # iSMT adapter can be at either dffd0000 or dfff0000
        if [[ $devname == 'SMBus iSMT adapter at '* ]]; then
            found=1
            break
        fi
    done

    [[ $found -eq 0 ]] && echo "cannot find iSMT" && exit 1
}

# Attach/Detach CPU board mux @ 0x70
cpu_board_mux() {
    case $1 in
        "new_device")    i2c_config "echo pca9547 0x70 > /sys/bus/i2c/devices/i2c-${devnum}/$1"
                         ;;
        "delete_device") i2c_config "echo 0x70 > /sys/bus/i2c/devices/i2c-${devnum}/$1"
                         ;;
        *)               echo "z9100_platform: cpu_board_mux: invalid command !"
                         ;;
    esac
}

# Attach/Detach switch board MUX to IOM CPLDs @ 0x71
switch_board_mux() {
    case $1 in
        "new_device")    i2c_config "echo pca9548 0x71 > /sys/bus/i2c/devices/i2c-4/$1"
                         ;;
        "delete_device") i2c_config "echo 0x71 > /sys/bus/i2c/devices/i2c-4/$1"
                         ;;
        *)               echo "z9100_platform: switch_board_mux : invalid command !"
                         ;;
    esac
}

# Attach/Detach syseeprom on CPU board
sys_eeprom() {
    case $1 in
        "new_device")    i2c_config "echo 24c02 0x50 > /sys/bus/i2c/devices/i2c-2/$1"
                         ;;
        "delete_device") i2c_config "echo 0x50 > /sys/bus/i2c/devices/i2c-2/$1"
                         ;;
        *)               echo "z9100_platform: sys_eeprom : invalid command !"
                         ;;
    esac
}

#Attach/Detach cpld devices to drivers for each iom
switch_board_cpld() {
    case $1 in
        "new_device")    
                      for ((i=14;i<=17;i++));
                      do
                          i2c_config "echo  dell_z9100_iom_cpld 0x3e > /sys/bus/i2c/devices/i2c-$i/$1"
                      done
                      ;;
        "delete_device")
                      for ((i=14;i<=17;i++));
                      do
                          i2c_config "echo  0x3e > /sys/bus/i2c/devices/i2c-$i/$1"
                      done
                      ;;
        *)            echo "z9100_platform: switch_board_cpld : invalid command !"
                      ;;
    esac
}

#Attach/Detach the MUX connecting all QSFPs
switch_board_qsfp_mux() {
    case $1 in
        "new_device")
                      for ((i=9;i>=6;i--));
                      do
                          # 0x71 mux on the IOM 1
                          mux_index=$(expr $i - 5)
                          echo "Attaching PCA9548 $mux_index"
                          i2c_config "echo pca9548 0x71 > /sys/bus/i2c/devices/i2c-$i/$1"
                      done
                      ;;
        "delete_device")
                      for ((i=9;i>=6;i--));
                      do
                          # 0x71 mux on the IOM 1
                          mux_index=$(expr $i - 5)
                          echo "Detaching PCA9548 $mux_index"
                          i2c_config "echo 0x71 > /sys/bus/i2c/devices/i2c-$devnum/i2c-$i/$1"
                      done
                      ;;
        *)            echo "z9100_platform: switch_board_qsfp_mux: invalid command !"
                      ;;
    esac
}

#Attach/Detach the SFP modules on PCA9548_2
switch_board_sfp() {
    case $1 in
        "new_device")    i2c_config "echo sff8436 0x50 > /sys/bus/i2c/devices/i2c-11/$1"
                         i2c_config "echo sff8436 0x50 > /sys/bus/i2c/devices/i2c-12/$1"
                         ;;
        "delete_device") i2c_config "echo 0x50 > /sys/bus/i2c/devices/i2c-11/$1"
                         i2c_config "echo 0x50 > /sys/bus/i2c/devices/i2c-12/$1"
                         ;;
        *)               echo "z9100_platform: switch_board_sfp: invalid command !"
                         ;;
    esac
}

# Attach/Detach 32 instances of EEPROM driver QSFP ports on IO module 1
#eeprom can dump data using below command
switch_board_qsfp() {
    case $1 in
        "new_device")
                        for ((i=18;i<=49;i++));
                        do
                            i2c_config "echo sff8436 0x50 > /sys/bus/i2c/devices/i2c-$i/$1"
                        done
                        ;;
        "delete_device")
                        for ((i=18;i<=49;i++));
                        do
                            i2c_config "echo 0x50 > /sys/bus/i2c/devices/i2c-$i/$1"
                        done
                        ;;

        *)              echo "z9100_platform: switch_board_qsfp: invalid command !"
                        ;;
    esac
}

init_devnum

if [[ "$1" == "init" ]]; then
    depmod -a
    modprobe i2c-dev
    modprobe i2c-mux-pca954x force_deselect_on_exit=1
    modprobe dell_mailbox
    modprobe dell_z9100_cpld

    cpu_board_mux "new_device"
    switch_board_mux "new_device"
    sys_eeprom "new_device"
    switch_board_cpld "new_device"
    switch_board_qsfp_mux "new_device"
    switch_board_sfp "new_device"
    switch_board_qsfp "new_device"
elif [[ "$1" == "deinit" ]]; then
    switch_board_sfp "delete_device"
    switch_board_cpld "delete_device"
    switch_board_mux "delete_device"
    sys_eeprom "delete_device"
    switch_board_qsfp "delete_device"
    switch_board_qsfp_mux "delete_device"
    cpu_board_mux "delete_device"

    modprobe -r dell_z9100_cpld
    modprobe -r dell_mailbox
    modprobe -r i2c-mux-pca954x
    modprobe -r i2c-dev
else
     echo "z9100_platform : Invalid option !"
fi
