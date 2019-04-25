.ONESHELL:
SHELL = /bin/bash
.SHELLFLAGS += -e

MAIN_TARGET = frr_$(FRR_VERSION)-1~sonic.debian9+1_amd64.deb
TOOLS_TARGET = frr-pythontools_$(FRR_VERSION)-1~sonic.debian9+1_amd64.deb
MAIN_TARGET_DBG = frr-dbgsym_$(FRR_VERSION)-1~sonic.debian9+1_amd64.deb
DERIVED_TARGET = $(TOOLS_TARGET) $(MAIN_TARGET_DBG)

$(addprefix $(DEST)/, $(MAIN_TARGET)): $(DEST)/% :

	# Build the package
	pushd ./frr

	# This could very well be tools/tarsource.sh -V -e sonic
	tools/tarsource.sh -V
	# This is a no-op but here in case the changelog stops being a symlink
	debchange -b -v $(FRR_VERSION)-1~sonic.debian9+1 'SONiC FRR debian package build'
	sudo apt-get -y install install-info
	dpkg-buildpackage -rfakeroot -b -us -uc -Ppkg.frr.nortrlib
	cd ..
	mv frr_$(FRR_VERSION)-*_amd64.deb $(MAIN_TARGET)
	mv frr-pythontools_$(FRR_VERSION)-*_all.deb $(TOOLS_TARGET)
	mv frr-dbgsym_$(FRR_VERSION)-*_amd64.deb $(MAIN_TARGET_DBG)
	mv $(DERIVED_TARGET) $* $(DEST)/

	popd

$(addprefix $(DEST)/, $(DERIVED_TARGET)): $(DEST)/% : $(DEST)/$(MAIN_TARGET)

