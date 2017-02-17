FROM docker-base

## Make apt-get non-interactive
ENV DEBIAN_FRONTEND=noninteractive

COPY deps/quagga_*.deb /deps/
RUN dpkg_apt() { [ -f $1 ] && { dpkg -i $1 || apt-get -y install -f; } || return 1; } &&        \
    dpkg_apt /deps/quagga_*.deb &&                                                              \
    apt-get clean -y && apt-get autoclean -y && apt-get autoremove -y &&                        \
    rm -rf /deps

COPY daemons /etc/quagga/

ENTRYPOINT service rsyslog start    \
    && service quagga start         \
    && /bin/bash
