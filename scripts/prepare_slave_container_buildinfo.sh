#!/bin/bash

SLAVE_DIR=$1
ARCH=$2
DISTRO=$3

# Install the latest debian package sonic-build-hooks in the slave container
sudo dpkg -i --force-overwrite $SLAVE_DIR/buildinfo/sonic-build-hooks_*.deb > /dev/null

# Enable the build hooks
symlink_build_hooks

# Build the slave running config
cp -rf $SLAVE_DIR/buildinfo/* /usr/local/share/buildinfo/
. /usr/local/share/buildinfo/scripts/buildinfo_base.sh

# Build the slave version config
[ -d /usr/local/share/buildinfo/versions ] && rm -rf /usr/local/share/buildinfo/versions
scripts/versions_manager.py generate -t "/usr/local/share/buildinfo/versions" -n "build-${SLAVE_DIR}" -d "$DISTRO" -a "$ARCH"
touch ${BUILDINFO_PATH}/versions/versions-deb

rm -f /etc/apt/preferences.d/01-versions-deb
([ "$ENABLE_VERSION_CONTROL_DEB" == "y" ] && [ -f $VERSION_DEB_PREFERENCE ]) && cp -f $VERSION_DEB_PREFERENCE /etc/apt/preferences.d/
exit 0
