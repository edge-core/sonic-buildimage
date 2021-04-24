.ONESHELL:
SHELL = /bin/bash
.SHELLFLAGS += -e

MAIN_TARGET = libnss-radius_$(NSS_RADIUS_VERSION)_amd64.deb

$(addprefix $(DEST)/, $(MAIN_TARGET)): $(DEST)/% :
	pushd ./libnss-radius

	make clean
	-rm -rf debian
	-rm -rf patches
	cp -r ../debian .
	cp -r ../patches .

	# Apply patch (if any)

	dpkg-buildpackage -rfakeroot -b -us -uc
	popd

	mv $(DERIVED_TARGETS) $* $(DEST)/

$(addprefix $(DEST)/, $(DERIVED_TARGETS)): $(DEST)/% : $(DEST)/$(MAIN_TARGET)
