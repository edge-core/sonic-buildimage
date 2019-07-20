.ONESHELL:
SHELL = /bin/bash
.SHELLFLAGS += -e

MAIN_TARGET = $(IFUPDOWN2)

$(addprefix $(DEST)/, $(MAIN_TARGET)): $(DEST)/% :
	# Remove any stale files
	rm -rf ./ifupdown2-$(IFUPDOWN2_VERSION) ./$(IFUPDOWN2_VERSION).tar.gz

	# Get ifupdown2 release
	wget --no-check-certificate https://github.com/CumulusNetworks/ifupdown2/archive/$(IFUPDOWN2_VERSION).tar.gz
	tar -z -f $(IFUPDOWN2_VERSION).tar.gz -x
	pushd ./ifupdown2-$(IFUPDOWN2_VERSION)

	# Build source and Debian packages
	dpkg-buildpackage -rfakeroot -b -us -uc -j$(SONIC_CONFIG_MAKE_JOBS)
	popd

	# Move the newly-built .deb packages to the destination directory
	mv $* $(DEST)/
