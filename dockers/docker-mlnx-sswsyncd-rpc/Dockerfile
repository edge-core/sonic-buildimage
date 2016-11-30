FROM docker-base

## Make apt-get non-interactive
ENV DEBIAN_FRONTEND=noninteractive

## Pre-install the fundamental packages
RUN apt-get update \
 && apt-get -y install  \
    net-tools

COPY deps /deps
RUN dpkg_apt() { [ -f $1 ] && { dpkg -i $1 || apt-get -y install -f; } || return 1; }; \
    dpkg_apt /deps/python-tabulate_*.deb    \
    && dpkg_apt /deps/applibs_*.deb         \
    && dpkg_apt /deps/applibs-dev_*.deb     \
    && dpkg_apt /deps/sx-complib_*.deb      \
    && dpkg_apt /deps/sxd-libs_*.deb        \
    && dpkg_apt /deps/sx-scew_*.deb         \
    && dpkg_apt /deps/sx-examples_*.deb     \
    && dpkg_apt /deps/sx-gen-utils_*.deb    \
    && dpkg_apt /deps/python-sdk-api_*.deb  \
    && dpkg_apt /deps/sx-libnl_*.deb        \
    && dpkg_apt /deps/iproute2_*.deb        \
    && dpkg_apt /deps/libsswsdk_*.deb       \
    && dpkg_apt /deps/libthrift-0.9.3_*.deb \
    && dpkg_apt /deps/libthrift-dev_*.deb

RUN dpkg_apt() { [ -f $1 ] && { dpkg -i $1 || apt-get -y install -f; } || return 1; }; \
    dpkg_apt /deps/mlnx-sai_*.deb \
    && dpkg_apt /deps/sswsyncd-saithrift_*.deb

## Clean up
RUN apt-get clean -y ; apt-get autoclean -y ; apt-get autoremove -y ; rm -rf /deps

ENTRYPOINT service rsyslog start    \
    && mkdir -p /dev/sxdevs && ( [ -e /dev/sxdevs/sxcdev ] || mknod /dev/sxdevs/sxcdev c 231 193 ) \
    && service sswsyncd start       \
    && /bin/bash
