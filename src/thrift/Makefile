SHELL = /bin/bash
.ONESHELL:
.SHELLFLAGS += -e

THRIFT_VERSION = 0.11.0
THRIFT_VERSION_FULL = $(THRIFT_VERSION)-4

MAIN_TARGET = libthrift-$(THRIFT_VERSION)_$(THRIFT_VERSION_FULL)_$(CONFIGURED_ARCH).deb
DERIVED_TARGETS = libthrift-dev_$(THRIFT_VERSION_FULL)_$(CONFIGURED_ARCH).deb \
		  python-thrift_$(THRIFT_VERSION_FULL)_$(CONFIGURED_ARCH).deb \
		  thrift-compiler_$(THRIFT_VERSION_FULL)_$(CONFIGURED_ARCH).deb

THRIFT_LINK_PRE = https://sonicstorage.blob.core.windows.net/packages/debian

$(addprefix $(DEST)/, $(MAIN_TARGET)): $(DEST)/% :
	rm -rf thrift-$(THRIFT_VERSION)

	wget -NO "thrift_$(THRIFT_VERSION).orig.tar.gz" "$(THRIFT_LINK_PRE)/thrift_0.11.0.orig.tar.gz?sv=2015-04-05&sr=b&sig=%2BrAjWESiSNRCMN7NGqEqVGceLefpwwS%2FWPKEfJpPLSQ%3D&se=2156-02-02T17%3A17%3A20Z&sp=r"
	wget -NO "thrift_$(THRIFT_VERSION_FULL).debian.tar.xz" "$(THRIFT_LINK_PRE)/thrift_0.11.0-4.debian.tar.xz?sv=2015-04-05&sr=b&sig=dj9uJ5YjUNupcmuxSX6%2F5IS9NqaGAyM9iF2h%2F2rROZA%3D&se=2156-02-02T17%3A19%3A34Z&sp=r"
	wget -NO "thrift_$(THRIFT_VERSION_FULL).dsc" "$(THRIFT_LINK_PRE)/thrift_0.11.0-4.dsc?sv=2015-04-05&sr=b&sig=pWfg55owvQ2jZtZ6ylHp0OP8uZyfc9sxO6H%2BP4Ez7w4%3D&se=2156-02-02T17%3A20%3A05Z&sp=r"

	dpkg-source -x thrift_$(THRIFT_VERSION_FULL).dsc
	pushd thrift-$(THRIFT_VERSION)

	# Revert breaking change in thrift 0.11.0
	# saithrift implementation relies on the bug in union serialization
	# (https://jira.apache.org/jira/browse/THRIFT-3650)
	patch -p1 < ../patch/0001-Revert-THRIFT-3650-incorrect-union-serialization.patch
	patch -p1 < ../patch/0002-cve-2017-1000487.patch
	CXXFLAGS="-DFORCE_BOOST_SMART_PTR" DEB_BUILD_OPTIONS=nocheck dpkg-buildpackage -d -rfakeroot -b -us -uc -j$(SONIC_CONFIG_MAKE_JOBS) --admindir $(SONIC_DPKG_ADMINDIR)
	popd

	mv $(DERIVED_TARGETS) $* $(DEST)/

$(addprefix $(DEST)/, $(DERIVED_TARGETS)): $(DEST)/% : $(DEST)/$(MAIN_TARGET)
