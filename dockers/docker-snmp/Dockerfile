FROM docker-base

COPY deps/snmp_*.deb deps/snmpd_*.deb deps/libsnmp-base_*.deb deps/libsnmp30_*.deb /deps/
COPY deps/python3/*.whl /python3/

# enable -O for all Python calls
ENV PYTHONOPTIMIZE 1

## Pre-install the fundamental packages
## Install Python SSWSDK (SNMP subagent dependancy)
## Install SNMP subagent
## Note: dpkg_apt function has the benefit to detect missing .deb file
## Clean up
RUN dpkg_apt() { [ -f $1 ] && { dpkg -i $1 || apt-get -y install -f; } || return 1; } &&        \
    dpkg_apt /deps/libsnmp-base_*.deb &&                                                        \
    dpkg_apt /deps/libsnmp30_*.deb &&                                                           \
    dpkg_apt /deps/snmp_*.deb &&                                                                \
	dpkg_apt /deps/snmpd_*.deb &&                                                               \
    rm -rf /deps 

# install subagent
RUN apt-get -y install build-essential wget libssl-dev openssl && \
    rm -rf /var/lib/apt/lists/* && \
    wget https://www.python.org/ftp/python/3.5.2/Python-3.5.2.tgz && \
    tar xvf Python-3.5.2.tgz && cd Python-3.5.2 && \
    ./configure --without-doc-strings --prefix=/usr --without-pymalloc --enable-shared && \
    make && make install && \
    ldconfig && \
    cd .. && rm -rf Python-3.5.2 && rm Python-3.5.2.tgz && \
    pip3 install --no-cache-dir /python3/*py3*.whl hiredis && \
    rm -rf /python3 && \
    python3 -m pip uninstall -y pip setuptools && \
    rm -rf /usr/lib/python3.5/unittest && \
    rm -rf /usr/lib/python3.5/lib2to3 && \
    rm -rf /usr/lib/python3.5/tkinter && \
    rm -rf /usr/lib/python3.5/idlelib && \
    rm -rf /usr/lib/python3.5/email && \
    rm -rf /usr/lib/python3.5/test && \
    apt-get -y remove build-essential wget libssl-dev openssl && \
    apt-get clean -y && apt-get autoclean -y && apt-get autoremove -y && \
    python3 -m acs_ax_impl install && \
    find / | grep -E "__pycache__" | xargs rm -rf && \
    rm -rf ~/.cache && \
    systemctl enable acs-snmp-subagent.service

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
EXPOSE 161/udp 162/udp

## Specify init as CMD to enable systemd
## Note: don't provide ENTRYPOINT at the same time
CMD ["/sbin/init"]
