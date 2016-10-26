FROM docker-base

COPY deps/snmp_*.deb deps/snmpd_*.deb deps/libsnmp-base_*.deb deps/libsnmp30_*.deb /deps/
COPY deps/python3/*.whl /python3/

# enable -O for all Python calls
ENV PYTHONOPTIMIZE 1

## Pre-install the fundamental packages
## Install Python SSWSDK (SNMP subagent dependency)
## Install SNMP subagent
## Note: dpkg_apt function has the benefit to detect missing .deb file
## Clean up
RUN apt-get update && \
    dpkg_apt() { [ -f $1 ] && { dpkg -i $1 || apt-get -y install -f; } || return 1; } &&        \
    dpkg_apt /deps/libsnmp-base_*.deb &&                                                        \
    dpkg_apt /deps/libsnmp30_*.deb &&                                                           \
    dpkg_apt /deps/snmp_*.deb &&                                                                \
    dpkg_apt /deps/snmpd_*.deb &&                                                               \
    rm -rf /deps 

# install subagent
RUN apt-get -y install build-essential wget libssl-dev openssl supervisor && \
    rm -rf /var/lib/apt/lists/* && \
    wget https://www.python.org/ftp/python/3.5.2/Python-3.5.2.tgz && \
    tar xvf Python-3.5.2.tgz && cd Python-3.5.2 && \
    ./configure --without-doc-strings --prefix=/usr --without-pymalloc --enable-shared && \
    make && make install && \
    ldconfig && \
    cd .. && rm -rf Python-3.5.2 && rm Python-3.5.2.tgz && \
    pip3 install --no-cache-dir /python3/*py3*.whl hiredis && \
    rm -rf /python3 && \
    python3 -m sonic_ax_impl install && \
    python3 -m pip uninstall -y pip setuptools && \
    /bin/bash -c "rm -rf /usr/lib/python3.5/{unittest,lib2to3,tkinter,idlelib,email,test}" && \
    apt-get -y purge build-essential wget libssl-dev openssl && \
    apt-get clean -y && apt-get autoclean -y && apt-get autoremove -y && \
    find / | grep -E "__pycache__" | xargs rm -rf && \
    rm -rf ~/.cache

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

## Although exposing ports is not need for host net mode, keep it for possible bridge mode
EXPOSE 161/udp 162/udp

ENTRYPOINT ["/usr/bin/supervisord"]
