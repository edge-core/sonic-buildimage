SHELL = /bin/bash
.ONESHELL:
.SHELLFLAGS += -e -x

THRIFT_VERSION = 0.13.0
THRIFT_VERSION_FULL = $(THRIFT_VERSION)-6

MAIN_TARGET = libthrift-$(THRIFT_VERSION)_$(THRIFT_VERSION_FULL)_$(CONFIGURED_ARCH).deb
DERIVED_TARGETS = libthrift-dev_$(THRIFT_VERSION_FULL)_$(CONFIGURED_ARCH).deb \
		  python3-thrift_$(THRIFT_VERSION_FULL)_$(CONFIGURED_ARCH).deb \
		  thrift-compiler_$(THRIFT_VERSION_FULL)_$(CONFIGURED_ARCH).deb

THRIFT_LINK_PRE = http://deb.debian.org/debian/pool/main/t/thrift/

$(addprefix $(DEST)/, $(MAIN_TARGET)): $(DEST)/% :
	rm -rf thrift-$(THRIFT_VERSION)

	wget -O "thrift_$(THRIFT_VERSION_FULL).debian.tar.xz" "$(THRIFT_LINK_PRE)/thrift_$(THRIFT_VERSION_FULL).debian.tar.xz"
	wget -O "thrift_$(THRIFT_VERSION).orig.tar.gz" "$(THRIFT_LINK_PRE)/thrift_$(THRIFT_VERSION).orig.tar.gz"
	wget -O "thrift_$(THRIFT_VERSION_FULL).dsc" "$(THRIFT_LINK_PRE)/thrift_$(THRIFT_VERSION_FULL).dsc"

	dpkg-source -x thrift_$(THRIFT_VERSION_FULL).dsc
	pushd thrift-$(THRIFT_VERSION)

	# Disable php perl and few other packages as they need additional packages to be installed
	patch -p1 < ../patch/0001-Remove-unneeded-packages.patch
	DEB_BUILD_OPTIONS=nocheck dpkg-buildpackage -d -rfakeroot -b -us -uc -j$(SONIC_CONFIG_MAKE_JOBS) --admindir $(SONIC_DPKG_ADMINDIR)
	popd

	mv $(DERIVED_TARGETS) $* $(DEST)/

$(addprefix $(DEST)/, $(DERIVED_TARGETS)): $(DEST)/% : $(DEST)/$(MAIN_TARGET)
