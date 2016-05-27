FROM docker-base

## Pre-install the fundamental packages
RUN apt-get update && apt-get -y install    \
    snmp                                    \
    snmpd

COPY deps /deps

## Install Python SSWSDK (SNMP subagent dependancy)
## Note: dpkg_apt function has the benefit to detect missing .deb file
RUN dpkg_apt() { [ -f $1 ] && { dpkg -i $1 || apt-get -y install -f; } || return 1; }; dpkg_apt /deps/python-sswsdk_*.deb
## Install SNMP subagent
RUN dpkg_apt() { [ -f $1 ] && { dpkg -i $1 || apt-get -y install -f; } || return 1; }; dpkg_apt /deps/acs-snmp-subagent_*.deb

## Clean up
RUN apt-get clean -y; apt-get autoclean -y; apt-get autoremove -y
RUN rm -rf /deps

## There is a known bug: agetty processes at 100% cpu
## When:
##   1. running container in --privileged mode
##   2. container runs /sbin/init
## ref: https://github.com/docker/docker/issues/4040
## Temporary solution:
##   Disable tty services permanently
RUN systemctl --no-pager list-unit-files --type=service | grep getty | awk '{print $1}' | xargs systemctl mask
## Note: getty@.service in last grep output will not mask below cases
RUN systemctl mask getty@tty1.service

## Although exposing ports is not need for host net mode, keep it for possible bridge mode
EXPOSE 161/udp
EXPOSE 162/udp

## Specify init as CMD to enable systemd
## Note: don't provide ENTRYPOINT at the same time
CMD ["/sbin/init"]
