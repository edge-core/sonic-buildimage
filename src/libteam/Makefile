.ONESHELL:
SHELL = /bin/bash
.SHELLFLAGS += -e

MAIN_TARGET = libteam5_$(LIBTEAM_VERSION)_amd64.deb
DERIVED_TARGETS = libteam-dev_$(LIBTEAM_VERSION)_amd64.deb \
		  libteamdctl0_$(LIBTEAM_VERSION)_amd64.deb \
		  libteam-utils_$(LIBTEAM_VERSION)_amd64.deb \
		  libteam5-dbgsym_$(LIBTEAM_VERSION)_amd64.deb \
		  libteamdctl0-dbgsym_$(LIBTEAM_VERSION)_amd64.deb \
		  libteam-utils-dbgsym_$(LIBTEAM_VERSION)_amd64.deb

$(addprefix $(DEST)/, $(MAIN_TARGET)): $(DEST)/% :
	# Obtain libteam
	rm -rf ./libteam
	git clone https://github.com/jpirko/libteam.git
	pushd ./libteam
	git checkout -b teamd -f 5c5e498bff9

	# Apply patch series
	stg init
	stg import -s ../patch/series
	popd

	# Obtain debian packaging
	git clone https://salsa.debian.org/debian/libteam.git tmp
	pushd ./tmp
	git checkout -f 7188c361  # v1.28-1
	popd

	mv tmp/debian libteam/
	rm -rf tmp
	pushd ./libteam
	dpkg-buildpackage -rfakeroot -b -us -uc -j$(SONIC_CONFIG_MAKE_JOBS)
	popd

	mv $(DERIVED_TARGETS) $* $(DEST)/

$(addprefix $(DEST)/, $(DERIVED_TARGETS)): $(DEST)/% : $(DEST)/$(MAIN_TARGET)
