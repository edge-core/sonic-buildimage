.ONESHELL:
SHELL = /bin/bash
.SHELLFLAGS += -e

MAIN_TARGET = libhiredis0.14_$(HIREDIS_VERSION_FULL)_$(CONFIGURED_ARCH).deb
DERIVED_TARGETS = libhiredis0.14-dbgsym_$(HIREDIS_VERSION_FULL)_$(CONFIGURED_ARCH).deb libhiredis-dev_$(HIREDIS_VERSION_FULL)_$(CONFIGURED_ARCH).deb

$(addprefix $(DEST)/, $(MAIN_TARGET)): $(DEST)/% :
	rm -rf hiredis-$(HIREDIS_VERSION)

	wget -O hiredis_$(HIREDIS_VERSION).orig.tar.gz http://http.debian.net/debian/pool/main/h/hiredis/hiredis_$(HIREDIS_VERSION).orig.tar.gz
	wget -O hiredis_$(HIREDIS_VERSION_FULL).debian.tar.xz http://http.debian.net/debian/pool/main/h/hiredis/hiredis_$(HIREDIS_VERSION_FULL).debian.tar.xz
	wget -O hiredis_$(HIREDIS_VERSION_FULL).dsc http://http.debian.net/debian/pool/main/h/hiredis/hiredis_$(HIREDIS_VERSION_FULL).dsc

	dpkg-source -x hiredis_$(HIREDIS_VERSION_FULL).dsc
	pushd hiredis-$(HIREDIS_VERSION)
	fakeroot debian/rules -j$(SONIC_CONFIG_MAKE_JOBS) binary
	popd

	mv $* $(DERIVED_TARGETS) $(DEST)/

$(addprefix $(DEST)/, $(DERIVED_TARGETS)): $(DEST)/% : $(DEST)/$(MAIN_TARGET)
