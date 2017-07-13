.ONESHELL:
SHELL = /bin/bash
.SHELLFLAGS += -e

MAIN_TARGET = cavm_platform_modules.deb
DEB_BUILD_DIR = cavm-platform-modules-deb
SCRIPT_SRC = $(DEB_BUILD_DIR)/
SYSTEMD_DIR = /etc/systemd/system

$(addprefix $(DEST)/, $(MAIN_TARGET)): $(DEST)/% :
	# get sources
	rm -rf SONiC
	git clone https://github.com/edge-core/SONiC.git

	# build
	pushd SONiC/AS7512-32X/module/

	KERNEL_SRC=/lib/modules/$(KVERSION)/build make
	popd
	mkdir -p $(DEB_BUILD_DIR)/lib/modules/$(KVERSION)
	mkdir -p $(DEB_BUILD_DIR)/usr/bin
	mkdir -p $(DEB_BUILD_DIR)$(SYSTEMD_DIR)/multi-user.target.wants/

	cp SONiC/AS7512-32X/module/*.ko $(DEB_BUILD_DIR)/lib/modules/$(KVERSION)
	cp SONiC/AS7512-32X/accton_as7512_util.py $(DEB_BUILD_DIR)/usr/bin
	chmod +x $(DEB_BUILD_DIR)/usr/bin/accton_as7512_util.py
	cp as7512-platform-init.service $(DEB_BUILD_DIR)$(SYSTEMD_DIR)
	ln -s $(SYSTEMD_DIR)/as7512-platform-init.service $(DEB_BUILD_DIR)$(SYSTEMD_DIR)/multi-user.target.wants/as7512-platform-init.service
	cp -r DEBIAN $(DEB_BUILD_DIR)
	dpkg-deb -b  $(DEB_BUILD_DIR) $(MAIN_TARGET)

	mv $(MAIN_TARGET) $(DEST)/
	rm -rf $(DEB_BUILD_DIR)
