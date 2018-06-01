.ONESHELL:
SHELL = /bin/bash
.SHELLFLAGS += -e

MAIN_TARGET = initramfs-tools_$(INITRAMFS_TOOLS_VERSION)_all.deb

$(addprefix $(DEST)/, $(MAIN_TARGET)): $(DEST)/% :
	# Obtaining the initramfs-tools
	rm -rf ./initramfs-tools
	git clone --branch v0.120 https://salsa.debian.org/kernel-team/initramfs-tools.git ./initramfs-tools

	# Patch
	pushd ./initramfs-tools
	patch -p1 < ../loopback-file-system-support.patch

	# Build the package
	rm -f debian/*.debhelper.log
	dpkg-buildpackage -rfakeroot -b -us -uc -j$(SONIC_CONFIG_MAKE_JOBS)
	popd

	mv $* $(DEST)/
