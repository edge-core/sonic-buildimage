FROM docker-base

RUN apt-get update

COPY ["deps/libhiredis0.13*.deb", "deps/libswsscommon_*.deb", "deps/libsairedis_*.deb", "/deps/"]

RUN dpkg_apt() { [ -f $1 ] && { dpkg -i $1 || apt-get -y install -f; } || return 1; }; dpkg_apt /deps/libhiredis0.13*.deb
RUN dpkg_apt() { [ -f $1 ] && { dpkg -i $1 || apt-get -y install -f; } || return 1; }; dpkg_apt /deps/libswsscommon_*.deb
RUN dpkg_apt() { [ -f $1 ] && { dpkg -i $1 || apt-get -y install -f; } || return 1; }; dpkg_apt /deps/libsairedis_*.deb

RUN apt-get install -f -y ifupdown bridge-utils

## Copy executable binaries
COPY ["deps/orchagent","deps/swssconfig","deps/portsyncd","deps/intfsyncd","deps/neighsyncd","/usr/local/bin/"]

COPY start.sh /usr/bin/start.sh

## Clean up
RUN apt-get clean -y; apt-get autoclean -y; apt-get autoremove -y
RUN rm -rf /deps

ENTRYPOINT /usr/bin/start.sh    \
        && /bin/bash
