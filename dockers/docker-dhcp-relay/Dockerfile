FROM docker-config-engine

# Make apt-get non-interactive
ENV DEBIAN_FRONTEND=noninteractive

# Update apt's cache of available packages
RUN apt-get update

# Install isc-dhcp-relay Debian package
RUN apt-get -y install isc-dhcp-relay

# Clean up
RUN apt-get clean -y; apt-get autoclean -y; apt-get autoremove -y
RUN rm -rf /debs

COPY ["start.sh", "isc-dhcp-relay.sh", "/usr/bin/"]
COPY ["supervisord.conf", "/etc/supervisor/conf.d/"]
COPY ["isc-dhcp-relay.j2", "/usr/share/sonic/templates/"]

ENTRYPOINT ["/usr/bin/supervisord"]

