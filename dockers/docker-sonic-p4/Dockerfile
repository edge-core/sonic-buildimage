FROM docker-base

RUN apt-get update

RUN apt-get install -y net-tools ethtool tcpdump ifupdown bridge-utils

COPY ["deps/libthrift-0.9.3_*.deb", "deps/libhiredis0.13*.deb", "deps/redis-tools_*.deb", "deps/redis-server_*.deb", "deps/libswsscommon_*.deb", "deps/p4-bmv2_*.deb", "deps/p4-switch_*.deb", "deps/libsairedis_*.deb", "deps/libsaimetadata_*.deb", "deps/syncd_*.deb", "deps/swss_*.deb", "deps/quagga_*.deb", "/deps/"]

RUN dpkg_apt() { [ -f $1 ] && { dpkg -i $1 || apt-get -y install -f; } || return 1; }; dpkg_apt /deps/libthrift-0.9.3_*.deb
RUN dpkg_apt() { [ -f $1 ] && { dpkg -i $1 || apt-get -y install -f; } || return 1; }; dpkg_apt /deps/libhiredis0.13*.deb
RUN dpkg_apt() { [ -f $1 ] && { dpkg -i $1 || apt-get -y install -f; } || return 1; }; dpkg_apt /deps/redis-tools_*.deb
RUN dpkg_apt() { [ -f $1 ] && { dpkg -i $1 || apt-get -y install -f; } || return 1; }; dpkg_apt /deps/redis-server_*.deb

RUN dpkg_apt() { [ -f $1 ] && { dpkg -i $1 || apt-get -y install -f; } || return 1; }; dpkg_apt /deps/libswsscommon_*.deb
RUN dpkg_apt() { [ -f $1 ] && { dpkg -i $1 || apt-get -y install -f; } || return 1; }; dpkg_apt /deps/p4-bmv2_*.deb
RUN dpkg_apt() { [ -f $1 ] && { dpkg -i $1 || apt-get -y install -f; } || return 1; }; dpkg_apt /deps/p4-switch_*.deb
RUN dpkg_apt() { [ -f $1 ] && { dpkg -i $1 || apt-get -y install -f; } || return 1; }; dpkg_apt /deps/libsairedis_*.deb
RUN dpkg_apt() { [ -f $1 ] && { dpkg -i $1 || apt-get -y install -f; } || return 1; }; dpkg_apt /deps/libsaimetadata_*.deb

RUN dpkg_apt() { [ -f $1 ] && { dpkg -i $1 || apt-get -y install -f; } || return 1; }; dpkg_apt /deps/syncd_*.deb
RUN dpkg_apt() { [ -f $1 ] && { dpkg -i $1 || apt-get -y install -f; } || return 1; }; dpkg_apt /deps/swss_*.deb
RUN dpkg_apt() { [ -f $1 ] && { dpkg -i $1 || apt-get -y install -f; } || return 1; }; dpkg_apt /deps/quagga_*.deb

ADD port_config.ini /port_config.ini
ADD startup.sh /scripts/startup.sh

ADD rsyslog.conf /etc/rsyslog.conf

## Clean up
RUN apt-get clean -y; apt-get autoclean -y; apt-get autoremove -y
RUN rm -rf /deps

ENTRYPOINT /bin/bash
