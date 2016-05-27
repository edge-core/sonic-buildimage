FROM docker-base

## Pre-install the fundamental packages
RUN apt-get update && apt-get -y install    \
    redis-server

RUN sed -ri 's/^daemonize yes$/daemonize no/' /etc/redis/redis.conf                 \
 && sed -ri 's/^logfile .*$/logfile ""/' /etc/redis/redis.conf                      \
 && sed -ri 's/^# syslog-enabled no$/syslog-enabled no/' /etc/redis/redis.conf

## Clean up
RUN apt-get clean -y; apt-get autoclean -y; apt-get autoremove -y

ENTRYPOINT service redis-server start
