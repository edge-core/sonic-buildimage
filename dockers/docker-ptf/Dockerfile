FROM debian:jessie

MAINTAINER Pavel Shirshov

## Copy dependencies
COPY deps /root/deps

## Make apt-get non-interactive
ENV DEBIAN_FRONTEND=noninteractive

## Set the apt source, update package cache and install necessary packages
RUN echo "deb http://ftp.us.debian.org/debian/ jessie main contrib non-free" > /etc/apt/sources.list \
    && apt-get update           \
    && apt-get upgrade -y       \
    && apt-get dist-upgrade -y  \
    && apt-get install -y --no-install-recommends \
        openssh-server      \
        vim                 \
        python              \
        python-scapy        \
        net-tools           \
        python-setuptools   \
        supervisor          \
        traceroute          \
        lsof                \
        tcpdump             \
        unzip               \
        pkg-config          \
        binutils            \
        net-tools           \
        python-pip          \
        build-essential     \
        libssl-dev          \
        libffi-dev          \
        python-dev          \
        wget                \
        cmake               \
    && dpkg_apt() { [ -f $1 ] && { dpkg -i $1 || apt-get -y install -f; } || return 1; } \
    && dpkg_apt /root/deps/python-ptf_*.deb \
    && dpkg_apt /root/deps/libthrift-0.9.2_*.deb \
    && dpkg_apt /root/deps/python-thrift_*.deb \
    && rm -rf /root/deps \
    && apt-get -y autoclean \
    && apt-get -y autoremove \
    && rm -rf /var/lib/apt/lists/* \
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
    && pip install cffi    \
    && pip install --upgrade cffi \
    && pip install nnpy    \
    && mkdir -p /opt       \
    && cd /opt             \
    && wget https://raw.githubusercontent.com/p4lang/ptf/master/ptf_nn/ptf_nn_agent.py

## Adjust sshd settings
RUN mkdir /var/run/sshd \
 && echo 'root:root' | chpasswd \
 && sed -ri 's/^PermitRootLogin\s+.*/PermitRootLogin yes/' /etc/ssh/sshd_config \
 && sed -ri 's/UsePAM yes/#UsePAM yes/g' /etc/ssh/sshd_config \
 && sed -i '$aUseDNS no' /etc/ssh/sshd_config \
 && mkdir /root/deps

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

EXPOSE 22

ENTRYPOINT ["/usr/bin/supervisord"]
