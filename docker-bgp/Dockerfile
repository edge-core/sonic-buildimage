FROM docker-base

COPY deps /deps
RUN dpkg_apt() { [ -f $1 ] && { dpkg -i $1 || apt-get -y install -f; } || return 1; }; dpkg_apt /deps/quagga_*.deb

## Clean up
RUN apt-get clean -y; apt-get autoclean -y; apt-get autoremove -y
RUN rm -rf /deps

ENTRYPOINT service rsyslog start    \
    && service quagga start         \
    && /bin/bash
