.ONESHELL:
SHELL = /bin/bash
.SHELLFLAGS += -e

MAIN_TARGET = libteam5_$(LIBTEAM_VERSION)_amd64.deb
DERIVED_TARGETS = libteam-dev_$(LIBTEAM_VERSION)_amd64.deb \
		  libteamdctl0_$(LIBTEAM_VERSION)_amd64.deb \
		  libteam-utils_$(LIBTEAM_VERSION)_amd64.deb

$(addprefix $(DEST)/, $(MAIN_TARGET)): $(DEST)/% :
	# Obtain libteam
	rm -rf ./libteam
	git clone https://github.com/jpirko/libteam.git
	pushd ./libteam
	git checkout -f v1.26

	# Apply patch
	git apply ../0001-libteam-Add-team_get_port_enabled-function.patch
	git apply ../0002-libteam-Temporarily-remove-redundant-debug-mes.patch
	git apply ../0003-teamd-lacp-runner-will-send-lacp-update-right-after-.patch
	git apply ../0004-libteam-Add-lacp-fallback-support-for-single-member-.patch
	popd

	# Obtain debian packaging
	git clone https://salsa.debian.org/debian/libteam.git tmp
	pushd ./tmp
	git checkout -f da006f2 # v1.26
	popd

	mv tmp/debian libteam/
	rm -rf tmp
	pushd ./libteam
	dpkg-buildpackage -rfakeroot -b -us -uc -j$(SONIC_CONFIG_MAKE_JOBS)
	popd

	mv $(DERIVED_TARGETS) $* $(DEST)/

$(addprefix $(DEST)/, $(DERIVED_TARGETS)): $(DEST)/% : $(DEST)/$(MAIN_TARGET)
