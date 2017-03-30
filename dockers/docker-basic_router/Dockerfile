FROM docker-base

MAINTAINER Xudong Wu

## Make apt-get non-interactive
ENV DEBIAN_FRONTEND=noninteractive

## Set the apt source
RUN apt-get clean && apt-get update

COPY deps /deps

RUN dpkg -i /deps/libopennsl_*.deb;         \
    dpkg -i /deps/libsaibcm_*.deb;          \
    apt-get -y install -f


RUN mv /deps/basic_router /usr/sbin/basic_router

ENTRYPOINT rm -f /var/run/rsyslogd.pid  \
    && service rsyslog start            \
    && /bin/bash
