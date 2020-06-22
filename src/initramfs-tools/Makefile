.ONESHELL:
SHELL = /bin/bash
.SHELLFLAGS += -e

MAIN_TARGET = initramfs-tools_$(INITRAMFS_TOOLS_VERSION)_all.deb
DERIVED_TARGETS = initramfs-tools-core_$(INITRAMFS_TOOLS_VERSION)_all.deb

INITRAMFS_TOOLS_REVISION = 40e544e13611c1b2690eb99a8096fc16c1b9c74e

$(addprefix $(DEST)/, $(MAIN_TARGET)): $(DEST)/% :
	# Obtaining the initramfs-tools
	rm -rf ./initramfs-tools
	git clone --branch v0.133 https://salsa.debian.org/kernel-team/initramfs-tools.git ./initramfs-tools

	# Patch
	pushd ./initramfs-tools
	git checkout $(INITRAMFS_TOOLS_REVISION)
	QUILT_PATCHES=.. quilt push -a

	# Build the package
	rm -f debian/*.debhelper.log
	dpkg-buildpackage -rfakeroot -b -us -uc -j$(SONIC_CONFIG_MAKE_JOBS)
	popd

	mv $(DERIVED_TARGETS) $* $(DEST)/

$(addprefix $(DEST)/, $(DERIVED_TARGETS)): $(DEST)/% : $(DEST)/$(MAIN_TARGET)
