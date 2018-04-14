.ONESHELL:
SHELL = /bin/bash
.SHELLFLAGS += -e

MAIN_TARGET = libwrap0_$(LIBWRAP_VERSION)_amd64.deb
DERIVED_TARGETS = tcpd_$(LIBWRAP_VERSION)_amd64.deb

$(addprefix $(DEST)/, $(MAIN_TARGET)): $(DEST)/% :
	# Remove any stale files
	rm -rf ./tcp-wrappers-7.6.q*

	# Get source package
	apt-get source libwrap0
	cp tcp_wrappers-7.6-allowlist.patch tcp-wrappers-7.6.q/debian/patches/tcp_wrappers-7.6-allowlist.patch
	echo tcp_wrappers-7.6-allowlist.patch >> tcp-wrappers-7.6.q/debian/patches/series

	# Build source and Debian packages
	pushd tcp-wrappers-7.6.q
	dpkg-buildpackage -rfakeroot -b -us -uc -j$(SONIC_CONFIG_MAKE_JOBS)
	popd

	# Move the newly-built .deb packages to the destination directory
	mv $(DERIVED_TARGETS) $* $(DEST)/

$(addprefix $(DEST)/, $(DERIVED_TARGETS)): $(DEST)/% : $(DEST)/$(MAIN_TARGET)

