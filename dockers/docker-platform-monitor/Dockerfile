FROM docker-config-engine

## Make apt-get non-interactive
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update

RUN apt-get install -y sensord

## Clean up
RUN apt-get clean -y; apt-get autoclean -y; apt-get autoremove -y
RUN rm -rf /debs

COPY ["start.sh", "lm-sensors.sh", "/usr/bin/"]
COPY ["supervisord.conf", "/etc/supervisor/conf.d/"]

ENTRYPOINT ["/usr/bin/supervisord"]

