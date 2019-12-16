#! /bin/sh

### BEGIN INIT INFO
# Provides:          fancontrol
# Required-Start:    $remote_fs
# Required-Stop:     $remote_fs
# Default-Start:     2 3 4 5
# Default-Stop:
# Short-Description: fancontrol
# Description:       fan speed regulator
### END INIT INFO

. /lib/lsb/init-functions

[ -f /etc/default/rcS ] && . /etc/default/rcS
PATH=/bin:/usr/bin:/sbin:/usr/sbin:/usr/local/bin
DAEMON=/usr/local/bin/fancontrol
DESC="fan speed regulator"
NAME="fancontrol"
PIDFILE=/var/run/fancontrol.pid
MAIN_CONF=/usr/share/sonic/device/x86_64-cel_seastone-r0/fancontrol
DEVPATH=/sys/devices/pci0000:00/0000:00:13.0/i2c-*/i2c-13/13-002e
GPIO_DIR=/sys/class/gpio
BASE_GPIO=$(find $GPIO_DIR | grep gpiochip | grep -o '[[:digit:]]*')
DIRGPIO_START=15

test -x $DAEMON || exit 0

for i in 1 2 3 4 5
do
	FANFAULT=$(cat ${DEVPATH}/fan${i}_fault)
        [ $FANFAULT = 1 ] && continue
	FANDIR_GPIO_NUMBER=$((DIRGPIO_START + BASE_GPIO))
	FANDIR_VALUE=$(cat ${GPIO_DIR}/gpio${FANDIR_GPIO_NUMBER}/value)
	DIRGPIO_START=$((DIRGPIO_START+1))
	FANDIR=$([ $FANDIR_VALUE = 1 ] && echo "B2F" || echo "F2B")
done
CONF=${MAIN_CONF}-${FANDIR}

case "$1" in
  start)
  	if [ -f $CONF ] ; then
		if $DAEMON --check $CONF 1>/dev/null 2>/dev/null ; then
			log_daemon_msg "Starting $DESC" "$NAME\n"
			start-stop-daemon --start --quiet --pidfile $PIDFILE --startas $DAEMON $CONF
			log_end_msg $?
		else
			log_failure_msg "Not starting fancontrol, broken configuration file; please re-run pwmconfig."
		fi
	else
		if [ "$VERBOSE" != no ]; then
			log_warning_msg "Not starting fancontrol; run pwmconfig first."
		fi
	fi
	;;
  stop)
		log_daemon_msg "Stopping $DESC" "$NAME"
		start-stop-daemon --stop --quiet --pidfile $PIDFILE --oknodo --startas $DAEMON $CONF
		rm -f $PIDFILE
		log_end_msg $?
	;;
  restart)
  	$0 stop
		sleep 3
		$0 start
	;;
  force-reload)
	if start-stop-daemon --stop --test --quiet --pidfile $PIDFILE --startas $DAEMON $CONF ; then
		$0 restart
	fi
	;;
  status)
		status_of_proc $DAEMON $NAME $CONF && exit 0 || exit $?
	;;
  *)
	log_success_msg "Usage: /etc/init.d/fancontrol {start|stop|restart|force-reload|status}"
	exit 1
	;;
esac

exit 0
