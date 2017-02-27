.ONESHELL:
SHELL = /bin/bash
.SHELLFLAGS += -e

MAIN_TARGET = sonic-device-data_$(SONIC_DEVICE_DATA_VERSION_FULL)_all.deb

$(addprefix $(DEST)/, $(MAIN_TARGET)): $(DEST)/% :
	pushd ./src

	# Remove any stale data
	rm -rf ./device

	# Create a new dir and copy all ONIE-platform-string-named dirs into it
	mkdir ./device
	cp -r ../../../device/*/* ./device/

	# Build the package
	dpkg-buildpackage -rfakeroot -b -us -uc

	popd

	mv $* $(DEST)/
