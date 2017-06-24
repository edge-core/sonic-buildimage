.ONESHELL:
SHELL = /bin/bash
.SHELLFLAGS += -e

MAIN_TARGET = isc-dhcp-common_$(ISC_DHCP_VERSION)_amd64.deb
DERIVED_TARGETS = isc-dhcp-relay_$(ISC_DHCP_VERSION)_amd64.deb

$(addprefix $(DEST)/, $(MAIN_TARGET)): $(DEST)/% :
	# Remove any stale files
	rm -rf ./isc-dhcp

	# Clone isc-dhcp repo
	git clone git://anonscm.debian.org/pkg-dhcp/isc-dhcp.git
	pushd ./isc-dhcp
	git checkout -f debian/4.3.1-6
	popd

	# Apply patch
	patch -p1 < isc-dhcp-4.3.1_dhcrelay-custom-circuit_id-remote_id-and-bridge-iface-support.patch

	# Build source and Debian packages
	pushd ./isc-dhcp
	dpkg-buildpackage -rfakeroot -b -us -uc
	popd

	# Move the newly-built .deb packages to the destination directory
	mv $* $(DERIVED_TARGETS) $(DEST)/

$(addprefix $(DEST)/, $(DERIVED_TARGETS)): $(DEST)/% : $(DEST)/$(MAIN_TARGET)

