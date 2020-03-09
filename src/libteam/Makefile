.ONESHELL:
SHELL = /bin/bash
.SHELLFLAGS += -e

MAIN_TARGET = libteam5_$(LIBTEAM_VERSION)_$(CONFIGURED_ARCH).deb
DERIVED_TARGETS = libteam-dev_$(LIBTEAM_VERSION)_$(CONFIGURED_ARCH).deb \
		  libteamdctl0_$(LIBTEAM_VERSION)_$(CONFIGURED_ARCH).deb \
		  libteam-utils_$(LIBTEAM_VERSION)_$(CONFIGURED_ARCH).deb \
		  libteam5-dbgsym_$(LIBTEAM_VERSION)_$(CONFIGURED_ARCH).deb \
		  libteamdctl0-dbgsym_$(LIBTEAM_VERSION)_$(CONFIGURED_ARCH).deb \
		  libteam-utils-dbgsym_$(LIBTEAM_VERSION)_$(CONFIGURED_ARCH).deb

$(addprefix $(DEST)/, $(MAIN_TARGET)): $(DEST)/% :
	# Obtain libteam
	rm -rf ./libteam
	git clone https://github.com/jpirko/libteam.git
	pushd ./libteam
	git checkout -b teamd -f c7237377dead39ae4a711297203bacf7edb9fa41

	# Apply patch series
	stg init
	stg import -s ../patch/series
	popd

	# Obtain debian packaging
	git clone https://salsa.debian.org/debian/libteam.git tmp
	pushd ./tmp
	git checkout -f debian/1.30-1
	popd

	mv tmp/debian libteam/
	rm -rf tmp
	pushd ./libteam
	dpkg-buildpackage -rfakeroot -b -us -uc -j$(SONIC_CONFIG_MAKE_JOBS)
	popd

	mv $(DERIVED_TARGETS) $* $(DEST)/

$(addprefix $(DEST)/, $(DERIVED_TARGETS)): $(DEST)/% : $(DEST)/$(MAIN_TARGET)
