FROM docker-base

RUN apt-get update \
    && apt-get install -y libsensors4-dev \
    python \
    python-dev

COPY deps /root/deps

RUN dpkg_apt() { [ -f $1 ] && { dpkg -i $1 || apt-get -y install -f; } || return 1; }; \
    dpkg_apt  /root/deps/xp-tools.deb              \
     && dpkg_apt  /root/deps/libsai.deb            \
     && dpkg_apt  /root/deps/sai.deb               \
     && dpkg_apt /root/deps/libthrift-0.9.3_*.deb  \
     && dpkg_apt /root/deps/libnl-3-200_*.deb      \
     && dpkg_apt /root/deps/libnl-genl-3-200_*.deb \
     && dpkg_apt /root/deps/libnl-route-3-200_*.deb


COPY ["deps/saiserver", "start.sh", "/usr/bin/"]

COPY ["supervisord.conf", "/etc/supervisor/conf.d/"]

COPY ["portmap.ini", "profile.ini", "/etc/sai/"]

## Clean up
RUN apt-get clean -y; apt-get autoclean -y; apt-get autoremove -y
RUN rm -rf deps

ENTRYPOINT ["/usr/bin/supervisord"]
