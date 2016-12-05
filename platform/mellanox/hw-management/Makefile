.ONESHELL:
SHELL = /bin/bash

MAIN_TARGET = hw-management_1.mlnx.$(MLNX_HW_MANAGEMENT_VERSION)_amd64.deb

$(addprefix $(DEST)/, $(MAIN_TARGET)): $(DEST)/% :
	# get sources
	sudo rm -rf hw-management
	wget -N -O mlnx-hw-mgmt-$(MLNX_HW_MANAGEMENT_VERSION).tar.gz https://github.com/Mellanox/mellanox-openswitch/raw/master/hw-mgmt/mlnx-hw-mgmt-$(MLNX_HW_MANAGEMENT_VERSION).tar.gz
	tar xzf mlnx-hw-mgmt-$(MLNX_HW_MANAGEMENT_VERSION).tar.gz

	# build
	pushd hw-management
	sudo debian/rules binary KVERSION=$(KVERSION)
	popd

	mv $* $(DEST)/
