.ONESHELL:
SHELL = /bin/bash

MAIN_TARGET = sx-scew_1.mlnx.$(MLNX_SDK_DEB_VERSION)_amd64.deb
DERIVED_TARGETS = sx-scew-dev_1.mlnx.$(MLNX_SDK_DEB_VERSION)_amd64.deb \
				  sx-scew-dev-static_1.mlnx.$(MLNX_SDK_DEB_VERSION)_amd64.deb \
				  sx-scew-dbgsym_1.mlnx.$(MLNX_SDK_DEB_VERSION)_amd64.deb
PACKAGE_NAME = sx_scew

$(addprefix $(DEST)/, $(MAIN_TARGET)): $(DEST)/% :
	# get sources
	rm -rf $(PACKAGE_NAME)-$(MLNX_SDK_VERSION)-$(MLNX_SDK_ISSU_VERSION)

	wget -c $(MLNX_SDK_SOURCE_BASE_URL)/$(PACKAGE_NAME)-$(MLNX_SDK_VERSION)-$(MLNX_SDK_ISSU_VERSION).tar.gz -O - | tar -xz

	# build
	pushd $(PACKAGE_NAME)-$(MLNX_SDK_VERSION)-$(MLNX_SDK_ISSU_VERSION)

	if [ -f autogen.sh ]; then
		./autogen.sh
	fi

	debuild -b -us -uc -j$(SONIC_CONFIG_MAKE_JOBS)

	popd

	mv $(DERIVED_TARGETS) $* $(DEST)/

$(addprefix $(DEST)/, $(DERIVED_TARGETS)): $(DEST)/% : $(DEST)/$(MAIN_TARGET)
