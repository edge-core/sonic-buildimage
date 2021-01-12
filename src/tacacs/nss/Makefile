.ONESHELL:
SHELL = /bin/bash
.SHELLFLAGS += -e

MAIN_TARGET = libnss-tacplus_$(NSS_TACPLUS_VERSION)_$(CONFIGURED_ARCH).deb

GIT_APPLY = am
ifneq (,$(filter $(CONFIGURED_ARCH), armhf arm64))
# Workaround git am issue "Out of memory getdelim failed" 
GIT_APPLY = apply
endif

$(addprefix $(DEST)/, $(MAIN_TARGET)): $(DEST)/% :
	# Obtain libnss-tacplus
	rm -rf ./libnss-tacplus
	git clone https://github.com/daveolson53/libnss-tacplus.git
	pushd ./libnss-tacplus
	git checkout -f 19008ab

	# Apply patch
	git $(GIT_APPLY) ../0001-Modify-user-map-profile.patch
	git $(GIT_APPLY) ../0002-Enable-modifying-local-user-permission.patch
	git $(GIT_APPLY) ../0003-management-vrf-support.patch
	git $(GIT_APPLY) ../0004-Skip-accessing-tacacs-servers-for-local-non-tacacs-u.patch
	git $(GIT_APPLY) ../0005-libnss-Modify-parsing-of-IP-addr-and-port-number-str.patch

	dpkg-buildpackage -rfakeroot -b -us -uc -j$(SONIC_CONFIG_MAKE_JOBS) --admindir $(SONIC_DPKG_ADMINDIR)
	popd

	mv $(DERIVED_TARGETS) $* $(DEST)/

$(addprefix $(DEST)/, $(DERIVED_TARGETS)): $(DEST)/% : $(DEST)/$(MAIN_TARGET)
