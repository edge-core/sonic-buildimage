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
	rm -rf ./libnl3-$(LIBNL3_VERSION_BASE)
	wget -O libnl3_$(LIBNL3_VERSION_BASE).orig.tar.gz -N "http://http.debian.net/debian/pool/main/libn/libnl3/libnl3_$(LIBNL3_VERSION_BASE).orig.tar.gz"
	wget -O libnl3_$(LIBNL3_VERSION).dsc -N "http://http.debian.net/debian/pool/main/libn/libnl3/libnl3_$(LIBNL3_VERSION).dsc"
	wget -O libnl3_$(LIBNL3_VERSION).debian.tar.xz -N "http://http.debian.net/debian/pool/main/libn/libnl3/libnl3_$(LIBNL3_VERSION).debian.tar.xz"
	dpkg-source -x libnl3_$(LIBNL3_VERSION).dsc

	pushd ./libnl3-$(LIBNL3_VERSION_BASE)
	dpkg-buildpackage -rfakeroot -b -us -uc -j$(SONIC_CONFIG_MAKE_JOBS)
	popd

	mv $(DERIVED_TARGETS) $* $(DEST)/

$(addprefix $(DEST)/, $(DERIVED_TARGETS)): $(DEST)/% : $(DEST)/$(MAIN_TARGET)
