FROM docker-syncd

## Make apt-get non-interactive
ENV DEBIAN_FRONTEND=noninteractive

COPY deps /deps

## Pre-install the fundamental packages
RUN apt-get update \
 && apt-get -y install  \
    net-tools           \
    python-pip          \
    build-essential     \
    libssl-dev          \
    libffi-dev          \
    python-dev          \
    wget                \
    cmake               \
    supervisor          \
 && wget https://github.com/nanomsg/nanomsg/archive/1.0.0.tar.gz \
 && tar xvfz 1.0.0.tar.gz \
 && cd nanomsg-1.0.0    \
 && mkdir -p build      \
 && cmake .             \
 && make install        \
 && ldconfig            \
 && cd ..               \
 && rm -fr nanomsg-1.0.0 \
 && rm -f 1.0.0.tar.gz  \
 && pip install cffi==1.7.0    \
 && pip install --upgrade cffi==1.7.0 \
 && pip install nnpy    \
 && mkdir -p /opt       \
 && cd /opt             \
 && wget https://raw.githubusercontent.com/p4lang/ptf/master/ptf_nn/ptf_nn_agent.py \
 && dpkg_apt() { [ -f $1 ] && { dpkg -i $1 || apt-get -y install -f; } || return 1; } \
 && dpkg -r syncd \
 && dpkg_apt /deps/syncd_*.deb \
 && dpkg_apt /deps/libthrift-0.9.2_*.deb \
 && apt-get clean -y; apt-get autoclean -y; apt-get autoremove -y \
 && rm -rf /deps

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY ptf_nn_agent.conf /etc/supervisor/conf.d/ptf_nn_agent.conf

ENTRYPOINT service rsyslog start \
    && service syncd start       \
    && /usr/bin/supervisord
