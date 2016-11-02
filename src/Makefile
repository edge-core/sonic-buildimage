## TODO: if install dev package really happens, rebuild the depending project

.ONESHELL:
SHELL := /bin/bash

REDIS_VERSION=3.2.4-1~bpo8+1_amd64

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

libteam5_1.26-1_amd64.deb libteam-dev_1.26-1_amd64.deb libteam-utils_1.26-1_amd64.deb libteamdctl0_1.26-1_amd64.deb: libnl-%.deb
	pushd libteam; ./build.sh; popd

redis-sentinel_$(REDIS_VERSION).deb redis-server_$(REDIS_VERSION).deb redis-tools_$(REDIS_VERSION).deb:
	pushd redis; ./build.sh; popd
	
libhiredis0.13_0.13.3-2_amd64.deb libhiredis-dbg_0.13.3-2_amd64.deb libhiredis-dev_0.13.3-2_amd64.deb: redis-server_$(REDIS_VERSION).deb redis-tools_$(REDIS_VERSION).deb redis-sentinel_$(REDIS_VERSION).deb
	pushd hiredis; ./build.sh; popd

libthrift-0.9.3_0.9.3-2_amd64.deb libthrift-dev_0.9.3-2_amd64.deb python-thrift_0.9.3-2_amd64.deb thrift-compiler_0.9.3-2_amd64.deb:
	pushd thrift; ./build.sh; popd

p4-bmv2_1.0.0_amd64.deb: thrift-compiler_0.9.3-2_amd64.deb python-thrift_0.9.3-2_amd64.deb libthrift-0.9.3_0.9.3-2_amd64.deb libthrift-dev_0.9.3-2_amd64.deb
	$(foreach dep, $^, $(call install_deb, $(dep)))
	pushd p4-bmv2; ./build.sh; popd

kernel-mft-dkms_4.5.0-3.16.0-4-amd64_all.deb mft-4.5.0-31.amd64.deb:
	pushd mft; ./build.sh; popd

python-p4-hlir_0.9.36-1_all.deb:
	pushd p4-hlir; ./build.sh; popd

python-p4c-bm_1.0.0-5415c416-1_all.deb: python-tenjin_1.1.1-1_all.deb python-p4-hlir_0.9.36-1_all.deb
	$(foreach dep, $^, $(call install_deb, $(dep)))
	pushd p4c-bm; ./build.sh; popd

python-tenjin_1.1.1-1_all.deb:
	pushd tenjin; ./build.sh; popd

p4-switch_1.0.0_amd64.deb: thrift-compiler_0.9.3-2_amd64.deb python-thrift_0.9.3-2_amd64.deb libthrift-0.9.3_0.9.3-2_amd64.deb libthrift-dev_0.9.3-2_amd64.deb python-p4-hlir_0.9.36-1_all.deb python-tenjin_1.1.1-1_all.deb python-p4c-bm_1.0.0-5415c416-1_all.deb p4-bmv2_1.0.0_amd64.deb 
	$(foreach dep, $^, $(call install_deb, $(dep)))
	pushd p4-switch; ./build.sh; popd
	
quagga_0.99.24.1-2.1_amd64.deb:
	$(call build_project, sonic-quagga)
	
libswsscommon_1.0.0_amd64.deb libswsscommon-dev_1.0.0_amd64.deb: redis-server_$(REDIS_VERSION).deb redis-tools_$(REDIS_VERSION).deb libhiredis0.13_0.13.3-2_amd64.deb libhiredis-dev_0.13.3-2_amd64.deb
	$(foreach dep, $^, $(call install_deb, $(dep)))
	$(call build_project, sonic-swss-common)

brcm/syncd_1.0.0_amd64.deb brcm/libsairedis_1.0.0_amd64.deb brcm/libsairedis-dev_1.0.0_amd64.deb brcm/libsaimetadata_1.0.0_amd64.deb brcm/libsaimetadata-dev_1.0.0_amd64.deb: libswsscommon_1.0.0_amd64.deb libswsscommon-dev_1.0.0_amd64.deb brcm-sdk/libopennsl_*_amd64.deb brcm-sdk/libsaibcm_1.0.2*_amd64.deb brcm-sdk/libsaibcm-dev_1.0.2*_amd64.deb
	$(foreach dep, $^, $(call install_deb, $(dep)))
	$(call build_project, sonic-sairedis)
	mkdir -p brcm
	cp syncd_1.0.0_amd64.deb libsairedis_1.0.0_amd64.deb libsairedis-dev_1.0.0_amd64.deb libsaimetadata_1.0.0_amd64.deb libsaimetadata-dev_1.0.0_amd64.deb brcm/
	
mlnx/syncd_1.0.0_amd64.deb mlnx/libsairedis_1.0.0_amd64.deb mlnx/libsairedis-dev_1.0.0_amd64.deb mlnx/libsaimetadata_1.0.0_amd64.deb mlnx/libsaimetadata-dev_1.0.0_amd64.deb: libswsscommon_1.0.0_amd64.deb libswsscommon-dev_1.0.0_amd64.deb mlnx-sdk/applibs_1.mlnx.4.2.2100_amd64.deb mlnx-sdk/*.deb
	$(foreach dep, $^, $(call install_deb, $(dep)))
	$(call build_project, sonic-sairedis)
	mkdir -p mlnx
	cp syncd_1.0.0_amd64.deb libsairedis_1.0.0_amd64.deb libsairedis-dev_1.0.0_amd64.deb libsaimetadata_1.0.0_amd64.deb libsaimetadata-dev_1.0.0_amd64.deb mlnx/

cavm/syncd_1.0.0_amd64.deb cavm/libsairedis_1.0.0_amd64.deb cavm/libsairedis-dev_1.0.0_amd64.deb cavm/libsaimetadata_1.0.0_amd64.deb cavm/libsaimetadata-dev_1.0.0_amd64.deb: libswsscommon_1.0.0_amd64.deb libswsscommon-dev_1.0.0_amd64.deb cavm-sdk/libsai.deb cavm-sdk/xp-tools.deb cavm-sdk/xpshell.deb
	$(foreach dep, $^, $(call install_deb, $(dep)))
	$(call build_project, sonic-sairedis)
	mkdir -p cavm
	cp syncd_1.0.0_amd64.deb libsairedis_1.0.0_amd64.deb libsairedis-dev_1.0.0_amd64.deb libsaimetadata_1.0.0_amd64.deb libsaimetadata-dev_1.0.0_amd64.deb cavm/
	
p4/syncd_1.0.0_amd64.deb p4/libsairedis_1.0.0_amd64.deb p4/libsairedis-dev_1.0.0_amd64.deb p4/libsaimetadata_1.0.0_amd64.deb p4/libsaimetadata-dev_1.0.0_amd64.deb: libswsscommon_1.0.0_amd64.deb libswsscommon-dev_1.0.0_amd64.deb p4-switch_1.0.0_amd64.deb p4-bmv2_1.0.0_amd64.deb libthrift-0.9.3_0.9.3-2_amd64.deb
	$(foreach dep, $^, $(call install_deb, $(dep)))
	$(call build_project, sonic-sairedis)
	mkdir -p p4
	cp syncd_1.0.0_amd64.deb libsairedis_1.0.0_amd64.deb libsairedis-dev_1.0.0_amd64.deb libsaimetadata_1.0.0_amd64.deb libsaimetadata-dev_1.0.0_amd64.deb p4/

## Note: fpmsyncd and teamsyncd are two implicit targets
brcm/swss_1.0.0_amd64.deb: brcm/syncd_1.0.0_amd64.deb brcm/libsairedis_1.0.0_amd64.deb brcm/libsairedis-dev_1.0.0_amd64.deb brcm/libsaimetadata_1.0.0_amd64.deb brcm/libsaimetadata-dev_1.0.0_amd64.deb
	$(foreach dep, $^, $(call install_deb, $(dep)))
	$(call build_project, sonic-swss)
	cp swss_1.0.0_amd64.deb brcm/
	cp sonic-swss/debian/swss/usr/bin/fpmsyncd .
	cp sonic-swss/debian/swss/usr/bin/teamsyncd .

## Note: fpmsyncd and teamsyncd are two implicit targets
mlnx/swss_1.0.0_amd64.deb: mlnx/syncd_1.0.0_amd64.deb mlnx/libsairedis_1.0.0_amd64.deb mlnx/libsairedis-dev_1.0.0_amd64.deb mlnx/libsaimetadata_1.0.0_amd64.deb mlnx/libsaimetadata-dev_1.0.0_amd64.deb
	$(foreach dep, $^, $(call install_deb, $(dep)))
	$(call build_project, sonic-swss)
	cp swss_1.0.0_amd64.deb mlnx/
	cp sonic-swss/debian/swss/usr/bin/fpmsyncd .
	cp sonic-swss/debian/swss/usr/bin/teamsyncd .

## Note: fpmsyncd and teamsyncd are two implicit targets
cavm/swss_1.0.0_amd64.deb: cavm/syncd_1.0.0_amd64.deb cavm/libsairedis_1.0.0_amd64.deb cavm/libsairedis-dev_1.0.0_amd64.deb cavm/libsaimetadata_1.0.0_amd64.deb cavm/libsaimetadata-dev_1.0.0_amd64.deb
	$(foreach dep, $^, $(call install_deb, $(dep)))
	$(call build_project, sonic-swss)
	cp swss_1.0.0_amd64.deb cavm/
	cp sonic-swss/debian/swss/usr/bin/fpmsyncd .
	cp sonic-swss/debian/swss/usr/bin/teamsyncd .
	
p4/swss_1.0.0_amd64.deb: p4/syncd_1.0.0_amd64.deb p4/libsairedis_1.0.0_amd64.deb p4/libsairedis-dev_1.0.0_amd64.deb p4/libsaimetadata_1.0.0_amd64.deb p4/libsaimetadata-dev_1.0.0_amd64.deb
	$(foreach dep, $^, $(call install_deb, $(dep)))
	$(call build_project, sonic-swss)
	cp swss_1.0.0_amd64.deb p4/

$(addprefix sonic-linux-kernel/,linux-headers-3.16.0-4-amd64_3.16.7-ckt11-2+acs8u2_amd64.deb linux-headers-3.16.0-4-common_3.16.7-ckt11-2+acs8u2_amd64.deb linux-image-3.16.0-4-amd64-dbg_3.16.7-ckt11-2+acs8u2_amd64.deb linux-image-3.16.0-4-amd64_3.16.7-ckt11-2+acs8u2_amd64.deb xen-linux-system-3.16.0-4-amd64_3.16.7-ckt11-2+acs8u2_amd64.deb):
	pushd sonic-linux-kernel; sudo ./build.sh; popd

initramfs-tools/initramfs-tools_0.120_all.deb:
	pushd initramfs-tools; ./build.sh; popd
