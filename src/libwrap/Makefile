.ONESHELL:
SHELL = /bin/bash
.SHELLFLAGS += -e

MAIN_TARGET = libwrap0_$(LIBWRAP_VERSION)_amd64.deb
DERIVED_TARGETS = tcpd_$(LIBWRAP_VERSION)_amd64.deb

$(addprefix $(DEST)/, $(MAIN_TARGET)): $(DEST)/% :
	# Remove any stale files
	rm -rf ./tcp-wrappers-7.6.q*

	# Get source package
	wget -NO tcp-wrappers_$(LIBWRAP_VERSION).dsc "https://sonicstorage.blob.core.windows.net/packages/debian/tcp-wrappers_7.6.q-26.dsc?sv=2015-04-05&sr=b&sig=5dxVp8RsLfnuMDm99g4JpgG6Q3zzTaoTkPNVoo0d8YE%3D&se=2155-07-05T06%3A34%3A45Z&sp=r"
	wget -NO tcp-wrappers_$(LIBWRAP_VERSION).debian.tar.xz "https://sonicstorage.blob.core.windows.net/packages/debian/tcp-wrappers_7.6.q-26.debian.tar.xz?sv=2015-04-05&sr=b&sig=6%2FquqekmGloVz%2FaDc%2BCOCLL%2FKqEfIWrr%2BdmnZhJ8k8Q%3D&se=2155-07-05T06%3A32%3A43Z&sp=r"
	wget -NO tcp-wrappers_7.6.q.orig.tar.gz "https://sonicstorage.blob.core.windows.net/packages/debian/tcp-wrappers_7.6.q.orig.tar.gz?sv=2015-04-05&sr=b&sig=%2B%2BQbllR9xfwmYvgLiz1jtyn6ZP4oLgbTENTL5Fj8M4w%3D&se=2155-07-05T06%3A35%3A24Z&sp=r"

	dpkg-source -x tcp-wrappers_$(LIBWRAP_VERSION).dsc

	cp tcp_wrappers-7.6-allowlist.patch tcp-wrappers-7.6.q/debian/patches/tcp_wrappers-7.6-allowlist.patch
	echo tcp_wrappers-7.6-allowlist.patch >> tcp-wrappers-7.6.q/debian/patches/series

	# Build source and Debian packages
	pushd tcp-wrappers-7.6.q
	dpkg-buildpackage -rfakeroot -b -us -uc -j$(SONIC_CONFIG_MAKE_JOBS)
	popd

	# Move the newly-built .deb packages to the destination directory
	mv $(DERIVED_TARGETS) $* $(DEST)/

$(addprefix $(DEST)/, $(DERIVED_TARGETS)): $(DEST)/% : $(DEST)/$(MAIN_TARGET)

