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
	cp -r -L ../../../device/*/* ./device/

	# Create hwsku for virtual switch
	for d in `find -L ../../../device -maxdepth 3 -mindepth 3 -type d | grep -vE "(plugins|led-code)"`; do \
		cp -Lr $$d device/x86_64-kvm_x86_64-r0/ ; \
		cp ./sai.vs_profile device/x86_64-kvm_x86_64-r0/$$(basename $$d)/sai.profile; \
		grep -v ^# device/x86_64-kvm_x86_64-r0/$$(basename $$d)/port_config.ini | awk '{i=i+1;print "eth"i":"$$2}' > device/x86_64-kvm_x86_64-r0/$$(basename $$d)/lanemap.ini
	done;

	# Build the package
	dpkg-buildpackage -rfakeroot -b -us -uc

	popd

	mv $* $(DEST)/
