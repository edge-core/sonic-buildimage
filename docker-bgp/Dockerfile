FROM debian:jessie

## Set the apt source
COPY files/sources.list /etc/sources.list
RUN apt-get clean && apt-get update

## Pre-install the fundamental packages
RUN apt-get -y install                  \
    rsyslog                             \
    python

COPY deps /deps
RUN dpkg_apt() { [ -f $1 ] && { dpkg -i $1 || apt-get -y install -f; } || return 1; }; dpkg_apt /deps/quagga_*.deb

ENTRYPOINT service rsyslog start    \
    && service quagga start         \
    && /bin/bash
