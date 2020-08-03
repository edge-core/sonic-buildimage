.ONESHELL:
SHELL = /bin/bash
.SHELLFLAGS += -e

MFT_NAME = mft-$(MFT_VERSION)-$(MFT_REVISION)-x86_64-deb
MFT_TGZ = $(MFT_NAME).tgz

SRC_DEB = kernel-mft-dkms_$(MFT_VERSION)-$(MFT_REVISION)_all.deb
MOD_DEB = kernel-mft-dkms-modules-$(KVERSION)_$(MFT_VERSION)_amd64.deb

MAIN_TARGET = mft_$(MFT_VERSION)-$(MFT_REVISION)_amd64.deb
DERIVED_TARGETS = $(MOD_DEB) mft-oem_$(MFT_VERSION)-$(MFT_REVISION)_amd64.deb

DKMS_BMDEB = /var/lib/dkms/kernel-mft-dkms/$(MFT_VERSION)/bmdeb

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

	popd

	sudo dkms build kernel-mft-dkms/$(MFT_VERSION) -k $(KVERSION) -a amd64
	sudo dkms mkbmdeb kernel-mft-dkms/$(MFT_VERSION) -k $(KVERSION) -a amd64

	cp -f $(DKMS_BMDEB)/$(MOD_DEB) $(MFT_NAME)/DEBS/$(MOD_DEB)

	# fix timestamp because we do not actually build tools, only kernel
	touch $(MFT_NAME)/DEBS/*.deb
	mv $(MFT_NAME)/DEBS/*.deb $(DEST)

$(addprefix $(DEST)/, $(DERIVED_TARGETS)): $(DEST)/% : $(DEST)/$(MAIN_TARGET)
