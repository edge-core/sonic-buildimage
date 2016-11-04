FROM docker-base

COPY ["deps/libnl-3-200_*.deb", "deps/libnl-genl-3-200_*.deb", "deps/libnl-route-3-200_*.deb", "deps/libnl-nf-3-200_*.deb", "deps/libnl-cli-3-200_*.deb", "deps/libteam5_*.deb", "deps/libteam-dev_*.deb", "deps/libteam-utils_*.deb", "deps/libteamdctl0_*.deb", "deps/libhiredis0.13_*.deb", "deps/libswsscommon_*.deb", "/deps/"]


RUN dpkg_apt() { [ -f $1 ] && { dpkg -i $1 || apt-get -y install -f; } || return 1; }; \
    dpkg_apt /deps/libnl-3-200_*.deb            \
    && dpkg_apt /deps/libnl-genl-3-200_*.deb    \
    && dpkg_apt /deps/libnl-route-3-200_*.deb   \
    && dpkg_apt /deps/libnl-nf-3-200_*.deb      \
    && dpkg_apt /deps/libnl-cli-3-200_*.deb     \
    && dpkg_apt /deps/libteam5_*.deb            \
    && dpkg_apt /deps/libteam-utils_*.deb       \
    && dpkg_apt /deps/libteamdctl0_*.deb        \
    && dpkg_apt /deps/libteam-dev_*.deb         \
    && dpkg_apt /deps/libhiredis0.13_*.deb      \
    && dpkg_apt /deps/libswsscommon_*.deb

COPY ["deps/teamsyncd", "start.sh", "/usr/bin/"]

RUN apt-get clean -y; apt-get autoclean -y; apt-get autoremove -y
RUN rm -rf /deps

ENTRYPOINT ["/bin/bash"]
CMD ["/usr/bin/start.sh"]

