.ONESHELL:
SHELL = /bin/bash
.SHELLFLAGS += -e

MAIN_TARGET = $(HSFLOWD)
DERIVED_TARGET = $(HSFLOWD_DBG)

$(addprefix $(DEST)/, $(MAIN_TARGET)): $(DEST)/% :
	rm -fr ./host-sflow
	git clone https://github.com/sflow/host-sflow

	pushd ./host-sflow
	git checkout -b sflow tags/v2.0.26-4

        # Apply patch series
	stg init
	stg import -s ../patch/series

	mkdir -p debian
	cp -r DEBIAN_build/* debian
	chmod u+x debian/rules
	sed -i -e s/_VERSION_/$(HSFLOWD_VERSION)-$(HSFLOWD_SUBVERSION)/g debian/changelog

	dpkg-buildpackage -rfakeroot -b -us -uc -j$(SONIC_CONFIG_MAKE_JOBS) --buildinfo-option=-u. --changes-option=-u.

	mv $(DERIVED_TARGET) $* $(DEST)/
	popd

$(addprefix $(DEST)/, $(DERIVED_TARGET)): $(DEST)/% : $(DEST)/$(MAIN_TARGET)
