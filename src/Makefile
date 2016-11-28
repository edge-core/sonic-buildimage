## TODO: if install dev package really happens, rebuild the depending project

.ONESHELL:
SHELL := /bin/bash

REDIS_VERSION=3.2.4-1~bpo8+1_amd64

LIBNL-DEBS=libnl-3-200_3.2.27-1_amd64.deb \
           libnl-3-dev_3.2.27-1_amd64.deb \
           libnl-genl-3-200_3.2.27-1_amd64.deb \
           libnl-genl-3-dev_3.2.27-1_amd64.deb \
           libnl-route-3-200_3.2.27-1_amd64.deb \
           libnl-route-3-dev_3.2.27-1_amd64.deb \
           libnl-nf-3-200_3.2.27-1_amd64.deb \
           libnl-nf-3-dev_3.2.27-1_amd64.deb \
           libnl-cli-3-200_3.2.27-1_amd64.deb \
           libnl-cli-3-dev_3.2.27-1_amd64.deb

LIBTEAM-DEBS=libteam5_1.26-1_amd64.deb \
             libteamdctl0_1.26-1_amd64.deb \
             libteam-dev_1.26-1_amd64.deb \
             libteam-utils_1.26-1_amd64.deb

MPDECIMAL_VER=2.4.2-1

MPDECIMAL-DEBS=libmpdec2_$(MPDECIMAL_VER)_amd64.deb \
               libmpdec-dev_$(MPDECIMAL_VER)_amd64.deb

PYTHON3_5_VER=3.5.2-8
               
PYTHON3_5-DEBS=libpython3.5-minimal_$(PYTHON3_5_VER)_amd64.deb \
               python3.5-minimal_$(PYTHON3_5_VER)_amd64.deb \
               libpython3.5-stdlib_$(PYTHON3_5_VER)_amd64.deb \
               python3.5_$(PYTHON3_5_VER)_amd64.deb

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

## Function: build_project_py2, directory
## Build the project and save the .deb target in the same directory
define build_project_py2
	pushd $(1)
	python2 setup.py bdist_wheel
	popd
endef

## Function: build_project_py3, directory
## Build the project and save the .deb target in the same directory
define build_project_py3
	pushd $(1)
	python3 setup.py bdist_wheel
	popd
endef

## Function: install_deb, debfile
install_deb = \
    [ -f $(1) ] && { sudo dpkg -i $(1) || sudo apt-get -y install -f; } || return 1;

## Function: install_py2, whlfile
install_py2 = \
    sudo pip install $(1)

## Function: install_py3, whlfile
install_py3 = \
    sudo pip3 install $(1)

## Rules
$(LIBNL-DEBS):
	pushd libnl3; ./build.sh; popd

$(LIBTEAM-DEBS): $(LIBNL-DEBS)
	$(foreach dep, $^, $(call install_deb, $(dep)))
	pushd libteam; ./build.sh; popd

$(MPDECIMAL-DEBS):
	pushd mpdecimal; ./build.sh; popd

$(PYTHON3_5-DEBS): $(MPDECIMAL-DEBS)
	$(foreach dep, $^, $(call install_deb, $(dep)))
	pushd python3.5; ./build.sh; popd

redis-sentinel_$(REDIS_VERSION).deb redis-server_$(REDIS_VERSION).deb redis-tools_$(REDIS_VERSION).deb:
	pushd redis; ./build.sh; popd

libhiredis0.13_0.13.3-2_amd64.deb libhiredis-dbg_0.13.3-2_amd64.deb libhiredis-dev_0.13.3-2_amd64.deb: redis-server_$(REDIS_VERSION).deb redis-tools_$(REDIS_VERSION).deb redis-sentinel_$(REDIS_VERSION).deb
	$(foreach dep, $^, $(call install_deb, $(dep)))
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

snmpd_5.7.3+dfsg-1.5_amd64.deb snmptrapd_5.7.3+dfsg-1.5_amd64.deb snmp_5.7.3+dfsg-1.5_amd64.deb libsnmp-base_5.7.3+dfsg-1.5_all.deb libsnmp30_5.7.3+dfsg-1.5_amd64.deb libsnmp30-dbg_5.7.3+dfsg-1.5_amd64.deb libsnmp-dev_5.7.3+dfsg-1.5_amd64.deb libsnmp-perl_5.7.3+dfsg-1.5_amd64.deb python-netsnmp_5.7.3+dfsg-1.5_amd64.deb tkmib_5.7.3+dfsg-1.5_all.deb:
	pushd snmpd; ./build.sh; popd

sswsdk-2.0.1-py2-none-any.whl:
	$(call build_project_py2, sonic-py-swsssdk)
	cp sonic-py-swsssdk/dist/$@ .

sswsdk-2.0.1-py3-none-any.whl:
	$(call build_project_py3, sonic-py-swsssdk)
	cp sonic-py-swsssdk/dist/$@ .

sonic_d-2.0.0-py2-none-any.whl: sswsdk-2.0.1-py2-none-any.whl
	$(foreach dep, $^, $(call install_py2, $(dep)))
	$(call build_project_py2, sonic-dbsyncd)
	cp sonic-dbsyncd/dist/$@ .

asyncsnmp-2.1.0-py3-none-any.whl: sswsdk-2.0.1-py3-none-any.whl
	$(foreach dep, $^, $(call install_py3, $(dep)))
	$(call build_project_py3, sonic-snmpagent)
	cp sonic-snmpagent/dist/$@ .

p4-switch_1.0.0_amd64.deb: thrift-compiler_0.9.3-2_amd64.deb python-thrift_0.9.3-2_amd64.deb libthrift-0.9.3_0.9.3-2_amd64.deb libthrift-dev_0.9.3-2_amd64.deb python-p4-hlir_0.9.36-1_all.deb python-tenjin_1.1.1-1_all.deb python-p4c-bm_1.0.0-5415c416-1_all.deb p4-bmv2_1.0.0_amd64.deb
	$(foreach dep, $^, $(call install_deb, $(dep)))
	pushd p4-switch; ./build.sh; popd

lldpd_0.9.5-0_amd64.deb liblldpctl-dev_0.9.5-0_amd64.deb:
	$(call build_project, lldpd)

quagga_0.99.24.1-2.1_amd64.deb:
	$(call build_project, sonic-quagga)

libswsscommon_1.0.0_amd64.deb libswsscommon-dev_1.0.0_amd64.deb: redis-server_$(REDIS_VERSION).deb redis-tools_$(REDIS_VERSION).deb libhiredis0.13_0.13.3-2_amd64.deb libhiredis-dev_0.13.3-2_amd64.deb $(LIBNL-DEBS)
	$(foreach dep, $^, $(call install_deb, $(dep)))
	$(call build_project, sonic-swss-common)

brcm/syncd_1.0.0_amd64.deb brcm/libsairedis_1.0.0_amd64.deb brcm/libsairedis-dev_1.0.0_amd64.deb brcm/libsaimetadata_1.0.0_amd64.deb brcm/libsaimetadata-dev_1.0.0_amd64.deb: libswsscommon_1.0.0_amd64.deb libswsscommon-dev_1.0.0_amd64.deb brcm-sdk/libopennsl_*_amd64.deb brcm-sdk/libsaibcm_1.0.2*_amd64.deb brcm-sdk/libsaibcm-dev_1.0.2*_amd64.deb
	$(foreach dep, $^, $(call install_deb, $(dep)))
	$(call build_project, sonic-sairedis)
	mkdir -p brcm
	cp syncd_1.0.0_amd64.deb libsairedis_1.0.0_amd64.deb libsairedis-dev_1.0.0_amd64.deb libsaimetadata_1.0.0_amd64.deb libsaimetadata-dev_1.0.0_amd64.deb brcm/

mlnx/syncd_1.0.0_amd64.deb mlnx/libsairedis_1.0.0_amd64.deb mlnx/libsairedis-dev_1.0.0_amd64.deb mlnx/libsaimetadata_1.0.0_amd64.deb mlnx/libsaimetadata-dev_1.0.0_amd64.deb: libswsscommon_1.0.0_amd64.deb libswsscommon-dev_1.0.0_amd64.deb mlnx-sdk/*.deb
	## Install applibs first for late depending packages
	$(call install_deb, mlnx-sdk/applibs_1.mlnx.*.deb)
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
brcm/swss_1.0.0_amd64.deb: brcm/syncd_1.0.0_amd64.deb brcm/libsairedis_1.0.0_amd64.deb brcm/libsairedis-dev_1.0.0_amd64.deb brcm/libsaimetadata_1.0.0_amd64.deb brcm/libsaimetadata-dev_1.0.0_amd64.deb $(LIBTEAM-DEBS) $(LIBNL-DEBS)
	$(foreach dep, $^, $(call install_deb, $(dep)))
	$(call build_project, sonic-swss)
	cp swss_1.0.0_amd64.deb brcm/
	cp sonic-swss/debian/swss/usr/bin/fpmsyncd .
	cp sonic-swss/debian/swss/usr/bin/teamsyncd .

## Note: fpmsyncd and teamsyncd are two implicit targets
mlnx/swss_1.0.0_amd64.deb: mlnx/syncd_1.0.0_amd64.deb mlnx/libsairedis_1.0.0_amd64.deb mlnx/libsairedis-dev_1.0.0_amd64.deb mlnx/libsaimetadata_1.0.0_amd64.deb mlnx/libsaimetadata-dev_1.0.0_amd64.deb $(LIBTEAM-DEBS) $(LIBNL-DEBS)
	$(foreach dep, $^, $(call install_deb, $(dep)))
	$(call build_project, sonic-swss)
	cp swss_1.0.0_amd64.deb mlnx/
	cp sonic-swss/debian/swss/usr/bin/fpmsyncd .
	cp sonic-swss/debian/swss/usr/bin/teamsyncd .

## Note: fpmsyncd and teamsyncd are two implicit targets
cavm/swss_1.0.0_amd64.deb: cavm/syncd_1.0.0_amd64.deb cavm/libsairedis_1.0.0_amd64.deb cavm/libsairedis-dev_1.0.0_amd64.deb cavm/libsaimetadata_1.0.0_amd64.deb cavm/libsaimetadata-dev_1.0.0_amd64.deb $(LIBTEAM-DEBS) $(LIBNL-DEBS)
	$(foreach dep, $^, $(call install_deb, $(dep)))
	$(call build_project, sonic-swss)
	cp swss_1.0.0_amd64.deb cavm/
	cp sonic-swss/debian/swss/usr/bin/fpmsyncd .
	cp sonic-swss/debian/swss/usr/bin/teamsyncd .

p4/swss_1.0.0_amd64.deb: p4/syncd_1.0.0_amd64.deb p4/libsairedis_1.0.0_amd64.deb p4/libsairedis-dev_1.0.0_amd64.deb p4/libsaimetadata_1.0.0_amd64.deb p4/libsaimetadata-dev_1.0.0_amd64.deb $(LIBTEAM-DEBS) $(LIBNL-DEBS)
	$(foreach dep, $^, $(call install_deb, $(dep)))
	$(call build_project, sonic-swss)
	cp swss_1.0.0_amd64.deb p4/

$(addprefix sonic-linux-kernel/,linux-headers-3.16.0-4-amd64_3.16.7-ckt11-2+acs8u2_amd64.deb linux-headers-3.16.0-4-common_3.16.7-ckt11-2+acs8u2_amd64.deb linux-image-3.16.0-4-amd64-dbg_3.16.7-ckt11-2+acs8u2_amd64.deb linux-image-3.16.0-4-amd64_3.16.7-ckt11-2+acs8u2_amd64.deb xen-linux-system-3.16.0-4-amd64_3.16.7-ckt11-2+acs8u2_amd64.deb):
	pushd sonic-linux-kernel; sudo ./build.sh; popd

initramfs-tools/initramfs-tools_0.120_all.deb:
	pushd initramfs-tools; ./build.sh; popd
