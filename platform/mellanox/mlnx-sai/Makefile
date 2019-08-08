.ONESHELL:
SHELL = /bin/bash
.SHELLFLAGS += -e

MAIN_TARGET = mlnx-sai_1.mlnx.$(MLNX_SAI_VERSION)_amd64.deb
DERIVED_TARGETS = mlnx-sai-dbgsym_1.mlnx.$(MLNX_SAI_VERSION)_amd64.deb

$(addprefix $(DEST)/, $(MAIN_TARGET)): $(DEST)/% :
	pushd SAI-Implementation
	pushd mlnx_sai

	chmod a+x autogen.sh
	debuild -e 'make_extra_flags="DEFS=-DACS_OS"' -us -uc -d -b
	popd

	mv $(DERIVED_TARGETS) $* $(DEST)/
	popd
