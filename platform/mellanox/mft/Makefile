.ONESHELL:
SHELL = /bin/bash
.SHELLFLAGS += -e

MFT_NAME = mft-$(MFT_VERSION)-$(MFT_REVISION)-x86_64-deb
MFT_TGZ = $(MFT_NAME).tgz
SRC_DEB = kernel-mft-dkms_$(MFT_VERSION)-$(MFT_REVISION)_all.deb

MAIN_TARGET = mft_$(MFT_VERSION)-$(MFT_REVISION)_amd64.deb
DERIVED_TARGETS = kernel-mft-dkms_$(MFT_VERSION)-$(KVERSION)_all.deb mft-oem_$(MFT_VERSION)-$(MFT_REVISION)_amd64.deb

$(addprefix $(DEST)/, $(MAIN_TARGET)): $(DEST)/% :
	rm -rf $(MFT_NAME)
	wget -O $(MFT_TGZ) http://www.mellanox.com/downloads/MFT/$(MFT_TGZ)
	tar xzf $(MFT_TGZ)
	pushd $(MFT_NAME)/SDEBS

	# put a lock here because dpkg does not allow installing packages in parallel
	while true; do
	if mkdir $(DEST)/dpkg_lock &> /dev/null; then
	{ sudo dpkg -i $(SRC_DEB) && rm -d $(DEST)/dpkg_lock && break; } || { rm -d $(DEST)/dpkg_lock && exit 1 ; }
	fi
	done

	tar xvf `sudo dkms mkdriverdisk kernel-mft-dkms/$(MFT_VERSION) -a all -d ubuntu -k $(KVERSION) --media tar | grep "Disk image location" | cut -d':' -f2`
	popd

	# fix timestamp because we do not actually build tools, only kernel
	touch $(MFT_NAME)/DEBS/*
	mv $(MFT_NAME)/SDEBS/ubuntu-drivers/4.9.0/kernel-mft-dkms_$(MFT_VERSION)-$(KVERSION)_all.deb $(MFT_NAME)/DEBS/* $(DEST)

$(addprefix $(DEST)/, $(DERIVED_TARGETS)): $(DEST)/% : $(DEST)/$(MAIN_TARGET)
