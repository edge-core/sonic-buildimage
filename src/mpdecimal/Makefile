.ONESHELL:
SHELL = /bin/bash
.SHELLFLAGS += -e

MAIN_TARGET = libmpdec2_$(MPDECIMAL_VERSION_FULL)_$(CONFIGURED_ARCH).deb
DERIVED_TARGETS = libmpdec-dev_$(MPDECIMAL_VERSION_FULL)_$(CONFIGURED_ARCH).deb

$(addprefix $(DEST)/, $(MAIN_TARGET)): $(DEST)/% :
	rm -rf mpdecimal-$(MPDECIMAL_VERSION)

	wget -N -O mpdecimal_$(MPDECIMAL_VERSION).orig.tar.gz http://http.debian.net/debian/pool/main/m/mpdecimal/mpdecimal_$(MPDECIMAL_VERSION).orig.tar.gz
	wget -N -O mpdecimal_$(MPDECIMAL_VERSION_FULL).debian.tar.xz http://http.debian.net/debian/pool/main/m/mpdecimal/mpdecimal_$(MPDECIMAL_VERSION_FULL).debian.tar.xz
	wget -N -O mpdecimal_$(MPDECIMAL_VERSION_FULL).dsc http://http.debian.net/debian/pool/main/m/mpdecimal/mpdecimal_$(MPDECIMAL_VERSION_FULL).dsc

	dpkg-source -x mpdecimal_$(MPDECIMAL_VERSION_FULL).dsc
	pushd mpdecimal-$(MPDECIMAL_VERSION)
	dpkg-buildpackage -us -uc -b -j$(SONIC_CONFIG_MAKE_JOBS)
	popd

	mv $* $(DERIVED_TARGETS) $(DEST)/

$(addprefix $(DEST)/, $(DERIVED_TARGETS)): $(DEST)/% : $(DEST)/$(MAIN_TARGET)
