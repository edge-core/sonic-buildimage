FROM docker-base

COPY ["deps/redis-tools_*.deb", "deps/redis-server_*.deb", "/deps/"]

## Install packages
## Clean up
RUN apt-get update &&                                                                   \
    dpkg_apt() { [ -f $1 ] && { dpkg -i $1 || apt-get -y install -f; } || return 1; };  \
    dpkg_apt /deps/redis-tools_*.deb &&                                                 \
    dpkg_apt /deps/redis-server_*.deb &&                                                \
    apt-get clean -y && apt-get autoclean -y && apt-get autoremove -y

RUN sed -ri 's/^daemonize yes$/daemonize no/;                                           \
             s/^logfile .*$/logfile ""/;                                                \
             s/^# syslog-enabled no$/syslog-enabled no/;                                \
             s/^# unixsocket/unixsocket/                                                \
            ' /etc/redis/redis.conf

ENTRYPOINT service redis-server start
