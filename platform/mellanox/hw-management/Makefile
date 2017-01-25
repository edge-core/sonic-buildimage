.ONESHELL:
SHELL = /bin/bash

MAIN_TARGET = hw-management_1.mlnx.$(MLNX_HW_MANAGEMENT_VERSION)_amd64.deb

$(addprefix $(DEST)/, $(MAIN_TARGET)): $(DEST)/% :
	# get sources
	sudo rm -rf hw-management
	git clone https://github.com/Mellanox/hw-mgmt/ -b $(MLNX_HW_MANAGEMENT_VERSION) hw-management

	# build
	pushd hw-management
	sed "s~@SED_VERSION@~$(MLNX_HW_MANAGEMENT_VERSION)~" -i debian/changelog
	chmod +x ./debian/rules
	sudo ./debian/rules binary KVERSION=$(KVERSION)
	popd

	mv $* $(DEST)/
