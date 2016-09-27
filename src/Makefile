## TODO: if install dev package really happens, rebuild the depending project

.ONESHELL:
SHELL := /bin/bash

## Function: build_project, directory
## Build the project and save the .deb target in the same directory
## TRICK: clean dh state so it will force recreating .deb later
define build_project
	rm -f $(1)/debian/*.debhelper.log
	pushd $(1)
	[ ! -f ./autogen.sh ] || ./autogen.sh
	dpkg-buildpackage -rfakeroot -b -us -uc
	popd
endef

## Function: install_deb, debfile
install_deb = \
    [ -f $(1) ] && { sudo dpkg -i $(1) || sudo apt-get -y install -f; } || return 1;

## Rules
libnl-%.deb:
	pushd libnl3; ./build.sh; popd

quagga_0.99.24.1-2_amd64.deb:
	pushd quagga; ./build.sh; popd
	
redis-server_3.0.7-2_amd64.deb redis-tools_3.0.7-2_amd64.deb redis-sentinel_3.0.7-2_amd64.deb:
	pushd redis; ./build.sh; popd
	
libhiredis0.13_0.13.3-2_amd64.deb libhiredis-dbg_0.13.3-2_amd64.deb libhiredis-dev_0.13.3-2_amd64.deb: redis-server_3.0.7-2_amd64.deb redis-tools_3.0.7-2_amd64.deb redis-sentinel_3.0.7-2_amd64.deb
	pushd hiredis; ./build.sh; popd

libswsscommon_1.0.0_amd64.deb libswsscommon-dev_1.0.0_amd64.deb: redis-server_3.0.7-2_amd64.deb redis-tools_3.0.7-2_amd64.deb libhiredis0.13_0.13.3-2_amd64.deb libhiredis-dev_0.13.3-2_amd64.deb
	$(foreach dep, $^, $(call install_deb, $(dep)))
	$(call build_project, sonic-swss-common)

brcm/syncd_1.0.0_amd64.deb brcm/libsairedis_1.0.0_amd64.deb brcm/libsairedis-dev_1.0.0_amd64.deb: libswsscommon_1.0.0_amd64.deb libswsscommon-dev_1.0.0_amd64.deb brcm-sdk/libopennsl_*_amd64.deb brcm-sdk/libsaibcm_1.0.2*_amd64.deb brcm-sdk/libsaibcm-dev_1.0.2*_amd64.deb
	$(foreach dep, $^, $(call install_deb, $(dep)))
	$(call build_project, sonic-sairedis)
	mkdir -p brcm
	cp syncd_1.0.0_amd64.deb libsairedis_1.0.0_amd64.deb libsairedis-dev_1.0.0_amd64.deb brcm/
	
mlnx/syncd_1.0.0_amd64.deb mlnx/libsairedis_1.0.0_amd64.deb mlnx/libsairedis-dev_1.0.0_amd64.deb: libswsscommon_1.0.0_amd64.deb libswsscommon-dev_1.0.0_amd64.deb mlnx-sdk/applibs_1.mlnx.4.2.2100_amd64.deb mlnx-sdk/*.deb
	$(foreach dep, $^, $(call install_deb, $(dep)))
	$(call build_project, sonic-sairedis)
	mkdir -p mlnx
	cp syncd_1.0.0_amd64.deb libsairedis_1.0.0_amd64.deb libsairedis-dev_1.0.0_amd64.deb mlnx/

cavm/syncd_1.0.0_amd64.deb cavm/libsairedis_1.0.0_amd64.deb cavm/libsairedis-dev_1.0.0_amd64.deb: libswsscommon_1.0.0_amd64.deb libswsscommon-dev_1.0.0_amd64.deb cavm-sdk/libsai.deb cavm-sdk/xp-tools.deb cavm-sdk/xpshell.deb
	$(foreach dep, $^, $(call install_deb, $(dep)))
	$(call build_project, sonic-sairedis)
	mkdir -p cavm
	cp syncd_1.0.0_amd64.deb libsairedis_1.0.0_amd64.deb libsairedis-dev_1.0.0_amd64.deb cavm/
	
## Note: fpmsyncd is one implicit target
brcm/swss_1.0.0_amd64.deb brcm/intfsyncd brcm/neighsyncd brcm/orchagent brcm/portsyncd brcm/routeresync brcm/swssconfig: brcm/syncd_1.0.0_amd64.deb brcm/libsairedis_1.0.0_amd64.deb brcm/libsairedis-dev_1.0.0_amd64.deb
	$(foreach dep, $^, $(call install_deb, $(dep)))
	$(call build_project, sonic-swss)
	cp swss_1.0.0_amd64.deb brcm/
	cp sonic-swss/debian/swss/usr/bin/fpmsyncd .

## Note: fpmsyncd is one implicit target
mlnx/swss_1.0.0_amd64.deb mlnx/intfsyncd mlnx/neighsyncd mlnx/orchagent mlnx/portsyncd mlnx/routeresync mlnx/swssconfig: mlnx/syncd_1.0.0_amd64.deb mlnx/libsairedis_1.0.0_amd64.deb mlnx/libsairedis-dev_1.0.0_amd64.deb
	$(foreach dep, $^, $(call install_deb, $(dep)))
	$(call build_project, sonic-swss)
	cp swss_1.0.0_amd64.deb mlnx/
	cp sonic-swss/debian/swss/usr/bin/fpmsyncd .

## Note: fpmsyncd is one implicit target
cavm/swss_1.0.0_amd64.deb cavm/intfsyncd cavm/neighsyncd cavm/orchagent cavm/portsyncd cavm/routeresync cavm/swssconfig: cavm/syncd_1.0.0_amd64.deb cavm/libsairedis_1.0.0_amd64.deb cavm/libsairedis-dev_1.0.0_amd64.deb
	$(foreach dep, $^, $(call install_deb, $(dep)))
	$(call build_project, sonic-swss)
	cp swss_1.0.0_amd64.deb cavm/
	cp sonic-swss/debian/swss/usr/bin/fpmsyncd .
	
$(addprefix sonic-linux-kernel/,linux-headers-3.16.0-4-amd64_3.16.7-ckt11-2+acs8u2_amd64.deb linux-headers-3.16.0-4-common_3.16.7-ckt11-2+acs8u2_amd64.deb linux-image-3.16.0-4-amd64-dbg_3.16.7-ckt11-2+acs8u2_amd64.deb linux-image-3.16.0-4-amd64_3.16.7-ckt11-2+acs8u2_amd64.deb xen-linux-system-3.16.0-4-amd64_3.16.7-ckt11-2+acs8u2_amd64.deb):
	pushd sonic-linux-kernel; sudo ./build.sh; popd

initramfs-tools/initramfs-tools_0.120_all.deb:
	pushd initramfs-tools; ./build.sh; popd
