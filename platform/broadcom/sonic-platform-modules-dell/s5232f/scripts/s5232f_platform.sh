#!/bin/bash

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

    [ $found -eq 0 ] && echo "cannot find iSMT" && exit 1
}

# Attach/Detach syseeprom on CPU board
sys_eeprom() {
    case $1 in
        "new_device")    echo 24c16 0x50 > /sys/bus/i2c/devices/i2c-0/$1
                         ;;
        "delete_device") echo 0x50 > /sys/bus/i2c/devices/i2c-0/$1
                         ;;
        *)               echo "s5232f_platform: sys_eeprom : invalid command !"
                         ;;
    esac
}

#Attach/Detach the MUX connecting all QSFPs
switch_board_qsfp_mux() {
    case $1 in
        "new_device")
                      for ((i=603;i<=607;i++));
                      do
                          echo "Attaching PCA9548 @ 0x74"
                          echo pca9548 0x74 > /sys/bus/i2c/devices/i2c-$i/$1
                      done

                      ;;
        "delete_device")
                      for ((i=603;i<=607;i++));
                      do
                          echo "Detaching PCA9548 @ 0x74"
                          echo 0x74 > /sys/bus/i2c/devices/i2c-$i/$1
                      done

                      ;;
        *)            echo "s5232f_platform: switch_board_qsfp_mux: invalid command !"
                      ;;
    esac
    sleep 2
}

#Attach/Detach 32 instances of EEPROM driver QSFP ports
#eeprom can dump data using below command
switch_board_qsfp() {
        case $1 in
        "new_device")
                        for ((i=2;i<=33;i++));
                        do
                            echo optoe1 0x50 > /sys/bus/i2c/devices/i2c-$i/$1
                        done
                        ;;
 
        "delete_device")
                        for ((i=2;i<=33;i++));
                        do
                            echo 0x50 > /sys/bus/i2c/devices/i2c-$i/$1
                        done
                        ;;

        *)              echo "s5232f_platform: switch_board_qsfp: invalid command !"
                        ;;
    esac
}

#Attach 2 instances of EEPROM driver SFP ports
switch_board_sfp() {
        case $1 in
        "new_device")
                        for ((i=34;i<=35;i++));
                        do
                            echo optoe2 0x50 > /sys/bus/i2c/devices/i2c-$i/$1
                        done
                        ;;

        "delete_device")
                        for ((i=34;i<=35;i++));
                        do
                            echo 0x50 > /sys/bus/i2c/devices/i2c-$i/$1
                        done
                        ;;

        *)              echo "s5232f_platform: switch_board_qsfp: invalid command !"
                        ;;
    esac
}

#Modsel 64 ports to applicable QSFP type modules
#This enables the adapter to respond for i2c commands
switch_board_modsel() {
	resource="/sys/bus/pci/devices/0000:04:00.0/resource0"
	for ((i=1;i<=64;i++));
	do
		port_addr=$(( 16384 + ((i - 1) * 16)))
		hex=$( printf "0x%x" $port_addr )
		python /usr/bin/pcisysfs.py --set --offset $hex --val 0x10 --res $resource  > /dev/null 2>&1
	done
}

#This enables the led control for CPU and default states 
switch_board_led_default() {
	resource="/sys/bus/pci/devices/0000:04:00.0/resource0"
	python /usr/bin/pcisysfs.py --set --offset 0x24 --val 0x194 --res $resource  > /dev/null 2>&1
}
init_devnum

if [ "$1" == "init" ]; then
    modprobe i2c-dev
    modprobe i2c-mux-pca954x force_deselect_on_exit=1
    modprobe ipmi_devintf
    modprobe ipmi_si
    modprobe i2c_ocores
    modprobe dell_s5232f_fpga_ocores
    sys_eeprom "new_device"
    switch_board_qsfp_mux "new_device"
    switch_board_qsfp "new_device"
    switch_board_sfp "new_device"
    switch_board_modsel
    switch_board_led_default
    python /usr/bin/qsfp_irq_enable.py

elif [ "$1" == "deinit" ]; then
    sys_eeprom "delete_device"
    switch_board_qsfp "delete_device"
    switch_board_qsfp_mux "delete_device"
    switch_board_sfp "delete_device"
    modprobe -r i2c-mux-pca954x
    modprobe -r i2c-dev
else
     echo "s5232f_platform : Invalid option !"
fi

