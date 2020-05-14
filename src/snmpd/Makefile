SHELL = /bin/bash
.ONESHELL:
.SHELLFLAGS += -e

MAIN_TARGET = libsnmp-base_$(SNMPD_VERSION_FULL)_all.deb
DERIVED_TARGETS = snmptrapd_$(SNMPD_VERSION_FULL)_$(CONFIGURED_ARCH).deb \
		  snmp_$(SNMPD_VERSION_FULL)_$(CONFIGURED_ARCH).deb \
		  snmpd_$(SNMPD_VERSION_FULL)_$(CONFIGURED_ARCH).deb \
		  snmp-dbgsym_$(SNMPD_VERSION_FULL)_$(CONFIGURED_ARCH).deb \
		  snmpd-dbgsym_$(SNMPD_VERSION_FULL)_$(CONFIGURED_ARCH).deb \
		  libsnmp30_$(SNMPD_VERSION_FULL)_$(CONFIGURED_ARCH).deb \
		  libsnmp30-dbg_$(SNMPD_VERSION_FULL)_$(CONFIGURED_ARCH).deb \
		  libsnmp-dev_$(SNMPD_VERSION_FULL)_$(CONFIGURED_ARCH).deb \
		  libsnmp-perl_$(SNMPD_VERSION_FULL)_$(CONFIGURED_ARCH).deb \
		  python-netsnmp_$(SNMPD_VERSION_FULL)_$(CONFIGURED_ARCH).deb \
		  tkmib_$(SNMPD_VERSION_FULL)_all.deb

$(addprefix $(DEST)/, $(MAIN_TARGET)): $(DEST)/% :
	rm -rf net-snmp-$(SNMPD_VERSION)

	# download debian net-snmp
	dget -u https://sonicstorage.blob.core.windows.net/debian/pool/main/n/net-snmp/net-snmp_$(SNMPD_VERSION_FULL).dsc

	pushd net-snmp-$(SNMPD_VERSION)
	git init
	git add -f *
	git commit -m "unmodified snmpd source"

	# Apply patches
	stg init
	stg import -s ../patch-$(SNMPD_VERSION)/series

	fakeroot debian/rules -j$(SONIC_CONFIG_MAKE_JOBS) binary
	popd

	mv $(DERIVED_TARGETS) $* $(DEST)/

$(addprefix $(DEST)/, $(DERIVED_TARGETS)): $(DEST)/% : $(DEST)/$(MAIN_TARGET)
