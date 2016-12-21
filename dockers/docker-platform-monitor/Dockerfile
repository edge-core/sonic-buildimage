FROM docker-base

## Pre-install the fundamental packages
## Clean up
RUN apt-get update &&                                                               \
    apt-get -y install                                                              \
        smartmontools                                                               \
        sensord                                                                     \
        &&                                                                          \
    apt-get clean -y && apt-get autoclean -y && apt-get autoremove -y

ENTRYPOINT service rsyslog start    \
    && service lm-sensors start     \
    && service smartmontools start  \
    && service sensord start        \
    && /bin/bash
