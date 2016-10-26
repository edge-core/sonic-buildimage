FROM docker-base

RUN apt-get update

COPY ["deps/libhiredis0.13*.deb", "deps/libnl-3-200_*.deb", "deps/libnl-genl-3-200_*.deb", "deps/libnl-route-3-200_*.deb", "deps/libswsscommon_*.deb", "deps/libsairedis_*.deb", "deps/libsaimetadata_*.deb", "deps/swss_*.deb", "/deps/"]

RUN dpkg_apt() { [ -f $1 ] && { dpkg -i $1 || apt-get -y install -f; } || return 1; }; \
    dpkg_apt /deps/libhiredis0.13*.deb          \
    && dpkg_apt /deps/libnl-3-200_*.deb         \
    && dpkg_apt /deps/libnl-genl-3-200_*.deb    \
    && dpkg_apt /deps/libnl-route-3-200_*.deb   \
    && dpkg_apt /deps/libswsscommon_*.deb       \
    && dpkg_apt /deps/libsairedis_*.deb         \
    && dpkg_apt /deps/libsaimetadata_*.deb         \
    && dpkg_apt /deps/swss_*.deb

RUN apt-get install -f -y ifupdown bridge-utils redis-tools

COPY start.sh /usr/bin/start.sh

## Clean up
RUN apt-get clean -y; apt-get autoclean -y; apt-get autoremove -y
RUN rm -rf /deps

ENTRYPOINT ["/bin/bash"]
CMD ["/usr/bin/start.sh"]
