FROM debian:jessie

MAINTAINER Pavel Shirshov

## Copy dependencies
COPY deps /root/deps

## Make apt-get non-interactive
ENV DEBIAN_FRONTEND=noninteractive

## Set the apt source, update package cache and install necessary packages
RUN echo "deb http://ftp.us.debian.org/debian/ jessie main contrib non-free" > /etc/apt/sources.list \
    && apt-get update \
    && apt-get upgrade -y  \
    && apt-get dist-upgrade -y  \
    && apt-get install -y --no-install-recommends \
        openssh-server \
        vim-tiny \
        python \
        python-scapy \
        net-tools \
        python-setuptools \
        supervisor \
        traceroute \
        lsof \
        tcpdump \
    && dpkg -i /root/deps/python-ptf_*.deb \
    && dpkg -i --force-depends /root/deps/libthrift-0.9.2_*.deb \
    && dpkg -i --force-depends /root/deps/python-thrift_*.deb \
    && apt-get -y install -f \
    && rm -rf /root/deps \
    && apt-get -y autoclean \
    && apt-get -y autoremove \
    && rm -rf /var/lib/apt/lists/*

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
