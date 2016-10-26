FROM docker-base

COPY deps/sswsdk*.whl deps/sonic_d*.whl deps/lldpsyncd_*.deb deps/lldpd_*.deb /deps/

## Pre-install the fundamental packages
## Install Python SSWSDK (lldpsyncd dependency)
## Install LLDP Sync Daemon
## Note: dpkg_apt function has the benefit to detect missing .deb file
## Clean up
RUN apt-get update && \
    dpkg_apt() { [ -f $1 ] && { dpkg -i $1 || apt-get -y install -f; } || return 1; } && \
    dpkg_apt /deps/lldpd_*.deb && \
    apt-get install -y python-pip supervisor && \
    pip install /deps/sswsdk*.whl && \
    pip install /deps/sonic_d*.whl && \
    apt-get remove -y python-pip && \
    apt-get purge -y && apt-get autoclean -y && apt-get autoremove -y && \
    rm -rf /deps ~/.cache

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

ENTRYPOINT ["/usr/bin/supervisord"]
