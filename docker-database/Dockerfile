FROM docker-base

## Pre-install the fundamental packages
## Clean up
RUN apt-get -y install                                                              \
        redis-server                                                                \
        &&                                                                          \
    apt-get clean -y && apt-get autoclean -y && apt-get autoremove -y

RUN sed -ri 's/^daemonize yes$/daemonize no/' /etc/redis/redis.conf                 \
 && sed -ri 's/^logfile .*$/logfile ""/' /etc/redis/redis.conf                      \
 && sed -ri 's/^# syslog-enabled no$/syslog-enabled no/' /etc/redis/redis.conf

ENTRYPOINT service redis-server start
