#/bin/bash

DIR=$(dirname $0)

# include files
source ${DIR}/funcs.sh

ACPI_INSTALL_PRINT=0
ACPID_INSTALL_PRINT=0
ACPI_SUPPORT_BASE_INSTALL_PRINT=0
BC_INSTALL_PRINT=0
ACPID_SOCKET_PRINT=0
ACPI_GPE01_PRINT=0
ACPI_GPE02_PRINT=0
ACPI_GPE47_PRINT=0
ACPI_STATUS=0

while [ 1 ]
do
    if [ `dpkg -l |grep -c "acpi "` -eq "0" ]; then
        dpkg -i /opt/debs/acpi_1.7-1_amd64.deb
        if [ "$?" -ne "0" ]; then
            if [ $ACPI_INSTALL_PRINT -eq 0 ]; then
                ACPI_INSTALL_PRINT=1
                log_msg "Wait for acpi package install."
            fi
            sleep 1
            continue
        else
            log_msg "Install acpi package success."
        fi
    fi
    break
done

while [ 1 ]
do
    if [ `dpkg -l |grep -c "acpid "` -eq "0" ]; then
        dpkg -i /opt/debs/acpid_2.0.23-2_amd64.deb
        if [ "$?" -ne "0" ]; then
            if [ $ACPID_INSTALL_PRINT -eq 0 ]; then
                ACPID_INSTALL_PRINT=1
                log_msg "Wait for acpid package install."
            fi
            sleep 1
            continue
        else
            log_msg "Install acpid package success."
        fi
    fi
    break
done

while [ 1 ]
do
    if [ `dpkg -l |grep -c "acpi-support-base"` -eq "0" ]; then
        dpkg -i /opt/debs/acpi-support-base_0.142-6_all.deb
        if [ "$?" -ne "0" ]; then
            if [ $ACPI_SUPPORT_BASE_INSTALL_PRINT -eq 0 ]; then
                ACPI_SUPPORT_BASE_INSTALL_PRINT=1
                log_msg "Wait for acpi-support-base package install."
            fi
            sleep 1
            continue
        else
            log_msg "Install acpi-support-base package success."
        fi
    fi
    break
done

while [ 1 ]
do
    if [ `dpkg -l |grep -c " bc "` -eq "0" ]; then
        dpkg -i /opt/debs/bc_1.06.95-9_amd64.deb
        if [ "$?" -ne "0" ]; then
            if [ $BC_INSTALL_PRINT -eq 0 ]; then
                BC_INSTALL_PRINT=1
                log_msg "Wait for bc package install."
            fi
            sleep 1
            continue
        else
            log_msg "Install bc package success."
        fi
    fi
    break
done

while [ 1 ]
do
    if [ ! -e "/sys/firmware/acpi/interrupts/gpe01" ]; then
        if [ $ACPI_GPE01_PRINT -eq 0 ]; then
            ACPI_GPE01_PRINT=1
            log_msg "Wait for acpi gpe01 ready."
        fi
        sleep 1
        continue
    fi
    log_msg "The acpi gpe01 ready."
    break
done

while [ 1 ]
do
    if [ ! -e "/sys/firmware/acpi/interrupts/gpe02" ]; then
        if [ $ACPI_GPE02_PRINT -eq 0 ]; then
            ACPI_GPE02_PRINT=1
            log_msg "Wait for acpi gpe02 ready."
        fi
        sleep 1
        continue
    fi
    log_msg "The acpi gpe02 ready."
    break
done

while [ 1 ]
do
    if [ ! -e "/sys/firmware/acpi/interrupts/gpe47" ]; then
        if [ $ACPI_GPE47_PRINT -eq 0 ]; then
            ACPI_GPE47_PRINT=1
            log_msg "Wait for acpi gpe47 ready."
        fi
        sleep 1
        continue
    fi
    log_msg "The acpi gpe47 ready."
    break
done

while [ 1 ]
do
    if [ ! -e "/var/run/acpid.socket" ]; then
        if [ $ACPID_SOCKET_PRINT -eq 0 ]; then
            ACPID_SOCKET_PRINT=1
            log_msg "Wait for acipd daemon start."
        fi
        sleep 1
        continue
    fi
    log_msg "The acpid daemon start."
    break
done

while [ 1 ]
do
    if [ `/etc/init.d/acpid status | grep -c  "active (running)"` -eq "0" ]; then
        if [ $ACPI_STATUS -eq 0 ]; then
            ACPI_STATUS=1
            log_msg "Wait for acpid running."
        fi
        sleep 1
        continue
    fi
    log_msg "The acpid running now."
    break
done

/etc/init.d/xcvr_servd start
/etc/init.d/sys_servd start
exit 0;
