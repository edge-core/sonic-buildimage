.ONESHELL:
SHELL = /bin/bash
.SHELLFLAGS += -e

MAIN_TARGET = libnss-tacplus_$(NSS_TACPLUS_VERSION)_amd64.deb

$(addprefix $(DEST)/, $(MAIN_TARGET)): $(DEST)/% :
	# Obtain libnss-tacplus
	rm -rf ./libnss-tacplus
	git clone https://github.com/daveolson53/libnss-tacplus.git
	pushd ./libnss-tacplus
	git checkout -f 19008ab

	# Apply patch
	git am ../0001-Modify-user-map-profile.patch
	git am ../0002-Enable-modifying-local-user-permission.patch
	git am ../0003-management-vrf-support.patch
	git am ../0004-Skip-accessing-tacacs-servers-for-local-non-tacacs-u.patch
	git am ../0005-libnss-Modify-parsing-of-IP-addr-and-port-number-str.patch

	dpkg-buildpackage -rfakeroot -b -us -uc -j$(SONIC_CONFIG_MAKE_JOBS) --admindir $(SONIC_DPKG_ADMINDIR)
	popd

	mv $(DERIVED_TARGETS) $* $(DEST)/

$(addprefix $(DEST)/, $(DERIVED_TARGETS)): $(DEST)/% : $(DEST)/$(MAIN_TARGET)
