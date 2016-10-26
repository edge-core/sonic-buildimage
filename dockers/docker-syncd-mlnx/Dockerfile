FROM docker-base

RUN apt-get update

COPY deps /deps

RUN dpkg_apt() { [ -f $1 ] && { dpkg -i $1 || apt-get -y install -f; } || return 1; }; \
    dpkg_apt /deps/applibs_*.deb           \
    && dpkg_apt /deps/applibs-dev_*.deb    \
    && dpkg_apt /deps/sx-complib_*.deb     \
    && dpkg_apt /deps/sxd-libs_*.deb       \
    && dpkg_apt /deps/sx-scew_*.deb        \
    && dpkg_apt /deps/sx-examples_*.deb    \
    && dpkg_apt /deps/sx-gen-utils_*.deb   \
    && dpkg_apt /deps/python-sdk-api_*.deb \
    && dpkg_apt /deps/iproute2_*.deb       \
    && dpkg_apt /deps/mft*.deb             \

    && dpkg_apt /deps/libhiredis0.13*.deb       \
    && dpkg_apt /deps/libnl-3-200_*.deb         \
    && dpkg_apt /deps/libnl-genl-3-200_*.deb    \
    && dpkg_apt /deps/libnl-route-3-200_*.deb   \
    && dpkg_apt /deps/libswsscommon_*.deb       \
    && dpkg_apt /deps/mlnx-sai_*.deb            \
    && dpkg_apt /deps/libsairedis_*.deb         \
    && dpkg_apt /deps/libsaimetadata_*.deb

RUN dpkg_apt() { [ -f $1 ] && { dpkg -i $1 || apt-get -y install -f; } || return 1; }; dpkg_apt /deps/syncd_*.deb

COPY ["start.sh", "/usr/bin/"]
COPY ["mlnx-fw-upgrade.sh", "/usr/bin/"]
COPY ["/deps/fw-SPC.mfa", "/etc/mlnx/"]

## Clean up
RUN apt-get clean -y; apt-get autoclean -y; apt-get autoremove -y
RUN rm -rf /deps

ENTRYPOINT ["/bin/bash"]
CMD ["/usr/bin/start.sh"]
