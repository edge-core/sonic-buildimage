.ONESHELL:
SHELL = /bin/bash
.SHELLFLAGS += -e

MAIN_TARGET = libnl-3-200_$(LIBNL3_VERSION)_amd64.deb
DERIVED_TARGETS = libnl-3-dev_$(LIBNL3_VERSION)_amd64.deb \
		  libnl-genl-3-200_$(LIBNL3_VERSION)_amd64.deb \
		  libnl-genl-3-dev_$(LIBNL3_VERSION)_amd64.deb \
		  libnl-route-3-200_$(LIBNL3_VERSION)_amd64.deb \
		  libnl-route-3-dev_$(LIBNL3_VERSION)_amd64.deb  \
		  libnl-nf-3-200_$(LIBNL3_VERSION)_amd64.deb \
		  libnl-nf-3-dev_$(LIBNL3_VERSION)_amd64.deb \
		  libnl-cli-3-200_$(LIBNL3_VERSION)_amd64.deb \
		  libnl-cli-3-dev_$(LIBNL3_VERSION)_amd64.deb

$(addprefix $(DEST)/, $(MAIN_TARGET)): $(DEST)/% :
	# Obtaining the libnl3
	rm -rf ./libnl3-$(LIBNL3_VERSION_BASE)
	wget -O libnl3_$(LIBNL3_VERSION_BASE).orig.tar.gz -N "https://sonicstorage.blob.core.windows.net/packages/libnl3_$(LIBNL3_VERSION_BASE).orig.tar.gz?sv=2015-04-05&sr=b&sig=b4DnqrIsyVBDLmYhw7qwfaUJWqGCX2lDVMmmx7ihfrU%3D&se=2028-06-16T21%3A06%3A00Z&sp=r"
	wget -O libnl3_$(LIBNL3_VERSION).dsc -N "https://sonicstorage.blob.core.windows.net/packages/libnl3_$(LIBNL3_VERSION).dsc?sv=2015-04-05&sr=b&sig=AWTX45oDbeGA%2BRJZyiCcHmeIfCAgSeNV3IqopOBaRDg%3D&se=2028-06-16T21%3A05%3A30Z&sp=r"
	wget -O libnl3_$(LIBNL3_VERSION).debian.tar.xz -N "https://sonicstorage.blob.core.windows.net/packages/libnl3_$(LIBNL3_VERSION).debian.tar.xz?sv=2015-04-05&sr=b&sig=upIZ9dp5WEcLqp3ODeWKJXq5pJWCfeT0TIM0bx76wxM%3D&se=2028-06-16T21%3A04%3A44Z&sp=r"
	dpkg-source -x libnl3_$(LIBNL3_VERSION).dsc

	pushd ./libnl3-$(LIBNL3_VERSION_BASE)
	dpkg-buildpackage -rfakeroot -b -us -uc -j$(SONIC_CONFIG_MAKE_JOBS) --admindir $(SONIC_DPKG_ADMINDIR)
	popd

	mv $(DERIVED_TARGETS) $* $(DEST)/

$(addprefix $(DEST)/, $(DERIVED_TARGETS)): $(DEST)/% : $(DEST)/$(MAIN_TARGET)
