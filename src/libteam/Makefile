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
	git checkout -b teamd -f v1.26

	# Apply patch series
	stg init
	stg import -s ../series
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
