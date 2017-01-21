FROM docker-base

## Make apt-get non-interactive
ENV DEBIAN_FRONTEND=noninteractive

## Install isc-dhcp-relay and clean up afterward
RUN apt-get update                          \
    && apt-get -y install isc-dhcp-relay    \
    && apt-get clean -y                     \
    && apt-get autoclean -y                 \
    && apt-get autoremove -y

COPY isc-dhcp-relay /etc/default/isc-dhcp-relay

ENTRYPOINT service rsyslog start    \
    && service isc-dhcp-relay start \
    && /bin/bash

