FROM docker-ptf

## Make apt-get non-interactive
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update

COPY ["deps/saithrift-0.9.tar.gz", "/deps/"]
COPY ["*.ini", "/etc/ptf/"]
COPY ["deps/SAI/test/saithrift/tests/*", "/usr/share/ptf-tests/"]

RUN tar xzf /deps/saithrift-0.9.tar.gz -C /usr/share/; \
    cd usr/share/saithrift-0.9;   \
    python setup.py install;      \
    rm -rf /deps
