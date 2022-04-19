.ONESHELL:
SHELL = /bin/bash
.SHELLFLAGS += -e

MAIN_TARGET = debootstrap_$(DEBOOTSTRAP_VERSION)_all.deb

$(addprefix $(DEST)/, $(MAIN_TARGET)): $(DEST)/% :
	# Remove any stale files
	rm -rf ./debootstrap-$(DEBOOTSTRAP_VERSION) ./debootstrap*.{deb,udeb,dsc}

	# Get source package
	dget https://deb.debian.org/debian/pool/main/d/debootstrap/debootstrap_$(DEBOOTSTRAP_VERSION).dsc

	# Build source and Debian packages
	pushd debootstrap-$(DEBOOTSTRAP_VERSION)
	patch -p1 -i ../proc-mount.patch
	dpkg-buildpackage -rfakeroot -b -us -uc -j$(SONIC_CONFIG_MAKE_JOBS) --admindir $(SONIC_DPKG_ADMINDIR)
	popd

	# Move the newly-built .deb packages to the destination directory
	mv $(DERIVED_TARGETS) $* $(DEST)/

$(addprefix $(DEST)/, $(DERIVED_TARGETS)): $(DEST)/% : $(DEST)/$(MAIN_TARGET)

