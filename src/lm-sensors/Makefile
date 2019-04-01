SHELL = /bin/bash
.ONESHELL:
	.SHELLFLAGS += -e


MAIN_TARGET = $(LM_SENSORS)
DERIVED_TARGETS = fancontrol_$(LM_SENSORS_VERSION_FULL)_all.deb \
				  libsensors4_$(LM_SENSORS_VERSION_FULL)_amd64.deb \
				  sensord_$(LM_SENSORS_VERSION_FULL)_amd64.deb

$(addprefix $(DEST)/, $(MAIN_TARGET)): $(DEST)/% :
	rm -rf lm-sensors-$(LM_SENSORS_VERSION)
	dget -u http://deb.debian.org/debian/pool/main/l/lm-sensors/lm-sensors_3.4.0-4.dsc
	git am *.patch
	pushd lm-sensors-$(LM_SENSORS_VERSION)
	DEB_BUILD_OPTIONS=nocheck PROG_EXTRA=sensord dpkg-buildpackage -us -uc -b -j$(SONIC_CONFIG_MAKE_JOBS)
	popd

	mv $* $(DEST)/

$(addprefix $(DEST)/, $(DERIVED_TARGETS)): $(DEST)/% : $(DEST)/$(MAIN_TARGET)
