.ONESHELL:
SHELL = /bin/bash
.SHELLFLAGS += -e

MAIN_TARGET = $(OPENSSH_SERVER)
DERIVED_TARGETS = $(OPENSSH_SERVER_DBG)

$(addprefix $(DEST)/, $(MAIN_TARGET)): $(DEST)/% :
	# Remove stale files
	rm -rf ./openssh-$(OPENSSH_VERSION)

	dget https://deb.debian.org/debian/pool/main/o/openssh/openssh_$(OPENSSH_VERSION_FULL).dsc
	pushd ./openssh-$(OPENSSH_VERSION)

	git init
	git add -f *
	git commit -qm "initial commit"

	# Apply patch series
	stg init
	stg import -s ../patch/series

	# Build package
	dpkg-buildpackage -rfakeroot -b -us -uc -j$(SONIC_CONFIG_MAKE_JOBS) --admindir $(SONIC_DPKG_ADMINDIR)
	popd

	mv $(DERIVED_TARGETS) $* $(DEST)/

$(addprefix $(DEST)/, $(DERIVED_TARGETS)): $(DEST)/% : $(DEST)/$(MAIN_TARGET)
