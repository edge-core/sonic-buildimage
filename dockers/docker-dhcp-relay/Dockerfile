FROM docker-base

## Make apt-get non-interactive
ENV DEBIAN_FRONTEND=noninteractive

## Install isc-dhcp-relay and clean up afterward
RUN apt-get update                          \
    && apt-get -y install isc-dhcp-relay    \
    && apt-get clean -y                     \
    && apt-get autoclean -y                 \
    && apt-get autoremove -y

COPY ["isc-dhcp-relay.j2", "/usr/share/dhcp-relay/"]
COPY ["config.sh", "/usr/bin/"]

ENTRYPOINT /usr/bin/config.sh       \
    && service rsyslog start        \
    && service isc-dhcp-relay start \
    && /bin/bash

