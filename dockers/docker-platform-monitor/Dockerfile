FROM docker-config-engine

RUN apt-get update

RUN apt-get install -y smartmontools sensord 

## Clean up
RUN apt-get clean -y; apt-get autoclean -y; apt-get autoremove -y
RUN rm -rf /debs

COPY ["config.sh", "/usr/bin/"]

ENTRYPOINT /usr/bin/config.sh       \
    && service rsyslog start        \
    && service lm-sensors start     \
    && service smartmontools start  \
    && service sensord start        \
    && /bin/bash
