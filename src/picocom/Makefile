.ONESHELL:
SHELL = /bin/bash
.SHELLFLAGS += -e

MAIN_TARGET = picocom_$(PICOCOM_VERSION)_amd64.deb

$(addprefix $(DEST)/, $(MAIN_TARGET)): $(DEST)/% :
	# Remove any stale files
	rm -rf ./picocom-3.1

	# Get source package
	wget -NO picocom_$(PICOCOM_VERSION).dsc "https://sonicstorage.blob.core.windows.net/packages/debian/picocom_3.1-2.dsc?sv=2015-04-05&sr=b&sig=puo9KA27jT9Ey%2FkxRPBLIm30gFDdQJF85VKA7vuv9hk%3D&se=2155-07-10T08%3A03%3A50Z&sp=r"
	wget -NO picocom_$(PICOCOM_VERSION).debian.tar.xz "https://sonicstorage.blob.core.windows.net/packages/debian/picocom_3.1-2.debian.tar.xz?sv=2015-04-05&sr=b&sig=4HPuUi2FTb0AzCEsH9%2FsSfj17qIukyyOdRrHQFtjyBE%3D&se=2155-07-10T08%3A04%3A23Z&sp=r"
	wget -NO picocom_3.1.orig.tar.gz "https://sonicstorage.blob.core.windows.net/packages/debian/picocom_3.1.orig.tar.gz?sv=2015-04-05&sr=b&sig=RjQ84sf%2B%2FQuI%2B0PAcbPHXvnlNAuP%2BQoVrp2xzDJZfX4%3D&se=2155-07-10T08%3A04%3A45Z&sp=r"

	dpkg-source -x picocom_$(PICOCOM_VERSION).dsc

	# Build source and Debian packages
	pushd picocom-3.1
	patch -p0 < ../debhelper_10.patch
	dpkg-buildpackage -rfakeroot -b -us -uc -j$(SONIC_CONFIG_MAKE_JOBS)
	popd

	# Move the newly-built .deb packages to the destination directory
	mv $(DERIVED_TARGETS) $* $(DEST)/

$(addprefix $(DEST)/, $(DERIVED_TARGETS)): $(DEST)/% : $(DEST)/$(MAIN_TARGET)

