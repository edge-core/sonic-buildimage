FROM ubuntu:16.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update
RUN apt-get install -y \
                openssh-server \
                gcc \
                vim \
                make \
                git \
                sudo \
                python \
                python-dev \
                python-cffi \
                libffi-dev \
                libssl-dev \
                sshpass \
                libxml2 \
                libxslt1-dev \
                python-setuptools

# For JNLP launcher 
RUN apt-get install -y default-jre

# For syslog test
RUN apt-get install -y rsyslog psmisc

# Remove cffi 1.5.2, will install 1.10.0 by pip later
RUN apt-get remove -y python-cffi python-cffi-backend

RUN easy_install pip

RUN pip install ipaddr \
                lxml \
                netaddr \
                natsort \
                six \
                pexpect \
                pyasn1==0.1.9 \
                pysnmp==4.2.5 \
                jinja2==2.7.2 \
                cffi==1.10.0 \
                paramiko==2.1.2

RUN git clone https://github.com/ansible/ansible
RUN cd ansible && git checkout v2.0.0.2-1 -b v2.0.0.2-1 && git submodule update --init --recursive && make && make install

RUN mkdir /var/run/sshd
EXPOSE 22

# Add user
ARG user
ARG uid
ARG guid
ARG hostname

ENV BUILD_HOSTNAME $hostname
ENV USER $user

RUN groupadd -f -r -g $guid g$user

RUN useradd $user -l -u $uid -g $guid -d /var/$user -m -s /bin/bash

COPY sonic-jenkins.pub /var/$user/.ssh/authorized_keys2

RUN echo "Host *\n\tStrictHostKeyChecking no\n" > /var/$user/.ssh/config
RUN chown $user /var/$user/.ssh -R
RUN chmod go= /var/$user/.ssh -R

# Add user to sudoers
RUN echo "$user ALL=(ALL) NOPASSWD:ALL" >>/etc/sudoers

USER $user

RUN cd /var/$user && git clone https://github.com/Azure/sonic-mgmt
