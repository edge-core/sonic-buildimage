SHELL = /bin/bash
.ONESHELL:
	.SHELLFLAGS += -e


MAIN_TARGET = $(LM_SENSORS)
DERIVED_TARGETS = fancontrol_$(LM_SENSORS_VERSION_FULL)_all.deb \
				  libsensors4_$(LM_SENSORS_VERSION_FULL)_amd64.deb \
				  sensord_$(LM_SENSORS_VERSION_FULL)_amd64.deb \
				  $(LM_SENSORS_DBG) \
				  $(LIBSENSORS_DBG) \
				  $(SENSORD_DBG)

$(addprefix $(DEST)/, $(MAIN_TARGET)): $(DEST)/% :
	rm -rf lm-sensors-$(LM_SENSORS_VERSION)
	dget -u http://deb.debian.org/debian/pool/main/l/lm-sensors/lm-sensors_$(LM_SENSORS_VERSION_FULL).dsc
	git apply *.patch
	pushd lm-sensors-$(LM_SENSORS_VERSION)
	DEB_BUILD_OPTIONS=nocheck PROG_EXTRA=sensord dpkg-buildpackage -us -uc -b -j$(SONIC_CONFIG_MAKE_JOBS)
	popd

	mv $(DERIVED_TARGETS) $* $(DEST)/

$(addprefix $(DEST)/, $(DERIVED_TARGETS)): $(DEST)/% : $(DEST)/$(MAIN_TARGET)
