.ONESHELL:
SHELL = /bin/bash
.SHELLFLAGS += -e

MAIN_TARGET = frr_$(FRR_VERSION)-1~sonic.debian8+1_amd64.deb

$(addprefix $(DEST)/, $(MAIN_TARGET)): $(DEST)/% :

	# Build the package
	pushd ./frr

	# This could very well be tools/tarsource.sh -V -e sonic
	tools/tarsource.sh -V
	# This is a no-op but here in case the changelog stops being a symlink
	debchange -b -v $(FRR_VERSION)-1~sonic.debian8+1 'SONiC FRR debian package build'
	dpkg-buildpackage -rfakeroot -b -us -uc -Ppkg.frr.nortrlib
	cd ..
	mv frr_$(FRR_VERSION)-*_amd64.deb frr_$(FRR_VERSION)-1~sonic.debian8+1_amd64.deb
	mv $* $(DEST)/

	popd

