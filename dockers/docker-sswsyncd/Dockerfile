FROM docker-base

COPY                                                                                            \
    deps/python-tabulate_*.deb                                                                  \
    deps/libopennsl_*.deb                                                                       \
    deps/libsaibcm_*.deb                                                                        \
    deps/libsswsdk_*.deb                                                                        \
    deps/sswsyncd_*.deb                                                                         \
    /deps/

## Make apt-get non-interactive
ENV DEBIAN_FRONTEND=noninteractive

## Install packages
## Clean up
RUN dpkg_apt() { [ -f $1 ] && { dpkg -i $1 || apt-get -y install -f; } || return 1; } &&        \
    dpkg_apt /deps/python-tabulate_*.deb &&                                                     \
    dpkg_apt /deps/libopennsl_*.deb &&                                                          \
    dpkg_apt /deps/libsaibcm_*.deb &&                                                           \
    dpkg_apt /deps/libsswsdk_*.deb &&                                                           \
    dpkg_apt /deps/sswsyncd_*.deb &&                                                            \
    apt-get clean -y && apt-get autoclean -y && apt-get autoremove -y &&                        \
    rm -rf /deps

ENTRYPOINT service rsyslog start    \
    && service sswsyncd start       \
    && /bin/bash
