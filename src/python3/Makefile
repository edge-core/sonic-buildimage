.ONESHELL:
SHELL = /bin/bash
.SHELLFLAGS += -e

PYTHON_VER=3.6.0
PYTHON_DEB_VER=1
PYTHON_PNAME=python3.6

MAIN_TARGET = lib$(PYTHON_PNAME)-minimal_$(PYTHON_VER)-$(PYTHON_DEB_VER)_$(CONFIGURED_ARCH).deb
DERIVED_TARGETS = lib$(PYTHON_PNAME)-stdlib_$(PYTHON_VER)-$(PYTHON_DEB_VER)_$(CONFIGURED_ARCH).deb \
				  lib$(PYTHON_PNAME)_$(PYTHON_VER)-$(PYTHON_DEB_VER)_$(CONFIGURED_ARCH).deb \
				  $(PYTHON_PNAME)-minimal_$(PYTHON_VER)-$(PYTHON_DEB_VER)_$(CONFIGURED_ARCH).deb \
				  $(PYTHON_PNAME)_$(PYTHON_VER)-$(PYTHON_DEB_VER)_$(CONFIGURED_ARCH).deb \
				  lib$(PYTHON_PNAME)-dev_$(PYTHON_VER)-$(PYTHON_DEB_VER)_$(CONFIGURED_ARCH).deb
				  #$(PYTHON_PNAME)-dev_$(PYTHON_VER)-$(PYTHON_DEB_VER)_$(CONFIGURED_ARCH).deb

$(addprefix $(DEST)/, $(MAIN_TARGET)): $(DEST)/% :
	# Remove any stale files
	rm -rf $(PYTHON_PNAME)-$(PYTHON_VER)

	## Obtaining the python3
	wget 'https://sonicstorage.blob.core.windows.net/packages/$(PYTHON_PNAME)_$(PYTHON_VER).orig.tar.xz?sv=2015-04-05&sr=b&sig=d42Wh1CA9NZvlskhW4fpWcHVgc7N3IKhdFzyeO2zbRA%3D&se=2027-02-02T01%3A00%3A57Z&sp=r' -O $(PYTHON_PNAME)_$(PYTHON_VER).orig.tar.xz
	wget 'https://sonicstorage.blob.core.windows.net/packages/$(PYTHON_PNAME)_$(PYTHON_VER)-$(PYTHON_DEB_VER).debian.tar.xz?sv=2015-04-05&sr=b&sig=KLX9pMJ3zpQvGBo6ZjzoZXgooMJRUUwMx8ZaTJtywK0%3D&se=2027-02-02T00%3A59%3A34Z&sp=r' -O $(PYTHON_PNAME)_$(PYTHON_VER)-$(PYTHON_DEB_VER).debian.tar.xz
	wget 'https://sonicstorage.blob.core.windows.net/packages/$(PYTHON_PNAME)_$(PYTHON_VER)-$(PYTHON_DEB_VER).dsc?sv=2015-04-05&sr=b&sig=95s%2FC4vKY6bRKtkUTz%2BmHLqOllBOYbfP3zV5ayAuzSM%3D&se=2027-02-02T01%3A00%3A26Z&sp=r' -O $(PYTHON_PNAME)_$(PYTHON_VER)-$(PYTHON_DEB_VER).dsc

	## Build
	dpkg-source -x $(PYTHON_PNAME)_$(PYTHON_VER)-$(PYTHON_DEB_VER).dsc
	pushd $(PYTHON_PNAME)-$(PYTHON_VER)
	mk-build-deps

	# put a lock here because dpkg does not allow installing packages in parallel
	while true; do
	if mkdir $(DEST)/dpkg_lock &> /dev/null; then
	{ echo here && (sudo dpkg -i $(PYTHON_PNAME)-build-deps_$(PYTHON_VER)-$(PYTHON_DEB_VER)_$(CONFIGURED_ARCH).deb || sudo apt-get install -f) && rm -d $(DEST)/dpkg_lock && break; } || { rm -d $(DEST)/dpkg_lock && exit 1 ; }
	fi
	done

	dpkg-buildpackage -rfakeroot -us -uc -b -j$(SONIC_CONFIG_MAKE_JOBS)
	popd

	cp $(DERIVED_TARGETS) $* $(DEST)/

$(addprefix $(DEST)/, $(DERIVED_TARGETS)): $(DEST)/% : $(DEST)/$(MAIN_TARGET)
