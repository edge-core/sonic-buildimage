FROM debian:jessie

## Set the apt source
COPY files/sources.list /etc/sources.list
RUN apt-get clean && apt-get update

## Pre-install the fundamental packages
RUN apt-get -y install                  \
    rsyslog                             \
    redis-server

ENTRYPOINT service rsyslog start    \
    && service redis-server start   \
    && /bin/bash
