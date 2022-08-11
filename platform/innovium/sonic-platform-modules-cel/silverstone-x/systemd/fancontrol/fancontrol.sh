#! /bin/bash

### BEGIN INIT INFO
# Provides:          fancontrol
# Required-Start:    $remote_fs
# Required-Stop:     $remote_fs
# Default-Start:     2 3 4 5
# Default-Stop:
# Short-Description: fancontrol
# Description:       fancontrol configuration selector
### END INIT INFO

. /lib/lsb/init-functions

[ -f /etc/default/rcS ] && . /etc/default/rcS
PATH=/bin:/usr/bin:/sbin:/usr/sbin:/usr/local/bin
DAEMON=/usr/local/bin/fancontrol
DESC="fan speed regulator"
NAME="fancontrol"
PIDFILE=/var/run/fancontrol.pid
MAIN_CONF=/usr/share/sonic/device/x86_64-cel_silverstone-x-r0/fancontrol
DEVPATH=/sys/bus/i2c/drivers/platform_fan/9-000d

# Baseboard CPLD file
BASECPLD_SETREG_FILE="/sys/devices/platform/sys_cpld/setreg"
# Fan LED control register in baseboard CPLD
FANCR_REG="0xA165"
# FAN LED off value in baseboard CPLD
FAN_LED_OFF="3"
FAN_LED_HW_CTRL="0x10"

# COMe power button control register in baseboard CPLD
COMe_PWRCR_REG="0xA124"
# COMe power off value in baseboard CPLD
COMe_PWRCR_OFF="0"

test -x $DAEMON || exit 0

if [[ -e "/dev/ipmi0" || -e "/dev/ipmi/0" || -e "/dev/ipmidev/0" ]]; then
    # if BMC exists, fan control strategy is owned by BMC and no need to implement here.
    exit 0
fi 

init() {
    FANFAULT=$(cat ${DEVPATH}/fan1_fault)
    [ "$FANFAULT"x = "1"x ] && DIRECTION=$(cat ${DEVPATH}/fan1_direction)
    FANDIR=$([ "$DIRECTION"x = "1"x ] && echo "F2B" || echo "B2F")
    CONF=${MAIN_CONF}-${FANDIR}
}

# if all fans are absent, power off
ChkFanStatus() {
    local fan_absent=0 fancnt=0
    
    while true; do
        fancnt=$(ls $DEVPATH/fan*_present | wc -l)
        fan_absent=$(cat $DEVPATH/fan*_present | grep "1" | wc -l)
        if [ $fan_absent -eq $fancnt ]; then
            echo $FANCR_REG $FAN_LED_OFF > $BASECPLD_SETREG_FILE
            PSU_STA=$(cat $BASECPLD_GETREG_FILE)
            echo "Critical errors, all fans are absent, shutdown now!!!"
            # poweroff
            echo $COMe_PWRCR_REG $COMe_PWRCR_OFF > $BASECPLD_SETREG_FILE
        fi
        sleep 1;
    done
}


install() {
    find /var/lib/docker/overlay*/ -path */sbin/fancontrol -exec cp /usr/local/bin/fancontrol {} \;
}

case "$1" in
start)
    init
    cp $CONF $MAIN_CONF
    # if all fans are absent, power off
    echo $FANCR_REG $FAN_LED_HW_CTRL > $BASECPLD_SETREG_FILE
    ChkFanStatus & 
    # delay for all drivers node come into effect
    sleep 30
    /usr/share/sonic/device/x86_64-cel_silverstone-x-r0/plugins/alarm_led_control.py & 
    ;;
install)
    install
    ;;
*)
    log_success_msg "Usage: /etc/init.d/fancontrol {start} | {install}"
    exit 1
    ;;
esac

exit 0
