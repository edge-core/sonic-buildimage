FROM docker-config-engine

## Make apt-get non-interactive
ENV DEBIAN_FRONTEND=noninteractive

## Update APT package lists
RUN apt-get update

## Install isc-dhcp-relay Debian package
RUN apt-get -y install isc-dhcp-relay

## Clean up
RUN apt-get clean -y; apt-get autoclean -y; apt-get autoremove -y
RUN rm -rf /debs

COPY ["isc-dhcp-relay.j2", "/usr/share/sonic/templates/"]
COPY ["config.sh", "/usr/bin/"]
COPY ["start.sh", "/usr/bin/"]

ENTRYPOINT /usr/bin/config.sh \
    && service rsyslog start  \
    && /usr/bin/start.sh      \
    && /bin/bash
