FROM docker-base

RUN apt-get update

COPY deps /deps
## Get fpmsyncd
RUN dpkg_apt() { [ -f $1 ] && { dpkg -i $1 || apt-get -y install -f; } || return 1; }; dpkg_apt /deps/libhiredis0.13*.deb
RUN dpkg_apt() { [ -f $1 ] && { dpkg -i $1 || apt-get -y install -f; } || return 1; }; dpkg_apt /deps/libswsscommon_*.deb
COPY /deps/fpmsyncd /usr/local/bin/fpmsyncd

## Get Quagga
RUN dpkg_apt() { [ -f $1 ] && { dpkg -i $1 || apt-get -y install -f; } || return 1; }; dpkg_apt /deps/quagga_*.deb

## Clean up
RUN apt-get clean -y; apt-get autoclean -y; apt-get autoremove -y
RUN rm -rf /deps

ENTRYPOINT service rsyslog start    \
    && service quagga start         \
    && (fpmsyncd &)                 \
    && /bin/bash
