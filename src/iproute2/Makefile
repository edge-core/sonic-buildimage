SHELL = /bin/bash
.ONESHELL:
.SHELLFLAGS += -e

IPROUTE2_VERSION = 4.9.0
IPROUTE2_VERSION_FULL = $(IPROUTE2_VERSION)-1

MAIN_TARGET = iproute2_$(IPROUTE2_VERSION_FULL)_$(CONFIGURED_ARCH).deb

$(addprefix $(DEST)/, $(MAIN_TARGET)): $(DEST)/% :
	# Remove any stale files
	rm -rf iproute2-$(IPROUTE2_VERSION)

	wget -O iproute2_$(IPROUTE2_VERSION).orig.tar.xz -N "https://sonicstorage.blob.core.windows.net/packages/iproute2_4.9.0.orig.tar.xz?sv=2015-04-05&sr=b&sig=9nvybd1xkXyRQbaG6Fy6wBazPA8IbZV0AO41GWXPEP8%3D&se=2154-10-23T11%3A59%3A00Z&sp=r"
	wget -O iproute2_$(IPROUTE2_VERSION_FULL).dsc -N "https://sonicstorage.blob.core.windows.net/packages/iproute2_4.9.0-1.dsc?sv=2015-04-05&sr=b&sig=m6FcMH9dOh8ggipBgOsONiXvDxoi6bfUO%2BxvidsMNMQ%3D&se=2154-10-23T11%3A59%3A53Z&sp=r"
	wget -O iproute2_$(IPROUTE2_VERSION_FULL).debian.tar.xz -N "https://sonicstorage.blob.core.windows.net/packages/iproute2_4.9.0-1.debian.tar.xz?sv=2015-04-05&sr=b&sig=U5NFuwG5C3vZXlUUNvoPMnKDtMKk66zbweA9rQYbEVY%3D&se=2154-10-23T12%3A00%3A15Z&sp=r"
	dpkg-source -x iproute2_$(IPROUTE2_VERSION_FULL).dsc

	pushd iproute2-$(IPROUTE2_VERSION)
	dpkg-buildpackage -us -uc -b -j$(SONIC_CONFIG_MAKE_JOBS)
	popd

	mv $* $(DEST)/
