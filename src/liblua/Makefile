SHELL = /bin/bash
.ONESHELL:
.SHELLFLAGS += -e

LIBLUA_VERSION = 5.1.5
LIBLUA_VERSION_FULL = $(LIBLUA_VERSION)-8.1

MAIN_TARGET = liblua5.1-0_$(LIBLUA_VERSION_FULL)_$(CONFIGURED_ARCH).deb

$(addprefix $(DEST)/, $(MAIN_TARGET)): $(DEST)/% :
	rm -rf lua5.1-$(LIBLUA_VERSION)

	wget -O lua5.1_$(LIBLUA_VERSION).orig.tar.gz -N "http://deb.debian.org/debian/pool/main/l/lua5.1/lua5.1_$(LIBLUA_VERSION).orig.tar.gz"
	wget -O lua5.1_$(LIBLUA_VERSION_FULL).dsc -N "http://deb.debian.org/debian/pool/main/l/lua5.1/lua5.1_$(LIBLUA_VERSION_FULL).dsc"
	wget -O lua5.1_$(LIBLUA_VERSION_FULL).debian.tar.xz -N "http://deb.debian.org/debian/pool/main/l/lua5.1/lua5.1_$(LIBLUA_VERSION_FULL).debian.tar.xz"

	dpkg-source -x lua5.1_$(LIBLUA_VERSION_FULL).dsc
	pushd lua5.1-$(LIBLUA_VERSION)
	patch -p1 < ../patch/0001-use-all-characters-to-calculate-string-hash.patch

	DEB_BUILD_OPTIONS=nocheck dpkg-buildpackage -us -uc -b -j$(SONIC_CONFIG_MAKE_JOBS) --admindir $(SONIC_DPKG_ADMINDIR)
	popd

	mv $(DERIVED_TARGETS) $* $(DEST)/
