.ONESHELL:
SHELL = /bin/bash
.SHELLFLAGS += -e

MAIN_TARGET = $(KDUMP_TOOLS)

$(addprefix $(DEST)/, $(MAIN_TARGET)): $(DEST)/% :
	# Remove any stale files
	rm -rf ./makedumpfile_$(KDUMP_TOOLS_VERSION_BASE).orig.tar.gz ./makedumpfile_$(KDUMP_TOOLS_VERSION).debian.tar.xz
	rm -rf ./makedumpfile-$(KDUMP_TOOLS_VERSION_BASE)

	# Get makedumpfile release
	wget http://deb.debian.org/debian/pool/main/m/makedumpfile/makedumpfile_$(KDUMP_TOOLS_VERSION_BASE).orig.tar.gz
	wget http://deb.debian.org/debian/pool/main/m/makedumpfile/makedumpfile_$(KDUMP_TOOLS_VERSION).debian.tar.xz
	tar -f makedumpfile_$(KDUMP_TOOLS_VERSION_BASE).orig.tar.gz -x
	pushd ./makedumpfile-$(KDUMP_TOOLS_VERSION_BASE)
	tar -f ../makedumpfile_$(KDUMP_TOOLS_VERSION).debian.tar.xz -x

	git init
	git add -f *
	git commit -m "unmodified kdump-tools source"

	# Apply patches
	stg init
	stg import -s ../patch/series

	# Build source and Debian packages
	fakeroot debian/rules binary-indep
	popd

	# Move the newly-built .deb packages to the destination directory
	mv $* $(DEST)/
