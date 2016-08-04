FROM docker-base

COPY deps/*py2*.whl deps/lldpsyncd_*.deb deps/lldpd_*.deb /deps/

## Pre-install the fundamental packages
## Install Python SSWSDK (lldpsyncd dependancy)
## Install LLDP Sync Daemon
## Note: dpkg_apt function has the benefit to detect missing .deb file
## Clean up
RUN dpkg_apt() { [ -f $1 ] && { dpkg -i $1 || apt-get -y install -f; } || return 1; } &&        \
    dpkg_apt /deps/lldpd_*.deb &&                                                       \
    dpkg_apt /deps/lldpsyncd_*.deb &&                                                           \
    apt-get install -y python-pip && \
    pip install /deps/*.whl && \
    apt-get remove -y python-pip && \
    apt-get clean -y && apt-get autoclean -y && apt-get autoremove -y &&                        \
    rm -rf /deps

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

## Specify init as CMD to enable systemd
## Note: don't provide ENTRYPOINT at the same time
CMD ["/sbin/init"]
