SHELL = /bin/bash
.ONESHELL:
.SHELLFLAGS += -e


MAIN_TARGET = smartmontools_$(SMARTMONTOOLS_VERSION_FULL)_$(CONFIGURED_ARCH).deb

$(addprefix $(DEST)/, $(MAIN_TARGET)): $(DEST)/% :
	rm -rf smartmontools-$(SMARTMONTOOLS_VERSION_MAJOR)
	wget -O smartmontools_$(SMARTMONTOOLS_VERSION_MAJOR).orig.tar.gz -N "https://packages.trafficmanager.net/public/debian/smartmontools_$(SMARTMONTOOLS_VERSION_MAJOR).orig.tar.gz"
	wget -O smartmontools_$(SMARTMONTOOLS_VERSION_FULL).dsc -N "https://packages.trafficmanager.net/public/debian/smartmontools_$(SMARTMONTOOLS_VERSION_FULL).dsc"
	wget -O smartmontools_$(SMARTMONTOOLS_VERSION_FULL).debian.tar.xz -N "https://packages.trafficmanager.net/public/debian/smartmontools_$(SMARTMONTOOLS_VERSION_FULL).debian.tar.xz"
	dpkg-source -x smartmontools_$(SMARTMONTOOLS_VERSION_FULL).dsc

	pushd smartmontools-$(SMARTMONTOOLS_VERSION_MAJOR)
	dpkg-buildpackage -us -uc -b -j$(SONIC_CONFIG_MAKE_JOBS) --admindir $(SONIC_DPKG_ADMINDIR)
	popd

	mv $* $(DEST)/
