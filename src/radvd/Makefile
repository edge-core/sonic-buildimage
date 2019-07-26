.ONESHELL:
SHELL = /bin/bash
.SHELLFLAGS += -e

MAIN_TARGET = radvd_$(RADVD_VERSION)_$(CONFIGURED_ARCH).deb
DERIVED_TARGETS = radvd-dbgsym_$(RADVD_VERSION)_$(CONFIGURED_ARCH).deb

$(addprefix $(DEST)/, $(MAIN_TARGET)): $(DEST)/% :
	# Remove any stale files
	rm -rf ./radvd

	# Clone radvd repo
	git clone https://salsa.debian.org/debian/radvd.git
	pushd ./radvd

	# Reset HEAD to the commit of the proper tag
	# NOTE: Using "git checkout <tag_name>" here detaches our HEAD,
	# which stg doesn't like, so we use this method instead
	# NOTE 1: For some reason, tags in the Debian radvd repo are prefixed with "1%"
	# NOTE 2: "~" in version string is replaced by "_" in branch name
	git reset --hard debian/1\%$(subst ~,_,$(RADVD_VERSION))

	# Apply patches
	stg init
	stg import -s ../patch/series

	# Build source and Debian packages
	dpkg-buildpackage -rfakeroot -b -us -uc -j$(SONIC_CONFIG_MAKE_JOBS)
	popd

	# Move the newly-built .deb package to the destination directory
	mv $(DERIVED_TARGETS) $* $(DEST)/
