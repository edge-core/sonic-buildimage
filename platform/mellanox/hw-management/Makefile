.ONESHELL:
SHELL = /bin/bash

MAIN_TARGET = hw-management_1.mlnx.$(MLNX_HW_MANAGEMENT_VERSION)_amd64.deb

$(addprefix $(DEST)/, $(MAIN_TARGET)): $(DEST)/% :

	pushd hw-mgmt
	git am ../*.patch
	chmod +x ./debian/rules
	KVERSION=$(KVERSION) dpkg-buildpackage -us -uc -b -rfakeroot -j$(SONIC_CONFIG_MAKE_JOBS) --admindir $(SONIC_DPKG_ADMINDIR)
	popd

	mv $* $(DEST)/
