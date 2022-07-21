.ONESHELL:
SHELL = /bin/bash
.SHELLFLAGS += -e

MAIN_TARGET = socat_$(SOCAT_VERSION)_$(CONFIGURED_ARCH).deb

$(addprefix $(DEST)/, $(MAIN_TARGET)): $(DEST)/% :
	# Remove any stale files
	rm -rf ./socat-1.7.4.1

	# Get source package
	wget -NO socat_$(SOCAT_VERSION).dsc "https://sonicstorage.blob.core.windows.net/packages/debian/socat_1.7.4.1-3.dsc?sv=2020-04-08&st=2021-12-14T00%3A00%3A00Z&se=2050-12-15T00%3A00%3A00Z&sr=b&sp=r&sig=fIy6dVz3s59K0TiMkTlwSWN8lCzRl3i76ruAtROhfWA%3D"
	wget -NO socat_$(SOCAT_VERSION).debian.tar.xz "https://sonicstorage.blob.core.windows.net/packages/debian/socat_1.7.4.1-3.debian.tar.xz?sv=2020-04-08&st=2021-12-14T08%3A00%3A00Z&se=2030-12-14T18%3A18%3A00Z&sr=b&sp=r&sig=C8aYSvaQgMJ58Z13kFY0Wr0J0QF6i7WCeET9%2BpF%2BAxc%3D"
	wget -NO socat_1.7.4.1.orig.tar.gz "https://sonicstorage.blob.core.windows.net/packages/debian/socat_1.7.4.1.orig.tar.gz?sv=2020-04-08&st=2021-12-14T00%3A00%3A00Z&se=2050-12-15T00%3A00%3A00Z&sr=b&sp=r&sig=gpihyZv%2Fr0bVrCUKCKwpS4bIoqiPpdd%2BgCfuUGNHOUc%3D"

	dpkg-source -x socat_$(SOCAT_VERSION).dsc

	# Build source and Debian packages
	pushd socat-1.7.4.1
	patch -p0 < ../enable_readline.patch
ifeq ($(CROSS_BUILD_ENVIRON), y)
	dpkg-buildpackage -rfakeroot -b -us -uc -a$(CONFIGURED_ARCH) -Pcross,nocheck -j$(SONIC_CONFIG_MAKE_JOBS) --admindir $(SONIC_DPKG_ADMINDIR)
else
	DEB_BUILD_OPTIONS=nocheck dpkg-buildpackage -rfakeroot -Pnocheck -b -us -uc -j$(SONIC_CONFIG_MAKE_JOBS) --admindir $(SONIC_DPKG_ADMINDIR)
endif
	popd

	# Move the newly-built .deb packages to the destination directory
	mv $(DERIVED_TARGETS) $* $(DEST)/

$(addprefix $(DEST)/, $(DERIVED_TARGETS)): $(DEST)/% : $(DEST)/$(MAIN_TARGET)

