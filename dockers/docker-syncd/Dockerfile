FROM docker-base

RUN apt-get update

COPY ["deps/libhiredis0.13*.deb", "deps/libswsscommon_*.deb", "deps/libopennsl_*.deb", "deps/libsaibcm_*.deb", "deps/libsairedis_*.deb", "deps/syncd_*.deb", "/deps/"]

RUN dpkg_apt() { [ -f $1 ] && { dpkg -i $1 || apt-get -y install -f; } || return 1; }; \
    dpkg_apt /deps/libhiredis0.13*.deb    \
    && dpkg_apt /deps/libswsscommon_*.deb \
    && dpkg_apt /deps/libopennsl_*.deb    \
    && dpkg_apt /deps/libsaibcm_*.deb     \
    && dpkg_apt /deps/libsairedis_*.deb   \
    && dpkg_apt /deps/syncd_*.deb

## TODO: add kmod into Depends
RUN apt-get install -f kmod

COPY ["deps/dsserve", "deps/bcmcmd", "start.sh", "/usr/bin/"]

## Clean up
RUN apt-get clean -y; apt-get autoclean -y; apt-get autoremove -y
RUN rm -rf /deps

ENTRYPOINT ["/bin/bash"]
CMD ["/usr/bin/start.sh"]
