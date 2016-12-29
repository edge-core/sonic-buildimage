.ONESHELL:
SHELL = /bin/bash
.SHELLFLAGS += -e

MAIN_TARGET = igb.ko

$(addprefix $(DEST)/, $(MAIN_TARGET)): $(DEST)/% :
	rm -rf ./igb-$(IGB_DRIVER_VERSION)
	wget -O igb-$(IGB_DRIVER_VERSION).tar.gz "https://downloadmirror.intel.com/13663/eng/igb-$(IGB_DRIVER_VERSION).tar.gz"
	tar xzf igb-$(IGB_DRIVER_VERSION).tar.gz

	# Patch
	pushd ./igb-$(IGB_DRIVER_VERSION)
	patch -p1 < ../patch/0001-add-support-for-BCM54616-phy-for-intel-igb-driver.patch

	# Build the package
	pushd src
	export BUILD_KERNEL=3.16.0-4-amd64
	make
	popd

	popd
	mv ./igb-$(IGB_DRIVER_VERSION)/src/$* $(DEST)/
