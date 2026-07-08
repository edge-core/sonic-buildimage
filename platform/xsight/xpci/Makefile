.ONESHELL:
SHELL = /bin/bash
.SHELLFLAGS += -e

XPCI_NAME =  xpci-dkms_$(XPCI_VERSION)_amd64
MOD_DEB_NAME = xpci-modules-$(KVERSION)
MOD_DEB = $(MOD_DEB_NAME)_$(XPCI_VERSION)_amd64.deb

MAIN_TARGET = $(MOD_DEB)

DKMS_TMP := $(shell mktemp -u -d -t dkms.XXXXXXXXXX)

$(addprefix $(DEST)/, $(MAIN_TARGET)): $(DEST)/% :

	mkdir -p $(DKMS_TMP)/DEBIAN
	mkdir -p $(DKMS_TMP)/lib/modules/$(KVERSION)/updates/dkms

	export kversion="$(KVERSION)"
	export xpci_version="$(XPCI_VERSION)"
	export mod_deb_name="$(MOD_DEB_NAME)"
	j2 templates/control.j2 > $(DKMS_TMP)/DEBIAN/control
	j2 templates/postinst.j2 > $(DKMS_TMP)/DEBIAN/postinst
	chmod +x $(DKMS_TMP)/DEBIAN/postinst

	XPCI_SRC=/usr/src/xpci-$(XPCI_VERSION)
	if [ -d xpci.patches ] && [ -f xpci.patches/series ] && \
	   grep -qE '^[^#[:space:]]' xpci.patches/series && [ -d "$$XPCI_SRC" ]; then
		PATCH_DIR=$$(readlink -f xpci.patches)
		sudo chmod -R u+w "$$XPCI_SRC"
		pushd "$$XPCI_SRC"
		sudo env QUILT_PATCHES="$$PATCH_DIR" quilt pop -a -f 2>/dev/null || true
		sudo env QUILT_PATCHES="$$PATCH_DIR" quilt push -a
		popd
	fi
	sudo dkms install --force xpci/$(XPCI_VERSION) -k $(KVERSION) -a $(CONFIGURED_ARCH)
	cp /lib/modules/$(KVERSION)/updates/dkms/xpci.ko $(DKMS_TMP)/lib/modules/$(KVERSION)/updates/dkms

	mkdir -p $(XPCI_NAME)/DEBS
	pushd $(XPCI_NAME)/DEBS
	dpkg -b $(DKMS_TMP) .
	popd

	rm -rf $(DKMS_TMP)

	cp $(XPCI_NAME)/DEBS/*.deb $(DEST)
