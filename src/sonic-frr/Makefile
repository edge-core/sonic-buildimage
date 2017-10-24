.ONESHELL:
SHELL = /bin/bash
.SHELLFLAGS += -e

MAIN_TARGET = frr_$(FRR_VERSION)_amd64.deb

$(addprefix $(DEST)/, $(MAIN_TARGET)): $(DEST)/% :
        # Replacing frr's rules/install files with SONiC's own versions to activate
        # specific knobs and adjust install process to address SONiC's needs.
	cp sonic_frr.rules frr/debian/rules
	cp sonic_frr.install frr/debian/frr.install

        # Build the package
	pushd ./frr
	rm -f debian/*.debhelper.log
	dpkg-buildpackage -rfakeroot -b -us -uc
	popd

	mv $* $(DEST)/
