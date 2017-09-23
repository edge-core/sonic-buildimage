FROM debian:stretch

MAINTAINER gulv@microsoft.com

RUN echo "deb http://debian-archive.trafficmanager.net/debian/ stretch main contrib non-free" >> /etc/apt/sources.list && \
        echo "deb-src http://debian-archive.trafficmanager.net/debian/ stretch main contrib non-free" >> /etc/apt/sources.list && \
        echo "deb http://debian-archive.trafficmanager.net/debian-security/ stretch/updates main contrib non-free" >> /etc/apt/sources.list && \
        echo "deb-src http://debian-archive.trafficmanager.net/debian-security/ stretch/updates main contrib non-free" >> /etc/apt/sources.list && \
        echo 'deb http://debian-archive.trafficmanager.net/debian stretch-backports main' >> /etc/apt/sources.list

## Make apt-get non-interactive
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
        apt-utils \
        default-jre-headless \
        openssh-server \
        curl \
        wget \
        unzip \
        git \
        build-essential \
        libtool \
        lintian \
        sudo \
        dh-make \
        dh-exec \
        kmod \
        libtinyxml2-4 \
        libboost-program-options1.62-dev \
        libtinyxml2-dev \
        python \
        python-pip \
        libncurses5-dev \
        texinfo \
        dh-autoreconf \
        python3-pip \
        doxygen \
        devscripts \
        git-buildpackage \
        perl-modules \
        libswitch-perl \
        dh-systemd \
# For quagga build
        libreadline-dev \
        texlive-latex-base \
        texlive-generic-recommended \
        texlive-fonts-recommended \
        libpam0g-dev \
        libpam-dev \
        libcap-dev \
        imagemagick \
        ghostscript \
        groff \
        libpcre3-dev \
        gawk \
        chrpath \
# For frr build
        libc-ares-dev \
        libsnmp-dev \
        libjson-c3 \
        libjson-c-dev \
        libsystemd-dev \
        python-ipaddr \
# For libnl3 (local) build
        cdbs \
# For SAI meta build
        libxml-simple-perl \
        graphviz \
        aspell \
# For linux build
        bc \
        fakeroot \
        build-essential \
        devscripts \
        quilt \
        stgit \
# For platform-modules build
        module-assistant \
# For thrift build\
        gem2deb \
        libboost-all-dev \
        libevent-dev \
        libglib2.0-dev \
        libqt4-dev \
        python-all-dev \
        python-twisted \
        phpunit \
        libbit-vector-perl \
        openjdk-8-jdk \
        javahelper \
        maven-debian-helper \
        ant \
        libmaven-ant-tasks-java \
        libhttpclient-java \
        libslf4j-java \
        libservlet3.1-java \
        qt5-default \
# For mellanox sdk build
        libpcre3 \
        libpcre3-dev \
        byacc \
        flex \
        libglib2.0-dev \
        bison \
        expat \
        libexpat1-dev \
        dpatch \
        libdb-dev \
        iptables-dev \
        swig \
# For mellanox sai build
        libtool-bin \
        libxml2-dev \
# For build image
        cpio \
        squashfs-tools \
        zip \
# For broadcom sdk build
        linux-compiler-gcc-6-x86 \
        linux-kbuild-4.9 \
# teamd build
        libdaemon-dev \
        libdbus-1-dev \
        libjansson-dev \
# For cavium sdk build
        libpcap-dev \
        dnsutils \
        libusb-dev \
# For debian image reconfiguration
        augeas-tools \
# For p4 build
        libyaml-dev \
        libevent-dev \
        libjudy-dev \
        libedit-dev \
        libnanomsg-dev \
        python-stdeb \
# For redis build
        libjemalloc-dev \
# For mft kernel module build
        dkms \
# For python3.5 build
        sharutils \
        libncursesw5-dev \
        libbz2-dev \
        liblzma-dev \
        libgdbm-dev \
        tk-dev \
        blt-dev \
        libmpdec-dev \
        libbluetooth-dev \
        locales \
        libsqlite3-dev \
        libgpm2 \
        time \
        net-tools \
        xvfb \
        python-sphinx \
        python3-sphinx \
# For Jenkins static analysis, unit testing and code coverage
        cppcheck \
        clang \
        pylint \
        python-pytest \
        gcovr \
        python-pytest-cov \
        python-parse \
# For snmpd
        default-libmysqlclient-dev \
        libssl-dev \
        libperl-dev \
        libpci-dev \
        libpci3 \
        libsensors4 \
        libsensors4-dev \
        libwrap0-dev \
# For mpdecimal
        docutils-common \
        libjs-sphinxdoc \
        libjs-underscore \
        python-docutils \
        python-jinja2 \
        python-markupsafe \
        python-pygments \
        python-roman \
        python-sphinx \
        sphinx-common \
        python3-sphinx \
# For sonic config engine testing
        python-lxml \
        python-jinja2 \
        python-netaddr \
        python-ipaddr \
        python-yaml \
# For lockfile
        procmail \
# For gtest
        libgtest-dev \
        cmake \
# For initramfs
        bash-completion

# For linux build
RUN apt-get -y build-dep linux

# For gobgp build
RUN export VERSION=1.8.3 \
 && wget https://storage.googleapis.com/golang/go$VERSION.linux-amd64.tar.gz \
 && tar -C /usr/local -xzf go$VERSION.linux-amd64.tar.gz \
 && echo 'export GOROOT=/usr/local/go' >> /etc/bash.bashrc \
 && echo 'export PATH=$PATH:$GOROOT/bin' >> /etc/bash.bashrc

# For p4 build
RUN pip install \
        ctypesgen \
        crc16

# For templating
RUN pip install j2cli

# For sonic config engine testing
RUN pip install pyangbind==0.5.10

# For supervisor build
RUN pip install meld3 mock

# Install dependencies for isc-dhcp-relay build
RUN apt-get -y build-dep isc-dhcp

RUN cd /usr/src/gtest && cmake . && make -C /usr/src/gtest

RUN mkdir /var/run/sshd
EXPOSE 22

# Install depot-tools (for git-retry)
RUN git clone https://chromium.googlesource.com/chromium/tools/depot_tools.git /usr/share/depot_tools
ENV PATH /usr/share/depot_tools:$PATH

# Install docker engine 17.03.2~ce-0 inside docker and enable experimental feature
RUN apt-get update
RUN apt-get install -y \
           apt-transport-https \
           ca-certificates \
           curl \
           gnupg2 \
           software-properties-common
RUN curl -fsSL https://download.docker.com/linux/debian/gpg | sudo apt-key add -
RUN add-apt-repository \
           "deb [arch=amd64] https://download.docker.com/linux/debian \
           $(lsb_release -cs) \
           stable"
RUN apt-get update
RUN apt-get install -y docker-ce=17.03.2~ce-0~debian-stretch
RUN echo "DOCKER_OPTS=\"--experimental\"" >> /etc/default/docker
