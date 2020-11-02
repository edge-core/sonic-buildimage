.ONESHELL:
SHELL = /bin/bash
.SHELLFLAGS += -e

MAIN_TARGET = openssh-server_$(OPENSSH_VERSION)_$(CONFIGURED_ARCH).deb
DERIVED_TARGETS = openssh-server-dbgsym_$(OPENSSH_VERSION)_$(CONFIGURED_ARCH).deb

$(addprefix $(DEST)/, $(MAIN_TARGET)): $(DEST)/% :
	# Obtain openssh: https://salsa.debian.org/ssh-team/openssh/-/tree/debian/1%257.9p1-10+deb10u2
	rm -rf ./openssh-server
	git clone https://salsa.debian.org/ssh-team/openssh.git openssh-server
	pushd ./openssh-server

	# Check out tag: debian/1%7.9p1-10+deb10u2
	git checkout -b openssh-src -f 6d9ca74c48d9911342c6ca5aaac8a25974fa2619

	# Apply patch series
	stg init
	stg import -s ../patch/series

	# Build package
	sudo apt-get -y build-dep openssh
	dpkg-buildpackage -rfakeroot -b -us -uc -j$(SONIC_CONFIG_MAKE_JOBS)
	popd

	mv $(DERIVED_TARGETS) $* $(DEST)/

$(addprefix $(DEST)/, $(DERIVED_TARGETS)): $(DEST)/% : $(DEST)/$(MAIN_TARGET)
