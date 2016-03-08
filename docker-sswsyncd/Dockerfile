FROM debian:jessie

## Set the apt source
COPY files/sources.list /etc/sources.list
RUN apt-get clean && apt-get update

## Pre-install the fundamental packages
## TODO: sswsyncd depends on ifupdown
RUN apt-get -y install  \
    ifupdown            \
    rsyslog

COPY deps /deps
RUN dpkg_apt() { [ -f $1 ] && { dpkg -i $1 || apt-get -y install -f; } || return 1; }; dpkg_apt /deps/libopennsl_*.deb
RUN dpkg_apt() { [ -f $1 ] && { dpkg -i $1 || apt-get -y install -f; } || return 1; }; dpkg_apt /deps/libsaibcm_*.deb
RUN dpkg_apt() { [ -f $1 ] && { dpkg -i $1 || apt-get -y install -f; } || return 1; }; dpkg_apt /deps/libsswsdk_*.deb
RUN dpkg_apt() { [ -f $1 ] && { dpkg -i $1 || apt-get -y install -f; } || return 1; }; dpkg_apt /deps/sswsyncd_*.deb

ENTRYPOINT service rsyslog start    \
    && service sswsyncd start       \
    && /bin/bash
