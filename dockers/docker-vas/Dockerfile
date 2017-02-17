FROM docker-base

COPY deps/vasclnt_*.deb deps/vasgp_*.deb /deps/
COPY user-override /etc/opt/quest/vas/user-override

## Make apt-get non-interactive
ENV DEBIAN_FRONTEND=noninteractive

## Pre-install the fundamental packages
## Clean up
RUN apt-get update &&                                                                           \
    dpkg_apt() { [ -f $1 ] && { dpkg -i $1 || apt-get -y install -f; } || return 1; } &&        \
    apt-get -y install                                                                          \
        sudo                                                                                    \
        &&                                                                                      \
    dpkg_apt /deps/vasclnt_*.deb &&                                                             \
    dpkg_apt /deps/vasgp_*.deb &&                                                               \
    apt-get clean -y && apt-get autoclean -y && apt-get autoremove -y &&                        \
    rm -rf /deps

## Expose to host, ie. image content will copy to host when container started
## For .so
VOLUME /host/lib/x86_64-linux-gnu
## For config
VOLUME /etc/pam.d/
VOLUME /host/etc
## For domain socket and local caches
VOLUME /var/opt/quest/vas/vasd/
## For home directory
VOLUME /home/

## Delete the symlinks and create full copies to host folder
ENTRYPOINT service rsyslog start                                                        \
    && cp --remove-destination /opt/quest/lib64/nss/libnss_vas4.so.2                    \
                               /host/lib/x86_64-linux-gnu/                              \
    && cp --remove-destination /opt/quest/lib64/security/pam_vas3.so                    \
                               /host/lib/x86_64-linux-gnu/security/                     \
    && cp --remove-destination /etc/nsswitch.conf                                       \
                               /host/etc/                                               \
    && service vasd start                                                               \
    && /bin/bash
