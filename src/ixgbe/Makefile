.ONESHELL:
SHELL = /bin/bash
.SHELLFLAGS += -e

MAIN_TARGET = ixgbe.ko

$(addprefix $(DEST)/, $(MAIN_TARGET)): $(DEST)/% :
	rm -rf ./ixgbe-$(IXGBE_DRIVER_VERSION)
	wget -O ixgbe-$(IXGBE_DRIVER_VERSION).tar.gz "https://sonicstorage.blob.core.windows.net/packages/ixgbe-5.2.4.tar.gz?sv=2015-04-05&sr=b&sig=AaqJHHaPiJRp8R3HKobi0GNDgHAVnqijk6hpahwJ0Mg%3D&se=2154-10-05T22%3A19%3A29Z&sp=r"
	tar xzf ixgbe-$(IXGBE_DRIVER_VERSION).tar.gz

	# Patch
	pushd ./ixgbe-$(IXGBE_DRIVER_VERSION)

	# Build the package
	pushd src
	export BUILD_KERNEL=$(KVERSION)
	make
	popd

	popd
	mv ./ixgbe-$(IXGBE_DRIVER_VERSION)/src/$* $(DEST)/
