#!/bin/bash

fw_uboot_env_cfg()
{
    echo "Setting up U-Boot environment..."
    FW_ENV_DEFAULT='/dev/mtd0 0x00500000 0x80000 0x100000 8'
    UBOOT_FW_DFAULT=1

    DTB_HAS_ENV_BLK=$(grep uboot-env /proc/mtd | sed -e 's/:.*$//')
    if [ -c "/dev/$DTB_HAS_ENV_BLK" ]; then
        PROC_ENV_FILE=$(find /proc/device-tree/ -name env_size)
        if [ -n "$PROC_ENV_FILE" ]
        then
            UBOOT_ENV_SIZ="0x$(hd $PROC_ENV_FILE | awk 'FNR==1 {print $2 $3 $4 $5}')"
            UBOOT_ENV_ERASE_SIZ="0x$(grep uboot-env /proc/mtd | awk '{print $3}')"
            if [[ -n "$UBOOT_ENV_SIZ" && -n "$UBOOT_ENV_ERASE_SIZ" ]]
            then
                # Env info from DTB 
                FW_ENV_DTB="/dev/$DTB_HAS_ENV_BLK 0x00000000 $UBOOT_ENV_SIZ $UBOOT_ENV_ERASE_SIZ"
            fi
        fi
    fi
    if [ -n "$FW_ENV_DTB" ]
    then
                echo $FW_ENV_DTB > /etc/fw_env.config
                echo "Found uboot env offset in device tree"
                UBOOT_ENV_CRC=$(fw_printenv -c /etc/fw_env.config 2>&1 | grep -c 'Warning: Bad CRC')
                if [ $UBOOT_ENV_CRC -eq 0 ]
                then
                    echo "Uboot env offset in device tree is valid"
                    UBOOT_FW_DFAULT=0
                else
                    echo "Uboot env offset in device tree is NOT valid"
                    UBOOT_FW_DFAULT=1
                fi
    fi
    if [ $UBOOT_FW_DFAULT -eq 1 ]
    then
        echo $FW_ENV_DEFAULT > /etc/fw_env.config
        echo "Using pre-configured uboot env"
    fi
}

et6448m_profile()
{
    MAC_ADDR=$(fw_printenv -n ethaddr)
    sed -i "s/switchMacAddress=.*/switchMacAddress=$MAC_ADDR/g" /usr/share/sonic/device/armhf-marvell_et6448m_52x-r0/et6448m/profile.ini
    echo "ET6448M: Updating switch mac address ${MAC_ADDR}"
}

main()
{
    fw_uboot_env_cfg
    et6448m_profile
}

main $@
