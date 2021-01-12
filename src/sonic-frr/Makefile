.ONESHELL:
SHELL = /bin/bash
.SHELLFLAGS += -e

MAIN_TARGET = frr_$(FRR_VERSION)-1~sonic.debian8+1_amd64.deb
DERIVED_TARGET = $(FRR_DBG)

$(addprefix $(DEST)/, $(MAIN_TARGET)): $(DEST)/% :

	# Build the package
	pushd ./frr

	# clean up the previous build
	rm -rf debian
	rm -f frr*.tar.gz
	rm -f frr*.tar.xz
	rm -f frr*.dsc

	# make a dist tarball
	./bootstrap.sh
	./configure
	make dist

	# Create backports debian sources
	cp -a debianpkg debian
	make -f debian/rules backports

	# new directory to build the package
	rm -rf frrpkg
	mkdir frrpkg
	cd frrpkg
	tar xf ../frr_*.orig.tar.gz
	cd frr*
	tar xf ../../frr_*sonic.debian8*.debian.tar.xz

	# build package
	dpkg-buildpackage -rfakeroot -b -us -uc -j$(SONIC_CONFIG_MAKE_JOBS) --admindir $(SONIC_DPKG_ADMINDIR)
	cd ..
	mv $(DERIVED_TARGET) $* $(DEST)/

	popd

$(addprefix $(DEST)/, $(DERIVED_TARGET)): $(DEST)/% : $(DEST)/$(MAIN_TARGET)
