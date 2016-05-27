FROM docker-base

## Pre-install the fundamental packages
RUN apt-get update && apt-get -y install    \
    smartmontools                           \
    sensord

## Clean up
RUN apt-get clean -y; apt-get autoclean -y; apt-get autoremove -y
RUN rm -rf /deps

ENTRYPOINT service rsyslog start    \
    && service lm-sensors start     \
    && service smartmontools start  \
    && service sensord start        \
    && /bin/bash
