.ONESHELL:
SHELL = /bin/bash
.SHELLFLAGS += -e

MAIN_TARGET = igb.ko

$(addprefix $(DEST)/, $(MAIN_TARGET)): $(DEST)/% :
	rm -rf ./igb-$(IGB_DRIVER_VERSION)
	wget -O igb-$(IGB_DRIVER_VERSION).tar.gz "https://sonicstorage.blob.core.windows.net/packages/igb-5.3.5.4.tar.gz?sv=2015-04-05&sr=b&sig=Y7pO2Y%2FLTdQe1XucyRhMZdbHV5duAdvRYOqgJ5D7l4c%3D&se=2031-03-08T08%3A31%3A39Z&sp=r"
	tar xzf igb-$(IGB_DRIVER_VERSION).tar.gz

	# Patch
	pushd ./igb-$(IGB_DRIVER_VERSION)
	patch -p1 < ../patch/0001-add-PHY-support-for-Broadcom-54616.patch

	# Build the package
	pushd src
	export BUILD_KERNEL=4.9.0-3-amd64
	make
	popd

	popd
	mv ./igb-$(IGB_DRIVER_VERSION)/src/$* $(DEST)/
