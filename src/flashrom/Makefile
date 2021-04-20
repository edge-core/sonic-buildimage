SHELL = /bin/bash
.ONESHELL:
.SHELLFLAGS += -e


MAIN_TARGET = flashrom_$(FLASHROM_VERSION_FULL)_$(CONFIGURED_ARCH).deb

$(addprefix $(DEST)/, $(MAIN_TARGET)): $(DEST)/% :
	rm -rf ./flashrom-$(FLASHROM_VERSION_FULL)
	# Obtain flashrom
	git clone https://github.com/flashrom/flashrom.git flashrom-$(FLASHROM_VERSION_FULL)
	pushd ./flashrom-$(FLASHROM_VERSION_FULL)

	# Check out tag: tags/0.9.7
	git checkout -b flashrom-src tags/$(FLASHROM_VERSION_FULL)

	# Apply patch series
	stg init
	stg import -s ../patch/series

	# Build package
	dpkg-buildpackage -rfakeroot -b -us -uc -j$(SONIC_CONFIG_MAKE_JOBS)
	popd

	mv $* $(DEST)/
