.ONESHELL:
SHELL = /bin/bash
.SHELLFLAGS += -e

MAIN_TARGET = ixgbe.ko

$(addprefix $(DEST)/, $(MAIN_TARGET)): $(DEST)/% :
	rm -rf ./ixgbe-$(IXGBE_DRIVER_VERSION)
	wget -O ixgbe-$(IXGBE_DRIVER_VERSION).tar.gz "https://downloadmirror.intel.com/14687/eng/ixgbe-5.2.4.tar.gz"
	tar xzf ixgbe-$(IXGBE_DRIVER_VERSION).tar.gz

	# Patch
	pushd ./ixgbe-$(IXGBE_DRIVER_VERSION)

	# Build the package
	pushd src
	export BUILD_KERNEL=3.16.0-4-amd64
	make
	popd

	popd
	mv ./ixgbe-$(IXGBE_DRIVER_VERSION)/src/$* $(DEST)/
