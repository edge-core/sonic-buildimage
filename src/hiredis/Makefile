.ONESHELL:
SHELL = /bin/bash
.SHELLFLAGS += -e

MAIN_TARGET = libhiredis0.13_$(HIREDIS_VERSION_FULL)_amd64.deb
DERIVED_TARGETS = libhiredis-dbg_$(HIREDIS_VERSION_FULL)_amd64.deb libhiredis-dev_$(HIREDIS_VERSION_FULL)_amd64.deb

$(addprefix $(DEST)/, $(MAIN_TARGET)): $(DEST)/% :
	rm -rf hiredis-$(HIREDIS_VERSION)

	wget -O hiredis_$(HIREDIS_VERSION).orig.tar.gz http://http.debian.net/debian/pool/main/h/hiredis/hiredis_$(HIREDIS_VERSION).orig.tar.gz
	wget -O hiredis_$(HIREDIS_VERSION_FULL).debian.tar.xz http://http.debian.net/debian/pool/main/h/hiredis/hiredis_$(HIREDIS_VERSION_FULL).debian.tar.xz
	wget -O hiredis_$(HIREDIS_VERSION_FULL).dsc http://http.debian.net/debian/pool/main/h/hiredis/hiredis_$(HIREDIS_VERSION_FULL).dsc

	dpkg-source -x hiredis_$(HIREDIS_VERSION_FULL).dsc
	pushd hiredis-$(HIREDIS_VERSION)
	dpkg-buildpackage -rfakeroot -d -b -us -uc -j$(SONIC_CONFIG_MAKE_JOBS) --admindir $(SONIC_DPKG_ADMINDIR)
	popd

	mv $* $(DERIVED_TARGETS) $(DEST)/

$(addprefix $(DEST)/, $(DERIVED_TARGETS)): $(DEST)/% : $(DEST)/$(MAIN_TARGET)
