FROM docker-base

RUN apt-get update

COPY ["deps/libhiredis0.13*.deb", "deps/libswsscommon_*.deb", "deps/quagga_*", "/deps/"]

## Get fpmsyncd
RUN dpkg_apt() { [ -f $1 ] && { dpkg -i $1 || apt-get -y install -f; } || return 1; }; dpkg_apt /deps/libhiredis0.13*.deb
RUN dpkg_apt() { [ -f $1 ] && { dpkg -i $1 || apt-get -y install -f; } || return 1; }; dpkg_apt /deps/libswsscommon_*.deb

## Get Quagga
RUN dpkg_apt() { [ -f $1 ] && { dpkg -i $1 || apt-get -y install -f; } || return 1; }; dpkg_apt /deps/quagga_*.deb

COPY ["deps/fpmsyncd", "start.sh", "/usr/bin/"]

## Clean up
RUN apt-get clean -y; apt-get autoclean -y; apt-get autoremove -y
RUN rm -rf /deps

ENTRYPOINT /usr/bin/start.sh    \
        && /bin/bash
