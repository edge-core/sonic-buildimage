.ONESHELL:
SHELL = /bin/bash
.SHELLFLAGS += -e

MAIN_TARGET = libnl-3-200_$(LIBNL3_VERSION)_amd64.deb
DERIVED_TARGETS = libnl-3-dev_$(LIBNL3_VERSION)_amd64.deb \
		  libnl-genl-3-200_$(LIBNL3_VERSION)_amd64.deb \
		  libnl-genl-3-dev_$(LIBNL3_VERSION)_amd64.deb \
		  libnl-route-3-200_$(LIBNL3_VERSION)_amd64.deb \
		  libnl-route-3-dev_$(LIBNL3_VERSION)_amd64.deb  \
		  libnl-nf-3-200_$(LIBNL3_VERSION)_amd64.deb \
		  libnl-nf-3-dev_$(LIBNL3_VERSION)_amd64.deb \
		  libnl-cli-3-200_$(LIBNL3_VERSION)_amd64.deb \
		  libnl-cli-3-dev_$(LIBNL3_VERSION)_amd64.deb

$(addprefix $(DEST)/, $(MAIN_TARGET)): $(DEST)/% :
	# Obtaining the libnl3
	rm -rf ./libnl3
	git clone https://github.com/qiluo-msft/libnl3.git
	pushd ./libnl3
	git checkout -f b77c0e49cb

	# Patch
	export QUILT_PATCHES=debian/patches
	quilt push
	quilt push
	quilt push
	quilt push
	quilt push
	dpkg-buildpackage -rfakeroot -b -us -uc -j$(SONIC_CONFIG_MAKE_JOBS)
	popd

	mv $(DERIVED_TARGETS) $* $(DEST)/

$(addprefix $(DEST)/, $(DERIVED_TARGETS)): $(DEST)/% : $(DEST)/$(MAIN_TARGET)
