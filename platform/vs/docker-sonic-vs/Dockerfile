FROM docker-config-engine

## Make apt-get non-interactive
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update

RUN apt-get install -y net-tools \
                       ethtool \
                       tcpdump \
                       ifupdown \
                       bridge-utils \
                       python-ply \
                       libqt5core5a \
                       libqt5network5 \
                       libboost-program-options1.55.0 \
                       libboost-system1.55.0 \
                       libboost-thread1.55.0 \
                       libgmp10 \
                       libjudydebian1 \
                       libnanomsg0 \
                       libdaemon0 \
                       libjansson4 \
                       libjemalloc1 \
                       openssh-client \
                       openssh-server \
                       libc-ares2 \
                       iproute

COPY \
debs/libnl-route-3-200_3.2.27-1_amd64.deb debs/libnl-genl-3-200_3.2.27-1_amd64.deb debs/libnl-nf-3-200_3.2.27-1_amd64.deb debs/libhiredis0.13_0.13.3-2_amd64.deb debs/libnl-3-200_3.2.27-1_amd64.deb debs/libnl-cli-3-200_3.2.27-1_amd64.deb debs/libswsscommon_1.0.0_amd64.deb debs/libsairedis_1.0.0_amd64.deb debs/libsaimetadata_1.0.0_amd64.deb debs/libteam5_1.26-1_amd64.deb debs/libsaivs_1.0.0_amd64.deb debs/swss_1.0.0_amd64.deb debs/syncd-vs_1.0.0_amd64.deb debs/redis-server_3.2.4-1~bpo8+1_amd64.deb debs/redis-tools_3.2.4-1~bpo8+1_amd64.deb debs/libteamdctl0_1.26-1_amd64.deb debs/libteam-utils_1.26-1_amd64.deb debs/sonic-device-data_1.0-1_all.deb debs/quagga_0.99.24.1-2.1_amd64.deb debs/

RUN dpkg -i \
debs/libnl-route-3-200_3.2.27-1_amd64.deb debs/libnl-genl-3-200_3.2.27-1_amd64.deb debs/libnl-nf-3-200_3.2.27-1_amd64.deb debs/libhiredis0.13_0.13.3-2_amd64.deb debs/libnl-3-200_3.2.27-1_amd64.deb debs/libnl-cli-3-200_3.2.27-1_amd64.deb debs/libswsscommon_1.0.0_amd64.deb debs/libsairedis_1.0.0_amd64.deb debs/libsaimetadata_1.0.0_amd64.deb debs/libteam5_1.26-1_amd64.deb debs/libsaivs_1.0.0_amd64.deb debs/swss_1.0.0_amd64.deb debs/syncd-vs_1.0.0_amd64.deb debs/redis-server_3.2.4-1~bpo8+1_amd64.deb debs/redis-tools_3.2.4-1~bpo8+1_amd64.deb debs/libteamdctl0_1.26-1_amd64.deb debs/libteam-utils_1.26-1_amd64.deb debs/sonic-device-data_1.0-1_all.deb debs/quagga_0.99.24.1-2.1_amd64.deb 

## Clean up
RUN apt-get clean -y; apt-get autoclean -y; apt-get autoremove -y
RUN rm -rf /debs

RUN sed -ri 's/^daemonize yes$/daemonize no/;                                           \
             s/^logfile .*$/logfile ""/;                                                \
             s/^# syslog-enabled no$/syslog-enabled no/;                                \
             s/^# unixsocket/unixsocket/                                                \
            ' /etc/redis/redis.conf

COPY ["50-default.conf", "/etc/rsyslog.d/"]
COPY ["start.sh", "orchagent.sh", "/usr/bin/"]
COPY ["brcm.profile.ini", "/usr/share/sonic/device/vswitch/"]
COPY ["supervisord.conf", "/etc/supervisor/conf.d/"]

ENTRYPOINT ["/usr/bin/supervisord"]