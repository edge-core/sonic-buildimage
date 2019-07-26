SHELL = /bin/bash
.ONESHELL:
.SHELLFLAGS += -e

MAIN_TARGET = bash_$(BASH_VERSION_FULL)_$(CONFIGURED_ARCH).deb

$(addprefix $(DEST)/, $(MAIN_TARGET)): $(DEST)/% :
	rm -rf bash-$(BASH_VERSION_MAJOR)

	dget -u https://launchpad.net/debian/+archive/primary/+sourcefiles/bash/$(BASH_VERSION_FULL)/bash_$(BASH_VERSION_FULL).dsc

	pushd bash-$(BASH_VERSION_MAJOR)
	DEB_BUILD_OPTIONS=nocheck dpkg-buildpackage -us -uc -b -j$(SONIC_CONFIG_MAKE_JOBS)
	popd

	mv $* $(DEST)/
