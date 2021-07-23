.ONESHELL:
SHELL = /bin/bash
.SHELLFLAGS += -e

MAIN_TARGET = openssh-server_$(OPENSSH_VERSION)_$(CONFIGURED_ARCH).deb
DERIVED_TARGETS = openssh-server-dbgsym_$(OPENSSH_VERSION)_$(CONFIGURED_ARCH).deb

$(addprefix $(DEST)/, $(MAIN_TARGET)): $(DEST)/% :
	# Obtain openssh: https://salsa.debian.org/ssh-team/openssh/-/tree/debian/1%258.4p1-5
	rm -rf ./openssh-server
	git clone https://salsa.debian.org/ssh-team/openssh.git openssh-server
	pushd ./openssh-server

	# Check out tag: debian/1%8.4p1-5
	git checkout -b openssh-src -f debian/1\%$(OPENSSH_VERSION)

	# Apply patch series
	stg init
	stg import -s ../patch/series

	# Build package
	dpkg-buildpackage -rfakeroot -b -us -uc -j$(SONIC_CONFIG_MAKE_JOBS) --admindir $(SONIC_DPKG_ADMINDIR)
	popd

	mv $(DERIVED_TARGETS) $* $(DEST)/

$(addprefix $(DEST)/, $(DERIVED_TARGETS)): $(DEST)/% : $(DEST)/$(MAIN_TARGET)
