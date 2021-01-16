#!/bin/bash

if [ -s /usr/local/bin/done_idt_init ];then
    echo "There is a done_idt_init file"
else
    cat /etc/init.d/opennsl-modules-4.9.0-14-amd64|grep idt_init.sh
    if [ $? -ne 0 ];then
        echo "Add idt_init.sh to opennsl-modules for TD3 MAC"
        sed -i '/modprobe linux-kernel-bde/i     sleep 1' /etc/init.d/opennsl-modules-4.9.0-14-amd64
        sed -i '/sleep/i /usr/local/bin/idt_init.sh' /etc/init.d/opennsl-modules-4.9.0-14-amd64
        sed -i '/idt_init/i echo "IDT init" ' /etc/init.d/opennsl-modules-4.9.0-14-amd64
        sed -i '/IDT init/i echo 1 > /usr/local/bin/done_idt_init'  /etc/init.d/opennsl-modules-4.9.0-14-amd64
    fi

fi


