FROM docker-base

RUN apt-get update

COPY ["deps/libhiredis0.13*.deb", "deps/libnl-3-200_*.deb", "deps/libnl-genl-3-200_*.deb", "deps/libnl-route-3-200_*.deb", "deps/libswsscommon_*.deb", "deps/libsairedis_*.deb", "deps/libsaimetadata_*.deb", "deps/syncd_*.deb", "deps/sai*.deb", "deps/libsai*.deb", "deps/xp-tools*.deb", "deps/xpshell*.deb", "/deps/"]

RUN dpkg_apt() { [ -f $1 ] && { dpkg -i $1 || apt-get -y install -f; } || return 1; }; \
    dpkg_apt /deps/libhiredis0.13*.deb              \
    && dpkg_apt /deps/libnl-3-200_*.deb             \
    && dpkg_apt /deps/libnl-genl-3-200_*.deb        \
    && dpkg_apt /deps/libnl-route-3-200_*.deb       \
    && dpkg_apt /deps/libswsscommon_*.deb           \
    && dpkg_apt /deps/sai*.deb                      \
    && dpkg_apt /deps/libsai*.deb                   \
    && dpkg_apt /deps/xp-tools*.deb                 \
    && dpkg_apt /deps/xpshell*.deb                  \
    && dpkg_apt /deps/libsairedis_*.deb             \
    && dpkg_apt /deps/libsaimetadata_*.deb          \
    && dpkg_apt /deps/syncd_*.deb

RUN apt-get -y install libpcap-dev libxml2-dev python-dev swig libsensors4-dev

COPY ["start.sh", "/usr/bin/"]

## Clean up
RUN apt-get clean -y; apt-get autoclean -y; apt-get autoremove -y
RUN rm -rf /deps

ENTRYPOINT /usr/bin/start.sh      \
        && /bin/bash
