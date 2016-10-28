FROM docker-base

RUN apt-get update

COPY ["/deps/libsaibcm*.deb","/deps/libopennsl_*.deb","/deps/python-sdk-api_*.deb", "/deps/iproute2_*.deb", "/deps/libthrift-0.9.3_*.deb", "/deps/libnl-3-200_*.deb", "/deps/libnl-genl-3-200_*.deb", "/deps/libnl-route-3-200_*.deb", "/deps/"]

RUN dpkg_apt() { [ -f $1 ] && { dpkg -i $1 || apt-get -y install -f; } || return 1; }; \
    dpkg_apt /deps/libopennsl_*.deb \
    && dpkg_apt /deps/libsaibcm_*.deb     \
    && dpkg_apt /deps/libthrift-0.9.3_*.deb    \
    && dpkg_apt /deps/libnl-3-200_*.deb        \
    && dpkg_apt /deps/libnl-genl-3-200_*.deb   \
    && dpkg_apt /deps/libnl-route-3-200_*.deb

COPY ["deps/saiserver", "start.sh", "/usr/bin/"]

COPY ["profile.ini", "portmap.ini", "/etc/sai/"]

## Clean up
RUN apt-get clean -y; apt-get autoclean -y; apt-get autoremove -y
RUN rm -rf /deps

ENTRYPOINT ["/bin/bash"]
CMD ["/usr/bin/start.sh"]
